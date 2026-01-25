"""
Fire Agent Policies

Rule-based decision policies for the Fire Agent.
These policies provide deterministic logic for safety, resources, and coordination.
"""

from typing import Dict, Any, List
from app.agents.fire.state import FireState


def apply_safety_policy(state: FireState) -> Dict[str, Any]:
    """
    Apply safety-first policy checks for emergency response
    
    Returns:
        {
            "passed": bool,
            "issues": List[str],
            "actions": List[str]
        }
    """
    issues = []
    actions = []
    
    # Check for critical severity
    severity_assessment = state.get("severity_assessment", {})
    if severity_assessment.get("level") == "Critical":
        actions.append("Dispatch maximum resources immediately")
        actions.append("Notify mutual aid agreements")
        actions.append("Alert hospital emergency departments")
    
    # Check casualties
    casualties = state.get("casualties", 0)
    if casualties > 0:
        issues.append(f"Casualties reported: {casualties}")
        actions.append("Coordinate with ambulance services")
        actions.append("Establish triage area")
    
    # Check fire intensity for fires
    fire_intensity = state.get("fire_intensity")
    if fire_intensity in ["major", "conflagration"]:
        issues.append(f"High fire intensity: {fire_intensity}")
        actions.append("Request additional water supply coordination")
        actions.append("Establish safety perimeter")
        actions.append("Coordinate with Water Department for hydrant access")
    
    # Check building type risks
    building_type = state.get("building_type")
    if building_type == "high-rise":
        issues.append("High-rise building requires specialized response")
        actions.append("Deploy aerial ladder equipment")
        actions.append("Establish command post")
        actions.append("Coordinate evacuation with police")
    elif building_type == "industrial":
        issues.append("Industrial facility may have hazardous materials")
        actions.append("Request hazmat assessment")
        actions.append("Review facility emergency plans")
    
    # Check active incidents (resource strain)
    active_incidents = state.get("active_incidents", [])
    if len(active_incidents) >= 2:
        issues.append(f"Multiple active incidents in area: {len(active_incidents)}")
        actions.append("Consider mutual aid request")
    
    passed = len(issues) == 0 or casualties == 0  # Pass if no casualties, even with issues
    
    return {
        "passed": passed,
        "issues": issues,
        "actions": actions
    }


def apply_resource_policy(state: FireState) -> Dict[str, Any]:
    """
    Apply resource availability policy checks
    
    Returns:
        {
            "passed": bool,
            "issues": List[str],
            "recommendations": List[str]
        }
    """
    issues = []
    recommendations = []
    
    # Check dispatch plan
    dispatch_plan = state.get("dispatch_plan", {})
    response_requirements = state.get("response_requirements", {})
    
    required_personnel = response_requirements.get("personnel", 4)
    available_personnel = dispatch_plan.get("total_personnel", 0)
    
    required_vehicles = response_requirements.get("vehicles", 1)
    available_vehicles = dispatch_plan.get("total_vehicles", 0)
    
    # Check personnel adequacy
    if available_personnel < required_personnel:
        deficit = required_personnel - available_personnel
        issues.append(f"Personnel shortage: {deficit} personnel short")
        recommendations.append("Request mutual aid from neighboring jurisdictions")
    elif available_personnel >= required_personnel * 1.5:
        recommendations.append("Sufficient resources available, consider backup unit")
    
    # Check vehicle adequacy
    if available_vehicles < required_vehicles:
        deficit = required_vehicles - available_vehicles
        issues.append(f"Vehicle shortage: {deficit} vehicles short")
        recommendations.append("Check neighboring station availability")
    
    # Check mutual aid flag
    if dispatch_plan.get("mutual_aid_needed", False):
        issues.append("Mutual aid required for adequate response")
        recommendations.append("Activate mutual aid agreement immediately")
    
    # Check backup availability
    backup_stations = dispatch_plan.get("backup_stations", [])
    if len(backup_stations) == 0:
        issues.append("No backup stations available")
        recommendations.append("Monitor situation closely for additional resource needs")
    
    # Check response time
    estimated_eta = dispatch_plan.get("estimated_eta", 999)
    if estimated_eta > 10:
        issues.append(f"Response time exceeds 10 minutes: {estimated_eta} min")
        recommendations.append("Dispatch closest available unit immediately")
    
    passed = len([i for i in issues if "shortage" in i.lower()]) == 0
    
    return {
        "passed": passed,
        "issues": issues,
        "recommendations": recommendations
    }


