"""
Task Orchestration Configuration
"""

import os
from typing import Optional

# Import shared global settings
try:
    from global_config import global_settings, global_llm_settings
    _has_global_config = True
except ImportError:
    _has_global_config = False


class TaskOrchestrationConfig:
    """Configuration for Task Orchestration System"""
    
    # LLM Configuration (for contingency planning)
    if _has_global_config:
        GROQ_API_KEY: Optional[str] = global_llm_settings.GROQ_API_KEY
        OPENAI_API_KEY: Optional[str] = global_llm_settings.OPENAI_API_KEY
        LLM_PROVIDER: str = global_llm_settings.LLM_PROVIDER
        LLM_MODEL: str = global_llm_settings.LLM_MODEL
        LLM_TEMPERATURE: float = global_llm_settings.LLM_TEMPERATURE
    else:
        GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
        OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
        LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
        LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))
    
    # Database Configuration
    if _has_global_config:
        DB_HOST: str = global_settings.DB_HOST
        DB_PORT: int = global_settings.DB_PORT
        DB_NAME: str = global_settings.DB_NAME
        DB_USER: str = global_settings.DB_USER
        DB_PASSWORD: str = global_settings.DB_PASSWORD
    else:
        DB_HOST: str = os.getenv("DB_HOST", "localhost")
        DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
        DB_NAME: str = os.getenv("DB_NAME", "departments")
        DB_USER: str = os.getenv("DB_USER", "postgres")
        DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    
    # Task Management Settings
    MAX_CONTINGENCY_PLANS: int = 5
    AUTO_GENERATE_CONTINGENCY: bool = True
    CONTINGENCY_GENERATION_THRESHOLD: float = 0.7  # Generate if confidence < 0.7
    
    # Dependency Resolution
    MAX_DEPENDENCY_DEPTH: int = 10  # Prevent infinite chains
    CIRCULAR_DEPENDENCY_CHECK: bool = True
    
    # Notification Settings
    ENABLE_NOTIFICATIONS: bool = True
    NOTIFICATION_BATCH_SIZE: int = 50
    NOTIFICATION_RETRY_ATTEMPTS: int = 3
    NOTIFICATION_RETRY_DELAY_SECONDS: int = 60
    
    # Deadline Reminders
    SEND_REMINDER_HOURS_BEFORE_DEADLINE: list = [24, 12, 4, 1]  # Hours before deadline
    SEND_OVERDUE_REMINDERS: bool = True
    OVERDUE_REMINDER_INTERVAL_HOURS: int = 6
    
    # Knowledge Graph Settings
    KG_AUTO_LAYOUT: bool = True
    KG_LAYOUT_ALGORITHM: str = "hierarchical"  # hierarchical, force-directed, circular
    KG_UPDATE_REALTIME: bool = True
    
    # Approval Settings
    AUTO_APPROVAL_COST_LIMIT: int = 50000  # Tasks under this cost auto-approve
    REQUIRE_APPROVAL_FOR_CRITICAL: bool = True
    APPROVAL_TIMEOUT_HOURS: int = 48
    
    # Performance Settings
    TASK_CACHE_TTL_SECONDS: int = 300  # Cache task data for 5 minutes
    ENABLE_ASYNC_PROCESSING: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_TASK_STATE_CHANGES: bool = True
    LOG_DEPENDENCY_RESOLUTION: bool = True
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Get database connection string"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        # LLM is optional - contingency plans can be manual
        if not cls.GROQ_API_KEY and not cls.OPENAI_API_KEY:
            import logging
            logging.warning(
                "No LLM API keys configured - contingency plan generation will be disabled. "
                "Plans can still be created manually."
            )
        
        # Database is required
        if not all([cls.DB_HOST, cls.DB_NAME, cls.DB_USER]):
            raise ValueError("Database configuration incomplete")
        
        return True


# Single instance
task_config = TaskOrchestrationConfig()
task_config.validate()
