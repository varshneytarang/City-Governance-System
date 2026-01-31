"""
Health agent configuration. Reuses `water_agent.config` for defaults but adds
health-specific settings.
"""

from typing import Optional
from pydantic_settings import BaseSettings
from water_agent.config import Settings as WaterSettings

# Import shared LLM settings from global_config so health agent can use same keys
import global_config


class HealthSettings(WaterSettings):
    HEALTH_CONFIDENCE_THRESHOLD: float = 0.65
    HEALTH_DATA_SOURCE: Optional[str] = None  # e.g., 'surveillance_api' or DB view name

    # LLM defaults come from shared global settings; allow HEALTH_ env prefix to override
    LLM_PROVIDER: str = global_config.global_llm_settings.LLM_PROVIDER
    OPENAI_API_KEY: Optional[str] = global_config.global_llm_settings.OPENAI_API_KEY
    GROQ_API_KEY: Optional[str] = global_config.global_llm_settings.GROQ_API_KEY
    LLM_MODEL: str = global_config.global_llm_settings.LLM_MODEL
    LLM_TEMPERATURE: float = global_config.global_llm_settings.LLM_TEMPERATURE

    class Config:
        env_prefix = "HEALTH_"
        env_file = ".env"


settings = HealthSettings()
