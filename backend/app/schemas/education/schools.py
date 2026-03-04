from pydantic import BaseModel, Field, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime

from backend.app.models.education.schools import SchoolType
from backend.app.models.education.schools import BoardType

class SchoolBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)

    type: Optional[SchoolType] = None
    board: Optional[BoardType] = None

    established_year: Optional[int] = Field(None, ge=1800, le=2026)
    accreditation_grade: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    medium_of_instruction: Optional[str] = Field(None, max_length=100)
    classes_offered: Optional[str] = Field(None, max_length=255)
    fees: Optional[str] = Field(None, max_length=100)
    reviews: Optional[str] = None

class SchoolCreate(SchoolBase):
    pass

class SchoolUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)

    type: Optional[SchoolType] = None
    board: Optional[BoardType] = None

    established_year: Optional[int] = Field(None, ge=1800, le=2026)
    accreditation_grade: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None
    google_maps_link: Optional[HttpUrl] = None
    medium_of_instruction: Optional[str] = Field(None, max_length=100)
    classes_offered: Optional[str] = Field(None, max_length=255)
    fees: Optional[str] = Field(None, max_length=100)
    reviews: Optional[str] = None

class SchoolResponse(SchoolBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
    class Config:
        from_attributes = True