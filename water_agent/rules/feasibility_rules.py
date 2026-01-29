"""
Feasibility Rules - Pure Python, deterministic validation.

PHASE 9: This is where rules, NOT LLM, decide if a plan is feasible.
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class FeasibilityRules:
    """Pure Python feasibility evaluation - deterministic and explainable"""
    
    @staticmethod
    def evaluate_schedule_shift(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """
        Evaluate if schedule shift is feasible.
        
        Returns: (feasible, reason, details)
        """
        
        details = {}
        violations = []
        
        # Constraint 1: Minimum manpower
        manpower_sufficient = observations.get("extracted_facts", {}).get("manpower_sufficient", False)
        available = observations.get("extracted_facts", {}).get("available_workers", 0)
        required = observations.get("extracted_facts", {}).get("required_workers", 0)
        
        details["manpower"] = {
            "available": available,
            "required": required,
            "sufficient": manpower_sufficient
        }
        
        if not manpower_sufficient:
            violations.append(f"Insufficient manpower: {available} available, {required} required")
        
        # Constraint 2: No schedule conflicts
        schedule_conflict = observations.get("extracted_facts", {}).get("schedule_conflict", False)
        details["schedule"] = {"conflict": schedule_conflict}
        
        if schedule_conflict:
            violations.append("Schedule conflict detected")
        
        # Constraint 3: Pipeline health
        pipeline_condition = observations.get("extracted_facts", {}).get("pipeline_condition", "unknown")
        critical_issues = observations.get("extracted_facts", {}).get("critical_pipeline_issues", 0)
        
        details["pipeline"] = {
            "condition": pipeline_condition,
            "critical_issues": critical_issues
        }
        
        if pipeline_condition in ["poor", "critical"] or critical_issues > 0:
            violations.append(f"Pipeline condition: {pipeline_condition}, Critical issues: {critical_issues}")
        
        # Constraint 4: Budget available
        budget_available = observations.get("extracted_facts", {}).get("budget_available", False)
        details["budget"] = {"available": budget_available}
        
        if not budget_available:
            violations.append("Insufficient budget")
        
        # Constraint 5: Zone risk
        zone_risk = observations.get("extracted_facts", {}).get("zone_risk_level", "low")
        details["zone_risk"] = {"level": zone_risk}
        
        if zone_risk in ["high", "critical"]:
            violations.append(f"Zone risk too high: {zone_risk}")
        
        # Constraint 6: No conflicting projects
        active_projects = observations.get("extracted_facts", {}).get("active_projects_count", 0)
        if active_projects > 3:
            violations.append(f"Too many active projects ({active_projects})")
        
        # ========== FINAL DECISION ==========
        feasible = len(violations) == 0
        
        if feasible:
            reason = "All constraints satisfied"
        else:
            reason = "; ".join(violations)
        
        details["violations"] = violations
        details["constraint_count"] = 6
        details["violations_count"] = len(violations)
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_emergency_response(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate emergency response feasibility"""
        
        details = {
            "emergency": True,
            "automatic_approval": True
        }
        
        # Emergency requests are always approved
        # But we check if response is possible
        
        manpower_some = observations.get("extracted_facts", {}).get("available_workers", 0) > 0
        
        if not manpower_some:
            return False, "No workers available for emergency response", details
        
        return True, "Emergency response approved - immediate action authorized", details
    
    @staticmethod
    def evaluate_maintenance(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate maintenance feasibility"""
        
        details = {}
        violations = []
        
        # Check manpower
        if not observations.get("extracted_facts", {}).get("manpower_sufficient", False):
            violations.append("Insufficient maintenance crew")
        
        # Check schedule
        if observations.get("extracted_facts", {}).get("schedule_conflict", False):
            violations.append("Conflicts with existing schedule")
        
        # Check pipeline condition
        if observations.get("extracted_facts", {}).get("critical_pipeline_issues", 0) > 0:
            # Critical issues actually mean maintenance is NEEDED
            details["critical_need"] = True
        
        feasible = len(violations) == 0
        reason = "Maintenance approved" if feasible else "; ".join(violations)
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_capacity_assessment(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate capacity assessment - always feasible"""
        
        details = {
            "assessment_type": "capacity",
            "always_feasible": True
        }
        
        return True, "Capacity assessment can proceed", details


class FeasibilityEvaluator:
    """Main feasibility evaluator - dispatches to specific rules"""
    
    def __init__(self):
        self.rules = FeasibilityRules()
    
    def evaluate(self, intent: str, observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """
        Evaluate feasibility based on intent.
        
        Returns: (feasible, reason, details)
        """
        
        if intent == "negotiate_schedule":
            return self.rules.evaluate_schedule_shift(observations, input_event)
        
        elif intent == "emergency_response":
            return self.rules.evaluate_emergency_response(observations, input_event)
        
        elif intent == "coordinate_maintenance":
            return self.rules.evaluate_maintenance(observations, input_event)
        
        elif intent == "assess_capacity":
            return self.rules.evaluate_capacity_assessment(observations, input_event)
        
        else:
            # Default: require all major constraints
            return self.rules.evaluate_schedule_shift(observations, input_event)
