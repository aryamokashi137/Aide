from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from app.core.database import get_db
from app.core.logger import logger
from app.api.v1.endpoints.deps import get_current_user, require_roles
from app.models.medical.doctor import Doctor
from app.models.medical.review import MedicalReview
from app.schemas.medical.doctor import DoctorCreate, DoctorUpdate, DoctorResponse
from app.schemas.medical.review import MedicalReviewCreate, MedicalReviewResponse

from enum import Enum

class SortBy(str, Enum):
    DISTANCE = "distance"
    RATING = "rating"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

class DoctorSpecialization(str, Enum):
    CARDIOLOGIST = "Cardiologist"
    DERMATOLOGIST = "Dermatologist"
    NEUROLOGIST = "Neurologist"
    PEDIATRICIAN = "Pediatrician"
    PSYCHIATRIST = "Psychiatrist"
    SURGEON = "Surgeon"
    GENERAL_PHYSICIAN = "General Physician"

router = APIRouter(prefix="/doctors", tags=["Doctors"])

from sqlalchemy import func, or_
from app.core.redis import redis_client
import json
import hashlib

# 1. Enums for type-safe filtering
# SortBy, Order, DoctorSpecialization are already defined above

# 2. Dependency class for clean filters
class DoctorFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        specialization: Optional[DoctorSpecialization] = Query(None, description="Filter by Specialization"),
        hospital_id: Optional[int] = Query(None, description="Filter by Hospital ID"),
        query: Optional[str] = Query(None, description="Search by doctor name"),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.specialization = specialization
        self.hospital_id = hospital_id
        self.query = query
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"doctors_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[DoctorResponse])
async def get_doctors(
    filters: DoctorFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get doctors with advanced dynamic filtering, caching, and hospital sorting.
    """
    # 1. Cache lookup
    cache_key = filters.get_cache_key()
    try:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Cache miss error: {e}")

    # 2. Build Base Query
    query = db.query(
        Doctor, 
        func.avg(MedicalReview.rating).label("avg_rating")
    ).outerjoin(MedicalReview, MedicalReview.doctor_id == Doctor.id)\
     .filter(Doctor.is_active == True)\
     .group_by(Doctor.id)

    # 3. Dynamic Filters
    if filters.specialization:
        query = query.filter(Doctor.specialization == filters.specialization)
    if filters.hospital_id:
        query = query.filter(Doctor.hospital_id == filters.hospital_id)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(Doctor.name.ilike(search))

    # 4. Fetch results
    results = query.all()
    doctors_list = []
    for doctor, avg_rating in results:
        doctor.rating = float(avg_rating) if avg_rating else 0.0
        doctors_list.append(doctor)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.RATING:
        doctors_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        doctors_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = doctors_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[DoctorResponse])
async def get_doctors_filtered(
    filters: DoctorFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main doctors search endpoint.
    """
    return await get_doctors(filters, db, current_user)

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.is_active == True).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.post("/", response_model=DoctorResponse, status_code=201)
async def create_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    doctor_dict = jsonable_encoder(doctor_data)
    doctor = Doctor(**doctor_dict)
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    logger.info(f"Doctor added: {doctor.name} by admin {current_user.id}")
    return doctor

@router.patch("/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(
    doctor_id: int,
    doctor_data: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.is_active == True).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    update_data = jsonable_encoder(doctor_data, exclude_unset=True)
    for key, value in update_data.items():
        setattr(doctor, key, value)
    
    db.commit()
    db.refresh(doctor)
    logger.info(f"Doctor updated: {doctor_id} by admin {current_user.id}")
    return doctor

@router.delete("/{doctor_id}", status_code=204)
async def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id, Doctor.is_active == True).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Soft delete
    doctor.is_active = False
    db.commit()
    logger.warning(f"Doctor deleted: {doctor_id} by admin {current_user.id}")
    return None

# Reviews
@router.get("/{doctor_id}/reviews", response_model=List[MedicalReviewResponse])
async def get_doctor_reviews(
    doctor_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(MedicalReview).filter(
        MedicalReview.doctor_id == doctor_id,
        MedicalReview.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews

@router.post("/{doctor_id}/reviews", response_model=MedicalReviewResponse, status_code=201)
async def create_doctor_review(
    doctor_id: int,
    review_data: MedicalReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["doctor_id"] = doctor_id
    
    review = MedicalReview(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info(f"Medical review added for doctor {doctor_id} by user {current_user.id}")
    return review
