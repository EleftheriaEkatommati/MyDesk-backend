import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from database.base import Base
from datetime import date

class BookingStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    desk_id = Column(String, ForeignKey("desks.id"), nullable=False)
    booking_date = Column(Date, nullable=False, default=date.today)
    status = Column(Enum(BookingStatus), default=BookingStatus.ACTIVE, nullable=False)

    user = relationship("User", back_populates="bookings")
    desk = relationship("Desk", back_populates="bookings")