def apply_coordination_policy(state: FireState) -> Dict[str, Any]:
    """
    Determine which departments need coordination
    
    Returns:
        {
            "required": bool,
            "departments": List[str],
            "reasons": Dict[str, str]
        }
    """
    departments = []
    reasons = {}
    
    incident_type = state.get("emergency_type", state.get("request_type", ""))
    fire_intensity = state.get("fire_intensity")
    casualties = state.get("casualties", 0)
    building_type = state.get("building_type")
    
    # Water Department coordination
    if incident_type == "fire" and fire_intensity in ["moderate", "major", "conflagration"]:
        departments.append("Water Department")
        reasons["Water Department"] = f"Large fire ({fire_intensity}) requires water supply coordination"
    
    # Health Department coordination
    if casualties > 0:
        departments.append("Health Department")
        reasons["Health Department"] = f"Medical response needed for {casualties} casualties"
    
    # Police Department coordination
    if building_type == "high-rise" or casualties > 5:
        departments.append("Police Department")
        reasons["Police Department"] = "Crowd control and evacuation assistance needed"
    
    # Public Works coordination
    if building_type == "industrial" or incident_type == "hazmat":
        departments.append("Public Works")
        reasons["Public Works"] = "Infrastructure protection and hazmat containment support"
    
    # Environmental Department coordination
    if incident_type == "hazmat":
        departments.append("Environmental Department")
        reasons["Environmental Department"] = "Hazmat incident requires environmental monitoring"
    
    return {
        "required": len(departments) > 0,
        "departments": departments,
        "reasons": reasons
    }


def apply_escalation_policy(state: FireState) -> Dict[str, Any]:
    """
    Determine if request requires escalation to higher authority
    
    Returns:
        {
            "required": bool,
            "reason": str,
            "escalation_level": str
        }
    """
    severity_score = state.get("severity_assessment", {}).get("score", 0)
    casualties = state.get("casualties", 0)
    mutual_aid = state.get("dispatch_plan", {}).get("mutual_aid_needed", False)
    estimated_cost = state.get("estimated_cost", 0)
    
    # Critical severity requires city-level coordination
    if severity_score >= 80:
        return {
            "required": True,
            "reason": f"Critical severity (score: {severity_score}) requires city emergency management",
            "escalation_level": "City Emergency Manager"
        }
    
    # Mass casualty incident
    if casualties >= 10:
        return {
            "required": True,
            "reason": f"Mass casualty incident ({casualties} casualties) requires city coordination",
            "escalation_level": "City Emergency Manager"
        }
    
    # Large-scale mutual aid
    if mutual_aid and severity_score >= 60:
        return {
            "required": True,
            "reason": "Large-scale incident requiring mutual aid coordination",
            "escalation_level": "Fire Chief"
        }
    
    # High cost operations
    if estimated_cost > 500000:  # ₹5 lakh
        return {
            "required": True,
            "reason": f"High cost operation (₹{estimated_cost:,.0f}) requires approval",
            "escalation_level": "Fire Chief"
        }
    
    return {
        "required": False,
        "reason": "No escalation required",
        "escalation_level": "Station Commander"
    }


