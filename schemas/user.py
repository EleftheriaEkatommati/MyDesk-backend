from pydantic import BaseModel, EmailStr
from typing import List, Optional

from models.user import RoleEnum

class RoleBase(BaseModel):
    name: RoleEnum

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    role: Optional[Role] = None

    class Config:
        from_attributes = True
