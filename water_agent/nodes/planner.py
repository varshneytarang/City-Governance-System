"""
PHASE 6: Planner Node (LLM)

Generate candidate plans. LLM only proposes, it does not decide feasibility.

Output: structured JSON with steps and alternatives.
"""

import logging
import json
from typing import Dict, List, Any

from ..state import DepartmentState
from ..config import settings

logger = logging.getLogger(__name__)


class WaterPlanner:
    """LLM-based planner for Water Department"""
    
    def __init__(self):
        """Initialize planner"""
        self.llm_provider = settings.LLM_PROVIDER
    
    def generate_plan(self, state: DepartmentState) -> Dict:
        """
        PHASE 6: Planner Node (LLM)
        
        Purpose: Generate candidate plan(s)
        
        This is the ONLY place where LLM is allowed to make suggestions.
        
        Input: goal, context, constraints
        Output: structured plan with steps and alternatives
        
        Important: LLM does NOT decide feasibility.
        It only proposes.
        """
        
        logger.info("📋 [NODE: Planner (LLM)]")
        
        try:
            goal = state.get("goal", "")
            intent = state.get("intent", "")
            context = state.get("context", {})
            input_event = state.get("input_event", {})
            
            # For now, return deterministic plans without LLM
            # This is production-ready - we'll add LLM integration separately
            
            plans = self._generate_deterministic_plans(
                intent=intent,
                goal=goal,
                context=context,
                input_event=input_event
            )
            
            logger.info(f"  → Generated {len(plans)} plan(s)")
            
            return {
                "primary_plan": plans[0] if plans else None,
                "alternative_plans": plans[1:] if len(plans) > 1 else [],
                "total_plans": len(plans)
            }
        
        except Exception as e:
            logger.error(f"✗ Planner error: {e}")
            return {
                "primary_plan": None,
                "alternative_plans": [],
                "error": str(e)
            }
    
    def _generate_deterministic_plans(self, intent: str, goal: str, 
                                     context: Dict, input_event: Dict) -> List[Dict]:
        """
        Generate deterministic plans based on intent.
        
        These are templates that would normally come from LLM.
        Structure is the same whether from LLM or here.
        """
        
        plans = []
        
        if intent == "negotiate_schedule":
            # Plan 1: Approve with conditions
            plans.append({
                "id": "plan_1_approve_conditional",
                "name": "Approve with resource check",
                "steps": [
                    "check_manpower_availability",
                    "check_schedule_conflicts",
                    "check_pipeline_health",
                    "check_budget_availability"
                ],
                "constraints": [
                    "Minimum 4 workers available",
                    "No critical incidents in zone",
                    "Budget remaining > 50000"
                ],
                "expected_outcome": "Approved with operational safeguards"
            })
            
            # Plan 2: Partial delay
            plans.append({
                "id": "plan_2_partial_delay",
                "name": "Approve with delay",
                "steps": [
                    "check_schedule_conflicts",
                    "check_manpower_availability"
                ],
                "duration_days": 1,
                "constraints": [
                    "Delayed by 1 day minimum",
                    "Notify coordinator"
                ],
                "expected_outcome": "Approved with modified dates"
            })
            
            # Plan 3: Escalate
            plans.append({
                "id": "plan_3_escalate",
                "name": "Escalate for approval",
                "steps": [
                    "document_request",
                    "log_decision"
                ],
                "expected_outcome": "Human decision required"
            })
        
        elif intent == "emergency_response":
            plans.append({
                "id": "plan_emergency_immediate",
                "name": "Immediate emergency response",
                "steps": [
                    "alert_all_workers",
                    "check_available_resources",
                    "assess_zone_risk",
                    "activate_emergency_protocol"
                ],
                "priority": "critical",
                "expected_outcome": "Emergency team mobilized"
            })
        
        elif intent == "coordinate_maintenance":
            plans.append({
                "id": "plan_maintenance_window",
                "name": "Schedule maintenance with minimal disruption",
                "steps": [
                    "check_work_schedule",
                    "check_manpower_availability",
                    "check_pipeline_health",
                    "calculate_service_impact"
                ],
                "expected_outcome": "Maintenance scheduled safely"
            })
        
        elif intent == "assess_capacity":
            plans.append({
                "id": "plan_capacity_assess",
                "name": "Assess current capacity",
                "steps": [
                    "check_reservoir_levels",
                    "check_pipeline_status",
                    "check_active_projects",
                    "forecast_demand"
                ],
                "expected_outcome": "Capacity report generated"
            })
        
        else:
            # Default plan
            plans.append({
                "id": "plan_default",
                "name": "Standard evaluation",
                "steps": [
                    "assess_zone_risk",
                    "check_manpower_availability",
                    "evaluate_resources"
                ],
                "expected_outcome": "Evaluation complete"
            })
        
        return plans


def planner_node(state: DepartmentState) -> DepartmentState:
    """Planner node that generates plans"""
    
    planner = WaterPlanner()
    plan_result = planner.generate_plan(state)
    
    state["plan"] = plan_result.get("primary_plan", {})
    state["alternative_plans"] = plan_result.get("alternative_plans", [])
    
    return state
