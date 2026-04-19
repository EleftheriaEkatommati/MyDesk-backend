from pydantic import BaseModel
from datetime import date
from typing import Optional

from models.booking import BookingStatus
from .user import User
from .desk import DeskSchema


class BookingBase(BaseModel):
    id: int
    desk_id: int
    user_id: int
    booking_date: date
    status: BookingStatus

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    booking_date: date

class Booking(BookingBase):
    user: Optional[User] = None
    desk: Optional[DeskSchema] = None