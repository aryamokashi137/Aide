from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime
from backend.app.models.education.coaching import CoachingType


class CoachingBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    coaching_type: CoachingType
    established_year: Optional[int] = Field(None, ge=1800, le=2026)
    courses_offered: Optional[str] = None
    exam_preparation_type: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    batch_timings: Optional[str] = None
    fees: Optional[str] = Field(None, max_length=100)
    faculty_details: Optional[str] = None
    reviews: Optional[str] = None

class CoachingCreate(CoachingBase):
    pass

class CoachingUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    coaching_type: Optional[CoachingType] = None
    established_year: Optional[int] = Field(None, ge=1800, le=2026)
    courses_offered: Optional[str] = None
    exam_preparation_type: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    batch_timings: Optional[str] = None
    fees: Optional[str] = None
    faculty_details: Optional[str] = None
    reviews: Optional[str] = None

class CoachingResponse(CoachingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True