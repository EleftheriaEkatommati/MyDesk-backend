from typing import List
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from models.user import User
from models.booking import Booking, BookingStatus
from schemas.booking import Booking as BookingSchema
from core.security import get_current_user

router = APIRouter()

@router.get("/me", response_model=List[BookingSchema])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all bookings for the currently authenticated user.
    """
    bookings = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.desk)
    ).filter(Booking.user_id == current_user.id).order_by(Booking.booking_date.desc()).all()
    return bookings

@router.put("/{booking_id}/cancel", response_model=BookingSchema)
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