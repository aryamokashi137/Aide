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
    phone_number: Optional[str] = Field(None, max_length=20)
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    streams_available: Optional[str] = None
    courses_offered: Optional[str] = None
    degree_types: Optional[str] = None
    fees: Optional[str] = Field(None, max_length=100)
    reviews: Optional[str] = None
    placement_ratio: Optional[float] = Field(None, ge=0, le=100)
   
class CollegeCreate(CollegeBase):
    pass

class CollegeUpdate(CollegeBase):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    type: Optional[str] = Field(None, max_length=100)
    established_year: Optional[int] = Field(None, ge=1800, le=2026)
    accreditation_grade: Optional[str] = Field(None, max_length=50)
    college_code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    streams_available: Optional[str] = None
    courses_offered: Optional[str] = None
    degree_types: Optional[str] = None
    fees: Optional[str] = Field(None, max_length=100)
    reviews: Optional[str] = None
    placement_ratio: Optional[float] = Field(None, ge=0, le=100)

class CollegeResponse(CollegeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True