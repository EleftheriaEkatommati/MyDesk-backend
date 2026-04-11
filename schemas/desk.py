from pydantic import BaseModel, Field
from typing import Optional

from .floor import FloorResponse

class DeskBase(BaseModel):
    id: str
    x: float
    y: float
    rotation: int
    floor_id: int = Field(alias='floorId')

class DeskSchema(DeskBase):
    floor_entity: Optional[FloorResponse] = None

    class Config:
        from_attributes = True
        populate_by_name = True

class DeskWithStatusSchema(DeskSchema):
    is_booked: bool = Field(alias='isBooked')
    booked_by: Optional[int] = Field(None, alias='bookedBy')

    class Config(DeskSchema.Config):
        populate_by_name = True