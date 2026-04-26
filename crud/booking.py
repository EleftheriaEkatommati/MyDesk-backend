from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from models.booking import Booking, BookingStatus
from models.desk import Desk


def get_booking_by_id(db: Session, booking_id: int) -> Optional[Booking]:
    """
    Get a single booking by its ID, with related user and desk info.
    """
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.user),
            joinedload(Booking.desk).joinedload(Desk.floor),
        )
        .filter(Booking.id == booking_id)
        .first()
    )

def cancel_booking(db: Session, booking: Booking) -> Booking:
    booking.status = BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking

def get_bookings_by_user(db: Session, user_id: int) -> List[Booking]:
    """
    Get all bookings for a specific user.
    Eager loads user, desk, and desk's floor information for an efficient query.
    """
    return (
        db.query(Booking)
        .options(
            joinedload(Booking.user),
            joinedload(Booking.desk).joinedload(Desk.floor),
        )
        .filter(Booking.user_id == user_id)
        .order_by(Booking.booking_date.desc())
        .all()
    )