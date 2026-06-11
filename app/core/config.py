import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Udaan AI"
    
    # SQLite Configuration
    # Uses a local file udaan.db in the data folder
    DATABASE_URL: str = "sqlite:///./data/udaan_v2.db"

    class Config:
        case_sensitive = True

settings = Settings()

