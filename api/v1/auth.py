import json
import secrets
from datetime import timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
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


def _normalize_google_setting(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


def _make_google_request(url: str, data: dict | None = None, headers: dict | None = None):
    body = None
    if data is not None:
        body = urlencode(data).encode()

    request = Request(
        url,
        data=body,
        headers=headers or {},
        method="POST" if data is not None else "GET",
    )

    try:
        with urlopen(request, timeout=10) as response:
            return json.load(response)
    except HTTPError as exc:
        try:
            error_body = exc.read().decode()
            error_json = json.loads(error_body)
            message = error_json.get("error_description") or error_json.get("error") or error_body
        except Exception:
            message = str(exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth request failed: {message}",
        )
    except URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Google OAuth network error: {exc.reason}",
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google OAuth returned an invalid response format.",
        )


def _get_google_token(code: str):
    token_endpoint = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": _normalize_google_setting(settings.GOOGLE_CLIENT_ID),
        "client_secret": _normalize_google_setting(settings.GOOGLE_CLIENT_SECRET),
        "redirect_uri": _normalize_google_setting(settings.GOOGLE_OAUTH_REDIRECT_URI),
        "grant_type": "authorization_code",
    }
    return _make_google_request(
        token_endpoint,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )


def _get_google_userinfo(access_token: str):
    userinfo_endpoint = "https://openidconnect.googleapis.com/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    return _make_google_request(userinfo_endpoint, headers=headers)


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

@router.get("/google/login")
def google_login():
    client_id = _normalize_google_setting(settings.GOOGLE_CLIENT_ID)
    client_secret = _normalize_google_setting(settings.GOOGLE_CLIENT_SECRET)
    redirect_uri = _normalize_google_setting(settings.GOOGLE_OAUTH_REDIRECT_URI)

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured in the environment.",
        )

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    authorization_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(authorization_url)


@router.get("/google/callback", response_model=AuthResponse)
def google_callback(
    code: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth error: {error}",
        )
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code from Google.",
        )
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured in the environment.",
        )

    token_data = _get_google_token(code)
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to obtain access token from Google.",
        )

    userinfo = _get_google_userinfo(access_token)
    email = userinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return an email address.",
        )

    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        default_role = crud_user.get_role_by_name(db, RoleEnum.user)
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default user role not found.",
            )
        hashed_password = get_password_hash(secrets.token_urlsafe(32))
        user = crud_user.create_user(
            db=db,
            email=email,
            name=userinfo.get("given_name") or userinfo.get("name"),
            surname=userinfo.get("family_name"),
            hashed_password=hashed_password,
        )
        user.role_id = default_role.id
        db.commit()
        db.refresh(user)

    role_name = user.role.name.value if getattr(user, "role", None) else RoleEnum.user.value
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    jwt_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

    return AuthResponse(
        id=str(user.id),
        name=user.name or user.email,
        role=role_name,
        token=jwt_token,
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
