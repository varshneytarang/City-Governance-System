from pydantic_settings import BaseSettings
from typing import Optional
import global_config


class FinanceSettings(BaseSettings):
    """Basic finance settings for scaffolded agent."""

    # Simple budget placeholder (scaffold)
    BUDGET_TOTAL: float = 100000.0
    MIN_RESERVE_PERCENT: float = 5.0

    # Database defaults (reuse global settings so `.env` is centralized)
    DB_HOST: str = global_config.global_settings.DB_HOST
    DB_PORT: int = global_config.global_settings.DB_PORT
    DB_NAME: str = global_config.global_settings.DB_NAME
    DB_USER: str = global_config.global_settings.DB_USER
    DB_PASSWORD: str = global_config.global_settings.DB_PASSWORD

    # LLM defaults (optional)
    LLM_PROVIDER: str = global_config.global_llm_settings.LLM_PROVIDER
    OPENAI_API_KEY: Optional[str] = global_config.global_llm_settings.OPENAI_API_KEY
    GROQ_API_KEY: Optional[str] = global_config.global_llm_settings.GROQ_API_KEY
    LLM_MODEL: str = global_config.global_llm_settings.LLM_MODEL
    LLM_TEMPERATURE: float = global_config.global_llm_settings.LLM_TEMPERATURE

    class Config:
        env_prefix = "FINANCE_"
        env_file = ".env"


settings = FinanceSettings()
