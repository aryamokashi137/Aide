from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from backend.app.models.education.mess import MessType

class MessBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    meal_types: MessType
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    google_maps_link: Optional[HttpUrl] = None
    monthly_charges: Optional[str] = Field(None, max_length=100)
    timing: Optional[str] = None
    home_delivery_available: Optional[bool] = None
    hygiene_rating: Optional[float] = Field(None, ge=0, le=5)
    reviews: Optional[str] = None

class MessCreate(MessBase):
    pass

class MessUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    meal_types: Optional[MessType] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    google_maps_link: Optional[HttpUrl] = None
    monthly_charges: Optional[str] = Field(None, max_length=100)
    timing: Optional[str] = None
    home_delivery_available: Optional[bool] = None
    hygiene_rating: Optional[float] = Field(None, ge=0, le=5)
    reviews: Optional[str] = None

class MessResponse(MessBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True