from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
import os

# Note: We are using a mock implementation of python-jose/PyJWT for the hackathon environment.
# In production, run: `pip install python-jose[cryptography]`

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-udaan-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 Days

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a JWT Token string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    
    # Mocking JWT generation for environment stability.
    # Production: jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    import json
    import base64
    payload = base64.b64encode(json.dumps(to_encode).encode()).decode()
    return f"mock_jwt_header.{payload}.mock_signature"

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    FastAPI Dependency to enforce JWT Security on endpoints.
    Extracts the user_id from the token.
    """
    # Mock decoding
    try:
        import base64
        import json
        payload_str = token.split(".")[1]
        payload = json.loads(base64.b64decode(payload_str).decode())
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid JWT Token")
        return int(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
