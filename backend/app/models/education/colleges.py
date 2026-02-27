from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.core.database import Base


class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))
    established_year = Column(Integer)
    accreditation_grade = Column(String(50))
    college_code = Column(String(50))
    description = Column(Text)
    address = Column(Text)
    phone_number = Column(String(20))
    website = Column(String(255))
    google_maps_link = Column(String(500))
    streams_available = Column(Text)
    courses_offered = Column(Text)
    degree_types = Column(Text)
    fees = Column(String(100))
    placement_ratio = Column(Float)

    # One College → Many Reviews
    reviews = relationship("Review", back_populates="college", cascade="all, delete-orphan")
    
    
    


   
   
   
