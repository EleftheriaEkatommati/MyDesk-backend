from pydantic import BaseModel
from typing import Optional

class FloorResponse(BaseModel):
    id: int
    floorNumber: int
    floorName: Optional[str] = None
