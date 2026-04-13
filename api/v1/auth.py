from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status

from crud import user as crud_user
from schemas.user import UserCreate, User
from schemas.token import Token
from database.session import get_db
from models.user import RoleEnum, User as UserModel
from core.security import verify_password, create_access_token, get_current_user, get_password_hash
from core.config import settings

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    id: str
    name: str
    role: str
    token: str

router = APIRouter()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED) # here get as arguments the user details and create a new user in the database
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    user_role = crud_user.get_role_by_name(db, RoleEnum.user)
    if not user_role:
        # This should be seeded in a real app
        raise HTTPException(status_code=500, detail="Default user role not found.")

    # The create_user function in crud should be updated to just create the user object
    hashed_password = get_password_hash(user.password)
    new_user = crud_user.create_user(
        db=db,
        email=user.email,
        name=user.name,
        surname=user.surname,
        hashed_password=hashed_password
    )

    new_user.role_id = user_role.id
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=AuthResponse) 
def login(request: LoginRequest, db: Session = Depends(get_db)): 
    user = crud_user.get_user_by_email(db, email=request.email)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # Ensure the role is fetched and included
    return AuthResponse(
        id=str(user.id),
        name=user.name or user.email,
        role=user.role.name.value if user.role else RoleEnum.user.value, # Default to 'user' if role somehow missing
        token=access_token
    )

@router.get("/me", response_model=AuthResponse)
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    # To use existing get_current_user logic but returning the frontend required shape
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.email}, expires_delta=access_token_expires
    )
    return AuthResponse(
        id=str(current_user.id),
        name=current_user.name or current_user.email,
        token=access_token
    )

@router.get("/me/profile", response_model=User)
def read_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    """
    Get the profile of the currently authenticated user.
    """
    return current_user
