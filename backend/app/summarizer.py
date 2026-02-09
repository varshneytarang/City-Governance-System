"""
LLM-based Chat Summarization Service

Generates concise 2-line summaries of agent conversations for the dashboard.
"""

import logging
from typing import Dict, Any, Optional
import json

logger = logging.getLogger(__name__)


def generate_chat_summary(request: Dict[str, Any], response: Dict[str, Any]) -> str:
    """
    Generate a 2-line summary of a chat conversation using LLM.
    
    Args:
        request: The user's request/query
        response: The agent's response
        
    Returns:
        A concise 2-line summary (max 150 characters)
    """
    try:
        from global_config import global_llm_settings
        
        # If LLM is not configured, return a simple summary
        if not global_llm_settings.GROQ_API_KEY and not global_llm_settings.OPENAI_API_KEY:
            return _generate_simple_summary(request, response)
        
        # Prepare conversation context
        conversation_text = _prepare_conversation_text(request, response)
        
        # Generate summary using LLM
        summary_prompt = f"""Summarize this government agent conversation in exactly 2 short lines (max 150 characters total).
Focus on: what the user asked and what action was taken.
Be concise and clear.

Conversation:
{conversation_text}

Summary (2 lines max):"""

        if global_llm_settings.LLM_PROVIDER == "groq":
            summary = _summarize_with_groq(summary_prompt)
        elif global_llm_settings.LLM_PROVIDER == "openai":
            summary = _summarize_with_openai(summary_prompt)
        else:
            summary = _generate_simple_summary(request, response)
        
        # Ensure it's not too long
        return _truncate_summary(summary)
        
    except Exception as e:
        logger.warning(f"Failed to generate LLM summary: {e}")
        return _generate_simple_summary(request, response)


def _prepare_conversation_text(request: Dict[str, Any], response: Dict[str, Any]) -> str:
    """Prepare conversation text for summarization"""
    parts = []
    
    # Extract user query
    query = (request.get('query') or 
             request.get('description') or 
             request.get('message') or
             request.get('type', 'Unknown request'))
    parts.append(f"User: {query}")
    
    # Extract location if present
    if request.get('location'):
        parts.append(f"Location: {request.get('location')}")
    
    # Extract agent response
    if response:
        decision = response.get('decision', 'unknown')
        reasoning = response.get('reasoning', '')
        parts.append(f"Agent Decision: {decision}")
        if reasoning and len(reasoning) < 200:
            parts.append(f"Reason: {reasoning}")
    
    return "\n".join(parts)


def _summarize_with_groq(prompt: str) -> str:
    """Generate summary using Groq API"""
    try:
        from groq import Groq
        from global_config import global_llm_settings
        
        client = Groq(api_key=global_llm_settings.GROQ_API_KEY)
        
        response = client.chat.completions.create(
            model=global_llm_settings.LLM_MODEL or "llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a concise summarizer. Generate exactly 2 short lines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100,
            timeout=5.0
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.warning(f"Groq summarization failed: {e}")
        raise


def _summarize_with_openai(prompt: str) -> str:
    """Generate summary using OpenAI API"""
    try:
        from openai import OpenAI
        from global_config import global_llm_settings
        
        client = OpenAI(api_key=global_llm_settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=global_llm_settings.LLM_MODEL or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise summarizer. Generate exactly 2 short lines."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100,
            timeout=5.0
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.warning(f"OpenAI summarization failed: {e}")
        raise


def _generate_simple_summary(request: Dict[str, Any], response: Dict[str, Any]) -> str:
    """Generate a simple rule-based summary when LLM is not available"""
    # Extract key information
    query = (request.get('query') or 
             request.get('description') or 
             request.get('message') or
             request.get('type', '').replace('_', ' ').title())
    
    location = request.get('location', '')
    decision = response.get('decision', 'processed') if response else 'processed'
    
    # Build simple 2-line summary
    line1 = f"Query: {query[:60]}..." if len(query) > 60 else f"Query: {query}"
    
    if location and decision:
        line2 = f"Action: {decision} for {location}"
    elif location:
        line2 = f"Location: {location}"
    elif decision:
        line2 = f"Result: {decision}"
    else:
        line2 = "Request processed successfully"
    
    return f"{line1}\n{line2}"


def _truncate_summary(summary: str) -> str:
    """Ensure summary is not too long (max 150 chars)"""
    lines = summary.strip().split('\n')
    
    # Take first 2 lines
    result_lines = []
    for line in lines[:2]:
        line = line.strip()
        if line:
            # Truncate line if too long
            if len(line) > 75:
                line = line[:72] + '...'
            result_lines.append(line)
    
    result = '\n'.join(result_lines)
    
    # If still too long, truncate
    if len(result) > 150:
        result = result[:147] + '...'
    
    return result
