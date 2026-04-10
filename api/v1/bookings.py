from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.session import get_db
from core.security import get_current_user
from crud import booking as crud_booking
from schemas import booking as booking_schema
from models import user as user_model
from models.booking import BookingStatus

router = APIRouter()

@router.get("/me", response_model=List[booking_schema.Booking])
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Retrieve all bookings for the currently authenticated user.
    """
    bookings = crud_booking.get_bookings_by_user(db, user_id=current_user.id)
    return bookings

@router.put("/{booking_id}/cancel", response_model=booking_schema.Booking)
def cancel_my_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Cancel a booking made by the currently authenticated user.
    """
    booking_to_cancel = crud_booking.get_booking_by_id(db, booking_id=booking_id)

    if not booking_to_cancel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    if booking_to_cancel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this booking",
        )

    if booking_to_cancel.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This booking is already cancelled",
        )

    return crud_booking.cancel_booking(db=db, booking=booking_to_cancel)