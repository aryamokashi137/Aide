from sqlalchemy import Column, Integer, Text, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Review(Base):
    """
    Review model stores user feedback (rating + content) for any entity.

    This model is designed to support POLYMORPHIC reviews, meaning a review
    can belong to different types of entities such as:

        - Product
        - Course
        - Service
        - Hotel
        - Instructor
        - etc.

    Instead of having separate tables like:
        product_reviews
        course_reviews
        service_reviews

    We use a single reviews table with:
        entity_type → tells WHAT is being reviewed
        entity_id   → tells WHICH record is being reviewed

    Example:
        entity_type = "course"
        entity_id   = 10

        → Means this review is for Course with id=10
    """

    __tablename__ = "reviews"  # Database table name

    # Primary key (unique identifier for each review)
    id = Column(Integer, primary_key=True, index=True)

    # Numeric rating given by the user
    # Example values: 1 to 5
    rating = Column(Integer, nullable=False)

    # Text review content written by the user
    # Example: "This course was excellent and well structured"
    content = Column(Text, nullable=False)

    # Timestamp when the review was created
    # default=datetime.utcnow ensures automatic creation time
    created_at = Column(DateTime, default=datetime.utcnow)

    # ---------------------------
    # Polymorphic Review Target
    # ---------------------------

    # Type of entity being reviewed
    # Example values:
    #   "course"
    #   "product"
    #   "service"
    entity_type = Column(String(50), nullable=False)

    # ID of the entity being reviewed
    # Example:
    #   entity_type="course"
    #   entity_id=5
    #
    # Means review belongs to Course with id=5
    entity_id = Column(Integer, nullable=False)

    # ---------------------------
    # User Relationship
    # ---------------------------

    # Foreign key linking review to the user who wrote it
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # SQLAlchemy relationship to User model
    # Allows access like:
    #
    #   review.user        → get user object
    #   user.reviews       → get all reviews by user
    #
    user = relationship("User", back_populates="reviews")