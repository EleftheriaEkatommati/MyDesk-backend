from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from models.desk import Desk
from models.user import User
from models.booking import Booking, BookingStatus
from schemas.booking import Booking as BookingSchema
from core.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=List[BookingSchema], response_model_by_alias=True)
def get_my_bookings(
    date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve bookings for the currently authenticated user.
    If a date is provided, it returns active bookings for that specific date.
    Otherwise, it returns all bookings.
    """
    query = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.desk).joinedload(Desk.floor_entity)
    ).filter(Booking.user_id == current_user.id)

    if date:
        query = query.filter(Booking.booking_date == date, Booking.status == BookingStatus.ACTIVE)

    bookings = query.order_by(Booking.booking_date.desc()).all()
    return bookings

@router.put("/{booking_id}/cancel", response_model=BookingSchema, response_model_by_alias=True)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a booking by its ID.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.user_id != current_user.id and current_user.role.name != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this booking")

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking is already cancelled")

    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    
    # Re-query to get the object with eager-loaded relationships for the response
    updated_booking = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.desk)
    ).filter(Booking.id == booking.id).one()

    return updated_booking