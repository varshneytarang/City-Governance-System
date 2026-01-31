"""
Global configuration shared across agents.

This module centralizes LLM/provider API keys and other global env-driven
settings so agent-specific config files can import them.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class GlobalLLMSettings(BaseSettings):
    # LLM provider settings (shared)
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.3

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


global_llm_settings = GlobalLLMSettings()


class GlobalSettings(BaseSettings):
    """Shared global settings for DB and agent defaults.

    Agents can import `global_config.global_settings` to reuse these values
    so a single `.env` file configures all agents consistently.
    """

    # Database (default values - can be overridden by env)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "departments"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"

    # Agent defaults
    MAX_PLANNING_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: float = 0.7

    # Optional toggle to require LLM availability
    REQUIRE_LLM: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


global_settings = GlobalSettings()
