"""
Configuration for Sanitation Department Agent
"""

from pydantic_settings import BaseSettings
from typing import Optional
try:
    import global_config
    _global_llm = getattr(global_config, "global_llm_settings", None)
except Exception:
    _global_llm = None


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DB_HOST: Optional[str] = None
    DB_PORT: int = 5432
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    
    # LLM
    # Prefer global LLM settings when available (so all agents use same provider/keys)
    LLM_PROVIDER: str = _global_llm.LLM_PROVIDER if _global_llm else "openai"
    OPENAI_API_KEY: Optional[str] = _global_llm.OPENAI_API_KEY if _global_llm else None
    GROQ_API_KEY: Optional[str] = _global_llm.GROQ_API_KEY if _global_llm else None
    LLM_MODEL: str = _global_llm.LLM_MODEL if _global_llm else "gpt-4"
    LLM_TEMPERATURE: float = _global_llm.LLM_TEMPERATURE if _global_llm else 0.3
    
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
