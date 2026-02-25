from sqlalchemy import Column, Integer, String, Text
from app.core.database import Base


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100))  # Government / Private
    board = Column(String(100))  # CBSE / ICSE / State
    established_year = Column(Integer)
    accreditation_grade = Column(String(50))
    description = Column(Text)
    address = Column(Text)
    phone_number = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))
    google_maps_link = Column(Text)
    medium_of_instruction = Column(String(100))
    classes_offered = Column(String(255))
    fees = Column(String(100))
    reviews = Column(Text)