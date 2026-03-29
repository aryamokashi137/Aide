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
from fastapi_cache.decorator import cache
from app.core.redis import geo_add_location, geo_remove_location, geo_search_nearby
from sqlalchemy import func, or_
from enum import Enum

class SortBy(str, Enum):
    DISTANCE = "distance"
    RATING = "rating"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

class HospitalCategory(str, Enum):
    GOVERNMENT = "Government"
    PRIVATE = "Private"
    GENERAL = "General"
    MULTISPECIALITY = "Multispeciality"

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

from enum import Enum
from typing import List, Optional
from pydantic import Field
from sqlalchemy import func, or_
from app.core.location import calculate_haversine_distance
from app.core.redis import geo_search_nearby, redis_client
import json
import hashlib

# 3. Dependency class for clean filters
class HospitalFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        category: Optional[HospitalCategory] = Query(None, description="Filter by Category"),
        query: Optional[str] = Query(None, description="Search by name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(20.0, ge=0.5, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.category = category
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"hospitals_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[HospitalResponse])
async def get_hospitals(
    filters: HospitalFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get hospitals with advanced dynamic filtering, caching, and geo-proximity sorting.
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
        Hospital, 
        func.avg(MedicalReview.rating).label("avg_rating")
    ).outerjoin(MedicalReview, MedicalReview.hospital_id == Hospital.id)\
     .filter(Hospital.is_active == True)\
     .group_by(Hospital.id)

    # 3. Dynamic Filters
    if filters.category:
        query = query.filter(Hospital.category == filters.category)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(Hospital.name.ilike(search), Hospital.address.ilike(search)))

    # 4. Geo-spatial Logic
    hospitals_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:hospitals", filters.lon, filters.lat, filters.radius)
        nearby_ids = [res["id"] for res in nearby_results]
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
        query = query.filter(Hospital.id.in_(nearby_ids))
        results = query.all()
        for hospital, avg_rating in results:
            hospital.distance = dist_map.get(hospital.id)
            hospital.rating = float(avg_rating) if avg_rating else 0.0
            hospitals_list.append(hospital)
    else:
        results = query.all()
        for hospital, avg_rating in results:
            hospital.rating = float(avg_rating) if avg_rating else 0.0
            hospital.distance = None
            hospitals_list.append(hospital)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        hospitals_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.RATING:
        hospitals_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        hospitals_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = hospitals_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[HospitalResponse])
async def get_hospitals_filtered(
    filters: HospitalFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main hospitals search endpoint.
    """
    return await get_hospitals(filters, db, current_user)


@router.get("/{hospital_id}", response_model=HospitalResponse)
@cache(expire=60)
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
    # Add to Redis Geo Index
    if hospital.latitude and hospital.longitude:
        await geo_add_location("geo:hospitals", hospital.longitude, hospital.latitude, hospital.id)
        
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
    
    # Update Redis Geo Index
    if hospital.latitude and hospital.longitude:
        await geo_add_location("geo:hospitals", hospital.longitude, hospital.latitude, hospital.id)
    else:
        await geo_remove_location("geo:hospitals", hospital.id)
        
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
    # Remove from Redis Geo Index
    await geo_remove_location("geo:hospitals", hospital_id)
    
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
