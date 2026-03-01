import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    DateTime,
    func,
)
from app.core.database import Base


class CoachingType(str, enum.Enum):
    ONLINE = "Online"
    OFFLINE = "Offline"


class Coaching(Base):
    __tablename__ = "coachings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    established_year = Column(Integer, nullable=True, index=True)
    courses_offered = Column(Text, nullable=True)
    exam_preparation_type = Column(String(255), nullable=True, index=True)
    coaching_type = Column(Enum(CoachingType),nullable=False,default=CoachingType.OFFLINE)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    website = Column(String(255), nullable=True)
    google_maps_link = Column(Text, nullable=True)
    batch_timings = Column(String(255), nullable=True)
    fees = Column(String(100), nullable=True)
    faculty_details = Column(Text, nullable=True)
    reviews = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)