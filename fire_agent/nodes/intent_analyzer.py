"""
Intent Analyzer Node for Fire Department Agent.
Determines the type and priority of fire/emergency service request.
"""

from typing import Dict, Any
from fire_agent.state import DepartmentState
from fire_agent.nodes.llm_helper import call_llm_with_fallback
import logging

logger = logging.getLogger(__name__)

# Fire department intent mapping
INTENT_MAPPING = {
    "station_deployment": "deploy_station_resources",
    "emergency_response": "respond_to_emergency",
    "equipment_maintenance": "coordinate_maintenance",
    "training_request": "schedule_training",
    "readiness_assessment": "assess_readiness",
    "hazmat_incident": "respond_to_hazmat",
    "inspection_request": "coordinate_maintenance"
}

# Risk factors for fire/emergency operations
RISK_FACTORS = {
    "response_time_critical": ["emergency", "fire", "rescue", "hazmat", "critical"],
    "personnel_intensive": ["structure_fire", "wildfire", "hazmat", "rescue", "multiple_alarm"],
    "equipment_intensive": ["ladder_needed", "hazmat", "water_supply", "ventilation"],
    "high_casualty_risk": ["casualties_reported", "trapped_persons", "explosion", "collapse"],
    "environmental_hazard": ["hazmat", "chemical", "gas_leak", "environmental"]
}


def analyze_intent(state: DepartmentState) -> Dict[str, Any]:
    """
    Analyze the intent and risk level of a fire department request.
    
    Determines:
    - Request type (emergency, deployment, maintenance, training, etc.)
    - Priority level (critical, high, medium, low)
    - Risk assessment
    - Resource urgency
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with intent and risk analysis
    """
    logger.info("Analyzing intent for fire department request")
    
    request = state.get("request", {})
    context = state.get("context", {})
    
    # Extract key fields
    request_type = request.get("type", "").lower()
    priority = request.get("priority", "medium").lower()
    incident_type = request.get("incident_type", "").lower()
    casualties_reported = request.get("casualties_reported", 0)
    reason = request.get("reason", "").lower()
    location = request.get("location", "")
    
    # Determine intent using LLM with deterministic fallback
    llm_prompt = f"""
    Analyze this fire department request and classify the intent:
    
    Request Type: {request_type}
    Incident Type: {incident_type}
    Priority: {priority}
    Reason: {reason}
    Casualties: {casualties_reported}
    Location: {location}
    
    Available intents:
    - deploy_station_resources: Deploy personnel/equipment to a location
    - respond_to_emergency: Respond to fire, rescue, or other emergency
    - coordinate_maintenance: Schedule equipment or station maintenance
    - schedule_training: Arrange training for firefighters
    - assess_readiness: Check operational readiness
    - respond_to_hazmat: Handle hazardous materials incident
    
    Return only the intent name.
    """
    
    def fallback_intent():
        """Deterministic fallback for intent classification"""
        # Check for emergency keywords
        if any(kw in reason or kw in request_type or kw in incident_type 
               for kw in ["emergency", "fire", "rescue", "alarm", "911"]):
            return "respond_to_emergency"
        
        # Check for hazmat
        if any(kw in reason or kw in incident_type 
               for kw in ["hazmat", "chemical", "gas", "spill", "leak"]):
            return "respond_to_hazmat"
        
        # Check for maintenance
        if any(kw in reason or kw in request_type 
               for kw in ["maintenance", "repair", "inspection", "service"]):
            return "coordinate_maintenance"
        
        # Check for training
        if any(kw in reason or kw in request_type 
               for kw in ["training", "drill", "exercise", "certification"]):
            return "schedule_training"
        
        # Check for readiness
        if any(kw in reason or kw in request_type 
               for kw in ["readiness", "assessment", "status", "check"]):
            return "assess_readiness"
        
        # Default to deployment
        return "deploy_station_resources"
    
    intent = call_llm_with_fallback(llm_prompt, fallback_intent)
    
    # Assess risk level
    risk_score = 0
    risk_factors_found = []
    
    # Response time criticality
    if priority == "critical" or casualties_reported > 0:
        risk_score += 3
        risk_factors_found.append("critical_priority")
    
    if any(kw in incident_type or kw in reason for kw in RISK_FACTORS["response_time_critical"]):
        risk_score += 2
        risk_factors_found.append("time_critical")
    
    # Personnel intensity
    if any(kw in incident_type for kw in RISK_FACTORS["personnel_intensive"]):
        risk_score += 2
        risk_factors_found.append("personnel_intensive")
    
    # Equipment intensity
    if any(kw in incident_type or kw in reason for kw in RISK_FACTORS["equipment_intensive"]):
        risk_score += 1
        risk_factors_found.append("equipment_intensive")
    
    # Casualty risk
    if casualties_reported > 0 or any(kw in reason for kw in RISK_FACTORS["high_casualty_risk"]):
        risk_score += 3
        risk_factors_found.append("high_casualty_risk")
    
    # Environmental hazard
    if any(kw in incident_type or kw in reason for kw in RISK_FACTORS["environmental_hazard"]):
        risk_score += 2
        risk_factors_found.append("environmental_hazard")
    
    # Determine risk level
    if risk_score >= 7:
        risk_level = "critical"
    elif risk_score >= 4:
        risk_level = "high"
    elif risk_score >= 2:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    analysis = {
        "intent": intent,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "risk_factors": risk_factors_found,
        "requires_immediate_response": risk_level in ["critical", "high"],
        "estimated_response_time_minutes": 10 if risk_level == "critical" else 15 if risk_level == "high" else 30
    }
    
    logger.info(f"Intent analysis: {analysis}")
    
    return {
        **state,
        "analysis": analysis,
        "phase": "intent_analyzed"
    }
