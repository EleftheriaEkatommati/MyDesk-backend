from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from core.config import settings
from crud import user as crud_user
from database.session import get_db
from schemas.token import TokenData
from models.user import RoleEnum, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # this is  needed to hash and verify passwords, bcrypt is a secure hashing algorithm that is widely used for password hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") # this is a standard way to define the token URL for OAuth2 authentication, it tells FastAPI where to find the login endpoint that issues JWT tokens
#for example, when a user tries to access a protected endpoint, FastAPI will look for the JWT token in the Authorization header, extract it and pass it to the get_current_user function to verify it and retrieve the user details.

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud_user.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_admin(current_user: User = Depends(get_current_user)):
    # The user object from get_current_user has a lazy-loaded 'role' relationship.
    # Accessing current_user.role will trigger a query to fetch the role.
    # We need to check if the role is present and if its name is 'admin'.
    if not current_user.role or current_user.role.name != RoleEnum.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user
