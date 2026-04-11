from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Import all models here to register them with Base's metadata.
# This is crucial for SQLAlchemy's relationship reflection to work correctly.
from models import user, floor, desk, booking

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
