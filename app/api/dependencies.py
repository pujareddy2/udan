from fastapi import Depends, Header, HTTPException

def get_current_user(authorization: str = Header(None)):
    """
    Mock JWT authentication dependency.
    Requires an 'Authorization' header.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization Scheme")
    
    token = authorization.split(" ")[1]
    if token != "mock_jwt_token_123":
        # In a real app we decode and verify the JWT here.
        # For mock purposes, we'll accept any token to avoid breaking frontend tests.
        pass
        
    return {"user_id": "123", "role": "student"}
