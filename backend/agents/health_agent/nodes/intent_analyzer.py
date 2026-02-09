"""
Intent Analyzer Node - Classifies query type and determines routing

Distinguishes between:
- Informational queries (status, inventory, reports) → Direct data retrieval
- Action requests (schedule, approve, allocate) → Full planning workflow
"""

import logging
import json
from typing import Dict

from ..state import HealthAgentState
from ..config import settings

logger = logging.getLogger(__name__)


def _get_llm_client():
    """Get LLM client for intent analysis"""
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
    except:
        return None
    return None


# Deterministic keyword patterns for quick classification
INFORMATIONAL_KEYWORDS = [
    "what", "show", "list", "how many", "status", "current", "available",
    "in stock", "inventory", "report", "summary", "check", "view", "display",
    "tell me", "get", "find", "which", "where is"
]

ACTION_KEYWORDS = [
    "schedule", "create", "approve", "allocate", "assign", "deploy", "send",
    "start", "launch", "initiate", "execute", "plan", "organize", "coordinate",
    "cancel", "modify", "update", "change", "request", "can we", "should we"
]


def intent_analyzer_node(state: HealthAgentState) -> HealthAgentState:
    """
    Analyze user intent and classify query type
    
    Returns:
        state with:
        - query_type: "informational" or "action"
        - intent: specific intent classification
        - needs_planning: boolean
    """
    
    logger.info("🔍 [NODE: Intent Analyzer]")
    
    try:
        input_event = state.get("input_event", {})
        query = input_event.get("reason", "").lower()
        request_type = input_event.get("type", "unknown")
        
        # Emergency requests always go through full workflow
        if request_type == "emergency_response" or "emergency" in query:
            logger.info("  → Emergency detected - full planning workflow")
            return {
                **state,
                "query_type": "action",
                "intent": "emergency_response",
                "needs_planning": True,
                "risk_level": "high"
            }
        
        # Try LLM classification first
        llm_client = _get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for intent analysis...")
            llm_result = _analyze_with_llm(llm_client, query, input_event)
            if llm_result:
                query_type = llm_result.get("query_type", "action")
                intent = llm_result.get("intent", "general_query")
                logger.info(f"  → LLM classified as: {query_type} ({intent})")
                
                return {
                    **state,
                    "query_type": query_type,
                    "intent": intent,
                    "needs_planning": query_type == "action"
                }
        
        # Fallback to deterministic keyword matching
        logger.info("  → Using deterministic keyword matching")
        
        # Check for informational indicators
        is_informational = any(keyword in query for keyword in INFORMATIONAL_KEYWORDS)
        is_action = any(keyword in query for keyword in ACTION_KEYWORDS)
        
        if is_informational and not is_action:
            query_type = "informational"
            intent = _classify_informational_intent(query)
            logger.info(f"  → Informational query: {intent}")
        else:
            query_type = "action"
            intent = _classify_action_intent(query, request_type)
            logger.info(f"  → Action request: {intent}")
        
        return {
            **state,
            "query_type": query_type,
            "intent": intent,
            "needs_planning": query_type == "action"
        }
        
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        # Default to action workflow on error (safer)
        return {
            **state,
            "query_type": "action",
            "intent": "unknown_request",
            "needs_planning": True
        }


def _analyze_with_llm(client, query: str, input_event: Dict) -> Dict:
    """Use LLM to classify intent"""
    try:
        prompt = f"""Classify this health department query:

Query: "{query}"
Request Type: {input_event.get('type', 'unknown')}

Classify as either:
1. "informational" - User wants to see/check/get existing data (status, inventory, reports)
2. "action" - User wants something done (schedule, create, approve, modify, plan)

Also identify the specific intent (e.g., "check_inventory", "schedule_campaign", "assess_risk").

Respond in JSON:
{{
  "query_type": "informational" or "action",
  "intent": "specific_intent_name",
  "reasoning": "brief explanation"
}}"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        logger.info(f"  LLM reasoning: {result.get('reasoning')}")
        return result
        
    except Exception as e:
        logger.warning(f"LLM intent analysis failed: {e}")
        return None


def _classify_informational_intent(query: str) -> str:
    """Classify specific informational intent"""
    if any(word in query for word in ["supply", "supplies", "stock", "inventory", "equipment", "resource"]):
        return "check_medical_supplies"
    elif any(word in query for word in ["campaign", "vaccination", "vaccine"]):
        return "check_vaccination_campaigns"
    elif any(word in query for word in ["incident", "disease", "outbreak"]):
        return "check_disease_incidents"
    elif any(word in query for word in ["facility", "facilities", "clinic", "hospital"]):
        return "check_health_facilities"
    elif any(word in query for word in ["policy", "policies", "regulation"]):
        return "check_policies"
    elif any(word in query for word in ["surveillance", "report", "reports", "monitoring"]):
        return "check_surveillance"
    elif any(word in query for word in ["budget", "spending", "cost"]):
        return "check_budget_status"
    else:
        return "general_status_query"


def _classify_action_intent(query: str, request_type: str) -> str:
    """Classify specific action intent"""
    if request_type != "unknown":
        return request_type
    
    if any(word in query for word in ["schedule", "plan", "organize"]):
        return "schedule_action"
    elif any(word in query for word in ["audit", "inspect", "check", "verify"]):
        return "conduct_audit"
    elif any(word in query for word in ["campaign", "vaccination"]):
        return "plan_campaign"
    else:
        return "general_action_request"


def intent_analyzer(state: HealthAgentState) -> HealthAgentState:
    """Alias for backward compatibility"""
    return intent_analyzer_node(state)
