from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from enum import Enum
from pydantic import Field
from sqlalchemy import func, or_
import json
import hashlib

from app.core.database import get_db
from app.core.logger import logger
from app.api.v1.endpoints.deps import get_current_user, require_roles
from app.models.stay.hostels import Hostel, GenderType, RoomType
from app.models.education.review import Review
from app.schemas.stay.hostels import HostelCreate, HostelUpdate, HostelResponse
from app.schemas.education.review import ReviewCreate, ReviewResponse
from app.core.location import calculate_haversine_distance
from app.core.redis import geo_add_location, geo_remove_location, geo_search_nearby, redis_client
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/hostels",
    tags=["Hostels"]
)

# 1. Enums for type-safe filtering
class SortBy(str, Enum):
    DISTANCE = "distance"
    RATING = "rating"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

# 2. Dependency class for clean filters
class HostelFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        gender: Optional[GenderType] = Query(None, description="Filter by Gender"),
        room_type: Optional[RoomType] = Query(None, description="Filter by Room Type"),
        query: Optional[str] = Query(None, description="Search by Hostel name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(20.0, ge=0.5, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.gender = gender
        self.room_type = room_type
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"hostels_search:{hashlib.md5(params_str.encode()).hexdigest()}"

# ------------------- GET ALL -------------------
@router.get("/", response_model=List[HostelResponse])
async def get_hostels(
    filters: HostelFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get Hostels with advanced dynamic filtering, caching, and geo-proximity sorting.
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
        Hostel, 
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Review, Review.hostel_id == Hostel.id)\
     .filter(Hostel.is_active == True)\
     .group_by(Hostel.id)

    # 3. Dynamic Filters
    if filters.gender:
        query = query.filter(Hostel.gender == filters.gender)
    if filters.room_type:
        query = query.filter(Hostel.room_type == filters.room_type)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(Hostel.name.ilike(search), Hostel.address.ilike(search)))

    # 4. Geo-spatial Logic
    hostels_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:hostels", filters.lon, filters.lat, filters.radius)
        nearby_ids = [res["id"] for res in nearby_results]
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
        query = query.filter(Hostel.id.in_(nearby_ids))
        results = query.all()
        for hostel, avg_rating in results:
            hostel.distance = dist_map.get(hostel.id)
            hostel.rating = float(avg_rating) if avg_rating else 0.0
            hostels_list.append(hostel)
    else:
        results = query.all()
        for hostel, avg_rating in results:
            hostel.rating = float(avg_rating) if avg_rating else 0.0
            hostel.distance = None
            hostels_list.append(hostel)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        hostels_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.RATING:
        hostels_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        hostels_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = hostels_list[filters.skip : filters.skip + filters.limit]
    
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[HostelResponse])
async def get_hostels_filtered(
    filters: HostelFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main hostels search endpoint.
    """
    return await get_hostels(filters, db, current_user)

# ------------------- GET ONE -------------------
@router.get("/{hostel_id}", response_model=HostelResponse)
async def get_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id, Hostel.is_active == True).first()
    if not hostel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
    return hostel

# ------------------- CREATE -------------------
@router.post("/", response_model=HostelResponse, status_code=status.HTTP_201_CREATED)
async def create_hostel(
    hostel_data: HostelCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    existing_hostel = db.query(Hostel).filter(Hostel.name == hostel_data.name).first()
    if existing_hostel:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Hostel with this name already exists")

    hostel_dict = jsonable_encoder(hostel_data)
    hostel = Hostel(**hostel_dict)
    db.add(hostel)
    db.commit()
    db.refresh(hostel)
    
    if hostel.latitude and hostel.longitude:
        await geo_add_location("geo:hostels", hostel.longitude, hostel.latitude, hostel.id)
        
    logger.info(f"Hostel created successfully: {hostel.name} by user {current_user.id}")
    return hostel

# ------------------- UPDATE -------------------
@router.patch("/{hostel_id}", response_model=HostelResponse)
async def update_hostel(
    hostel_id: int,
    hostel_data: HostelUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id, Hostel.is_active == True).first()
    if not hostel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")

    update_data = jsonable_encoder(hostel_data, exclude_unset=True)
    for key, value in update_data.items():
        setattr(hostel, key, value)

    db.commit()
    db.refresh(hostel)
    
    if hostel.latitude and hostel.longitude:
        await geo_add_location("geo:hostels", hostel.longitude, hostel.latitude, hostel.id)
    else:
        await geo_remove_location("geo:hostels", hostel.id)
        
    logger.info(f"Hostel updated successfully: {hostel.name} by user {current_user.id}")
    return hostel

# ------------------- DELETE -------------------
@router.delete("/{hostel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hostel(
    hostel_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    hostel = db.query(Hostel).filter(Hostel.id == hostel_id, Hostel.is_active == True).first()
    if not hostel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
    
    hostel.is_active = False
    await geo_remove_location("geo:hostels", hostel_id)
    db.commit()
    logger.info(f"Hostel deleted successfully: {hostel.id} by user {current_user.id}")
    return None

# ------------------- REVIEWS -------------------
@router.get("/{hostel_id}/reviews", response_model=List[ReviewResponse])
async def get_hostel_reviews(
    hostel_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.hostel_id == hostel_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews

@router.post("/{hostel_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_hostel_review(
    hostel_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(Hostel).filter(Hostel.id == hostel_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hostel not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["hostel_id"] = hostel_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to Hostel {hostel_id} by user {current_user.id}")
    return review
