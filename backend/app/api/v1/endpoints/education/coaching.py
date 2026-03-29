from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.education.coaching import Coaching, CoachingType
from app.schemas.education.coaching import (
    CoachingCreate,
    CoachingUpdate,
    CoachingResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder
from enum import Enum
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/coaching", tags=["Coaching"])

from pydantic import Field
from sqlalchemy import func, or_
from app.core.location import calculate_haversine_distance
from app.core.redis import geo_search_nearby, redis_client
import json
import hashlib

# 1. Enums for type-safe filtering
class SortBy(str, Enum):
    DISTANCE = "distance"
    RATING = "rating"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

# 2. Dependency class for clean filters
class CoachingFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        type: Optional[CoachingType] = Query(None, description="Filter by Coaching Type"),
        query: Optional[str] = Query(None, description="Search by name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(10.0, ge=0.5, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.type = type
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"coaching_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[CoachingResponse])
async def get_coaching_classes(
    filters: CoachingFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get coaching classes with advanced dynamic filtering, caching, and geo-proximity sorting.
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
        Coaching, 
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Review, Review.coaching_id == Coaching.id)\
     .filter(Coaching.is_active == True)\
     .group_by(Coaching.id)

    # 3. Dynamic Filters
    if filters.type:
        query = query.filter(Coaching.coaching_type == filters.type)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(Coaching.name.ilike(search), Coaching.address.ilike(search)))

    # 4. Geo-spatial Logic
    coaching_data_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:coaching", filters.lon, filters.lat, filters.radius)
        nearby_ids = [res["id"] for res in nearby_results]
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
        query = query.filter(Coaching.id.in_(nearby_ids))
        results = query.all()
        for coaching, avg_rating in results:
            coaching.distance = dist_map.get(coaching.id)
            coaching.rating = float(avg_rating) if avg_rating else 0.0
            coaching_data_list.append(coaching)
    else:
        results = query.all()
        for coaching, avg_rating in results:
            coaching.rating = float(avg_rating) if avg_rating else 0.0
            coaching.distance = None
            coaching_data_list.append(coaching)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        coaching_data_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.RATING:
        coaching_data_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        coaching_data_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = coaching_data_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[CoachingResponse])
async def get_coaching_filtered(
    filters: CoachingFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main Coaching search endpoint.
    """
    return await get_coaching_classes(filters, db, current_user)

# ------------------- GET ONE -------------------
@router.get("/{coaching_id}", response_model=CoachingResponse)
@cache(expire=60)
async def get_coaching_class(
    coaching_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    coaching = db.query(Coaching).filter(Coaching.id == coaching_id, Coaching.is_active == True).first()

    if not coaching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching class not found"
        )
    return coaching

# ------------------- CREATE -------------------
@router.post("/", response_model=CoachingResponse, status_code=status.HTTP_201_CREATED)
async def create_coaching_class(
    coaching_data: CoachingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    # Check duplicate name
    existing_coaching = db.query(Coaching).filter(Coaching.name == coaching_data.name).first()
    if existing_coaching:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coaching class with this name already exists"
        )

    coaching_dict = jsonable_encoder(coaching_data)

    # Convert coaching_type string → Enum
    if coaching_dict.get("coaching_type"):
        try:
            coaching_dict["coaching_type"] = CoachingType(coaching_dict["coaching_type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coaching type"
            )

    coaching = Coaching(**coaching_dict)
    db.add(coaching)
    db.commit()
    db.refresh(coaching)

    return coaching

# ------------------- UPDATE -------------------
@router.patch("/{coaching_id}", response_model=CoachingResponse)
async def update_coaching_class(
    coaching_id: int,
    coaching_data: CoachingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    coaching = db.query(Coaching).filter(Coaching.id == coaching_id, Coaching.is_active == True).first()

    if not coaching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching class not found"
        )

    update_data = jsonable_encoder(coaching_data, exclude_unset=True)

    # Check for duplicate name
    if "name" in update_data and update_data["name"] != coaching.name:
        dup = db.query(Coaching).filter(Coaching.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Coaching class with this name already exists"
            )

    # Enum conversion
    if "coaching_type" in update_data:
        try:
            update_data["coaching_type"] = CoachingType(update_data["coaching_type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coaching type"
            )

    for key, value in update_data.items():
        setattr(coaching, key, value)

    db.commit()
    db.refresh(coaching)
    return coaching

# ------------------- DELETE -------------------
@router.delete("/{coaching_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coaching_class(
    coaching_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    coaching = db.query(Coaching).filter(Coaching.id == coaching_id, Coaching.is_active == True).first()

    if not coaching:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coaching class not found"
        )

    # Soft delete
    coaching.is_active = False
    db.commit()
    return None


# ------------------- REVIEWS -------------------
@router.get("/{coaching_id}/reviews", response_model=List[ReviewResponse])
async def get_coaching_reviews(
    coaching_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.coaching_id == coaching_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{coaching_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_coaching_review(
    coaching_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(Coaching).filter(Coaching.id == coaching_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coaching not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["coaching_id"] = coaching_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to Coaching {coaching_id} by user {current_user.id}")
    return review
