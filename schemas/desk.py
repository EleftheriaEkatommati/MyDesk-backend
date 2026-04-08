from pydantic import BaseModel
from typing import Optional

class DeskResponse(BaseModel):
    id: str
    x: float
    y: float
    rotation: int
    isBooked: bool
    bookedBy: Optional[str] = None

class DeskBookRequest(BaseModel):
    book: bool
