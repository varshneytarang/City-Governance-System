"""
Policy Rules - Department policies and compliance checking

PHASE 10: Check if plans comply with department policies
"""

import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PolicyRules:
    """
    Sanitation Department Policies
    
    These are the SOPs (Standard Operating Procedures) that must be followed.
    """
    
    # Policy Constants
    MAX_ROUTE_DELAY_DAYS = 2
    MIN_TRUCK_FUEL_PERCENT = 25.0
    MAX_LANDFILL_UTILIZATION = 90.0
    REQUIRED_CREW_SIZE = 3
    MAX_DAILY_ROUTES_PER_TRUCK = 2
    COMPLAINT_RESPONSE_HOURS = 48
    MIN_EQUIPMENT_CONDITION_FOR_OPERATION = "fair"  # excellent, good, fair (poor and critical require maintenance)
    MAX_BIN_FILL_BEFORE_EMERGENCY = 95.0
    MIN_RECYCLING_CENTER_CAPACITY_PERCENT = 20.0
    
    @staticmethod
    def validate_route_delay(plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate route delay doesn't exceed policy"""
        violations = []
        
        delay_days = plan.get("delay_days", 0)
        if delay_days > PolicyRules.MAX_ROUTE_DELAY_DAYS:
            violations.append(
                f"Route delay ({delay_days} days) exceeds maximum allowed "
                f"({PolicyRules.MAX_ROUTE_DELAY_DAYS} days)"
            )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_truck_fuel(plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate trucks have sufficient fuel"""
        violations = []
        
        trucks = observations.get("extracted_facts", {}).get("trucks", [])
        for truck in trucks:
            fuel = truck.get("fuel_percent", 100)
            if fuel < PolicyRules.MIN_TRUCK_FUEL_PERCENT:
                violations.append(
                    f"Truck {truck.get('number', 'unknown')} has insufficient fuel "
                    f"({fuel}% < {PolicyRules.MIN_TRUCK_FUEL_PERCENT}%)"
                )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_landfill_capacity(plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate landfill capacity is within limits"""
        violations = []
        
        landfills = observations.get("extracted_facts", {}).get("landfills", [])
        for lf in landfills:
            util = lf.get("utilization_percent", 0)
            if util > PolicyRules.MAX_LANDFILL_UTILIZATION:
                violations.append(
                    f"Landfill {lf.get('name', 'unknown')} exceeds capacity limit "
                    f"({util}% > {PolicyRules.MAX_LANDFILL_UTILIZATION}%)"
                )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_crew_size(plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate crew size meets minimum requirements"""
        violations = []
        
        crew_size = plan.get("crew_size", PolicyRules.REQUIRED_CREW_SIZE)
        if crew_size < PolicyRules.REQUIRED_CREW_SIZE:
            violations.append(
                f"Crew size ({crew_size}) below minimum required "
                f"({PolicyRules.REQUIRED_CREW_SIZE})"
            )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_routes_per_truck(plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate trucks aren't assigned too many routes per day"""
        violations = []
        
        routes_assigned = plan.get("routes_per_truck", 1)
        if routes_assigned > PolicyRules.MAX_DAILY_ROUTES_PER_TRUCK:
            violations.append(
                f"Routes per truck ({routes_assigned}) exceeds maximum "
                f"({PolicyRules.MAX_DAILY_ROUTES_PER_TRUCK})"
            )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def validate_equipment_condition(plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """Validate equipment is in acceptable condition"""
        violations = []
        
        condition_hierarchy = ["excellent", "good", "fair", "poor", "critical"]
        min_index = condition_hierarchy.index(PolicyRules.MIN_EQUIPMENT_CONDITION_FOR_OPERATION)
        
        equipment_issues = observations.get("extracted_facts", {}).get("equipment_issues", [])
        for issue in equipment_issues:
            truck = issue.get("truck", "unknown")
            for problem in issue.get("issues", []):
                if any(cond in problem.lower() for cond in ["poor", "critical"]):
                    violations.append(
                        f"Truck {truck} has equipment below acceptable condition: {problem}"
                    )
        
        return len(violations) == 0, violations


class PolicyValidator:
    """Main policy validator"""
    
    def __init__(self):
        self.rules = PolicyRules()
    
    def validate(self, intent: str, plan: Dict, observations: Dict) -> Tuple[bool, List[str]]:
        """
        Validate plan against all relevant policies.
        
        Returns: (compliant, violations)
        """
        
        all_violations = []
        
        # Always check these policies
        ok, violations = self.rules.validate_truck_fuel(plan, observations)
        if not ok:
            all_violations.extend(violations)
        
        ok, violations = self.rules.validate_equipment_condition(plan, observations)
        if not ok:
            all_violations.extend(violations)
        
        # Intent-specific policy checks
        if intent in ["modify_route", "adjust_schedule"]:
            ok, violations = self.rules.validate_route_delay(plan, observations)
            if not ok:
                all_violations.extend(violations)
            
            ok, violations = self.rules.validate_crew_size(plan, observations)
            if not ok:
                all_violations.extend(violations)
        
        if intent in ["route_to_landfill", "emergency_collection"]:
            ok, violations = self.rules.validate_landfill_capacity(plan, observations)
            if not ok:
                all_violations.extend(violations)
        
        if intent == "modify_route":
            ok, violations = self.rules.validate_routes_per_truck(plan, observations)
            if not ok:
                all_violations.extend(violations)
        
        policy_ok = len(all_violations) == 0
        
        if policy_ok:
            logger.info("✓ All policies satisfied")
        else:
            logger.warning(f"✗ {len(all_violations)} policy violation(s)")
        
        return policy_ok, all_violations
