from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "City Governance System API"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://postgres:password@localhost:5432/city_mas"
    
    # Groq API (Free - Primary LLM)
    groq_api_key: str = ""
    
    # OpenAI API (Optional)
    openai_api_key: str = ""
    
    # Google Gemini API (Optional)
    google_api_key: str = ""
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def async_database_url(self) -> str:
        """Convert PostgreSQL URL to async driver"""
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        elif self.database_url.startswith("postgresql+psycopg2://"):
            return self.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
        return self.database_url
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
