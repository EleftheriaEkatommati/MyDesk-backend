from pydantic import BaseModel, Field, computed_field
from typing import Optional

class DeskBase(BaseModel):
    id: str # Assuming desk ID is a string like "101"
    x: float
    y: float
    rotation: float
    floor_id: int # Foreign key to Floor

class DeskCreate(DeskBase):
    pass

class DeskSchema(DeskBase):
    isBooked: bool = False
    bookedBy: Optional[int] = None
    floorName: Optional[str] = None
    
    # Add floorId and floor for frontend compatibility
    @computed_field
    @property
    def floorId(self) -> int:
        return self.floor_id

    @computed_field
    @property
    def floor(self) -> Optional[str]:
        # For backward compatibility, same as floorName
        return self.floorName

    class Config:
        from_attributes = True # Enable ORM mode for SQLAlchemy models
        populate_by_name = True # Allow population by field name (e.g., floorId)