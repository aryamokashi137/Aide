from sqlalchemy import Column, Integer, String, Text, Boolean
from app.core.database import Base


class PG(Base):
    __tablename__ = "pg"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    # Boys / Girls / Co-ed
    gender_type = Column(String(50), nullable=False)

    description = Column(Text)
    address = Column(Text, nullable=False)

    phone_number = Column(String(20))
    email = Column(String(255))
    google_maps_link = Column(Text)

    room_types = Column(Text)  # Single / Double / Triple etc.

    one_month_rent = Column(String(100), nullable=False)

    food_included = Column(Boolean, default=False)

    facilities_available = Column(Text)

    security_features = Column(Text)

    reviews = Column(Text)