from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database.session import SessionLocal
from models.desk import Desk as DeskModel
from models.user import User as UserModel
from schemas.desk import DeskResponse, DeskBookRequest
from core.security import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[DeskResponse])
def get_desks(db: Session = Depends(get_db)):
    desks = db.query(DeskModel).all()
    return [
        DeskResponse(
            id=str(desk.id),
            x=desk.x,
            y=desk.y,
            rotation=desk.rotation,
            isBooked=desk.is_booked,
            bookedBy=str(desk.booked_by) if desk.booked_by else None
        ) for desk in desks
    ]

@router.post("/{desk_id}/book", response_model=DeskResponse)
def book_desk(
    desk_id: str,
    request: DeskBookRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    desk = db.query(DeskModel).filter(DeskModel.id == desk_id).first()
    if not desk:
        raise HTTPException(status_code=404, detail="Desk not found")
        
    if request.book:
        if desk.is_booked:
            raise HTTPException(status_code=400, detail="Desk is already booked")
        desk.is_booked = True
        desk.booked_by = current_user.id
    else:
        if desk.booked_by != current_user.id:
            raise HTTPException(status_code=403, detail="You cannot unbook a desk booked by another user")
        desk.is_booked = False
        desk.booked_by = None
        
    db.commit()
    db.refresh(desk)
    
    return DeskResponse(
        id=str(desk.id),
        x=desk.x,
        y=desk.y,
        rotation=desk.rotation,
        isBooked=desk.is_booked,
        bookedBy=str(desk.booked_by) if desk.booked_by else None
    )
