from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload # Import joinedload
from typing import List, Optional
from datetime import date
from pydantic import Field

from database.session import get_db # Import get_db from the shared location
from models.desk import Desk
from models.floor import Floor
from models.booking import Booking, BookingStatus
from models.user import User
from schemas.desk import DeskSchema, DeskWithStatusSchema
from schemas.floor import FloorResponse
from schemas.booking import BookingCreate, Booking as BookingSchema
from core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DeskWithStatusSchema])
def get_all_desks(date: date, db: Session = Depends(get_db)):
    """
    API endpoint to get all desks with their booking status for a given date.
    """
    desks = db.query(Desk).options(joinedload(Desk.floor_entity)).order_by(Desk.id).all()

    # Get all active bookings for the given date
    bookings = db.query(Booking).filter(
        Booking.booking_date == date,
        Booking.status == BookingStatus.ACTIVE
    ).all()

    # Create a lookup map for booked desks
    booked_desks_map = {booking.desk_id: booking for booking in bookings}

    # Prepare the response
    response_desks = []
    for desk in desks:
        booking = booked_desks_map.get(desk.id)
        desk_data = {
            "id": desk.id,
            "x": desk.x,
            "y": desk.y,
            "rotation": desk.rotation,
            "floor_id": desk.floor_id,
            "floor_entity": desk.floor_entity,
            "is_booked": booking is not None,
            "booked_by": booking.user_id if booking else None,
        }
        response_desks.append(desk_data)
    
    return response_desks

@router.get("/floors", response_model=List[FloorResponse])
def get_all_floors(db: Session = Depends(get_db)):
    """
    API endpoint to get all floors.
    """
    floors = db.query(Floor).order_by(Floor.floor_number).all()
    return floors

@router.get("/floors/{floor_id}", response_model=FloorResponse)
def get_floor_by_id(floor_id: int, db: Session = Depends(get_db)):
    """
    API endpoint to get a single floor by its ID.
    """
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Floor with ID {floor_id} not found"
        )
    return floor


@router.post("/{desk_id}/book", response_model=BookingSchema, status_code=status.HTTP_201_CREATED)
def book_desk(
    desk_id: str,
    booking_request: BookingCreate, # The user_id field should be removed from this schema
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    API endpoint to book a specific desk.

    The `booking_request` should contain the `booking_date`.
    - **desk_id**: The ID of the desk to book (e.g., "101").
    - **booking_request**: JSON body containing the date for the booking.
    The user is identified from the authentication token.
    """
    desk = db.query(Desk).options(joinedload(Desk.floor_entity)).filter(Desk.id == desk_id).first()

    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Desk with ID {desk_id} not found"
        )

    # Check if desk is already booked for the given date
    existing_booking = db.query(Booking).filter(
        Booking.desk_id == desk_id,
        Booking.booking_date == booking_request.booking_date,
        Booking.status == BookingStatus.ACTIVE
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Desk {desk_id} is already booked for {booking_request.booking_date}"
        )

    new_booking = Booking(
        desk_id=desk_id,
        user_id=current_user.id,
        booking_date=booking_request.booking_date,
        status=BookingStatus.ACTIVE
    )
    db.add(new_booking)
    db.commit()
    
    # Query the new booking again to eager load relationships for the response
    created_booking = db.query(Booking).options(
        joinedload(Booking.user),
        joinedload(Booking.desk).joinedload(Desk.floor_entity)
    ).filter(Booking.id == new_booking.id).one()

    return created_booking

@router.get("/floors/{floor_id}/desks", response_model=List[DeskWithStatusSchema])
def get_desks_by_floor(floor_id: int, booking_date: date, db: Session = Depends(get_db)):
    """
    API endpoint to get all desks for a specific floor, including their booking status for a given date.
    """
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Floor with id {floor_id} not found")

    # 1. Get all desks for the floor
    desks = db.query(Desk).options(joinedload(Desk.floor_entity)).filter(Desk.floor_id == floor_id).order_by(Desk.id).all()
    
    # 2. Get all active bookings for these desks on the given date
    desk_ids = [desk.id for desk in desks]
    bookings = db.query(Booking).filter(
        Booking.desk_id.in_(desk_ids),
        Booking.booking_date == booking_date,
        Booking.status == BookingStatus.ACTIVE
    ).all()

    # 3. Create a lookup map for booked desks
    booked_desks_map = {booking.desk_id: booking for booking in bookings}

    # 4. Prepare the response
    response_desks = []
    for desk in desks:
        booking = booked_desks_map.get(desk.id)
        desk_data = {
            "id": desk.id,
            "x": desk.x,
            "y": desk.y,
            "rotation": desk.rotation,
            "floor_id": desk.floor_id,
            "floor_entity": desk.floor_entity,
            "is_booked": booking is not None,
            "booked_by": booking.user_id if booking else None,
        }
        response_desks.append(desk_data)
    
    return response_desks