import enum
from sqlalchemy import Column, Integer, String, Text, Enum
from app.core.database import Base
from sqlalchemy.orm import relationship

# School Type Enum
class SchoolType(str, enum.Enum):
    GOVERNMENT = "Government"
    PRIVATE = "Private"


# Board Enum
class BoardType(str, enum.Enum):
    CBSE = "CBSE"
    ICSE = "ICSE"
    STATE = "State"


class School(Base):
    __tablename__ = "schools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)

    type = Column(Enum(SchoolType), nullable=True)
    board = Column(Enum(BoardType), nullable=True)

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

    # Proper One-to-Many relationship
    reviews = relationship("Review", back_populates="school", cascade="all, delete-orphan")