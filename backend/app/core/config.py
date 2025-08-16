from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/travel_guide"
    
    # AI Services
    WATSONX_API_KEY: str = ""
    WATSONX_PROJECT_ID: str = ""
    HF_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    USE_REPLICATE: bool = False
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Supabase (optional)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    
    # Firebase (optional)
    FIREBASE_CONFIG: str = ""
    
    # Demo credentials
    DEMO_EMAIL: str = "demo@travelguide.id"
    DEMO_PASSWORD: str = "demo123456"
    
    # Application settings
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    MAX_IMAGE_SIZE: int = 5242880  # 5MB
    CACHE_TTL: int = 3600  # 1 hour
    
    # File upload settings
    UPLOAD_DIR: str = "uploads"
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
