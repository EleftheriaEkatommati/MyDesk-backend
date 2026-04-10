from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload # Import joinedload
from typing import List, Optional
from datetime import date
from fastapi import Query
from database.session import get_db # Import get_db from the shared location
from models.desk import Desk
from models.floor import Floor
from models.booking import Booking, BookingStatus
from models.user import User
from schemas.desk import DeskSchema
from schemas.floor import FloorResponse
from schemas.booking import BookingCreate, Booking as BookingSchema

router = APIRouter()

@router.get("/", response_model=List[DeskSchema])
def get_all_desks(date: date = Query(...), db: Session = Depends(get_db)):
    """
    API endpoint to get all desks for a specific date.
    Query parameter 'date' (required) to filter bookings for a specific date.
    """
    desks = db.query(Desk).options(joinedload(Desk.floor_entity)).order_by(Desk.id).all()
    
    # Get all bookings for the date
    bookings = db.query(Booking).filter(
        Booking.booking_date == date,
        Booking.status == BookingStatus.ACTIVE
    ).all()
    booked_desk_map = {b.desk_id: b.user_id for b in bookings}
    
    # Create response dicts with all needed fields
    result = []
    for desk in desks:
        is_booked = desk.id in booked_desk_map
        booked_by = booked_desk_map.get(desk.id)
        floor_name = desk.floor_entity.floor_name if desk.floor_entity else None
        
        result.append(DeskSchema(
            id=desk.id,
            x=desk.x,
            y=desk.y,
            rotation=desk.rotation,
            floor_id=desk.floor_id,
            isBooked=is_booked,
            bookedBy=booked_by,
            floorName=floor_name
        ))
    
    return result

@router.get("/floors", response_model=List[FloorResponse])
def get_all_floors(db: Session = Depends(get_db)):
    """
    API endpoint to get all floors.
    """
    floors = db.query(Floor).order_by(Floor.floor_number).all()
    return floors


@router.post("/{desk_id}/book", response_model=BookingSchema, status_code=status.HTTP_201_CREATED)
def book_desk(
    desk_id: str,
    booking_request: BookingCreate,
    db: Session = Depends(get_db)
):
    """
    API endpoint to book a specific desk.

    The `booking_request` should contain `user_id` and `booking_date`.
    - **desk_id**: The ID of the desk to book (e.g., "101").
    - **booking_request**: JSON body containing the user_id of the person booking.
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

    # Verify user exists
    user = db.query(User).filter(User.id == booking_request.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with ID {booking_request.user_id} not found")

    new_booking = Booking(
        desk_id=desk_id,
        user_id=booking_request.user_id,
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

@router.get("/floor/{floor_id}", response_model=List[DeskSchema])
def get_desks_by_floor(
    floor_id: int,
    date: date = Query(...),
    db: Session = Depends(get_db)
):
    """
    API endpoint to get all desks for a specific floor.
    
    Required query parameter 'date' to filter bookings for that date.
    """
    floor = db.query(Floor).filter(Floor.id == floor_id).first()
    if not floor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Floor with id {floor_id} not found"
        )

    desks = db.query(Desk).options(joinedload(Desk.floor_entity)).filter(Desk.floor_id == floor_id).order_by(Desk.id).all()
    
    # Get all bookings for the date
    bookings = db.query(Booking).filter(
        Booking.booking_date == date,
        Booking.status == BookingStatus.ACTIVE
    ).all()
    booked_desk_map = {b.desk_id: b.user_id for b in bookings}
    
    # Create response dicts with all needed fields
    result = []
    for desk in desks:
        is_booked = desk.id in booked_desk_map
        booked_by = booked_desk_map.get(desk.id)
        floor_name = desk.floor_entity.floor_name if desk.floor_entity else None
        
        result.append(DeskSchema(
            id=desk.id,
            x=desk.x,
            y=desk.y,
            rotation=desk.rotation,
            floor_id=desk.floor_id,
            isBooked=is_booked,
            bookedBy=booked_by,
            floorName=floor_name
        ))
    
    return result

    return result