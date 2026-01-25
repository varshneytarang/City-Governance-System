"""
Water Agent Decision Policies
Rule-based policies for deterministic decisions
"""
from typing import Dict, Any, List


def apply_safety_policy(pipeline_condition: str, risk_level: str) -> Dict[str, Any]:
    """
    Apply safety policy rules for excavation/digging requests
    
    Returns:
        Policy decision with conditions
    """
    # Critical condition pipelines - automatic deny
    if pipeline_condition == "critical":
        return {
            "allowed": False,
            "reason": "Pipeline in critical condition - excavation prohibited",
            "required_action": "Pipeline replacement required before any excavation"
        }
    
    # High risk - requires special precautions
    if risk_level in ["high", "critical"]:
        return {
            "allowed": True,
            "conditions": [
                "24-hour advance notice required",
                "Water department supervisor must be on-site",
                "Emergency repair crew on standby",
                "Temporary water supply arrangements if needed",
                "Daily progress reports mandatory"
            ],
            "reason": "High-risk operation - special precautions required"
        }
    
    # Poor condition - needs coordination
    if pipeline_condition == "poor":
        return {
            "allowed": True,
            "conditions": [
                "Joint inspection with Roads department required",
                "Excavation to be done manually near pipeline",
                "Water pressure monitoring during work",
                "Repair materials on standby"
            ],
            "reason": "Pipeline in poor condition - careful excavation required"
        }
    
    # Normal conditions
    return {
        "allowed": True,
        "conditions": [
            "Standard excavation protocols",
            "Mark pipeline locations clearly",
            "Notify residents 48 hours in advance"
        ],
        "reason": "Standard safety protocols apply"
    }


def apply_resource_policy(reservoir_level: float, demand_increase: float) -> Dict[str, Any]:
    """
    Apply resource management policy for new projects
    
    Args:
        reservoir_level: Current reservoir level percentage
        demand_increase: Projected demand increase percentage
    
    Returns:
        Resource policy decision
    """
    # Critical reservoir level
    if reservoir_level < 30:
        return {
            "allowed": False,
            "reason": "Critical water shortage - no new connections approved",
            "required_action": "Improve water conservation and storage before new projects"
        }
    
    # Low reservoir with high demand increase
    if reservoir_level < 50 and demand_increase > 20:
        return {
            "allowed": False,
            "reason": "Insufficient water resources for projected demand increase",
            "required_action": "Enhance water infrastructure capacity first",
            "recommendations": [
                "Increase reservoir capacity",
                "Install additional pumping stations",
                "Implement water conservation measures"
            ]
        }
    
    # Low reservoir but manageable demand
    if reservoir_level < 50:
        return {
            "allowed": True,
            "conditions": [
                "Rainwater harvesting mandatory for new buildings",
                "Water meters mandatory",
                "Usage restrictions during peak hours",
                "Quarterly water audit required"
            ],
            "reason": "Conditional approval with conservation measures"
        }
    
    # Sufficient resources
    return {
        "allowed": True,
        "conditions": ["Standard water connection protocols"],
        "reason": "Adequate water resources available"
    }


def apply_coordination_policy(
    conflicts: List[Dict[str, Any]],
    risk_level: str,
    request_type: str
) -> Dict[str, List[str]]:
    """
    Determine which departments need to be coordinated with
    
    Returns:
        Dictionary of departments and reasons
    """
    coordination = {}
    
    # Roads department coordination
    if request_type == "road_digging" or any("road" in str(c).lower() for c in conflicts):
        coordination["roads"] = [
            "Joint excavation planning required",
            "Traffic management coordination",
            "Utility marking and safety protocols"
        ]
    
    # Fire department coordination
    if risk_level in ["high", "critical"]:
        coordination["fire"] = [
            "Emergency response preparedness",
            "Hydrant access planning",
            "Water pressure management during operations"
        ]
    
    # Finance department coordination
    if request_type == "new_project":
        coordination["finance"] = [
            "Budget approval required",
            "Cost estimation review",
            "Payment milestone planning"
        ]
    
    # Health department coordination
    if request_type == "leakage" and risk_level in ["high", "critical"]:
        coordination["health"] = [
            "Water quality testing",
            "Contamination risk assessment",
            "Public health advisory if needed"
        ]
    
    return coordination


