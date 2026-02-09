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
    def evaluate_route_change(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """
        Evaluate if route change/modification is feasible.
        
        Returns: (feasible, reason, details)
        """
        
        details = {}
        violations = []
        
        # Constraint 1: Truck availability
        truck_available = observations.get("extracted_facts", {}).get("truck_available", False)
        details["truck"] = {"available": truck_available}
        
        if not truck_available:
            violations.append("No trucks available for route assignment")
        
        # Constraint 2: Route capacity
        route_overload = observations.get("extracted_facts", {}).get("route_overload", False)
        details["route_capacity"] = {"overloaded": route_overload}
        
        if route_overload:
            violations.append("Route already at/over capacity")
        
        # Constraint 3: Budget
        budget_available = observations.get("extracted_facts", {}).get("budget_available", False)
        details["budget"] = {"available": budget_available}
        
        if not budget_available:
            violations.append("Insufficient budget for route modification")
        
        # Constraint 4: Crew availability
        crew_sufficient = observations.get("extracted_facts", {}).get("crew_sufficient", True)
        details["crew"] = {"sufficient": crew_sufficient}
        
        if not crew_sufficient:
            violations.append("Insufficient crew available")
        
        feasible = len(violations) == 0
        reason = "Route change feasible" if feasible else "; ".join(violations)
        
        details["violations"] = violations
        details["constraint_count"] = 4
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_emergency_collection(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate emergency collection (overflow, hazard) feasibility"""
        
        details = {
            "emergency": True
        }
        violations = []
        
        # Emergency collections are high priority
        truck_count = observations.get("extracted_facts", {}).get("available_trucks", 0)
        
        if truck_count == 0:
            violations.append("No trucks available for emergency collection")
        
        # Check landfill capacity
        landfill_critical = observations.get("extracted_facts", {}).get("landfill_critical", False)
        if landfill_critical:
            violations.append("All landfills at critical capacity")
        
        feasible = len(violations) == 0
        reason = "Emergency collection approved" if feasible else "; ".join(violations)
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_equipment_maintenance(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate equipment maintenance request feasibility"""
        
        details = {}
        violations = []
        
        # Check if maintenance is critical
        equipment_issues = observations.get("extracted_facts", {}).get("equipment_issues", [])
        details["equipment_issues"] = equipment_issues
        
        # Check if other trucks can cover routes
        backup_trucks = observations.get("extracted_facts", {}).get("backup_trucks", 0)
        details["backup_trucks"] = backup_trucks
        
        if backup_trucks == 0 and len(equipment_issues) > 0:
            violations.append("No backup trucks to cover routes during maintenance")
        
        # Check schedule conflicts
        schedule_conflict = observations.get("extracted_facts", {}).get("schedule_conflict", False)
        if schedule_conflict:
            violations.append("Maintenance conflicts with critical collection schedule")
        
        feasible = len(violations) == 0
        reason = "Maintenance can proceed" if feasible else "; ".join(violations)
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_schedule_adjustment(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate schedule adjustment feasibility"""
        
        details = {}
        violations = []
        
        # Check requested delay duration
        requested_delay_days = input_event.get("requested_delay_days", 0)
        details["requested_delay_days"] = requested_delay_days
        
        if requested_delay_days > 2:  # MAX_ROUTE_DELAY_DAYS = 2
            violations.append(f"Requested delay ({requested_delay_days} days) exceeds maximum (2 days)")
        
        # Check bin fill levels
        critical_bins = observations.get("extracted_facts", {}).get("critical_fill_bins", 0)
        details["critical_bins"] = critical_bins
        
        if critical_bins > 5:
            violations.append(f"{critical_bins} bins at critical fill level - delay not advisable")
        
        # Check complaint history
        high_priority_complaints = observations.get("extracted_facts", {}).get("high_priority_complaints", 0)
        if high_priority_complaints > 3:
            violations.append(f"{high_priority_complaints} high-priority complaints - schedule adjustment risky")
        
        feasible = len(violations) == 0
        reason = "Schedule adjustment feasible" if feasible else "; ".join(violations)
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_landfill_routing(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate landfill routing decision feasibility"""
        
        details = {}
        violations = []
        
        # Check landfill availability
        operational_landfills = observations.get("extracted_facts", {}).get("operational_landfills", 0)
        details["operational_landfills"] = operational_landfills
        
        if operational_landfills == 0:
            violations.append("No operational landfills available")
        
        # Check capacity
        avg_utilization = observations.get("extracted_facts", {}).get("landfill_avg_utilization", 0)
        details["avg_utilization_percent"] = avg_utilization
        
        if avg_utilization > 90:
            violations.append(f"Average landfill utilization critical: {avg_utilization}%")
        
        feasible = len(violations) == 0
        reason = "Landfill routing feasible" if feasible else "; ".join(violations)
        
        return feasible, reason, details
    
    @staticmethod
    def evaluate_complaint_response(observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate complaint response feasibility"""
        
        details = {"complaint_response": True}
        violations = []
        
        # Complaints should almost always be addressed
        # Only constraint is resource availability
        
        available_resources = observations.get("extracted_facts", {}).get("available_trucks", 0)
        if available_resources == 0:
            violations.append("No resources available for complaint response")
        
        feasible = len(violations) == 0
        reason = "Complaint response feasible" if feasible else "; ".join(violations)
        
        return feasible, reason, details


class FeasibilityEvaluator:
    """Main feasibility evaluator - dispatches to specific rules"""
    
    def __init__(self):
        self.rules = FeasibilityRules()
    
    def evaluate(self, intent: str, observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """
        Evaluate feasibility based on intent.
        
        Returns: (feasible, reason, details)
        """
        
        # Dispatch to appropriate rule set based on intent
        if intent == "modify_route":
            return self.rules.evaluate_route_change(observations, input_event)
        
        elif intent == "emergency_collection":
            return self.rules.evaluate_emergency_collection(observations, input_event)
        
        elif intent == "schedule_maintenance":
            return self.rules.evaluate_equipment_maintenance(observations, input_event)
        
        elif intent == "adjust_schedule":
            return self.rules.evaluate_schedule_adjustment(observations, input_event)
        
        elif intent == "route_to_landfill":
            return self.rules.evaluate_landfill_routing(observations, input_event)
        
        elif intent == "respond_to_complaint":
            return self.rules.evaluate_complaint_response(observations, input_event)
        
        else:
            # Default evaluation for unknown intents
            logger.warning(f"Unknown intent: {intent}, using default evaluation")
            return self._default_evaluation(observations, input_event)
    
    def _default_evaluation(self, observations: Dict, input_event: Dict) -> Tuple[bool, str, Dict]:
        """Default feasibility check"""
        
        violations = []
        
        # Basic checks
        if not observations.get("extracted_facts", {}).get("truck_available", True):
            violations.append("Resource constraints exist")
        
        if not observations.get("extracted_facts", {}).get("budget_available", True):
            violations.append("Budget constraints exist")
        
        feasible = len(violations) == 0
        reason = "Operation feasible" if feasible else "; ".join(violations)
        
        return feasible, reason, {"violations": violations}
