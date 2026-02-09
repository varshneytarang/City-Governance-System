"""
Configuration for Sanitation Department Agent
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # LLM
    LLM_PROVIDER: str = "openai"  # openai, groq, or local
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.3
    
    # LLM Usage Control (to reduce API calls)
    USE_LLM_FOR_PLANNER: bool = True
    USE_LLM_FOR_OBSERVER: bool = False
    USE_LLM_FOR_POLICY: bool = False
    USE_LLM_FOR_CONFIDENCE: bool = True
    
    # Agent
    DEPARTMENT: str = "sanitation"
    MAX_PLANNING_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
