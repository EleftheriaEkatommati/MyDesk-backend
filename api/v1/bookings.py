from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel, Field

from database.session import get_db
from models.desk import Desk
from models.user import User, RoleEnum
from models.booking import Booking, BookingStatus
from schemas.booking import Booking as BookingSchema
from core.security import get_current_user
from core.email import send_booking_cancellation_email

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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a booking by its ID and sends a cancellation email.
    """
    # Eager load relationships needed for the email and the response
    booking = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.desk).joinedload(Desk.floor_entity)
    ).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # A user can cancel their own booking, or an admin can cancel any booking.
    if booking.user_id != current_user.id and (not current_user.role or current_user.role.name != RoleEnum.admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this booking")

    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking is already cancelled")

    # Soft-delete the booking by changing its status
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)

    # Add email sending to background tasks so the user doesn't have to wait
    background_tasks.add_task(
        send_booking_cancellation_email,
        booking.user.email,
        booking.user.name,
        booking.desk_id,
        booking.booking_date,
    )

    return booking

class CheckInRequest(BaseModel):
    qr_data: str = Field(..., description="The raw data scanned from the QR code, e.g., 'BOOKING_ID:123'")

@router.post("/check-in", response_model=BookingSchema, response_model_by_alias=True)
def check_in_booking(
    check_in_request: CheckInRequest,
    db: Session = Depends(get_db),
    # For security, let's assume an admin or a device with admin rights performs the check-in.
    current_user: User = Depends(get_current_user)
):
    """
    Check in a user for their booking using the data from a QR code.
    """

    if not current_user.role or current_user.role.name != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform check-in"
        )
    # 1. Parse QR data to get booking ID
    try:
        prefix, booking_id_str = check_in_request.qr_data.split(':')
        if prefix != "BOOKING_ID":
            raise ValueError("Invalid QR code format.")
        booking_id = int(booking_id_str)
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid QR code data. Expected format: 'BOOKING_ID:<id>'",
        )

    # 2. Find the booking
    booking = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.desk).joinedload(Desk.floor_entity)
    ).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Booking with ID {booking_id} not found")

    # 3. Perform validation checks
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This booking has been cancelled.")

    if booking.status == BookingStatus.CHECKED_IN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This booking has already been checked in.")

    # Check if the booking is for today
    if booking.booking_date != date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"This booking is for {booking.booking_date}, not for today ({date.today()})."
        )

    # 4. Update status to CHECKED_IN
    booking.status = BookingStatus.CHECKED_IN
    db.commit()
    db.refresh(booking)

    return booking