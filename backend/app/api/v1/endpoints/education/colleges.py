from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.education.colleges import College, CollegeType
from app.schemas.education.colleges import (
    CollegeCreate,
    CollegeUpdate,
    CollegeResponse
)
from sqlalchemy import func, or_
from app.models.education.review import Review
from app.api.v1.endpoints.deps import get_current_user, require_roles

router = APIRouter(prefix="/colleges", tags=["Colleges"])

from enum import Enum
from typing import List, Optional
from pydantic import Field, field_validator
from sqlalchemy import func, or_
from app.core.location import calculate_haversine_distance
from fastapi_cache.decorator import cache
from app.core.redis import geo_add_location, geo_remove_location, geo_search_nearby, redis_client
import json
import hashlib

# 1. Enums for type-safe filtering and Swagger dropdowns
class SortBy(str, Enum):
    DISTANCE = "distance"
    RATING = "rating"
    NAME = "name"
    ESTABLISHED = "established"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

# 2. Dependency class for clean, validated query parameters
class CollegeFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip"),
        limit: int = Query(10, ge=1, le=100, description="Max records to return (capped at 100)"),
        type: Optional[CollegeType] = Query(None, description="Filter by College Type (e.g. Government, Private)"),
        query: Optional[str] = Query(None, description="Search by name, description, or courses"),
        lat: Optional[float] = Query(None, ge=-90, le=90, description="User's latitude for distance calculation"),
        lon: Optional[float] = Query(None, ge=-180, le=180, description="User's longitude for distance calculation"),
        radius: Optional[float] = Query(10.0, ge=0.5, le=100.0, description="Search radius in km (max 100km)"),
        sort_by: Optional[SortBy] = Query(SortBy.NAME, description="Field to sort by"),
        order: Optional[Order] = Query(Order.ASC, description="Sort order (asc/desc)")
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
        """Generate a unique cache key based on filter parameters."""
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"colleges_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[CollegeResponse])
async def get_colleges(
    filters: CollegeFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a paginated list of colleges with dynamic filtering and sorting.
    Supports:
    - Text search (name, description, etc.)
    - Category/Type filtering
    - Geo-spatial proximity search (if lat/lon/radius provided)
    - Sorting by name, rating, or distance
    """
    
    # 1. Check Redis Cache
    cache_key = filters.get_cache_key()
    try:
        cached_data = await redis_client.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached results for {cache_key}")
            return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"Redis cache error: {e}")

    # 2. Build Base Query (including average rating)
    query = db.query(
        College, 
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Review, Review.college_id == College.id)\
     .filter(College.is_active == True)\
     .group_by(College.id)

    # 3. Apply Dynamic Filters
    if filters.type:
        query = query.filter(College.type == filters.type)
    
    if filters.query:
        search_term = f"%{filters.query}%"
        query = query.filter(
            or_(
                College.name.ilike(search_term),
                College.description.ilike(search_term),
                College.streams_available.ilike(search_term)
            )
        )

    # 4. Handle Geo-spatial logic (Hybrid: Redis + SQL)
    colleges_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    
    if use_geo:
        # Use Redis for high-performance proximity finding
        nearby_results = await geo_search_nearby("geo:colleges", filters.lon, filters.lat, filters.radius)
        nearby_ids = [res["id"] for res in nearby_results]
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
        # Filter DB query to only include nearby colleges
        query = query.filter(College.id.in_(nearby_ids))
        
        # Execute query
        results = query.all()
        for college, avg_rating in results:
            college.distance = dist_map.get(college.id)
            college.rating = float(avg_rating) if avg_rating else 0.0
            colleges_list.append(college)
    else:
        # Standard DB fetch
        results = query.all()
        for college, avg_rating in results:
            college.rating = float(avg_rating) if avg_rating else 0.0
            college.distance = None
            colleges_list.append(college)

    # 5. Apply Sorting
    is_desc = (filters.order == Order.DESC)
    
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        colleges_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.RATING:
        colleges_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        colleges_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)
    elif filters.sort_by == SortBy.ESTABLISHED:
        colleges_list.sort(key=lambda x: x.established_year if x.established_year else 0, reverse=is_desc)

    # 6. Pagination & JSON response
    final_results = colleges_list[filters.skip : filters.skip + filters.limit]
    
    # Simple conversion to dict for caching
    from fastapi.encoders import jsonable_encoder
    json_results = jsonable_encoder(final_results)
    
    # 7. Background: Save to Cache
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_results)) # Cache for 5 mins
    except Exception as e:
        logger.error(f"Failed to cache data: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[CollegeResponse])
async def get_colleges_filtered(
    filters: CollegeFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main colleges search endpoint.
    """
    return await get_colleges(filters, db, current_user)

@router.get("/{college_id}", response_model=CollegeResponse)
@cache(expire=60)
async def get_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    college = db.query(College).filter(
        College.id == college_id, College.is_active == True
    ).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    return college

@router.post("/", response_model=CollegeResponse, status_code=201)
async def create_college(
    college_data: CollegeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    # Check duplicate name
    existing_college = db.query(College).filter(
        College.name == college_data.name
    ).first()

    if existing_college:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="College with this name already exists"
        )

    # Convert request model to plain data. use jsonable_encoder so that
    # HttpUrl values (which are pydantic Url objects) turn into strings
    # before we hand them to SQLAlchemy. otherwise psycopg2 raises
    # "can't adapt type 'pydantic_core._pydantic_core.Url'".
    from fastapi.encoders import jsonable_encoder

    college_dict = jsonable_encoder(college_data)

    # Convert type string → Enum
    if college_dict.get("type"):
        try:
            college_dict["type"] = CollegeType(college_dict["type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid college type"
            )

    college = College(**college_dict)

    db.add(college)
    db.commit()
    db.refresh(college)

    return college

@router.patch("/{college_id}", response_model=CollegeResponse)
async def update_college(
    college_id: int,
    college_data: CollegeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    college = db.query(College).filter(College.id == college_id).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    # encode model to plain data (handles Url → str, etc.)
    from fastapi.encoders import jsonable_encoder
    update_data = jsonable_encoder(college_data, exclude_unset=True)

    # check for duplicate name or code if they are being changed
    if "name" in update_data and update_data["name"] != college.name:
        dup = db.query(College).filter(College.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="College with this name already exists"
            )
    if "college_code" in update_data and update_data["college_code"] != college.college_code:
        dup = db.query(College).filter(College.college_code == update_data["college_code"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="College with this code already exists"
            )

    if "type" in update_data:
        try:
            update_data["type"] = CollegeType(update_data["type"])
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid college type"
            )

    for key, value in update_data.items():
        setattr(college, key, value)

    db.commit()
    db.refresh(college)

    return college

@router.delete("/{college_id}", status_code=204)
async def delete_college(
    college_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    college = db.query(College).filter(College.id == college_id).first()

    if not college:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="College not found"
        )

    # Soft delete
    college.is_active = False
    db.commit()
    
    # Remove from Redis Geo Index
    await geo_remove_location("geo:colleges", college_id)

    return None



# ------------------- REVIEWS -------------------
@router.get("/{college_id}/reviews", response_model=List[ReviewResponse])
async def get_college_reviews(
    college_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.college_id == college_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{college_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_college_review(
    college_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(College).filter(College.id == college_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="College not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["college_id"] = college_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to College {college_id} by user {current_user.id}")
    return review
