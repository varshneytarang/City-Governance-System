"""
PHASE 5: Goal Setter Node

Give the agent a specific purpose using LLM.

LLM formulates clear, actionable goals based on intent and context.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)


# Goal mapping from intent
GOAL_MAPPING = {
    "negotiate_schedule": "Evaluate feasibility of requested schedule change",
    "emergency_response": "Assess emergency and recommend immediate actions",
    "coordinate_maintenance": "Plan maintenance without disrupting service",
    "assess_capacity": "Determine current and future capacity",
    "respond_to_incident": "Analyze incident and recommend resolution",
    "plan_project": "Evaluate project feasibility and resource requirements",
    "unknown_request": "Understand request and determine next steps"
}


def goal_setter_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 5: Goal Setter Node (LLM-Enhanced)
    
    Uses LLM to formulate clear, actionable goals.
    """
    
    logger.info("🎯 [NODE: Goal Setter]")
    
    try:
        intent = state.get("intent", "unknown_request")
        input_event = state.get("input_event", {})
        risk_level = state.get("risk_level", "low")
        context = state.get("context", {})
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for goal formulation...")
            llm_goal = _formulate_goal_with_llm(llm_client, intent, input_event, risk_level, context)
            
            if llm_goal:
                goal = llm_goal
                logger.info(f"  → LLM Goal: {goal}")
                state["goal"] = goal
                return state
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        base_goal = GOAL_MAPPING.get(intent, GOAL_MAPPING["unknown_request"])
        
        # Enhance goal with specific details from request
        goal = base_goal
        
        # Add specifics based on request type
        request_type = input_event.get("type", "")
        
        if request_type == "schedule_shift_request":
            requested_days = input_event.get("requested_shift_days", "?")
            location = input_event.get("location", "?")
            goal += f" for {requested_days} days at {location}"
        
        elif request_type == "maintenance_request":
            activity = input_event.get("activity", "maintenance")
            goal += f" for {activity}"
        
        elif request_type == "incident_report":
            incident_type = input_event.get("incident_type", "incident")
            goal += f" ({incident_type})"
        
        logger.info(f"  → Goal: {goal}")
        
        state["goal"] = goal
        
    except Exception as e:
        logger.error(f"✗ Goal setter error: {e}")
        state["goal"] = "Handle water department request"
    
    return state


def _formulate_goal_with_llm(client, intent: str, input_event: dict, risk_level: str, context: dict) -> str:
    """Use LLM to formulate a clear, actionable goal"""
    try:
        prompt = f"""Formulate a clear, actionable goal for this Water Department request.

INTENT: {intent}
RISK LEVEL: {risk_level}

REQUEST:
{json.dumps(input_event, indent=2)}

CONTEXT:
- Active Projects: {len(context.get('active_projects', []))}
- Available Workers: {context.get('worker_info', {}).get('available_count', 'unknown')}
- Budget Available: ${context.get('budget_status', {}).get('available', 0):,}

Return ONLY valid JSON:
{{
  "goal": "Specific, measurable, actionable goal statement (1-2 sentences)",
  "success_criteria": ["criterion 1", "criterion 2"],
  "constraints": ["constraint 1", "constraint 2"]
}}

The goal should:
1. Be specific and actionable
2. Include key details (location, timeline, scope)
3. Be measurable
4. Guide the planning process"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department goal formulation AI. Create clear, actionable goals from requests. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startswith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        result = json.loads(llm_output.strip())
        return result.get("goal", None)
        
    except Exception as e:
        logger.warning(f"LLM goal formulation failed: {e}")
        return None
