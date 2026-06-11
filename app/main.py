from fastapi import FastAPI
from app.core.db import init_db
from app.models import *  # This imports the __init__.py which registers all models

# Initialize FastAPI App
app = FastAPI(title="Udaan AI", version="1.0.0")

@app.on_event("startup")
def on_startup():
    print("Initializing Database...")
    init_db()
    print("Database Initialized.")

@app.get("/")
def root():
    return {"message": "Welcome to Udaan AI API"}

# Include Routers
from app.api.routers.auth import router as auth_router
from app.api.routers.profile import router as profile_router
from app.api.routers.opportunities import router as opp_router
from app.api.routers.wallet import router as wallet_router
from app.api.routers.lifecycle import router as lifecycle_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(opp_router, prefix="/api/v1")
app.include_router(wallet_router, prefix="/api/v1")
app.include_router(lifecycle_router, prefix="/api/v1")
