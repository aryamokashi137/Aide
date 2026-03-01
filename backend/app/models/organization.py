from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    # auth_policy can be "STANDARD" (email/password allowed) or "SSO_ONLY"
    auth_policy = Column(String(50), default="STANDARD", nullable=False)

    # users belonging to this organization
    users = relationship("User", back_populates="organization")
