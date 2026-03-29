from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi.encoders import jsonable_encoder

from app.core.database import get_db
from app.core.logger import logger
from app.api.v1.endpoints.deps import get_current_user, require_roles
from app.models.medical.blood_bank import BloodBank
from app.schemas.medical.blood_bank import BloodBankCreate, BloodBankUpdate, BloodBankResponse

router = APIRouter(prefix="/blood-banks", tags=["Blood Banks"])

from enum import Enum
from typing import List, Optional
from sqlalchemy import func, or_
from app.core.redis import redis_client
import json
import hashlib

# 1. Enums for type-safe filtering
class SortBy(str, Enum):
    DISTANCE = "distance"
    NAME = "name"

class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"

class BloodGroup(str, Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"

# 2. Dependency class for clean filters
class BloodBankFilterParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        blood_group: Optional[BloodGroup] = Query(None, description="Check availability for blood group"),
        query: Optional[str] = Query(None, description="Search by name or address"),
        lat: Optional[float] = Query(None, ge=-90, le=90),
        lon: Optional[float] = Query(None, ge=-180, le=180),
        radius: Optional[float] = Query(20.0, ge=0.5, le=100.0),
        sort_by: Optional[SortBy] = Query(SortBy.NAME),
        order: Optional[Order] = Query(Order.ASC)
    ):
        self.skip = skip
        self.limit = limit
        self.blood_group = blood_group
        self.query = query
        self.lat = lat
        self.lon = lon
        self.radius = radius
        self.sort_by = sort_by
        self.order = order

    def get_cache_key(self) -> str:
        params_dict = {k: str(v) for k, v in self.__dict__.items()}
        params_str = json.dumps(params_dict, sort_keys=True)
        return f"blood_banks_search:{hashlib.md5(params_str.encode()).hexdigest()}"

@router.get("/", response_model=List[BloodBankResponse])
async def get_blood_banks(
    filters: BloodBankFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get blood banks with advanced dynamic filtering, caching, and geo-proximity sorting.
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
    query = db.query(BloodBank).filter(BloodBank.is_active == True)

    # 3. Dynamic Filters
    if filters.query:
        search = f"%{filters.query}%"
        query = query.filter(or_(BloodBank.name.ilike(search), BloodBank.address.ilike(search)))

    # 4. Fetch the data (for custom blood group check in Python)
    results = query.all()
    
    # Blood group filter (Python level for simplicity across DB types)
    if filters.blood_group:
        results = [bb for bb in results if bb.blood_group_units and bb.blood_group_units.get(filters.blood_group, 0) > 0]
    
    # 5. Geo-spatial Logic (Backing up to Haversine for now as it's not indexed)
    from app.core.location import calculate_haversine_distance
    blood_banks_list = []
    use_geo = all(v is not None for v in [filters.lat, filters.lon])
    
    for bb in results:
        bb.rating = 0.0 # Blood banks don't have reviews in this model
        if use_geo and bb.latitude and bb.longitude:
            dist = calculate_haversine_distance(filters.lat, filters.lon, bb.latitude, bb.longitude)
            bb.distance = round(dist, 2)
            if dist <= filters.radius:
                blood_banks_list.append(bb)
        elif not use_geo:
            bb.distance = None
            blood_banks_list.append(bb)

    # 6. Sorting
    is_desc = (filters.order == Order.DESC)
    if filters.sort_by == SortBy.DISTANCE and use_geo:
        blood_banks_list.sort(key=lambda x: x.distance if x.distance is not None else float('inf'), reverse=is_desc)
    elif filters.sort_by == SortBy.NAME:
        blood_banks_list.sort(key=lambda x: x.name.lower(), reverse=is_desc)

    # 7. Pagination & Caching
    final_results = blood_banks_list[filters.skip : filters.skip + filters.limit]
    
    from fastapi.encoders import jsonable_encoder
    json_data = jsonable_encoder(final_results)
    try:
        await redis_client.setex(cache_key, 300, json.dumps(json_data))
    except Exception as e:
        logger.error(f"Cache failed: {e}")

    return final_results

# ------------------- FILTERS ALIAS -------------------
@router.get("/filters", response_model=List[BloodBankResponse])
async def get_blood_banks_filtered(
    filters: BloodBankFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Alias for the main blood banks search endpoint.
    """
    return await get_blood_banks(filters, db, current_user)

@router.get("/{blood_bank_id}", response_model=BloodBankResponse)
async def get_blood_bank(
    blood_bank_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    bb = db.query(BloodBank).filter(BloodBank.id == blood_bank_id, BloodBank.is_active == True).first()
    if not bb:
        raise HTTPException(status_code=404, detail="Blood Bank not found")
    return bb

@router.post("/", response_model=BloodBankResponse, status_code=201)
async def create_blood_bank(
    bb_data: BloodBankCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    bb_dict = jsonable_encoder(bb_data)
    bb = BloodBank(**bb_dict)
    db.add(bb)
    db.commit()
    db.refresh(bb)
    logger.info(f"Blood Bank added: {bb.name} by admin {current_user.id}")
    return bb

@router.patch("/{blood_bank_id}", response_model=BloodBankResponse)
async def update_blood_bank(
    blood_bank_id: int,
    bb_data: BloodBankUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    bb = db.query(BloodBank).filter(BloodBank.id == blood_bank_id, BloodBank.is_active == True).first()
    if not bb:
        raise HTTPException(status_code=404, detail="Blood Bank not found")
    
    update_data = jsonable_encoder(bb_data, exclude_unset=True)
    for key, value in update_data.items():
        setattr(bb, key, value)
    
    db.commit()
    db.refresh(bb)
    logger.info(f"Blood Bank updated: {blood_bank_id} by admin {current_user.id}")
    return bb

@router.delete("/{blood_bank_id}", status_code=204)
async def delete_blood_bank(
    blood_bank_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["ADMIN"]))
):
    bb = db.query(BloodBank).filter(BloodBank.id == blood_bank_id, BloodBank.is_active == True).first()
    if not bb:
        raise HTTPException(status_code=404, detail="Blood Bank not found")
    
    # Soft delete
    bb.is_active = False
    db.commit()
    logger.warning(f"Blood Bank deleted: {blood_bank_id} by admin {current_user.id}")
    return None
