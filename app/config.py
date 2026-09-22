import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "PredictSense Predictive Maintenance"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase Credentials & Database Connection
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "https://frfkburreisufcdkqpji.supabase.co")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "your-supabase-anon-key")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://postgres:YOUR_PASSWORD@db.frfkburreisufcdkqpji.supabase.co:5432/postgres"
    )
    
    # JWT Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "predictsense_secret_key_super_secure_987654321")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
