from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from app.core.database import get_db
from app.core.logger import logger
from app.api.v1.endpoints.deps import get_current_user, require_roles
from app.models.medical.ambulance import Ambulance
from app.schemas.medical.ambulance import AmbulanceCreate, AmbulanceUpdate, AmbulanceResponse

router = APIRouter(prefix="/ambulances", tags=["Ambulances"])

from enum import Enum
from typing import List, Optional
from pydantic import Field
from sqlalchemy import func, or_
from app.core.location import calculate_haversine_distance
from app.core.redis import geo_add_location, geo_remove_location, geo_search_nearby, redis_client
from fastapi_cache.decorator import cache
import json
import hashlib

class SortBy(str, Enum):
    DISTANCE = "distance"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

class AmbulanceType(str, Enum):
    BASIC = "Basic"
    ADVANCED = "Advanced"
    AIR = "Air"
    MORTUARY = "Mortuary"

@router.get("/", response_model=List[AmbulanceResponse])

# 3. Dependency class for clean filters
class AmbulanceFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        type: Optional[AmbulanceType] = Query(None, description="Filter by Ambulance Type"),
        available_only: bool = Query(False, description="Show only currently available ambulances"),
        query: Optional[str] = Query(None, description="Search by provider name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(20.0, ge=0.5, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.type = type
        self.available_only = available_only
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"ambulances_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[AmbulanceResponse])
async def get_ambulances(
    filters: AmbulanceFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get ambulances with advanced dynamic filtering, caching, and geo-proximity sorting.
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
    query = db.query(Ambulance).filter(Ambulance.is_active == True)

    # 3. Dynamic Filters
    if filters.type:
        query = query.filter(Ambulance.type == filters.type)
    if filters.available_only:
        query = query.filter(Ambulance.availability == True)
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(Ambulance.provider_name.ilike(search), Ambulance.address.ilike(search)))

    # 4. Geo-spatial Logic
    ambulances_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    
    if use_geo:
        nearby_results = await geo_search_nearby("geo:ambulances", filters.lon, filters.lat, filters.radius)
        nearby_ids = [res["id"] for res in nearby_results]
        dist_map = {res["id"]: res["dist"] for res in nearby_results}
        
        query = query.filter(Ambulance.id.in_(nearby_ids))
        results = query.all()
        for ambulance in results:
            ambulance.distance = dist_map.get(ambulance.id)
            ambulance.rating = 0.0 # Ambulances don't have reviews in this model yet
            ambulances_list.append(ambulance)
    else:
        results = query.all()
        for ambulance in results:
            ambulance.rating = 0.0
            ambulance.distance = None
            ambulances_list.append(ambulance)

    # 5. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        ambulances_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        ambulances_list.sort(key=lambda x: x.provider_name.lower(), reverse=is_desc)

    # 6. Pagination & Caching
    final_results = ambulances_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[AmbulanceResponse])
async def get_ambulances_filtered(
    filters: AmbulanceFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main ambulances search endpoint.
    """
    return await get_ambulances(filters, db, current_user)

@router.get("/{ambulance_id}", response_model=AmbulanceResponse)
@cache(expire=60)
async def get_ambulance(
    ambulance_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id, Ambulance.is_active == True).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    return ambulance

@router.post("/", response_model=AmbulanceResponse, status_code=201)
async def create_ambulance(
    ambulance_data: AmbulanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    ambulance_dict = jsonable_encoder(ambulance_data)
    ambulance = Ambulance(**ambulance_dict)
    db.add(ambulance)
    db.commit()
    db.refresh(ambulance)
    
    # Sync with Redis Geo
    if ambulance.latitude and ambulance.longitude:
        await geo_add_location("geo:ambulances", ambulance.longitude, ambulance.latitude, ambulance.id)
        
    logger.info(f"Ambulance provider added: {ambulance.provider_name} by admin {current_user.id}")
    return ambulance

@router.patch("/{ambulance_id}", response_model=AmbulanceResponse)
async def update_ambulance(
    ambulance_id: int,
    ambulance_data: AmbulanceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id, Ambulance.is_active == True).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
    update_data = jsonable_encoder(ambulance_data, exclude_unset=True)
    for key, value in update_data.items():
        setattr(ambulance, key, value)
    
    db.commit()
    db.refresh(ambulance)
    
    # Sync with Redis Geo
    if ambulance.latitude and ambulance.longitude:
        await geo_add_location("geo:ambulances", ambulance.longitude, ambulance.latitude, ambulance.id)
    else:
        await geo_remove_location("geo:ambulances", ambulance.id)
        
    logger.info(f"Ambulance updated: {ambulance_id} by admin {current_user.id}")
    return ambulance

@router.delete("/{ambulance_id}", status_code=204)
async def delete_ambulance(
    ambulance_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id, Ambulance.is_active == True).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
    # Soft delete
    ambulance.is_active = False
    # Remove from Redis Geo Index
    await geo_remove_location("geo:ambulances", ambulance_id)
    
    logger.warning(f"Ambulance deleted: {ambulance_id} by admin {current_user.id}")
    return None
