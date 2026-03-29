from pydantic import BaseModel, EmailStr, HttpUrl, Field
from typing import Optional, List
from datetime import datetime

class HospitalBase(BaseModel):
    name: str
    category: Optional[str] = None
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available_beds: int = 0
    icu_beds: int = 0
    emergency_contact: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None

class HospitalCreate(HospitalBase):
    pass

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    available_beds: Optional[int] = None
    icu_beds: Optional[int] = None
    emergency_contact: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    google_maps_link: Optional[str] = None

class HospitalResponse(HospitalBase):
    id: int
    is_active: bool
    distance: Optional[float] = None  # in km, calculated if lat/lon provided
    rating: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
