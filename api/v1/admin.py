from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from crud import user as crud_user
from schemas.user import User, UserCreate
from core.security import get_current_active_admin
from models.user import User as UserModel

router = APIRouter()

def get_db():
    from database.session import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Create a new user.
    """
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = crud_user.create_user(db=db, user=user)
    # This is a good place to assign roles if they are passed in the request
    return new_user

from schemas.user import User, UserCreate, Role as RoleSchema
from pydantic import BaseModel
from models.user import RoleEnum

class RolesUpdate(BaseModel):
    roles: List[RoleEnum]

@router.put("/users/{user_id}/roles", response_model=User)
def update_user_roles(
    user_id: int,
    roles: RolesUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_admin),
):
    """
    Update roles for a user.
    """
    db_user = crud_user.get_user_by_id(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    updated_user = crud_user.update_user_roles(db, user=db_user, roles=roles.roles)
    return updated_user

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
