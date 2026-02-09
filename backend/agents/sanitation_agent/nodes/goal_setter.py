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
    "negotiate_route_change": "Evaluate feasibility of requested route change",
    "emergency_collection": "Assess emergency and recommend immediate collection actions",
    "coordinate_maintenance": "Plan equipment maintenance without disrupting service",
    "adjust_schedule": "Determine optimal schedule adjustment",
    "optimize_landfill_routing": "Optimize waste routing to available landfills",
    "respond_to_complaint": "Analyze complaint and recommend resolution",
    "assess_capacity": "Determine current and future sanitation capacity",
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
        
        if request_type == "route_change_request":
            route_id = input_event.get("route_id", "?")
            location = input_event.get("location", "?")
            goal += f" for route {route_id} at {location}"
        
        elif request_type == "equipment_maintenance":
            equipment_type = input_event.get("equipment_type", "equipment")
            goal += f" for {equipment_type}"
        
        elif request_type == "complaint_response":
            complaint_type = input_event.get("complaint_type", "complaint")
            goal += f" ({complaint_type})"
        
        elif request_type == "emergency_collection":
            location = input_event.get("location", "?")
            goal += f" at {location}"
        
        logger.info(f"  → Goal: {goal}")
        
        state["goal"] = goal
        
    except Exception as e:
        logger.error(f"✗ Goal setter error: {e}")
        state["goal"] = "Handle sanitation department request"
    
    return state


def _formulate_goal_with_llm(client, intent: str, input_event: dict, risk_level: str, context: dict) -> str:
    """Use LLM to formulate a clear, actionable goal"""
    try:
        prompt = f"""Formulate a clear, actionable goal for this Sanitation Department request.

INTENT: {intent}
RISK LEVEL: {risk_level}

REQUEST:
{json.dumps(input_event, indent=2)}

CONTEXT:
- Active Routes: {len(context.get('routes', []))}
- Available Trucks: {sum(1 for t in context.get('trucks', []) if t.get('status') == 'available')}
- Available Workers: {context.get('worker_info', {}).get('available_count', 'unknown')}
- Budget Available: ${context.get('budget', {}).get('available', 0):,}
- Recent Complaints: {context.get('recent_complaints', 0)}

Return ONLY valid JSON:
{{
  "goal": "Specific, measurable, actionable goal statement (1-2 sentences)",
  "success_criteria": ["criterion 1", "criterion 2"],
  "constraints": ["constraint 1", "constraint 2"]
}}

The goal should:
1. Be specific and actionable
2. Include key details (location, route, timeline, scope)
3. Be measurable
4. Guide the planning process"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Sanitation Department goal formulation AI. Create clear, actionable goals from requests. Always return valid JSON."},
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
