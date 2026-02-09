"""
Configuration for Engineering Department Agent
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
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.3
    
    # Agent
    DEPARTMENT: str = "engineering"
    MAX_PLANNING_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Engineering-Specific Thresholds
    MAX_TENDER_AMOUNT_WITHOUT_APPROVAL: float = 500000  # ₹5 lakh
    MIN_CONTRACTOR_RATING: float = 3.5  # out of 5
    MONSOON_BLACKOUT_MONTHS: list = [7, 8, 9]  # July-Sept
    MAX_CONCURRENT_PROJECTS: int = 10
    MIN_SAFETY_SCORE: float = 4.0  # out of 5
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
