from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    # -------------------------
    # Primary Key
    # -------------------------
    id = Column(Integer, primary_key=True, index=True)

    # -------------------------
    # Review Content
    # -------------------------
    content = Column(Text, nullable=False)

    rating = Column(Integer, nullable=False)

    # Ensure rating is between 1 and 5
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="check_rating_range"
        ),
    )

    # -------------------------
    # Polymorphic Review Target
    # -------------------------

    # Type of entity being reviewed
    # Example: "college", "mess", "coaching"
    entity_type = Column(String(50), nullable=False)

    # ID of the entity being reviewed
    entity_id = Column(Integer, nullable=False)

    # -------------------------
    # User Relationship
    # -------------------------
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    user = relationship("User", back_populates="reviews")

    # -------------------------
    # Timestamps
    # -------------------------
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # -------------------------
    # Soft Delete
    # -------------------------
    is_active = Column(Boolean, default=True, nullable=False)