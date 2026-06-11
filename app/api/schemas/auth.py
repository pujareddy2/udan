import re
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str

    @validator("password")
    def validate_password_strength(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
        
    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v

class ProfileCreate(BaseModel):
    full_name: str = Field(..., min_length=2)
    mobile_number: str
    age: int = Field(..., ge=13, le=120)
    gender: Literal["Male", "Female", "Other", "Prefer Not to Say"]
    state: str
    district: str
    category: Literal["General", "OBC", "SC", "ST", "Minority"]
    preferred_language: str = "en"
    
    @validator("mobile_number")
    def validate_mobile(cls, v):
        # Allow optional +91 or just 10 digits
        clean_number = re.sub(r"[^\d]", "", v)
        if len(clean_number) == 12 and clean_number.startswith("91"):
            clean_number = clean_number[2:]
        if len(clean_number) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        return clean_number

class RoleCreate(BaseModel):
    role: Literal['student', 'farmer', 'jobseeker', 'entrepreneur', 'women_entrepreneur', 'startup', 'senior_citizen']
