"""
Goal Setter Node for Fire Department Agent.
Establishes clear goals and success criteria based on intent and context.
"""

from typing import Dict, Any
from fire_agent.state import DepartmentState
from fire_agent.nodes.llm_helper import call_llm_with_fallback
import logging

logger = logging.getLogger(__name__)


def set_goals(state: DepartmentState) -> Dict[str, Any]:
    """
    Set clear goals and success criteria for the fire department request.
    
    Goals are based on:
    - Request intent
    - Risk level
    - Available resources
    - Policy constraints
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with goals defined
    """
    logger.info("Setting goals for fire department request")
    
    request = state.get("request", {})
    analysis = state.get("analysis", {})
    context = state.get("context", {})
    
    intent = analysis.get("intent", "")
    risk_level = analysis.get("risk_level", "medium")
    
    # Use LLM to generate goals with deterministic fallback
    llm_prompt = f"""
    Define clear, measurable goals for this fire department request:
    
    Intent: {intent}
    Risk Level: {risk_level}
    Request: {request.get('reason', '')}
    Available Trucks: {context.get('summary', {}).get('available_trucks', 0)}
    Available Firefighters: {context.get('summary', {}).get('available_firefighters', 0)}
    
    Provide 2-4 specific, measurable goals.
    """
    
    def fallback_goals():
        """Deterministic fallback for goal setting"""
        goals = []
        
        if intent == "respond_to_emergency":
            goals = [
                f"Respond to emergency within {analysis.get('estimated_response_time_minutes', 10)} minutes",
                "Deploy sufficient resources for effective response",
                "Ensure firefighter safety and proper equipment",
                "Minimize property damage and casualties"
            ]
        
        elif intent == "respond_to_hazmat":
            goals = [
                "Deploy certified hazmat team immediately",
                "Establish containment perimeter",
                "Minimize environmental impact",
                "Ensure personnel safety with proper PPE"
            ]
        
        elif intent == "deploy_station_resources":
            goals = [
                "Deploy requested resources efficiently",
                "Maintain minimum station staffing levels",
                "Ensure equipment readiness",
                "Optimize response coverage"
            ]
        
        elif intent == "coordinate_maintenance":
            goals = [
                "Schedule maintenance with minimal operational impact",
                "Ensure equipment availability during critical periods",
                "Complete maintenance within budget",
                "Maintain safety standards"
            ]
        
        elif intent == "schedule_training":
            goals = [
                "Schedule training without compromising readiness",
                "Ensure required certifications are maintained",
                "Maximize training effectiveness",
                "Stay within training budget"
            ]
        
        elif intent == "assess_readiness":
            goals = [
                "Evaluate current operational capacity",
                "Identify resource gaps",
                "Ensure policy compliance",
                "Provide actionable recommendations"
            ]
        
        else:
            goals = [
                "Address the request effectively",
                "Maintain operational readiness",
                "Ensure safety and compliance",
                "Optimize resource utilization"
            ]
        
        return goals
    
    goals = call_llm_with_fallback(llm_prompt, fallback_goals)
    
    # Ensure goals is a list
    if isinstance(goals, str):
        goals = [g.strip() for g in goals.split('\n') if g.strip() and not g.strip().startswith('#')]
    
    # Define success criteria
    success_criteria = {
        "response_time_met": True,
        "resources_adequate": True,
        "safety_ensured": True,
        "policy_compliant": True,
        "budget_within_limits": True
    }
    
    goal_data = {
        "goals": goals,
        "success_criteria": success_criteria,
        "priority": risk_level
    }
    
    logger.info(f"Goals set: {len(goals)} goals defined")
    
    return {
        **state,
        "goals": goal_data,
        "phase": "goals_set"
    }
