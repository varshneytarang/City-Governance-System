"""
Planner Node for Fire Department Agent.
Generates executable action plans based on goals and context.
"""

from typing import Dict, Any, List
from fire_agent.state import DepartmentState
from fire_agent.nodes.llm_helper import call_llm_with_fallback
import logging

logger = logging.getLogger(__name__)


def plan_actions(state: DepartmentState) -> Dict[str, Any]:
    """
    Generate a concrete action plan for the fire department request.
    
    Plans include:
    - Sequence of tool calls
    - Resource allocation
    - Timeline/schedule
    - Contingencies
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with action plan
    """
    logger.info("Planning actions for fire department request")
    
    request = state.get("request", {})
    analysis = state.get("analysis", {})
    goals = state.get("goals", {})
    context = state.get("context", {})
    
    intent = analysis.get("intent", "")
    risk_level = analysis.get("risk_level", "medium")
    
    # Use LLM to generate plan with deterministic fallback
    llm_prompt = f"""
    Create an action plan for this fire department request:
    
    Intent: {intent}
    Risk Level: {risk_level}
    Goals: {goals.get('goals', [])}
    Available Resources: {context.get('summary', {})}
    
    Available tools:
    - check_truck_availability
    - check_firefighter_availability
    - check_equipment_status
    - assess_response_time
    - check_hydrant_status
    - get_incident_history
    - estimate_resource_needs
    - check_station_capacity
    - check_budget_availability
    
    Provide a step-by-step plan with tool names.
    """
    
    def fallback_plan():
        """Deterministic fallback for planning"""
        plan = {
            "name": "",
            "steps": [],
            "estimated_duration_minutes": 0,
            "resource_requirements": {}
        }
        
        if intent == "respond_to_emergency":
            plan["name"] = "Emergency Response Plan"
            plan["steps"] = [
                "check_truck_availability",
                "check_firefighter_availability",
                "check_equipment_status",
                "assess_response_time",
                "check_hydrant_status",
                "estimate_resource_needs"
            ]
            plan["estimated_duration_minutes"] = 10 if risk_level == "critical" else 15
            plan["resource_requirements"] = {
                "trucks": 2 if risk_level == "critical" else 1,
                "firefighters": 8 if risk_level == "critical" else 4,
                "equipment": ["hoses", "breathing_apparatus", "ladders"]
            }
        
        elif intent == "respond_to_hazmat":
            plan["name"] = "Hazmat Response Plan"
            plan["steps"] = [
                "check_firefighter_availability",  # Need certified hazmat personnel
                "check_equipment_status",  # Need hazmat gear
                "check_truck_availability",  # Need hazmat truck
                "assess_response_time",
                "estimate_resource_needs"
            ]
            plan["estimated_duration_minutes"] = 15
            plan["resource_requirements"] = {
                "trucks": 1,  # Hazmat truck
                "firefighters": 6,  # Certified hazmat team
                "equipment": ["hazmat_suits", "containment_equipment", "detection_devices"]
            }
        
        elif intent == "deploy_station_resources":
            plan["name"] = "Station Resource Deployment"
            plan["steps"] = [
                "check_truck_availability",
                "check_firefighter_availability",
                "check_station_capacity",
                "check_equipment_status",
                "check_budget_availability"
            ]
            plan["estimated_duration_minutes"] = 20
            plan["resource_requirements"] = {
                "trucks": 1,
                "firefighters": 3,
                "equipment": ["standard_gear"]
            }
        
        elif intent == "coordinate_maintenance":
            plan["name"] = "Maintenance Coordination Plan"
            plan["steps"] = [
                "check_equipment_status",
                "check_station_capacity",
                "check_budget_availability",
                "check_truck_availability"  # Ensure backup coverage
            ]
            plan["estimated_duration_minutes"] = 60
            plan["resource_requirements"] = {
                "budget": 5000,
                "downtime_hours": 4
            }
        
        elif intent == "schedule_training":
            plan["name"] = "Training Schedule Plan"
            plan["steps"] = [
                "check_firefighter_availability",
                "check_station_capacity",
                "check_budget_availability",
                "check_truck_availability"  # Ensure coverage during training
            ]
            plan["estimated_duration_minutes"] = 240  # 4 hours
            plan["resource_requirements"] = {
                "firefighters": 5,
                "budget": 2000,
                "training_hours": 8
            }
        
        elif intent == "assess_readiness":
            plan["name"] = "Readiness Assessment Plan"
            plan["steps"] = [
                "check_truck_availability",
                "check_firefighter_availability",
                "check_equipment_status",
                "check_station_capacity",
                "check_hydrant_status",
                "get_incident_history"
            ]
            plan["estimated_duration_minutes"] = 45
            plan["resource_requirements"] = {}
        
        else:
            plan["name"] = "General Fire Department Operation"
            plan["steps"] = [
                "check_truck_availability",
                "check_firefighter_availability",
                "check_budget_availability"
            ]
            plan["estimated_duration_minutes"] = 30
            plan["resource_requirements"] = {}
        
        return plan
    
    plan = call_llm_with_fallback(llm_prompt, fallback_plan)
    
    # Ensure plan is a dictionary with required fields
    if not isinstance(plan, dict):
        plan = fallback_plan()
    
    # Validate required fields
    if "name" not in plan:
        plan["name"] = f"Plan for {intent}"
    if "steps" not in plan:
        plan["steps"] = []
    if "estimated_duration_minutes" not in plan:
        plan["estimated_duration_minutes"] = 30
    
    logger.info(f"Plan created: {plan['name']} with {len(plan.get('steps', []))} steps")
    
    return {
        **state,
        "plan": plan,
        "phase": "plan_created"
    }
