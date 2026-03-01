import enum
from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base


# School Type Enum
class SchoolType(str, enum.Enum):
    GOVERNMENT = "Government"
    PRIVATE = "Private"


# Board Enum
class BoardType(str, enum.Enum):
    CBSE = "CBSE"
    ICSE = "ICSE"
    STATE = "State"


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    type = Column(Enum(SchoolType), nullable=False, default=SchoolType.PRIVATE, index=True)
    board = Column(Enum(BoardType), nullable=True, index=True)

    established_year = Column(Integer, nullable=True, index=True)
    accreditation_grade = Column(String(50), nullable=True, index=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    website = Column(String(255), nullable=True)
    google_maps_link = Column(Text, nullable=True)
    medium_of_instruction = Column(String(100), nullable=True)
    classes_offered = Column(String(255), nullable=True)
    fees = Column(String(100), nullable=True)

    # Reviews relationship
    reviews = relationship("Review",back_populates="school",cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)