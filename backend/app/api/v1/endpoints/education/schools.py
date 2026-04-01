from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.education.schools import School, SchoolType, BoardType
from app.schemas.education.schools import (
    SchoolCreate,
    SchoolUpdate,
    SchoolResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder
from enum import Enum
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/schools", tags=["Schools"])

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
class SchoolFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        type: Optional[SchoolType] = Query(None, description="Filter by School Type"),
        board: Optional[BoardType] = Query(None, description="Filter by Board Type"),
        query: Optional[str] = Query(None, description="Search by name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(10.0, ge=0.1, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.type = type
        self.board = board
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"schools_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[SchoolResponse])
async def get_schools(
    filters: SchoolFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get schools with advanced dynamic filtering, caching, and geo-proximity sorting.
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
        School, 
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Review, Review.school_id == School.id)\
     .filter(School.is_active == True)\
     .group_by(School.id)

    # 3. Dynamic Filters
    if filters.type:
        query = query.filter(School.type == filters.type)
    if filters.board:
        query = query.filter(School.board == filters.board)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(School.name.ilike(search), School.address.ilike(search)))

    # 4. Geo-spatial Logic (Inclusive Search)
    schools_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    dist_map = {}
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:schools", filters.lon, filters.lat, filters.radius)
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
    results = query.all()
    for school, avg_rating in results:
        school.rating = float(avg_rating) if avg_rating else 0.0
        school.distance = dist_map.get(school.id)
        schools_list.append(school)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        schools_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.RATING:
        schools_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        schools_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = schools_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")
    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[SchoolResponse])
async def get_schools_filtered(
    filters: SchoolFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main schools search endpoint.
    """
    return await get_schools(filters, db, current_user)

# ------------------- GET ONE -------------------
@router.get("/{school_id}", response_model=SchoolResponse)
@cache(expire=60)
async def get_school(
    school_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    school = db.query(School).filter(School.id == school_id, School.is_active == True).first()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    return school

# ------------------- CREATE -------------------
@router.post("/", response_model=SchoolResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    school_data: SchoolCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    # Check duplicate name
    existing_school = db.query(School).filter(School.name == school_data.name).first()
    if existing_school:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="School with this name already exists"
        )

    school_dict = jsonable_encoder(school_data)

    # Convert type string → Enum
    if school_dict.get("type"):
        try:
            school_dict["type"] = SchoolType(school_dict["type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid school type"
            )

    if school_dict.get("board"):
        try:
            school_dict["board"] = BoardType(school_dict["board"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid board type"
            )

    school = School(**school_dict)
    db.add(school)
    db.commit()
    db.refresh(school)

    return school

# ------------------- UPDATE -------------------
@router.patch("/{school_id}", response_model=SchoolResponse)
async def update_school(
    school_id: int,
    school_data: SchoolUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    school = db.query(School).filter(School.id == school_id, School.is_active == True).first()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    update_data = jsonable_encoder(school_data, exclude_unset=True)

    # Check for duplicate name
    if "name" in update_data and update_data["name"] != school.name:
        dup = db.query(School).filter(School.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="School with this name already exists"
            )

    # Enum conversion
    if "type" in update_data:
        try:
            update_data["type"] = SchoolType(update_data["type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid school type"
            )
    if "board" in update_data:
        try:
            update_data["board"] = BoardType(update_data["board"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid board type"
            )

    for key, value in update_data.items():
        setattr(school, key, value)

    db.commit()
    db.refresh(school)
    
    # Sync with Redis Geo
    if school.latitude and school.longitude:
        await geo_add_location("geo:schools", school.longitude, school.latitude, school.id)
        
    return school

# ------------------- DELETE -------------------
@router.delete("/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_school(
    school_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    school = db.query(School).filter(School.id == school_id, School.is_active == True).first()

    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )

    # Soft delete
    # Remove from Redis Geo Index
    await geo_remove_location("geo:schools", school_id)
    
    return None

# ------------------- REVIEWS -------------------
@router.get("/{school_id}/reviews", response_model=List[ReviewResponse])
async def get_school_reviews(
    school_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.school_id == school_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{school_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_school_review(
    school_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(School).filter(School.id == school_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["school_id"] = school_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to School {school_id} by user {current_user.id}")
    return review
