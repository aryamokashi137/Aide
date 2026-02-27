import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, Float
from app.core.database import Base
from sqlalchemy.orm import relationship

class MessType(str, enum.Enum):
    VEG = "Veg"
    NON_VEG = "Non-Veg"
    BOTH = "Both"

class Mess(Base):
    __tablename__ = "mess"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(Text)
    phone_number = Column(String(20))
    google_maps_link = Column(Text)
    meal_types = Column(String(255))
    monthly_charges = Column(String(100))
    timing = Column(String(255))
    home_delivery_available = Column(Boolean)
    hygiene_rating = Column(Float)
    reviews = Column(Text)

    hostels = relationship("Hostel", back_populates="mess", cascade="all, delete")