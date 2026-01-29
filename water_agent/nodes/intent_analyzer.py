"""
PHASE 4: Intent + Risk Analyzer Node

Classify the request and assess immediate risk.

Rule: If risk == high → escalate immediately.
"""

from typing import Dict, List
import logging

from ..state import DepartmentState
from ..database import WaterDepartmentQueries
from ..tools import WaterDepartmentTools

logger = logging.getLogger(__name__)


# Intent classification mapping
INTENT_MAPPING = {
    "schedule_shift_request": "negotiate_schedule",
    "emergency_response": "emergency_response",
    "maintenance_request": "coordinate_maintenance",
    "capacity_query": "assess_capacity",
    "incident_report": "respond_to_incident",
    "project_planning": "plan_project"
}


def intent_analyzer_node(state: DepartmentState, 
                        tools: WaterDepartmentTools) -> DepartmentState:
    """
    PHASE 4: Intent + Risk Analysis Node
    
    Purpose: Decide if this can be handled autonomously.
    
    Logic:
    - Classify request type
    - Assess safety implications
    - Check for legal/policy exposure
    
    Output:
    - intent: what is the request trying to accomplish?
    - risk_level: low, medium, high, critical
    - safety_concerns: list of issues
    
    Rule: If risk == critical → escalate immediately.
    """
    
    logger.info("🔍 [NODE: Intent + Risk Analysis]")
    
    try:
        input_event = state.get("input_event", {})
        request_type = input_event.get("type", "unknown")
        location = input_event.get("location")
        context = state.get("context", {})
        
        # ========== INTENT CLASSIFICATION ==========
        intent = INTENT_MAPPING.get(request_type, "unknown_request")
        logger.info(f"  → Request: {request_type} → Intent: {intent}")
        
        # ========== RISK ASSESSMENT ==========
        risk_level = "low"
        safety_concerns = []
        
        # Check 1: Location-based risk
        if context.get("is_high_risk_zone"):
            safety_concerns.append("Location is a known high-risk zone")
            risk_level = "high"
        
        # Check 2: Critical incidents
        critical_incidents = context.get("incident_severity", {}).get("critical", 0)
        if critical_incidents > 0:
            safety_concerns.append(f"Critical incidents in area: {critical_incidents}")
            risk_level = "critical"
        
        # Check 3: Pipeline status
        pipeline_status = context.get("pipelines_status", {})
        poor_pipelines = pipeline_status.get("poor", 0) + pipeline_status.get("critical", 0)
        if poor_pipelines > 0:
            safety_concerns.append(f"Infrastructure issues: {poor_pipelines} pipelines")
            if risk_level != "critical":
                risk_level = "high"
        
        # Check 4: Reservoir levels (drought conditions)
        avg_reservoir = context.get("avg_reservoir_level", 100)
        if avg_reservoir < 20:
            safety_concerns.append(f"Critical water shortage: {avg_reservoir:.1f}%")
            risk_level = "critical"
        elif avg_reservoir < 40:
            safety_concerns.append(f"Low water levels: {avg_reservoir:.1f}%")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 5: Emergency request type
        if request_type == "emergency_response":
            safety_concerns.append("Emergency request detected")
            if risk_level != "critical":
                risk_level = "high"
        
        # Check 6: Recent incidents in location
        recent_incidents = context.get("recent_incidents", 0)
        if recent_incidents > 5:
            safety_concerns.append(f"Multiple recent incidents: {recent_incidents}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 7: Budget constraints
        budget = context.get("budget", {})
        utilization = budget.get("utilization_percent", 0)
        if utilization > 90:
            safety_concerns.append(f"Budget nearly exhausted: {utilization:.1f}%")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 8: Assess zone risk using tools
        logger.info(f"  → Assessing zone risk for {location}")
        zone_risk_result = tools.assess_zone_risk(location) if location else {}
        zone_risk_level = zone_risk_result.get("risk_level", "low")
        
        # Escalate risk if tool reports high
        if zone_risk_level in ["high", "critical"]:
            for factor in zone_risk_result.get("contributing_factors", []):
                if factor not in safety_concerns:
                    safety_concerns.append(factor)
            if zone_risk_level == "critical":
                risk_level = "critical"
            elif zone_risk_level == "high" and risk_level != "critical":
                risk_level = "high"
        
        logger.info(f"  → Risk Level: {risk_level}")
        logger.info(f"  → Safety Concerns: {len(safety_concerns)}")
        
        # Update state
        state["intent"] = intent
        state["risk_level"] = risk_level
        state["safety_concerns"] = safety_concerns
        
        # ========== IMMEDIATE ESCALATION RULE ==========
        if risk_level == "critical":
            logger.warning(f"⚠️  CRITICAL RISK DETECTED - Automatic escalation")
            state["escalate"] = True
            state["escalation_reason"] = f"Critical risk level: {'; '.join(safety_concerns)}"
        
    except Exception as e:
        logger.error(f"✗ Intent analysis error: {e}")
        state["intent"] = "unknown"
        state["risk_level"] = "unknown"
        state["safety_concerns"] = [f"Analysis error: {str(e)}"]
    
    return state
