from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class Coaching(Base):
    __tablename__ = "coaching"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # Online / Offline
    established_year = Column(Integer)
    courses_offered = Column(Text)
    exam_preparation_type = Column(String(255))
    description = Column(Text)
    address = Column(Text)
    phone_number = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    google_maps_link = Column(Text)
    batch_timings = Column(String(255))
    fees = Column(String(100))
    faculty_details = Column(Text)
    reviews = Column(Text)