from typing import List
from models.booking import Booking, BookingStatus
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from starlette import status
from schemas.desk import DeskCreate, DeskUpdate, DeskSchema
from crud import user as crud_user
from core.security import get_current_active_admin, get_password_hash
from core.email import send_desk_deleted_notification_email, send_admin_booking_cancellation_email, send_floor_deleted_notification_email
from models.desk import Desk
from schemas.floor import FloorResponse, FloorCreate
from models.floor import Floor
from schemas.user import User, UserCreate, RoleUpdate
from models.user import User as UserModel, RoleEnum
from database.session import get_db

router = APIRouter()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Create a new user.
    Here we check if the email is already registered, if not we create a new user in the database.  
    """
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed_password = get_password_hash(user.password)
    new_user = crud_user.create_user(
        db=db,
        email=user.email,
        name=user.name,
        surname=user.surname,
        hashed_password=hashed_password
    )
    
    # Assign the default 'user' role, consistent with the /register endpoint
    user_role = crud_user.get_role_by_name(db, RoleEnum.user)
    if not user_role:
        raise HTTPException(status_code=500, detail="Default user role not found. Please seed the database.")
    
    new_user.role_id = user_role.id
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}/role", response_model=User)
def update_user_role(
    user_id: int, 
    role_update: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Update role for a user. A user can only have one role.
    """
    db_user = crud_user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    role = crud_user.get_role_by_name(
        db,
        RoleEnum(role_update.role)
    )
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Role '{role_update.role}' not found")

    db_user.role_id = role.id
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0, # here we can add pagination parameters
    limit: int = 100, 
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Retrieve users.
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users



@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Delete a user by ID.
    """
    db_user = crud_user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    db.delete(db_user)
    db.commit()

@router.delete("/bookings/{booking_id}", status_code=204)
def delete_booking(
    booking_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Delete a booking by ID. If the booking is active, it notifies the
    affected user via email that their booking was cancelled.
    """
    # Eager load the user to send an email notification
    booking = db.query(Booking).options(joinedload(Booking.user)).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )

    # If the booking was active, notify the user that an admin has cancelled it.
    if booking.user and booking.status == BookingStatus.ACTIVE:
        background_tasks.add_task(
            send_admin_booking_cancellation_email,
            booking.user.email,
            booking.user.name,
            booking.desk_id,
            booking.booking_date,
        )

    db.delete(booking)
    db.commit()
    return None

@router.post("/desks", response_model=DeskSchema, status_code=201)
def create_desk(
    desk: DeskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    # ID is now auto-generated by the database, so we don't receive it.
    # The check for an existing desk by ID is removed.
    new_desk = Desk(
        floor_id=desk.floor_id,
        x=desk.x,
        y=desk.y,
        rotation=desk.rotation,
    )
    db.add(new_desk)
    db.commit()
    # Re-query to load relationship for response, as it's not loaded by default
    created_desk = db.query(Desk).options(joinedload(Desk.floor)).filter(Desk.id == new_desk.id).one()
    return created_desk


@router.put("/desks/{desk_id}", response_model=DeskSchema)
def update_desk(
    desk_id: int,
    desk_data: DeskUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Update a desk's properties (e.g., x, y, rotation).
    """
    desk = db.query(Desk).options(joinedload(Desk.floor)).filter(Desk.id == desk_id).first()
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Desk with ID {desk_id} not found",
        )
    update_data = desk_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(desk, key, value)
    db.commit()
    db.refresh(desk)
    return desk


@router.delete("/desks/{desk_id}", status_code=204)
def delete_desk(
    desk_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Delete a desk by ID. If the desk has active bookings, it notifies the
    affected users via email that their booking is cancelled.
    """
    # Eagerly load the desk with its bookings and the user for each booking
    # to efficiently send notifications without extra DB queries.
    desk = db.query(Desk).options(
        joinedload(Desk.bookings).joinedload(Booking.user)
    ).filter(Desk.id == desk_id).first()

    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desk not found",
        )

    # Find all active bookings for this desk and schedule email notifications.
    # The bookings are already loaded due to the joinedload above.
    active_bookings = [b for b in desk.bookings if b.status == BookingStatus.ACTIVE]

    for booking in active_bookings:
        # The user is pre-loaded, so this doesn't cause an extra DB query.
        if booking.user:
            background_tasks.add_task(
                send_desk_deleted_notification_email,
                booking.user.email,
                booking.user.name,
                booking.booking_date,
                desk.id
            )

    # Now, delete the desk. The `cascade="all, delete-orphan"` on the
    # Desk.bookings relationship will automatically delete all associated bookings.
    db.delete(desk)
    db.commit()
    return None

@router.post("/floors", response_model=FloorResponse, status_code=status.HTTP_201_CREATED)
def create_floor(
    floor_data: FloorCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Create a new floor.
    """
    existing_floor = db.query(Floor).filter(Floor.floor_number == floor_data.floor_number).first()
    if existing_floor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Floor with number {floor_data.floor_number} already exists."
        )

    new_floor = Floor(
        floor_number=floor_data.floor_number,
        floor_name=floor_data.floor_name
    )
    db.add(new_floor)
    db.commit()
    db.refresh(new_floor)
    return new_floor

@router.delete("/floors/{floor_id}", status_code=204)
def delete_floor(
    floor_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Delete a floor and all its associated desks.
    This will also cancel all active bookings for the desks on this floor and
    notify the affected users via email.
    """
    # Eagerly load the floor with its desks, and for each desk, its bookings,
    # and for each booking, its user. This is a deep load to get all necessary
    # data in one go for sending notifications.
    floor = db.query(Floor).options(
        joinedload(Floor.desks).joinedload(Desk.bookings).joinedload(Booking.user)
    ).filter(Floor.id == floor_id).first()

    if not floor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Floor with ID {floor_id} not found",
        )

    # Collect all active bookings and schedule notifications
    for desk in floor.desks:
        active_bookings = [b for b in desk.bookings if b.status == BookingStatus.ACTIVE]
        for booking in active_bookings:
            if booking.user:
                background_tasks.add_task(
                    send_floor_deleted_notification_email,
                    user_email=booking.user.email,
                    user_name=booking.user.name,
                    booking_date=booking.booking_date,
                    desk_id=desk.id,
                    floor_name=floor.floor_name,
                    floor_number=floor.floor_number,
                )

    # Now, delete the floor. The cascade settings will handle deleting all
    # associated desks and their bookings automatically.
    db.delete(floor)
    db.commit()
    return None