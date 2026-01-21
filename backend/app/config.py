from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "City Governance System API"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./governance.db"
    
    # OpenAI/LangChain
    openai_api_key: str = ""
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
