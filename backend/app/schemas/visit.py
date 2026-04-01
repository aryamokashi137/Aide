from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VisitStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class VisitBase(BaseModel):
    entity_type: str
    entity_id: int
    entity_name: str
    visit_date: datetime
    preferred_time: Optional[str] = "Morning"
    message: Optional[str] = None

class VisitCreate(VisitBase):
    pass

class VisitUpdate(BaseModel):
    status: Optional[VisitStatus] = None
    visit_date: Optional[datetime] = None
    message: Optional[str] = None

class VisitResponse(VisitBase):
    id: int
    user_id: int
    status: VisitStatus
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
