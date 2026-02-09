"""
Fire Department Feasibility Rules

Deterministic rules to evaluate if a plan is feasible.
"""

import logging
from typing import Dict, Any, Tuple, List

logger = logging.getLogger(__name__)


class FeasibilityEvaluator:
    """Evaluate feasibility of fire department operations"""
    
    def evaluate(self, intent: str, observations: Dict[str, Any], 
                 input_event: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Main evaluation method.
        
        Returns: (feasible: bool, reason: str, details: dict)
        """
        
        logger.info(f"Evaluating feasibility for intent: {intent}")
        
        # Route to appropriate rule set
        if intent == "deploy_station_resources":
            return self._evaluate_station_deployment(observations, input_event)
        
        elif intent == "respond_to_emergency":
            return self._evaluate_emergency_response(observations, input_event)
        
        elif intent == "coordinate_maintenance":
            return self._evaluate_equipment_maintenance(observations, input_event)
        
        elif intent == "schedule_training":
            return self._evaluate_training_schedule(observations, input_event)
        
        elif intent == "assess_readiness":
            return self._evaluate_readiness_assessment(observations, input_event)
        
        elif intent == "respond_to_hazmat":
            return self._evaluate_hazmat_response(observations, input_event)
        
        else:
            # Default evaluation
            return self._evaluate_default(observations, input_event)
    
    def _evaluate_station_deployment(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate station resource deployment"""
        
        extracted = obs.get('extracted_facts', {})
        
        # Check 1: Truck availability
        trucks_available = extracted.get('trucks_sufficient', False)
        if not trucks_available:
            return (False, "Insufficient trucks available for deployment", {
                "trucks_available": extracted.get('available_trucks', 0),
                "trucks_required": extracted.get('required_trucks', 1)
            })
        
        # Check 2: Firefighter availability
        firefighters_available = extracted.get('firefighters_sufficient', False)
        if not firefighters_available:
            return (False, "Insufficient firefighters available", {
                "firefighters_available": extracted.get('available_firefighters', 0),
                "firefighters_required": extracted.get('required_firefighters', 3)
            })
        
        # Check 3: Equipment status
        equipment_condition = extracted.get('equipment_condition', 'unknown')
        if equipment_condition == 'poor':
            return (False, "Critical equipment in poor condition", {
                "equipment_condition": equipment_condition
            })
        
        # All checks passed
        return (True, "All resources available for deployment", {
            "trucks_available": extracted.get('available_trucks', 0),
            "firefighters_available": extracted.get('available_firefighters', 0),
            "equipment_condition": equipment_condition
        })
    
    def _evaluate_emergency_response(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate emergency response feasibility"""
        
        extracted = obs.get('extracted_facts', {})
        
        # Check 1: Response time
        response_time = extracted.get('estimated_response_minutes', 999)
        if response_time > 15:
            return (False, f"Response time too long: {response_time} minutes", {
                "estimated_response_minutes": response_time,
                "max_acceptable_minutes": 15
            })
        
        # Check 2: Required resources vs available
        required_trucks = extracted.get('estimated_trucks', 1)
        available_trucks = extracted.get('available_trucks', 0)
        
        if available_trucks < required_trucks:
            return (False, f"Insufficient trucks: {available_trucks}/{required_trucks}", {
                "available_trucks": available_trucks,
                "required_trucks": required_trucks
            })
        
        # Check 3: Firefighter count
        required_firefighters = extracted.get('estimated_firefighters', 3)
        available_firefighters = extracted.get('available_firefighters', 0)
        
        if available_firefighters < required_firefighters:
            return (False, f"Insufficient firefighters: {available_firefighters}/{required_firefighters}", {
                "available_firefighters": available_firefighters,
                "required_firefighters": required_firefighters
            })
        
        # Check 4: Hydrant availability (for structure fires)
        incident_type = event.get('incident_type', '')
        if 'fire' in incident_type.lower():
            hydrants_adequate = extracted.get('hydrants_sufficient', False)
            if not hydrants_adequate:
                return (False, "Inadequate hydrant coverage in response area", {
                    "adequate_hydrants": extracted.get('adequate_hydrants', 0)
                })
        
        # All checks passed
        return (True, "Emergency response resources available", {
            "response_time": response_time,
            "trucks": f"{available_trucks}/{required_trucks}",
            "firefighters": f"{available_firefighters}/{required_firefighters}"
        })
    
    def _evaluate_equipment_maintenance(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate equipment maintenance feasibility"""
        
        extracted = obs.get('extracted_facts', {})
        
        # Check 1: Spare equipment/trucks available
        trucks_available = extracted.get('available_trucks', 0)
        if trucks_available < 2:
            return (False, "Insufficient spare trucks during maintenance", {
                "available_trucks": trucks_available,
                "minimum_required": 2
            })
        
        # Check 2: Budget availability
        budget_available = extracted.get('budget_affordable', False)
        if not budget_available:
            return (False, "Insufficient budget for maintenance", {
                "available_budget": extracted.get('budget_available', 0),
                "estimated_cost": extracted.get('estimated_cost', 0)
            })
        
        # Check 3: Maintenance doesn't impact critical operations
        station_capacity = extracted.get('station_utilization_percent', 0)
        if station_capacity > 85:
            return (False, "Station at near-capacity, cannot spare equipment", {
                "station_utilization": station_capacity
            })
        
        # All checks passed
        return (True, "Maintenance feasible without impacting operations", {
            "spare_trucks": trucks_available,
            "budget_ok": budget_available
        })
    
    def _evaluate_training_schedule(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate training schedule feasibility"""
        
        extracted = obs.get('extracted_facts', {})
        
        # Check 1: Enough personnel to maintain operations
        firefighters_available = extracted.get('available_firefighters', 0)
        training_count = event.get('training_participants', 0)
        
        remaining = firefighters_available - training_count
        if remaining < 6:  # Minimum operational staffing
            return (False, f"Insufficient firefighters remain on duty: {remaining}", {
                "available_firefighters": firefighters_available,
                "training_participants": training_count,
                "remaining_on_duty": remaining,
                "minimum_required": 6
            })
        
        # Check 2: No active emergencies
        active_calls = extracted.get('active_emergency_calls', 0)
        if active_calls > 0:
            return (False, f"Active emergencies prevent training: {active_calls}", {
                "active_calls": active_calls
            })
        
        # All checks passed
        return (True, "Training can be scheduled without impacting readiness", {
            "personnel_available": remaining,
            "training_size": training_count
        })
    
    def _evaluate_readiness_assessment(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate readiness assessment feasibility"""
        
        # Readiness assessments are generally always feasible
        # They are observational/analytical, not operational
        
        extracted = obs.get('extracted_facts', {})
        
        return (True, "Readiness assessment feasible", {
            "trucks_operational": extracted.get('available_trucks', 0),
            "firefighters_on_duty": extracted.get('available_firefighters', 0),
            "equipment_status": extracted.get('equipment_condition', 'unknown')
        })
    
    def _evaluate_hazmat_response(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Evaluate hazmat incident response feasibility"""
        
        extracted = obs.get('extracted_facts', {})
        
        # Check 1: Hazmat-certified personnel
        certifications = extracted.get('certifications_available', {})
        hazmat_certified = certifications.get('hazmat', 0)
        
        if hazmat_certified < 2:
            return (False, f"Insufficient hazmat-certified personnel: {hazmat_certified}", {
                "hazmat_certified": hazmat_certified,
                "minimum_required": 2
            })
        
        # Check 2: Hazmat truck/equipment available
        # (This would be in tool results)
        # For now, assume basic check
        
        # Check 3: Response time acceptable
        response_time = extracted.get('estimated_response_minutes', 999)
        if response_time > 12:
            return (False, f"Hazmat response time too long: {response_time} min", {
                "response_time": response_time,
                "max_acceptable": 12
            })
        
        # All checks passed
        return (True, "Hazmat response resources available", {
            "hazmat_certified_personnel": hazmat_certified,
            "response_time": response_time
        })
    
    def _evaluate_default(self, obs: Dict, event: Dict) -> Tuple[bool, str, Dict]:
        """Default evaluation for unknown intents"""
        
        extracted = obs.get('extracted_facts', {})
        
        # Basic feasibility check: resources available
        trucks_ok = extracted.get('trucks_sufficient', False)
        firefighters_ok = extracted.get('firefighters_sufficient', False)
        
        if trucks_ok and firefighters_ok:
            return (True, "Basic resources available", extracted)
        else:
            return (False, "Insufficient basic resources", {
                "trucks_ok": trucks_ok,
                "firefighters_ok": firefighters_ok
            })
