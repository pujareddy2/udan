from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Udaan AI"
    API_V1_STR: str = "/api/v1"
    
    # SECURITY
    JWT_SECRET_KEY: str = "supersecretkey_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # DATABASE
    DATABASE_URL: str = "sqlite:///./udaan_v2.db"
    
    # EXTERNAL APIS
    GEMINI_API_KEY: str = ""
    SERPER_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # STORAGE (S3 or Cloudinary)
    STORAGE_PROVIDER: str = "cloudinary" # or "s3"
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
