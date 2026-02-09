"""
Coordination Agent Configuration
"""

import os
from typing import Dict, Any, Optional

# Import shared global settings
try:
    import global_config
    _has_global_config = True
except ImportError:
    _has_global_config = False


class CoordinationConfig:
    """Configuration for Coordination Agent"""
    
    # LLM Configuration
    if _has_global_config:
        GROQ_API_KEY: Optional[str] = global_config.global_llm_settings.GROQ_API_KEY
        LLM_MODEL: str = global_config.global_llm_settings.LLM_MODEL
        LLM_TEMPERATURE: float = global_config.global_llm_settings.LLM_TEMPERATURE
    else:
        GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", "")
        LLM_MODEL: str = "llama-3.3-70b-versatile"
        LLM_TEMPERATURE: float = 0.3
    
    # Decision Thresholds
    COMPLEXITY_THRESHOLD: float = 0.6  # Above this: use LLM
    CONFIDENCE_THRESHOLD: float = 0.7  # Below this: escalate to human
    AUTO_APPROVAL_COST_LIMIT: int = 5000000  # ₹50 lakh
    
    # Priority Levels (higher = more important)
    PRIORITY_LEVELS: Dict[str, int] = {
        "emergency": 10,
        "safety_critical": 9,
        "public_health": 8,
        "maintenance": 5,
        "expansion": 3,
        "routine": 1
    }
    
    # Conflict Resolution Rules
    EMERGENCY_OVERRIDE: bool = True
    MONSOON_MONTHS: list = [7, 8, 9]  # July, August, September
    
    # Human Escalation
    HUMAN_APPROVAL_REQUIRED_FOR: list = [
        "cost_exceeds_limit",
        "low_confidence",
        "public_safety_impact",
        "political_sensitivity",
        "legal_implications"
    ]
    
    # Database
    if _has_global_config:
        DB_HOST: Optional[str] = global_config.global_settings.DB_HOST
        DB_PORT: int = global_config.global_settings.DB_PORT
        DB_NAME: Optional[str] = global_config.global_settings.DB_NAME
        DB_USER: Optional[str] = global_config.global_settings.DB_USER
        DB_PASSWORD: Optional[str] = global_config.global_settings.DB_PASSWORD
    else:
        DB_HOST: Optional[str] = os.getenv("DB_HOST")  # No default - must be set
        DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
        DB_NAME: Optional[str] = os.getenv("DB_NAME")
        DB_USER: Optional[str] = os.getenv("DB_USER")
        DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    
    # Timeouts
    LLM_TIMEOUT: int = 30  # seconds
    HUMAN_RESPONSE_TIMEOUT: int = 86400  # 24 hours
    
    # Logging
    LOG_LEVEL: str = "INFO"
    AUDIT_ALL_DECISIONS: bool = True
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Get database connection string"""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        # Allow operation without GROQ_API_KEY (will just skip LLM features)
        if not cls.GROQ_API_KEY:
            import logging
            logging.warning("GROQ_API_KEY not set - LLM negotiation will be disabled")
        return True
