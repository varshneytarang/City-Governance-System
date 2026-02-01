"""
Configuration for Health Department Agent

Aligns with water_agent.config: loads DB and LLM settings from shared
`global_config`, driven by `.env` without special prefixes.
"""

from typing import Optional
from pydantic_settings import BaseSettings

import global_config


class HealthSettings(BaseSettings):
    """Application settings loaded from environment variables.

    Defaults are read from `global_config` so a single `.env` configures
    DB and LLM for all agents consistently.
    """

    # Database (defaults from global settings)
    DB_HOST: str = global_config.global_settings.DB_HOST
    DB_PORT: int = global_config.global_settings.DB_PORT
    DB_NAME: str = global_config.global_settings.DB_NAME
    DB_USER: str = global_config.global_settings.DB_USER
    DB_PASSWORD: str = global_config.global_settings.DB_PASSWORD

    # LLM (defaults from global LLM settings)
    LLM_PROVIDER: str = global_config.global_llm_settings.LLM_PROVIDER
    OPENAI_API_KEY: Optional[str] = global_config.global_llm_settings.OPENAI_API_KEY
    GROQ_API_KEY: Optional[str] = global_config.global_llm_settings.GROQ_API_KEY
    LLM_MODEL: str = global_config.global_llm_settings.LLM_MODEL
    LLM_TEMPERATURE: float = global_config.global_llm_settings.LLM_TEMPERATURE

    # Agent-specific
    DEPARTMENT: str = "health"
    MAX_PLANNING_ATTEMPTS: int = global_config.global_settings.MAX_PLANNING_ATTEMPTS
    CONFIDENCE_THRESHOLD: float = global_config.global_settings.CONFIDENCE_THRESHOLD
    HEALTH_CONFIDENCE_THRESHOLD: float = 0.65
    HEALTH_DATA_SOURCE: Optional[str] = None  # e.g., 'surveillance_api' or DB view name

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = HealthSettings()
