"""
Configuration for Water Department Agent
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "departments"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    
    # LLM
    LLM_PROVIDER: str = "openai"  # openai or local
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.3
    
    # Agent
    DEPARTMENT: str = "water"
    MAX_PLANNING_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