def apply_dispatch_policy(state: FireState) -> Dict[str, Any]:
    """
    Apply dispatch decision policy
    
    Returns decision with reasoning
    """
    request_type = state.get("request_type", "")
    
    # For emergency responses, always approve dispatch
    if request_type == "emergency_response":
        safety_check = state.get("safety_check_passed", True)
        resource_check = state.get("resource_check_passed", True)
        escalation = state.get("escalation_required", False)
        
        if escalation:
            return {
                "decision": "ESCALATE",
                "reasoning": "Critical incident requires higher authority coordination"
            }
        elif not resource_check:
            return {
                "decision": "APPROVE",
                "reasoning": "Emergency requires immediate response despite resource constraints. Mutual aid requested."
            }
        elif not safety_check:
            return {
                "decision": "APPROVE",
                "reasoning": "Emergency response approved with enhanced safety protocols"
            }
        else:
            return {
                "decision": "APPROVE",
                "reasoning": "All checks passed. Emergency response authorized."
            }
    
    # For inspections
    elif request_type == "fire_inspection":
        risk_level = state.get("risk_level", "medium")
        
        if risk_level in ["high", "critical"]:
            return {
                "decision": "APPROVE",
                "reasoning": f"High priority inspection required due to {risk_level} risk level"
            }
        else:
            return {
                "decision": "APPROVE",
                "reasoning": "Inspection scheduled as per routine safety protocol"
            }
    
    # For awareness programs
    elif request_type == "awareness_program":
        return {
            "decision": "APPROVE",
            "reasoning": "Community awareness program approved for fire safety education"
        }
    
    # For maintenance
    elif request_type == "equipment_maintenance":
        active_incidents = state.get("active_incidents", [])
        
        if len(active_incidents) > 0:
            return {
                "decision": "COORDINATE",
                "reasoning": "Maintenance postponed due to active incidents. Coordinate alternative timing."
            }
        else:
            return {
                "decision": "APPROVE",
                "reasoning": "Equipment maintenance approved during non-emergency period"
            }
    
    # Default
    return {
        "decision": "APPROVE",
        "reasoning": "Request approved based on standard procedures"
    }


def calculate_estimated_cost(state: FireState) -> float:
    """
    Calculate estimated cost for the operation
    """
    request_type = state.get("request_type", "")
    
    if request_type == "emergency_response":
        # Emergency response cost calculation
        dispatch_plan = state.get("dispatch_plan", {})
        personnel = dispatch_plan.get("total_personnel", 4)
        vehicles = dispatch_plan.get("total_vehicles", 1)
        duration_hours = state.get("estimated_duration", 2) / 60  # Convert minutes to hours
        
        # Base costs (example rates)
        personnel_cost = personnel * 500 * duration_hours  # ₹500/hr per person
        vehicle_cost = vehicles * 1000 * duration_hours    # ₹1000/hr per vehicle
        equipment_cost = vehicles * 5000                   # ₹5000 per vehicle equipment
        
        total = personnel_cost + vehicle_cost + equipment_cost
        
        # Add 20% for high-severity incidents
        severity_score = state.get("severity_assessment", {}).get("score", 0)
        if severity_score >= 70:
            total *= 1.2
        
        return round(total, 2)
    
    elif request_type == "fire_inspection":
        return 2000.0  # Fixed inspection cost
    
    elif request_type == "awareness_program":
        return 10000.0  # Program cost
    
    elif request_type == "equipment_maintenance":
        return 15000.0  # Maintenance cost
    
    return 0.0


def calculate_estimated_duration(state: FireState) -> int:
    """
    Calculate estimated duration (minutes for emergency, hours for others)
    """
    request_type = state.get("request_type", "")
    
    if request_type == "emergency_response":
        severity_score = state.get("severity_assessment", {}).get("score", 0)
        
        # Duration in minutes
        if severity_score >= 70:
            return 180  # 3 hours
        elif severity_score >= 50:
            return 120  # 2 hours
        else:
            return 60   # 1 hour
    
    elif request_type == "fire_inspection":
        return 2  # 2 hours
    
    elif request_type == "awareness_program":
        return 4  # 4 hours
    
    elif request_type == "equipment_maintenance":
        return 8  # 8 hours
    
    return 1
