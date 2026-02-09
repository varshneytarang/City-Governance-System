"""
Configuration for Water Department Agent
"""

from pydantic_settings import BaseSettings
from typing import Optional

# Import shared global settings and LLM defaults
import global_config


class Settings(BaseSettings):
    """Application settings loaded from environment variables

    Defaults are read from `global_config.global_settings` so a single
    `.env` file can configure DB and agent-wide defaults for all agents.
    """

    # Database (default to global settings)
    DB_HOST: Optional[str] = global_config.global_settings.DB_HOST
    DB_PORT: int = global_config.global_settings.DB_PORT
    DB_NAME: Optional[str] = global_config.global_settings.DB_NAME
    DB_USER: Optional[str] = global_config.global_settings.DB_USER
    DB_PASSWORD: Optional[str] = global_config.global_settings.DB_PASSWORD

    # LLM (defaults come from global shared LLM settings)
    LLM_PROVIDER: str = global_config.global_llm_settings.LLM_PROVIDER
    OPENAI_API_KEY: Optional[str] = global_config.global_llm_settings.OPENAI_API_KEY
    GROQ_API_KEY: Optional[str] = global_config.global_llm_settings.GROQ_API_KEY
    LLM_MODEL: str = global_config.global_llm_settings.LLM_MODEL
    LLM_TEMPERATURE: float = global_config.global_llm_settings.LLM_TEMPERATURE

    # Agent (defaults come from global settings)
    DEPARTMENT: str = "water"
    MAX_PLANNING_ATTEMPTS: int = global_config.global_settings.MAX_PLANNING_ATTEMPTS
    CONFIDENCE_THRESHOLD: float = global_config.global_settings.CONFIDENCE_THRESHOLD

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
