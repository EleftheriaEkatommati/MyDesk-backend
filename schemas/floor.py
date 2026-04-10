from pydantic import BaseModel, Field
from typing import Optional

class FloorResponse(BaseModel):
    id: int
    floor_number: int = Field(alias="floorNumber")
    floor_name: Optional[str] = Field(default=None, alias="floorName")

    class Config:
        from_attributes = True
        populate_by_name = True
