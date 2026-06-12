from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.core.db import engine
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

def get_db() -> Generator:
    with Session(engine) as session:
        yield session

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """
    Dependency to get current user from JWT token.
    Mocked for architecture definition.
    """
    # In production, decode JWT, query User table
    return {"id": 1, "role": "user"}

def get_current_admin(
    current_user = Depends(get_current_user)
):
    """
    Dependency to enforce Admin role.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
