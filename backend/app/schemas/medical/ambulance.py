from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AmbulanceBase(BaseModel):
    provider_name: str
    type: str
    cost_per_km: float
    availability: bool = True
    contact_number: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    base_address: Optional[str] = None

class AmbulanceCreate(AmbulanceBase):
    pass

class AmbulanceUpdate(BaseModel):
    provider_name: Optional[str] = None
    type: Optional[str] = None
    cost_per_km: Optional[float] = None
    availability: Optional[bool] = None
    contact_number: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    base_address: Optional[str] = None

class AmbulanceResponse(AmbulanceBase):
    id: int
    is_active: bool
    distance: Optional[float] = None  # in km
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
