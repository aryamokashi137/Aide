from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Dict
from datetime import datetime

class BloodBankBase(BaseModel):
    name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    blood_group_units: Optional[Dict[str, int]] = None
    price_per_unit: Optional[float] = None
    emergency_contact: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None

class BloodBankCreate(BloodBankBase):
    pass

class BloodBankUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    blood_group_units: Optional[Dict[str, int]] = None
    price_per_unit: Optional[float] = None
    emergency_contact: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None

class BloodBankResponse(BloodBankBase):
    id: int
    is_active: bool
    distance: Optional[float] = None  # in km
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
