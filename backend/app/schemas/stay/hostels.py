from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime
from app.models.stay.hostels import GenderType, RoomType

class HostelBase(BaseModel):
    name: str
    gender: GenderType
    description: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    deposit: Optional[int] = None
    ac_available: Optional[bool] = False
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    room_type: RoomType
    facilities_available: Optional[str] = None
    mess_available: Optional[bool] = False
    monthly_rent: int
    security_features: Optional[str] = None
    reviews: Optional[str] = None

class HostelCreate(HostelBase):
    pass

class HostelUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[GenderType] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    deposit: Optional[int] = None
    ac_available: Optional[bool] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    room_type: Optional[RoomType] = None
    facilities_available: Optional[str] = None
    mess_available: Optional[bool] = None
    monthly_rent: Optional[int] = None
    security_features: Optional[str] = None
    reviews: Optional[str] = None

class HostelResponse(HostelBase):
    id: int
    is_active: bool
    distance: Optional[float] = None  # in km
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)