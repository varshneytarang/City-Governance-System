"""
Global Configuration Module

Provides shared configuration settings for all agents and the backend.
This module defines global database and LLM settings that are used
across all department agents and the coordination agent.

Usage:
    from global_config import global_settings, global_llm_settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Load .env file using python-dotenv for reliability
from dotenv import load_dotenv

# Determine .env file location (check backend dir, then parent dir)
_backend_dir = Path(__file__).parent
_env_path = _backend_dir / ".env"
if not _env_path.exists():
    # Try parent directory (project root)
    _env_path = _backend_dir.parent / ".env"

# Load the .env file explicitly
if _env_path and _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
    print(f"✅ Loaded environment from: {_env_path}")
else:
    print("⚠️  No .env file found, using environment variables")


class GlobalSettings(BaseSettings):
    """
    Global application settings shared across all agents.
    
    These settings provide defaults for database connection and 
    agent behavior that can be overridden by individual agents.
    """
    
    # Database Configuration
    DB_HOST: str = None  # Must be set via environment variable
    DB_PORT: int = 5432
    DB_NAME: str = "city_mas"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "passwordpassword"
    
    # Agent Behavior Defaults
    MAX_PLANNING_ATTEMPTS: int = 3
    CONFIDENCE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = str(_env_path) if _env_path else ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


class GlobalLLMSettings(BaseSettings):
    """
    Global LLM configuration shared across all agents.
    
    Provides centralized LLM configuration (provider, API keys, model settings)
    that all department agents can use as defaults.
    """
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "groq"  # "groq" or "openai"
    
    # API Keys (at least one should be set based on provider)
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Model Configuration
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.3
    
    class Config:
        env_file = str(_env_path) if _env_path else ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global instances - these are imported by agents and backend
global_settings = GlobalSettings()
global_llm_settings = GlobalLLMSettings()


# Validation: Ensure API key is set for selected provider
def validate_llm_config():
    """Validate LLM configuration on module import"""
    if global_llm_settings.LLM_PROVIDER == "groq":
        if not global_llm_settings.GROQ_API_KEY:
            import warnings
            warnings.warn(
                "GROQ_API_KEY not set but LLM_PROVIDER is 'groq'. "
                "Agents will operate in fallback mode without LLM capabilities.",
                UserWarning
            )
    elif global_llm_settings.LLM_PROVIDER == "openai":
        if not global_llm_settings.OPENAI_API_KEY:
            import warnings
            warnings.warn(
                "OPENAI_API_KEY not set but LLM_PROVIDER is 'openai'. "
                "Agents will operate in fallback mode without LLM capabilities.",
                UserWarning
            )


# Run validation on import
validate_llm_config()
