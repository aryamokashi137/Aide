from pydantic import BaseModel, Field, EmailStr, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.stay.pg import GenderType, RoomType

class PGBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    deposit: Optional[int] = None
    ac_available: Optional[bool] = False
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    google_maps_link: Optional[HttpUrl] = None
    one_month_rent: int = Field(..., gt=0)
    food_included: Optional[bool] = False
    gender: GenderType
    room_type: RoomType
    facilities_available: Optional[str] = None
    security_features: Optional[str] = None
    reviews: Optional[str] = None

class PGCreate(PGBase):
    pass

class PGUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    deposit: Optional[int] = None
    ac_available: Optional[bool] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    google_maps_link: Optional[HttpUrl] = None
    one_month_rent: Optional[int] = Field(None, gt=0)
    food_included: Optional[bool] = None
    gender: Optional[GenderType] = None
    room_type: Optional[RoomType] = None
    facilities_available: Optional[str] = None
    security_features: Optional[str] = None
    reviews: Optional[str] = None

class PGResponse(PGBase):
    id: int
    is_active: bool
    distance: Optional[float] = None  # in km
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)