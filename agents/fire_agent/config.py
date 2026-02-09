"""
Fire Department Configuration

Settings for the fire department autonomous agent.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Fire Department Agent Settings"""
    
    # Department identification
    DEPARTMENT: str = "fire"
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "city_governance"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # LLM Configuration
    LLM_PROVIDER: str = "groq"  # "groq" or "openai"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.3
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # LLM Usage Control (to reduce API calls)
    USE_LLM_FOR_PLANNER: bool = True
    USE_LLM_FOR_OBSERVER: bool = False
    USE_LLM_FOR_POLICY: bool = False
    USE_LLM_FOR_CONFIDENCE: bool = True
    
    # Agent Behavior
    CONFIDENCE_THRESHOLD: float = 0.70
    MAX_PLANNING_ATTEMPTS: int = 3
    
    # Fire-specific thresholds
    MAX_RESPONSE_TIME_MINUTES: int = 10
    MIN_FIREFIGHTERS_PER_TRUCK: int = 3
    MIN_TRUCK_FUEL_PERCENT: int = 30
    MIN_HYDRANT_PRESSURE_PSI: int = 50
    MAX_STATION_STAFFING_PERCENT: int = 90
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env


settings = Settings()
