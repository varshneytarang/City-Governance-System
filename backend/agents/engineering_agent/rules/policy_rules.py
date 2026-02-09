"""
Policy Rules - validate against department rules and regulations.
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PolicyRules:
    """Department policy validation"""
    
    # Water Department Policies
    MAX_SHIFT_DELAY_DAYS = 3
    MIN_MAINTENANCE_NOTICE_HOURS = 24
    MAX_CONCURRENT_PROJECTS = 5
    MIN_WORKERS_MAINTENANCE = 3
    MAX_BUDGET_UTILIZATION_PERCENT = 85
    SERVICE_CONTINUITY_REQUIREMENT = True
    
    @staticmethod
    def validate_schedule_policy(input_event: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate schedule shift against policies"""
        
        violations = []
        
        # Policy 1: Maximum delay allowed
        requested_delay = input_event.get("requested_shift_days", 0)
        if requested_delay > PolicyRules.MAX_SHIFT_DELAY_DAYS:
            violations.append(
                f"Requested delay ({requested_delay} days) exceeds max allowed "
                f"({PolicyRules.MAX_SHIFT_DELAY_DAYS} days)"
            )
        
        # Policy 2: Service continuity
        if PolicyRules.SERVICE_CONTINUITY_REQUIREMENT:
            if observations.get("extracted_facts", {}).get("critical_pipeline_issues", 0) > 0:
                violations.append("Cannot proceed - service continuity at risk")
        
        # Policy 3: Budget constraint
        remaining_budget = observations.get("extracted_facts", {}).get("remaining_budget", 0)
        estimated_cost = input_event.get("estimated_cost", 0)
        
        if estimated_cost > remaining_budget and remaining_budget > 0:
            violations.append(
                f"Estimated cost (${estimated_cost}) exceeds remaining budget (${remaining_budget})"
            )
        
        # Policy 4: Active project limit
        active_projects = observations.get("extracted_facts", {}).get("active_projects_count", 0)
        if active_projects >= PolicyRules.MAX_CONCURRENT_PROJECTS:
            violations.append(
                f"Cannot start new work - {active_projects} projects already active "
                f"(max: {PolicyRules.MAX_CONCURRENT_PROJECTS})"
            )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_maintenance_policy(input_event: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate maintenance against policies"""
        
        violations = []
        
        # Policy 1: Minimum notice
        notice_hours = input_event.get("notice_hours", 0)
        if notice_hours < PolicyRules.MIN_MAINTENANCE_NOTICE_HOURS:
            violations.append(
                f"Notice period ({notice_hours}h) below minimum ({PolicyRules.MIN_MAINTENANCE_NOTICE_HOURS}h)"
            )
        
        # Policy 2: Minimum crew size
        available_workers = observations.get("extracted_facts", {}).get("available_workers", 0)
        if available_workers < PolicyRules.MIN_WORKERS_MAINTENANCE:
            violations.append(
                f"Insufficient crew ({available_workers} workers, min {PolicyRules.MIN_WORKERS_MAINTENANCE})"
            )
        
        # Policy 3: No maintenance during peak hours (simplified)
        scheduled_time = input_event.get("scheduled_time", "00:00")
        # Could add more sophisticated time window checks
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_emergency_policy(input_event: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Emergency requests bypass most policies"""
        
        violations = []
        
        # Emergencies get priority - minimal policy checks
        # Just verify we have SOME resources
        
        if observations.get("extracted_facts", {}).get("available_workers", 0) == 0:
            violations.append("No workers available for emergency response")
        
        return len(violations) == 0, violations


class PolicyValidator:
    """Main policy validator"""
    
    def __init__(self):
        self.rules = PolicyRules()
    
    def validate(self, intent: str, input_event: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """
        Validate against all applicable policies.
        
        Returns: (compliant, violations_list)
        """
        
        if intent == "emergency_response":
            return self.rules.validate_emergency_policy(input_event, observations)
        
        elif intent == "coordinate_maintenance":
            return self.rules.validate_maintenance_policy(input_event, observations)
        
        else:
            # Default to schedule policy
            return self.rules.validate_schedule_policy(input_event, observations)
