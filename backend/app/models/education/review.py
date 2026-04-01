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
    """
    Review model stores user feedback (rating + content) for any entity.
    
    Each review is linked to ONE entity through foreign keys:
    - college_id
    - school_id
    - hostel_id
    - mess_id
    - coaching_id
    
    Only ONE of these will be non-null for any given review.
    """

    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    
    # Review Content
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)

    # Ensure rating is between 0 and 5
    __table_args__ = (
        CheckConstraint(
            "rating >= 0 AND rating <= 5",
            name="check_rating_range"
        ),
    )

    # Foreign Keys to different entity types (polymorphic)
    college_id = Column(Integer, ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"), nullable=True, index=True)
    hostel_id = Column(Integer, ForeignKey("hostels.id", ondelete="CASCADE"), nullable=True, index=True)
    mess_id = Column(Integer, ForeignKey("mess.id", ondelete="CASCADE"), nullable=True, index=True)
    coaching_id = Column(Integer, ForeignKey("coachings.id", ondelete="CASCADE"), nullable=True, index=True)
    pg_id = Column(Integer, ForeignKey("pgs.id", ondelete="CASCADE"), nullable=True, index=True)

    # User who wrote the review
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    college = relationship("College", back_populates="reviews")
    school = relationship("School", back_populates="reviews")
    hostel = relationship("Hostel", back_populates="reviews")
    mess = relationship("Mess", back_populates="reviews")
    coaching = relationship("Coaching", back_populates="reviews")
    pg = relationship("PG", back_populates="reviews")

    # Timestamps
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

    # Soft Delete
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def entity_type(self) -> str:
        if self.college_id: return "college"
        if self.school_id: return "school"
        if self.hostel_id: return "hostel"
        if self.mess_id: return "mess"
        if self.coaching_id: return "coaching"
        if self.pg_id: return "pg"
        return "unknown"

    @property
    def entity_id(self) -> int:
        return self.college_id or self.school_id or self.hostel_id or self.mess_id or self.coaching_id or self.pg_id or 0
    @property
    def user_name(self) -> str:
        return self.user.full_name if self.user else "Anonymous Student"
