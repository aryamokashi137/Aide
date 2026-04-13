from sqlalchemy import Column, Integer, Text, String, DateTime, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class MedicalReview(Base):
    __tablename__ = "medical_reviews"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 5", name="check_medical_rating_range"),
    )

    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"), nullable=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="medical_reviews")
    hospital = relationship("Hospital", back_populates="reviews")
    doctor = relationship("Doctor", back_populates="reviews")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    @property
    def entity_type(self) -> str:
        if self.hospital_id: return "hospital"
        if self.doctor_id: return "doctor"
        return "medical"

    @property
    def entity_id(self) -> int:
        return self.hospital_id or self.doctor_id or 0

    @property
    def entity_name(self) -> str:
        if self.hospital: return self.hospital.name
        if self.doctor: return self.doctor.name
        return "Unknown Medical Center"

    @property
    def user_name(self) -> str:
        return self.user.full_name if self.user else "Anonymous Student"
