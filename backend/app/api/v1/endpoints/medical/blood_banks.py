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

from app.core.location import calculate_haversine_distance

@router.get("/", response_model=List[BloodBankResponse])
async def get_blood_banks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    blood_group: Optional[str] = Query(None, description="Check availability for blood group, e.g., 'A+'"),
    lat: Optional[float] = Query(None, description="User's current latitude"),
    lon: Optional[float] = Query(None, description="User's current longitude"),
    radius: Optional[float] = Query(None, description="Radius in km", ge=0.1),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get blood banks with optional name/blood group filtering and nearby search.
    """
    query = db.query(BloodBank).filter(BloodBank.is_active == True)
    if name:
        query = query.filter(BloodBank.name.ilike(f"%{name}%"))
    
    # Execute query
    blood_banks = query.all()
    
    # Blood group filter (Python level for simplicity across DB types)
    if blood_group:
        blood_banks = [bb for bb in blood_banks if bb.blood_group_units and bb.blood_group_units.get(blood_group, 0) > 0]
        
    # Logic for nearby search
    if lat is not None and lon is not None:
        nearby_bb = []
        for bb in blood_banks:
            if bb.latitude and bb.longitude:
                dist = calculate_haversine_distance(lat, lon, bb.latitude, bb.longitude)
                bb.distance = round(dist, 2)
                
                if radius is None or dist <= radius:
                    nearby_bb.append(bb)
        
        nearby_bb.sort(key=lambda x: x.distance)
        return nearby_bb[skip : skip + limit]
        
    # Standard pagination for non-location search
    return blood_banks[skip : skip + limit]


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
