import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, Enum, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class GenderType(str, enum.Enum):
    BOYS = "Boys"
    GIRLS = "Girls"
    CO_ED = "Co-ed"


class RoomType(str, enum.Enum):
    SINGLE = "Single"
    DOUBLE = "Double"
    TRIPLE = "Triple"


class PG(Base):
    __tablename__ = "pgs"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True, unique=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone_number = Column(String(20), nullable=False, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    google_maps_link = Column(Text, nullable=True)

    one_month_rent = Column(Integer, nullable=False)
    food_included = Column(Boolean, default=False, nullable=False)
    facilities_available = Column(Text, nullable=True)
    security_features = Column(Text, nullable=True)

    gender = Column(Enum(GenderType), nullable=False, default=GenderType.CO_ED, index=True)
    room_type = Column(Enum(RoomType), nullable=False, default=RoomType.SINGLE, index=True)

    # Reviews relationship
    reviews = relationship(
        "Review",
        back_populates="pg",
        cascade="all, delete-orphan"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)