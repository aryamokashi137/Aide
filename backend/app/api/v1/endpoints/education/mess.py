from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.education.mess import Mess, MessType
from app.schemas.education.mess import (
    MessCreate,
    MessUpdate,
    MessResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder
from enum import Enum
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/mess", tags=["Mess"])

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
class MessFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        meal_type: Optional[MessType] = Query(None, description="Filter by Meal Type"),
        query: Optional[str] = Query(None, description="Search by name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(10.0, ge=0.5, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.meal_type = meal_type
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"mess_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[MessResponse])
async def get_mess_list(
    filters: MessFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get mess list with advanced dynamic filtering, caching, and geo-proximity sorting.
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
        Mess, 
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Review, Review.mess_id == Mess.id)\
     .filter(Mess.is_active == True)\
     .group_by(Mess.id)

    # 3. Dynamic Filters
    if filters.meal_type:
        query = query.filter(Mess.meal_types == filters.meal_type)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(Mess.name.ilike(search), Mess.address.ilike(search)))

    # 4. Geo-spatial Logic (Inclusive Search)
    mess_data_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    dist_map = {}
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:mess", filters.lon, filters.lat, filters.radius)
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
    results = query.all()
    for mess, avg_rating in results:
        mess.rating = float(avg_rating) if avg_rating else 0.0
        mess.distance = dist_map.get(mess.id)
        mess_data_list.append(mess)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        mess_data_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.RATING:
        mess_data_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        mess_data_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = mess_data_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[MessResponse])
async def get_mess_filtered(
    filters: MessFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main Mess search endpoint.
    """
    return await get_mess(filters, db, current_user)

# ------------------- GET ONE -------------------
@router.get("/{mess_id}", response_model=MessResponse)
@cache(expire=60)
async def get_mess(
    mess_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    mess = db.query(Mess).filter(Mess.id == mess_id, Mess.is_active == True).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess not found"
        )
    return mess

# ------------------- CREATE -------------------
@router.post("/", response_model=MessResponse, status_code=status.HTTP_201_CREATED)
async def create_mess(
    mess_data: MessCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    # Check duplicate name
    existing_mess = db.query(Mess).filter(Mess.name == mess_data.name).first()
    if existing_mess:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mess with this name already exists"
        )

    mess_dict = jsonable_encoder(mess_data)

    # Convert meal_types string → Enum
    if mess_dict.get("meal_types"):
        try:
            mess_dict["meal_types"] = MessType(mess_dict["meal_types"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid meal type"
            )

    mess = Mess(**mess_dict)
    db.add(mess)
    db.commit()
    db.refresh(mess)

    return mess

# ------------------- UPDATE -------------------
@router.patch("/{mess_id}", response_model=MessResponse)
async def update_mess(
    mess_id: int,
    mess_data: MessUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    mess = db.query(Mess).filter(Mess.id == mess_id, Mess.is_active == True).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess not found"
        )

    update_data = jsonable_encoder(mess_data, exclude_unset=True)

    # Check for duplicate name
    if "name" in update_data and update_data["name"] != mess.name:
        dup = db.query(Mess).filter(Mess.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mess with this name already exists"
            )

    # Enum conversion
    if "meal_types" in update_data:
        try:
            update_data["meal_types"] = MessType(update_data["meal_types"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid meal type"
            )

    for key, value in update_data.items():
        setattr(mess, key, value)

    db.commit()
    db.refresh(mess)
    return mess

# ------------------- DELETE -------------------
@router.delete("/{mess_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mess(
    mess_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    mess = db.query(Mess).filter(Mess.id == mess_id, Mess.is_active == True).first()

    if not mess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mess not found"
        )

    # Soft delete
    mess.is_active = False
    db.commit()
    return None


# ------------------- REVIEWS -------------------
@router.get("/{mess_id}/reviews", response_model=List[ReviewResponse])
async def get_mess_reviews(
    mess_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.mess_id == mess_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{mess_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_mess_review(
    mess_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(Mess).filter(Mess.id == mess_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mess not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["mess_id"] = mess_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to Mess {mess_id} by user {current_user.id}")
    return review
