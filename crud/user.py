from sqlalchemy.orm import Session, joinedload
from models.user import User, Role, RoleEnum
from schemas.user import UserCreate
from core.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    return db.query(User).options(joinedload(User.role)).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, name=user.name, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_role_by_name(db: Session, role_name: RoleEnum):
    return db.query(Role).filter(Role.name == role_name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).options(joinedload(User.role)).offset(skip).limit(limit).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user
