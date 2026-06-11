from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.models.domain import User, UserProfile, UserRole
from app.api.schemas.auth import UserRegister, ProfileCreate, RoleCreate
import bcrypt

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)

def authenticate_user(session: Session, email: str, password: str) -> User | bool:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def register_user(session: Session, data: UserRegister) -> User:
    # Check if email exists
    statement = select(User).where(User.email == data.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
        
    hashed_pwd = hash_password(data.password)
    new_user = User(
        email=data.email,
        password_hash=hashed_pwd
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

def create_profile(session: Session, user_id: int, data: ProfileCreate) -> UserProfile:
    # Verify User exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Verify profile doesn't already exist
    statement = select(UserProfile).where(UserProfile.user_id == user_id)
    existing_profile = session.exec(statement).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Profile already exists for this user")
        
    profile = UserProfile(
        user_id=user_id,
        full_name=data.full_name,
        mobile_number=data.mobile_number,
        age=data.age,
        gender=data.gender,
        state=data.state,
        district=data.district,
        category=data.category,
        preferred_language=data.preferred_language
    )
    
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile

def assign_role(session: Session, user_id: int, data: RoleCreate) -> UserRole:
    # Verify User exists
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Check if user already has this specific role
    statement = select(UserRole).where(UserRole.user_id == user_id, UserRole.role == data.role)
    existing_role = session.exec(statement).first()
    if existing_role:
        raise HTTPException(status_code=400, detail=f"User already has the role '{data.role}'")
        
    role = UserRole(
        user_id=user_id,
        role=data.role
    )
    
    session.add(role)
    session.commit()
    session.refresh(role)
    return role
