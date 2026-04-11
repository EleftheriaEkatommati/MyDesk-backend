from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.v1 import admin, auth, bookings, desks

app = FastAPI(title="MyDesk API")

# CORS (Cross-Origin Resource Sharing) Middleware
# This allows your frontend to make requests to your backend.
# In production, you should restrict `allow_origins` to your frontend's domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(desks.router, prefix="/api/v1/desks", tags=["Desks & Floors"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["Bookings"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the MyDesk API"}