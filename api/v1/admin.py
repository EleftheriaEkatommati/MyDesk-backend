from typing import List
from models.booking import Booking
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from schemas.desk import DeskCreate
from crud import user as crud_user
from core.security import get_current_active_admin, get_password_hash
from models.desk import Desk
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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Delete a booking by ID.
    """
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found",
        )
    db.delete(booking)
    db.commit()
    return {"message": "Booking deleted successfully"}

@router.post("/desks", status_code=201)
def create_desk(
    desk: DeskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    new_desk = Desk(
        id=desk.id,
        floor_id=desk.floor_id,
        x=desk.x,
        y=desk.y,
        rotation=desk.rotation,
    )
    db.add(new_desk)
    db.commit()
    db.refresh(new_desk)
    return new_desk


@router.delete("/desks/{desk_id}", status_code=204)
def delete_desk(
    desk_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Delete a desk by ID.
    """
    desk = db.query(Desk).filter(Desk.id == desk_id).first()
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desk not found",
        )
    db.delete(desk)
    db.commit()
    return {"message": "Desk deleted successfully"}