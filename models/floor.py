from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.base import Base

class Floor(Base):
    __tablename__ = "floors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    floor_number = Column(Integer, nullable=False)
    floor_name = Column(String(255), nullable=True)

    desks = relationship("Desk", back_populates="floor_entity", cascade="all, delete-orphan")
