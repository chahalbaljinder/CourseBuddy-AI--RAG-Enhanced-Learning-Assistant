import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info").lower()
    MAX_RESPONSE_TIME: int = int(os.getenv("MAX_RESPONSE_TIME", "30"))
    
    # Google AI settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # Data paths
    COURSE_DATA_PATH: str = os.getenv("COURSE_DATA_PATH", "./data/course_content")
    DISCOURSE_DATA_PATH: str = os.getenv("DISCOURSE_DATA_PATH", "./data/discourse_posts")
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
    
    # Performance settings
    NUM_RETRIEVED_DOCS: int = int(os.getenv("NUM_RETRIEVED_DOCS", "3"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
