from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    rating: int = Field(..., ge=0, le=5, description="Rating must be between 0 and 5")


class ReviewCreate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int
    user_id: int
    user_name: str
    entity_type: str
    entity_id: int
    entity_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
