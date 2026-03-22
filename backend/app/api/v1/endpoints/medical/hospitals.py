from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from app.core.database import get_db
from app.core.logger import logger
from app.api.v1.endpoints.deps import get_current_user, require_roles
from app.models.medical.hospital import Hospital
from app.models.medical.review import MedicalReview
from app.schemas.medical.hospital import HospitalCreate, HospitalUpdate, HospitalResponse
from app.schemas.medical.review import MedicalReviewCreate, MedicalReviewResponse

from app.core.location import calculate_haversine_distance

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

@router.get("/", response_model=List[HospitalResponse])
async def get_hospitals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    lat: Optional[float] = Query(None, description="User's current latitude"),
    lon: Optional[float] = Query(None, description="User's current longitude"),
    radius: Optional[float] = Query(None, description="Radius in km", ge=0.1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get hospitals with optional category filtering and nearby search.
    If lat and lon are provided, hospitals will be sorted by distance.
    If radius is also provided, results will be filtered within that radius.
    """
    query = db.query(Hospital).filter(Hospital.is_active == True)
    if name:
        query = query.filter(Hospital.name.ilike(f"%{name}%"))
    if category:
        query = query.filter(Hospital.category.ilike(f"%{category}%"))
    
    # Execute query
    hospitals = query.all()
    
    # Logic for nearby search
    if lat is not None and lon is not None:
        nearby_hospitals = []
        for hospital in hospitals:
            if hospital.latitude and hospital.longitude:
                dist = calculate_haversine_distance(lat, lon, hospital.latitude, hospital.longitude)
                
                # Assign distance to the model object (Pydantic will pick it up)
                hospital.distance = round(dist, 2)
                
                if radius is None or dist <= radius:
                    nearby_hospitals.append(hospital)
        
        # Sort by distance
        nearby_hospitals.sort(key=lambda x: x.distance)
        
        # Apply pagination after sorting
        return nearby_hospitals[skip : skip + limit]
        
    # Standard pagination for non-location search
    return query.offset(skip).limit(limit).all()


@router.get("/{hospital_id}", response_model=HospitalResponse)
async def get_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.post("/", response_model=HospitalResponse, status_code=201)
async def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hospital_dict = jsonable_encoder(hospital_data)
    hospital = Hospital(**hospital_dict)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    logger.info(f"Hospital created: {hospital.name} by admin {current_user.id}")
    return hospital

@router.patch("/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: int,
    hospital_data: HospitalUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    update_data = jsonable_encoder(hospital_data, exclude_unset=True)
    for key, value in update_data.items():
        setattr(hospital, key, value)
    
    db.commit()
    db.refresh(hospital)
    logger.info(f"Hospital updated: {hospital_id} by admin {current_user.id}")
    return hospital

@router.delete("/{hospital_id}", status_code=204)
async def delete_hospital(
    hospital_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id, Hospital.is_active == True).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Soft delete
    hospital.is_active = False
    db.commit()
    logger.warning(f"Hospital deleted: {hospital_id} by admin {current_user.id}")
    return None

# Reviews
@router.get("/{hospital_id}/reviews", response_model=List[MedicalReviewResponse])
async def get_hospital_reviews(
    hospital_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(MedicalReview).filter(
        MedicalReview.hospital_id == hospital_id,
        MedicalReview.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews

@router.post("/{hospital_id}/reviews", response_model=MedicalReviewResponse, status_code=201)
async def create_hospital_review(
    hospital_id: int,
    review_data: MedicalReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["hospital_id"] = hospital_id
    
    review = MedicalReview(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    logger.info(f"Medical review added for hospital {hospital_id} by user {current_user.id}")
    return review
