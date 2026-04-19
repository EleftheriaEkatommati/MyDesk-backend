import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship

from database.base import Base

class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    desk_id = Column(Integer, ForeignKey("desks.id"), nullable=False)
    booking_date = Column(Date, nullable=False, index=True)
    status = Column(SQLAlchemyEnum(BookingStatus), nullable=False, default=BookingStatus.ACTIVE, index=True)

    user = relationship("User", back_populates="bookings")
    desk = relationship("Desk", back_populates="bookings")