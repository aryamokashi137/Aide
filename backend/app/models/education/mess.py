import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class MessType(str, enum.Enum):
    VEG = "Veg"
    NON_VEG = "Non-Veg"
    BOTH = "Both"


class Mess(Base):
    __tablename__ = "mess"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    google_maps_link = Column(Text, nullable=True)
    meal_types = Column(Enum(MessType),nullable=False,default=MessType.BOTH,index=True)
    monthly_charges = Column(String(100), nullable=True)
    timing = Column(String(255), nullable=True)
    home_delivery_available = Column(Boolean, nullable=False, default=False)
    hygiene_rating = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at = Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
    # Optional: Reviews can be normalized like in College
    reviews = Column(Text, nullable=True)

    hostels = relationship("Hostel", back_populates="mess", cascade="all, delete")