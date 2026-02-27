import enum
from sqlalchemy import Column, Integer, String, Text, Boolean ,ForeignKey
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
    name = Column(String(255), nullable=False)
    description = Column(Text)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    google_maps_link = Column(Text)
    facilities_available = Column(Text)
    mess_available = Column(Boolean, default=False)
    monthly_rent = Column(String(100), nullable=False)
    security_features = Column(Text)
    reviews = Column(Text)

    mess_id = Column(Integer, ForeignKey("mess.id"))
    mess = relationship("Mess", back_populates="hostels")