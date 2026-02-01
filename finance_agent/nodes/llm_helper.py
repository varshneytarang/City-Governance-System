"""LLM helper for Finance Agent - initialize OpenAI/Groq client using Finance settings."""

import logging
from finance_agent.config import settings

logger = logging.getLogger(__name__)


def get_llm_client():
    """Return an OpenAI-compatible client or None.

    Respects `settings.LLM_PROVIDER` and `settings.OPENAI_API_KEY` / `settings.GROQ_API_KEY`.
    """
    try:
        if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
            import openai
            return openai.OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            import openai
            return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        logger.warning(f"Finance LLM client init failed: {e}")
        return None

    return None
