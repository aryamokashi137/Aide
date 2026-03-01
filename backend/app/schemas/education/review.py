from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    rating: int = Field(..., ge=1, le=5, description="Rating must be between 1 and 5")
    entity_type: str = Field(..., min_length=1, max_length=50, description="Type of entity being reviewed (e.g., 'college', 'school', 'hostel', 'mess', 'coaching')")
    entity_id: int = Field(..., gt=0, description="ID of the entity being reviewed")
    user_id: int = Field(..., gt=0, description="ID of the user who wrote the review")


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    rating: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None


class ReviewResponse(ReviewBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
