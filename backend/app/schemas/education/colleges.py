from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional
from datetime import datetime

class CollegeBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    type: Optional[str] = Field(None, max_length=100)
    established_year: Optional[int] = Field(None, ge=1800, le=2026)
    accreditation_grade: Optional[str] = Field(None, max_length=50)
    college_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    streams_available: Optional[str] = None
    courses_offered: Optional[str] = None
    degree_types: Optional[str] = None
    fees: Optional[str] = Field(None, max_length=100)
    placement_ratio: Optional[float] = Field(None, ge=0, le=100)
   
class CollegeCreate(CollegeBase):
    pass

class CollegeUpdate(BaseModel):
    # Partial update schema: minimal validation to allow null/missing fields.
    # Callers should only send fields they want to update.
    name: Optional[str] = None
    type: Optional[str] = None
    established_year: Optional[int] = None
    accreditation_grade: Optional[str] = None
    college_code: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    streams_available: Optional[str] = None
    courses_offered: Optional[str] = None
    degree_types: Optional[str] = None
    fees: Optional[str] = None
    placement_ratio: Optional[float] = None

class CollegeResponse(CollegeBase):
    id: int
    is_active: bool
    distance: Optional[float] = None  # in km
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True