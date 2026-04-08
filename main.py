from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database.session import SessionLocal
from database.base import Base
from database.session import engine

from api.v1 import auth, admin, desks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MyDesk Backend")

# Configure CORS
origins = [
    "http://localhost:3000",  # Default React/Next.js/Vue port
    "http://localhost:5173",  # Default Vite port
    "*"  # Allows all origins (for development only, you should restrict this in production)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(desks.router, prefix="/api/desks", tags=["desks"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to MyDesk Backend"}

@app.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "ok", "database": "ok"}
    except Exception as e:
        return {"status": "ok", "database": "error", "detail": str(e)}

