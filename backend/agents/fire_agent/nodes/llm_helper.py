"""
LLM Helper - Shared LLM client initialization
"""

import logging
from ..config import settings

logger = logging.getLogger(__name__)


def get_llm_client():
    """Get configured LLM client (Groq or OpenAI)"""
    try:
        if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
            import openai
            return openai.OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
        elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            import openai
            return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize LLM client: {e}")
        return None
    return None


def call_llm_with_fallback(prompt, fallback_fn):
    """
    Call LLM with a deterministic fallback.
    
    Args:
        prompt: The prompt to send to LLM
        fallback_fn: Function to call if LLM unavailable
        
    Returns:
        LLM response or fallback result
    """
    try:
        client = get_llm_client()
        if client:
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.LLM_TEMPERATURE
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        logger.debug(f"LLM call failed, using fallback: {e}")
    
    return fallback_fn()
