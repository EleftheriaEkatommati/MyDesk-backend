from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base

class Desk(Base):
    __tablename__ = "desks"

    id = Column(String(255), primary_key=True, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    rotation = Column(Integer, nullable=False)
    floor_id = Column(Integer, ForeignKey("floors.id"), nullable=False)
    is_booked = Column(Boolean, default=False)
    booked_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    floor_entity = relationship("Floor", back_populates="desks")
    user = relationship("User")