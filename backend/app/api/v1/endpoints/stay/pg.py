from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.education.review import Review
from app.schemas.education.review import ReviewCreate, ReviewResponse

from app.core.logger import logger
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.stay.pg import PG, GenderType, RoomType
from app.schemas.stay.pg import (
    PGCreate,
    PGUpdate,
    PGResponse
)
from app.api.v1.endpoints.deps import get_current_user, require_roles
from fastapi.encoders import jsonable_encoder

router = APIRouter(
    prefix="/pgs",
    tags=["PGs"]
)

from app.core.redis import geo_add_location, geo_remove_location, geo_search_nearby
from sqlalchemy import func, or_
from enum import Enum
from fastapi_cache.decorator import cache

class SortBy(str, Enum):
    DISTANCE = "distance"
    RATING = "rating"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

from enum import Enum
from typing import List, Optional
from pydantic import Field
from sqlalchemy import func, or_
from app.core.location import calculate_haversine_distance
from app.core.redis import geo_search_nearby, redis_client
import json
import hashlib

# 1. Enums for type-safe filtering
# SortBy and Order are already defined above

# 2. Dependency class for clean filters
class PGFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        gender: Optional[GenderType] = Query(None, description="Filter by Gender"),
        room_type: Optional[RoomType] = Query(None, description="Filter by Room Type"),
        query: Optional[str] = Query(None, description="Search by PG name, address or description"),
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
        return f"pgs_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[PGResponse])
async def get_pgs(
    filters: PGFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get PGs with advanced dynamic filtering, caching, and geo-proximity sorting.
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
        PG, 
        func.avg(Review.rating).label("avg_rating")
    ).outerjoin(Review, Review.pg_id == PG.id)\
     .filter(PG.is_active == True)\
     .group_by(PG.id)

    # 3. Dynamic Filters
    if filters.gender:
        query = query.filter(PG.gender == filters.gender)
    if filters.room_type:
        query = query.filter(PG.room_type == filters.room_type)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(
            PG.name.ilike(search), 
            PG.address.ilike(search),
            PG.description.ilike(search),
            PG.facilities_available.ilike(search)
        ))

    # 4. Geo-spatial Logic (Inclusive Search)
    pgs_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    dist_map = {}
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:pgs", filters.lon, filters.lat, filters.radius)
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
    results = query.all()
    for pg, avg_rating in results:
        pg.rating = float(avg_rating) if avg_rating else 0.0
        pg.distance = dist_map.get(pg.id)
        pgs_list.append(pg)

    # 5. Sorting (Prioritize distance if geolocation is active)
    is_desc = (filters.order == Order.DESC)
    
    # If no explicit sorting provided and we have geo, use distance
    sort_criterion = filters.sort_by
    if use_geo and (not filters.sort_by or filters.sort_by == SortBy.NAME):
        sort_criterion = SortBy.DISTANCE
        
    if sort_criterion == SortBy.DISTANCE and use_geo:
        pgs_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif sort_criterion == SortBy.RATING:
        pgs_list.sort(key=lambda x: x.rating, reverse=is_desc)
    elif sort_criterion == SortBy.NAME:
        pgs_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = pgs_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[PGResponse])
async def get_pgs_filtered(
    filters: PGFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main PGs search endpoint.
    """
    return await get_pgs(filters, db, current_user)

@router.get("/{pg_id}", response_model=PGResponse)
@cache(expire=60)
async def get_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    pg = db.query(PG).filter(PG.id == pg_id, PG.is_active == True).first()
    if not pg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PG not found"
        )
    return pg

@router.post("/", response_model=PGResponse, status_code=status.HTTP_201_CREATED)
async def create_pg(
    pg_data: PGCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    existing_pg = db.query(PG).filter(PG.name == pg_data.name).first()
    if existing_pg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PG with this name already exists"
        )

    pg_dict = jsonable_encoder(pg_data)
    
    if "gender" in pg_dict and pg_dict["gender"]:
        try:
            pg_dict["gender"] = GenderType(pg_dict["gender"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid gender type")
            
    if "room_type" in pg_dict and pg_dict["room_type"]:
        try:
            pg_dict["room_type"] = RoomType(pg_dict["room_type"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room type")

    pg = PG(**pg_dict)
    db.add(pg)
    db.commit()
    db.refresh(pg)
    
    # Sync with Redis Geo
    if pg.latitude and pg.longitude:
        await geo_add_location("geo:pgs", pg.longitude, pg.latitude, pg.id)
        
    logger.info(f"PG created successfully: {pg.name} by user {current_user.id}")
    return pg

@router.patch("/{pg_id}", response_model=PGResponse)
async def update_pg(
    pg_id: int,
    pg_data: PGUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    pg = db.query(PG).filter(PG.id == pg_id, PG.is_active == True).first()
    if not pg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PG not found"
        )

    update_data = jsonable_encoder(pg_data, exclude_unset=True)

    if "name" in update_data and update_data["name"] != pg.name:
        dup = db.query(PG).filter(PG.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="PG with this name already exists"
            )

    if "gender" in update_data and update_data["gender"]:
        try:
            update_data["gender"] = GenderType(update_data["gender"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid gender type")
            
    if "room_type" in update_data and update_data["room_type"]:
        try:
            update_data["room_type"] = RoomType(update_data["room_type"])
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid room type")

    for key, value in update_data.items():
        setattr(pg, key, value)

    db.commit()
    db.refresh(pg)
    
    # Sync with Redis Geo
    if pg.latitude and pg.longitude:
        await geo_add_location("geo:pgs", pg.longitude, pg.latitude, pg.id)
    else:
        await geo_remove_location("geo:pgs", pg.id)
        
    logger.info(f"PG updated successfully: {pg.name} by user {current_user.id}")
    return pg

@router.delete("/{pg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pg(
    pg_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    pg = db.query(PG).filter(PG.id == pg_id, PG.is_active == True).first()
    if not pg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PG not found"
        )
    
    # Remove from Redis Geo Index
    await geo_remove_location("geo:pgs", pg_id)
    
    logger.info(f"PG deleted successfully: {pg.id} by user {current_user.id}")
    return None


# ------------------- REVIEWS -------------------
@router.get("/{pg_id}/reviews", response_model=List[ReviewResponse])
async def get_pg_reviews(
    pg_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    reviews = db.query(Review).filter(
        Review.pg_id == pg_id, Review.is_active == True
    ).offset(skip).limit(limit).all()
    return reviews


@router.post("/{pg_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_pg_review(
    pg_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    entity = db.query(PG).filter(PG.id == pg_id).first()
    if not entity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG not found")
        
    review_dict = review_data.model_dump()
    review_dict["user_id"] = current_user.id
    review_dict["pg_id"] = pg_id
    
    review = Review(**review_dict)
    db.add(review)
    db.commit()
    db.refresh(review)
    
    logger.info(f"Review added to PG {pg_id} by user {current_user.id}")
    return review
