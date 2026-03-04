import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from sqlalchemy.orm import relationship



class GenderType(str, enum.Enum):
    BOYS = "Boys"
    GIRLS = "Girls"
    CO_ED = "Co-ed"


class RoomType(str, enum.Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    TRIPLE = "Triple"
    

class Hostel(Base):
    __tablename__ = "hostels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(50), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    website = Column(String(255), nullable=True)
    google_maps_link = Column(Text, nullable=True)
    facilities_available = Column(Text, nullable=True)
    mess_available = Column(Boolean, default=False, nullable=False)
    monthly_rent = Column(String(100), nullable=False)

    # Optional features
    security_features = Column(Text, nullable=True)
    gender = Column(Enum(GenderType), nullable=False, default=GenderType.CO_ED, index=True)
    room_type = Column(Enum(RoomType), nullable=False, default=RoomType.SINGLE, index=True)

    # Reviews relationship
    reviews = relationship("Review",back_populates="hostel",cascade="all, delete-orphan")
    mess = relationship("Mess", back_populates="hostels")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)

    mess_id = Column(Integer, ForeignKey("mess.id", ondelete="SET NULL"), nullable=True) 