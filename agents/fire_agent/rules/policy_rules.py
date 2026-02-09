"""
Fire Department Policy Rules

Policy constraints for fire department operations.
"""

import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)


# ============================================================
# FIRE DEPARTMENT POLICIES
# ============================================================

MAX_RESPONSE_TIME_MINUTES = 10  # Maximum acceptable response time
MIN_FIREFIGHTERS_PER_TRUCK = 3  # Minimum crew size per truck
MIN_TRUCK_FUEL_PERCENT = 30  # Minimum fuel level for deployment
MIN_HYDRANT_PRESSURE_PSI = 50  # Minimum hydrant pressure
MAX_STATION_STAFFING_PERCENT = 90  # Maximum station capacity utilization
REQUIRED_HAZMAT_CERTIFICATION = True  # Hazmat incidents require certification
MIN_EQUIPMENT_CONDITION = "fair"  # Minimum equipment condition for use
MAX_TRAINING_DURATION_HOURS = 8  # Maximum training session duration
EMERGENCY_OVERRIDE_ALLOWED = True  # Emergencies can bypass certain rules
MAX_BUDGET_OVERAGE_PERCENT = 10  # Maximum budget overage allowed


class PolicyValidator:
    """Validate fire department policy compliance"""
    
    def validate(self, intent: str, input_event: Dict[str, Any],
                 observations: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate policy compliance.
        
        Returns: (policy_ok: bool, violations: List[str])
        """
        
        logger.info(f"Validating policy compliance for: {intent}")
        
        violations = []
        extracted = observations.get('extracted_facts', {})
        
        # Check emergency override
        is_emergency = input_event.get('priority') in ['critical', 'high']
        emergency_type = input_event.get('incident_type', '').lower()
        
        # Policy 1: Response time limits
        response_time = extracted.get('estimated_response_minutes', 0)
        if response_time > MAX_RESPONSE_TIME_MINUTES:
            if not (is_emergency and EMERGENCY_OVERRIDE_ALLOWED):
                violations.append(
                    f"Response time {response_time}min exceeds max {MAX_RESPONSE_TIME_MINUTES}min"
                )
        
        # Policy 2: Minimum crew size per truck
        firefighters = extracted.get('available_firefighters', 0)
        trucks = extracted.get('available_trucks', 0)
        
        if trucks > 0:
            crew_per_truck = firefighters / trucks if trucks > 0 else 0
            if crew_per_truck < MIN_FIREFIGHTERS_PER_TRUCK:
                violations.append(
                    f"Crew size {crew_per_truck:.1f} per truck below minimum {MIN_FIREFIGHTERS_PER_TRUCK}"
                )
        
        # Policy 3: Minimum fuel level
        # (Would check individual truck fuel from tool results)
        # Simplified: assume checked in tools
        
        # Policy 4: Hydrant requirements for structure fires
        if 'fire' in emergency_type:
            hydrants_adequate = extracted.get('hydrants_sufficient', False)
            hydrant_count = extracted.get('adequate_hydrants', 0)
            
            if not hydrants_adequate and not is_emergency:
                violations.append(
                    f"Inadequate hydrants ({hydrant_count}) for structure fire response"
                )
        
        # Policy 5: Station capacity limits
        station_util = extracted.get('station_utilization_percent', 0)
        if station_util > MAX_STATION_STAFFING_PERCENT:
            violations.append(
                f"Station utilization {station_util}% exceeds max {MAX_STATION_STAFFING_PERCENT}%"
            )
        
        # Policy 6: Hazmat certification requirement
        if 'hazmat' in emergency_type:
            if REQUIRED_HAZMAT_CERTIFICATION:
                certs = extracted.get('certifications_available', {})
                hazmat_certified = certs.get('hazmat', 0)
                
                if hazmat_certified < 2:
                    violations.append(
                        f"Insufficient hazmat-certified personnel: {hazmat_certified} (min 2 required)"
                    )
        
        # Policy 7: Equipment condition requirements
        equipment_condition = extracted.get('equipment_condition', 'unknown')
        if equipment_condition == 'poor' and not is_emergency:
            violations.append(
                f"Equipment condition '{equipment_condition}' below minimum '{MIN_EQUIPMENT_CONDITION}'"
            )
        
        # Policy 8: Training duration limits
        if intent == "schedule_training":
            training_hours = input_event.get('duration_hours', 0)
            if training_hours > MAX_TRAINING_DURATION_HOURS:
                violations.append(
                    f"Training duration {training_hours}h exceeds max {MAX_TRAINING_DURATION_HOURS}h"
                )
        
        # Policy 9: Budget constraints
        budget_overage = extracted.get('budget_constraint', False)
        if budget_overage:
            utilization = extracted.get('budget_utilization_percent', 0)
            max_allowed = 100 + MAX_BUDGET_OVERAGE_PERCENT
            
            if utilization > max_allowed:
                violations.append(
                    f"Budget utilization {utilization}% exceeds max {max_allowed}%"
                )
        
        policy_ok = len(violations) == 0
        
        if policy_ok:
            logger.info("✓ All policies compliant")
        else:
            logger.warning(f"✗ {len(violations)} policy violations")
            for v in violations:
                logger.warning(f"  - {v}")
        
        return (policy_ok, violations)
