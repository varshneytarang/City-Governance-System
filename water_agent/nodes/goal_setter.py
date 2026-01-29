"""
PHASE 5: Goal Setter Node

Give the agent a specific purpose.

Simple mapping from intent to concrete goals.
"""

import logging

from ..state import DepartmentState

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
    PHASE 5: Goal Setter Node
    
    Purpose: Give the agent a specific purpose.
    
    Takes the intent and derives a concrete goal.
    This goal guides the planning process.
    
    Example outputs:
    - "Evaluate feasibility of delay"
    - "Check participation in joint work"
    - "Assess safety of maintenance window"
    """
    
    logger.info("🎯 [NODE: Goal Setter]")
    
    try:
        intent = state.get("intent", "unknown_request")
        input_event = state.get("input_event", {})
        
        # Get base goal from intent
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
