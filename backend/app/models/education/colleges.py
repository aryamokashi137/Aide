from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class CollegeType(str, enum.Enum):
    GOVERNMENT = "Government"
    PRIVATE = "Private"
    AUTONOMOUS = "Autonomous"


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    type = Column(Enum(CollegeType), nullable=False, default=CollegeType.PRIVATE, index=True)
    established_year = Column(Integer, nullable=True, index=True)
    accreditation_grade = Column(String(50), nullable=True, index=True)
    college_code = Column(String(50), nullable=True, unique=True, index=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    website = Column(String(255), nullable=True)
    google_maps_link = Column(String(500), nullable=True)
    streams_available = Column(Text, nullable=True)
    courses_offered = Column(Text, nullable=True)
    degree_types = Column(Text, nullable=True)
    fees = Column(String(100), nullable=True)
    placement_ratio = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)

     # One College → Many Reviews
    reviews = relationship("Review", back_populates="college", cascade="all, delete-orphan")