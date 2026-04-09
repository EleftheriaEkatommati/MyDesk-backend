from pydantic import BaseModel
from typing import Optional

class DeskResponse(BaseModel):
    id: str
    x: float
    y: float
    rotation: int
    floorId: int
    floorName: Optional[str] = None
    floor: Optional[str] = None
    isBooked: bool
    bookedBy: Optional[str] = None

class DeskBookRequest(BaseModel):
    book: bool