def calculate_priority_score(
    request_type: str,
    severity: str,
    conflicts_count: int,
    population_affected: int = 0
) -> int:
    """
    Calculate priority score for request processing
    
    Returns:
        Priority score (0-100, higher = more urgent)
    """
    score = 0
    
    # Base score by request type
    type_scores = {
        "leakage": 70,
        "contamination": 90,
        "road_digging": 40,
        "new_project": 30,
        "maintenance": 50,
        "inspection": 20
    }
    score += type_scores.get(request_type, 30)
    
    # Severity modifier
    severity_multipliers = {
        "critical": 1.5,
        "high": 1.3,
        "medium": 1.1,
        "low": 1.0
    }
    score *= severity_multipliers.get(severity, 1.0)
    
    # Conflicts penalty
    score += conflicts_count * 5
    
    # Population impact
    if population_affected > 1000:
        score += 20
    elif population_affected > 500:
        score += 10
    elif population_affected > 100:
        score += 5
    
    return min(int(score), 100)


def estimate_project_cost(
    request_type: str,
    pipeline_length_m: float = 0,
    pipeline_diameter_mm: int = 100,
    repairs_needed: bool = False,
    excavation_depth_m: float = 0
) -> Dict[str, float]:
    """
    Estimate cost for water-related work
    
    Returns:
        Cost breakdown dictionary
    """
    costs = {
        "materials": 0.0,
        "labor": 0.0,
        "equipment": 0.0,
        "contingency": 0.0,
        "total": 0.0
    }
    
    if request_type == "new_project":
        # New pipeline installation
        cost_per_meter = {
            50: 1200,
            100: 2500,
            150: 4000,
            200: 6000,
            300: 10000,
            400: 15000
        }.get(pipeline_diameter_mm, 2500)
        
        costs["materials"] = pipeline_length_m * cost_per_meter * 0.6
        costs["labor"] = pipeline_length_m * cost_per_meter * 0.3
        costs["equipment"] = pipeline_length_m * cost_per_meter * 0.1
    
    elif request_type == "leakage" or repairs_needed:
        # Repair costs
        costs["materials"] = 15000
        costs["labor"] = 8000
        costs["equipment"] = 5000
    
    elif request_type == "road_digging":
        # Excavation supervision and safety
        costs["labor"] = excavation_depth_m * 5000
        costs["equipment"] = excavation_depth_m * 3000
    
    # Contingency (20%)
    subtotal = sum(costs.values())
    costs["contingency"] = subtotal * 0.2
    costs["total"] = subtotal + costs["contingency"]
    
    return costs


def determine_response_timeline(
    request_type: str,
    severity: str,
    priority_score: int
) -> Dict[str, Any]:
    """
    Determine response and completion timelines
    
    Returns:
        Timeline dictionary with response and completion estimates
    """
    timelines = {
        "leakage": {
            "critical": {"response_hours": 0.5, "completion_days": 1},
            "high": {"response_hours": 2, "completion_days": 2},
            "medium": {"response_hours": 6, "completion_days": 3},
            "low": {"response_hours": 24, "completion_days": 5}
        },
        "road_digging": {
            "critical": {"response_hours": 4, "completion_days": 7},
            "high": {"response_hours": 12, "completion_days": 10},
            "medium": {"response_hours": 48, "completion_days": 14},
            "low": {"response_hours": 72, "completion_days": 21}
        },
        "new_project": {
            "critical": {"response_hours": 24, "completion_days": 90},
            "high": {"response_hours": 48, "completion_days": 120},
            "medium": {"response_hours": 72, "completion_days": 150},
            "low": {"response_hours": 120, "completion_days": 180}
        }
    }
    
    default_timeline = {"response_hours": 48, "completion_days": 30}
    timeline = timelines.get(request_type, {}).get(severity, default_timeline)
    
    # Adjust for priority score
    if priority_score > 80:
        timeline["response_hours"] *= 0.5
        timeline["completion_days"] *= 0.8
    
    return {
        "response_time_hours": timeline["response_hours"],
        "estimated_completion_days": timeline["completion_days"],
        "milestone_schedule": _generate_milestones(timeline["completion_days"])
    }


def _generate_milestones(total_days: int) -> List[Dict[str, Any]]:
    """Generate project milestones"""
    milestones = [
        {"day": 0, "milestone": "Project initiation and planning"},
        {"day": int(total_days * 0.25), "milestone": "Site preparation and marking"},
        {"day": int(total_days * 0.50), "milestone": "50% completion checkpoint"},
        {"day": int(total_days * 0.75), "milestone": "Testing and quality check"},
        {"day": total_days, "milestone": "Project completion and handover"}
    ]
    return milestones
