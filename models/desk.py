from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class Desk(Base):
    __tablename__ = "desks"

    id = Column(Integer, primary_key=True, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    rotation = Column(Integer, nullable=False)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False)

    floor = relationship("Floor", back_populates="desks")
    bookings = relationship("Booking", back_populates="desk", cascade="all, delete-orphan")