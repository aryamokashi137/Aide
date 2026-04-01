from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class VisitStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Visit(Base):
    """
    Visit model stores appointments scheduled by students to visit a PG, Hostel or Institution.
    """
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Target Entity (Polymorphic-lite)
    entity_type = Column(String(50), nullable=False) # 'pg', 'college', etc.
    entity_id = Column(Integer, nullable=False)
    entity_name = Column(String(255), nullable=False)
    
    visit_date = Column(DateTime, nullable=False)
    preferred_time = Column(String(50), nullable=True) # Morning, Afternoon, Evening
    
    status = Column(Enum(VisitStatus), default=VisitStatus.PENDING, nullable=False)
    
    message = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", back_populates="visits")

# Add relationship to User model as well
