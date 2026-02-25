from sqlalchemy import Column, Integer, String, Text, Boolean, Float
from app.core.database import Base


class Mess(Base):
    __tablename__ = "mess"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # Veg / Non-Veg / Both
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