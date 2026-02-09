"""
PHASE 6: Planner Node (LLM)

Generate candidate plans. LLM only proposes, it does not decide feasibility.

Output: structured JSON with steps and alternatives.
"""

import logging
import json
import os
from typing import Dict, List, Any

from ..state import DepartmentState
from ..config import settings

logger = logging.getLogger(__name__)


class SanitationPlanner:
    """LLM-based planner for Sanitation Department"""
    
    def __init__(self):
        """Initialize planner with LLM support"""
        self.llm_provider = settings.LLM_PROVIDER
        self.use_llm = self._check_llm_available()
        
        if self.use_llm:
            self._init_llm_client()
    
    def _check_llm_available(self) -> bool:
        """Check if LLM is configured"""
        groq_key = settings.GROQ_API_KEY
        openai_key = settings.OPENAI_API_KEY
        
        if self.llm_provider == "groq" and groq_key:
            logger.info("✓ Groq LLM configured")
            return True
        elif self.llm_provider == "openai" and openai_key:
            logger.info("✓ OpenAI LLM configured")
            return True
        else:
            logger.warning("⚠️  No LLM configured, using deterministic fallback")
            return False
    
    def _init_llm_client(self):
        """Initialize LLM client"""
        try:
            import openai
            
            if self.llm_provider == "groq":
                self.client = openai.OpenAI(
                    api_key=settings.GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                logger.info("✓ Groq client initialized")
            else:
                self.client = openai.OpenAI(
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("✓ OpenAI client initialized")
        except ImportError:
            logger.error("✗ 'openai' package not installed. Run: pip install openai")
            self.use_llm = False
        except Exception as e:
            logger.error(f"✗ Failed to initialize LLM: {e}")
            self.use_llm = False
    
    def generate_plan(self, state: DepartmentState) -> Dict:
        """
        PHASE 6: Planner Node (LLM)
        
        Purpose: Generate candidate plan(s) using LLM or fallback
        """
        
        logger.info("📋 [NODE: Planner (LLM)]")
        
        try:
            goal = state.get("goal", "")
            intent = state.get("intent", "")
            context = state.get("context", {})
            input_event = state.get("input_event", {})
            
            # 🔥 CALL LLM IF AVAILABLE 🔥
            if self.use_llm:
                logger.info("🤖 Calling Groq/OpenAI API...")
                plans = self._generate_llm_plans(
                    intent=intent,
                    goal=goal,
                    context=context,
                    input_event=input_event
                )
                logger.info("✓ LLM response received")
            else:
                logger.info("Using deterministic fallback (no LLM)")
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
                "total_plans": len(plans),
                "llm_used": self.use_llm
            }
        
        except Exception as e:
            logger.error(f"✗ Planner error: {e}")
            return {
                "primary_plan": None,
                "alternative_plans": [],
                "error": str(e),
                "llm_used": False
            }
    
    def _generate_llm_plans(self, intent: str, goal: str, 
                           context: Dict, input_event: Dict) -> List[Dict]:
        """Generate plans using Groq/OpenAI LLM - ACTUAL API CALL! 🚀"""
        
        prompt = self._build_planning_prompt(intent, goal, context, input_event)
        
        try:
            # Make API call to Groq/OpenAI
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Sanitation Department planning AI. Generate structured plans "
                            "for waste management and sanitation operations. Return ONLY valid JSON with this structure: "
                            '{"plans": [{"name": "Plan A", "steps": ["step1", "step2"], '
                            '"estimated_duration": "X days", "estimated_cost": 50000, '
                            '"resources_needed": ["resource1"], "risk_level": "low"}]}'
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=1000
            )
            
            llm_output = response.choices[0].message.content
            logger.info(f"LLM raw output: {llm_output[:200]}...")
            
            # Clean markdown code blocks
            if llm_output.startswith("```json"):
                llm_output = llm_output[7:]
            elif llm_output.startswith("```"):
                llm_output = llm_output[3:]
            if llm_output.endswith("```"):
                llm_output = llm_output[:-3]
            
            # Parse JSON
            parsed = json.loads(llm_output.strip())
            plans = parsed.get("plans", [])
            
            if not plans:
                logger.warning("LLM returned no plans, using fallback")
                return self._generate_deterministic_plans(intent, goal, context, input_event)
            
            return plans
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON: {e}")
            return self._generate_deterministic_plans(intent, goal, context, input_event)
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return self._generate_deterministic_plans(intent, goal, context, input_event)
    
    def _build_planning_prompt(self, intent: str, goal: str, 
                              context: Dict, input_event: Dict) -> str:
        """Build prompt for LLM"""
        return f"""Generate a detailed operational plan for the Sanitation Department.

INTENT: {intent}
GOAL: {goal}

REQUEST DETAILS:
{json.dumps(input_event, indent=2)}

CURRENT CONTEXT:
- Active Routes: {len(context.get('routes', []))}
- Available Trucks: {sum(1 for t in context.get('trucks', []) if t.get('status') == 'available')}
- Available Workers: {context.get('worker_info', {}).get('available_count', 'unknown')}
- Budget Status: ${context.get('budget', {}).get('available', 0):,}
- Recent Complaints: {context.get('recent_complaints', 0)}

AVAILABLE TOOLS (use these exact names in steps):
- check_truck_availability: Check available sanitation trucks
- check_route_capacity: Check route workload and capacity
- check_landfill_capacity: Check landfill availability
- assess_collection_delay: Assess delay risks in collection
- check_equipment_status: Check truck and equipment condition
- get_complaint_history: Get complaint history for location
- check_recycling_center_availability: Check recycling center status
- estimate_waste_volume: Estimate waste volume for zone
- check_budget_availability: Verify budget (use 'estimated_cost' parameter)

Return ONLY valid JSON:
{{
  "plans": [
    {{
      "name": "Plan A",
      "steps": ["Step 1", "Step 2", ...],
      "estimated_duration": "2 days",
      "estimated_cost": 50000,
      "resources_needed": ["3 trucks", "5 workers"],
      "risk_level": "low"
    }}
  ]
}}"""
    
    def _generate_deterministic_plans(self, intent: str, goal: str, 
                                     context: Dict, input_event: Dict) -> List[Dict]:
        """
        Generate deterministic plans based on intent.
        
        These are templates that would normally come from LLM.
        Structure is the same whether from LLM or here.
        """
        
        plans = []
        
        if intent == "negotiate_route_change":
            # Plan 1: Approve with validation
            plans.append({
                "id": "plan_1_approve_conditional",
                "name": "Approve route change with validation",
                "steps": [
                    "check_truck_availability",
                    "check_route_capacity",
                    "check_equipment_status",
                    "check_budget_availability"
                ],
                "constraints": [
                    "Minimum 2 trucks available",
                    "Route capacity not exceeded",
                    "Budget available for fuel"
                ],
                "expected_outcome": "Route change approved with safeguards"
            })
            
            # Plan 2: Alternative route
            plans.append({
                "id": "plan_2_alternative",
                "name": "Suggest alternative route",
                "steps": [
                    "check_route_capacity",
                    "check_landfill_capacity"
                ],
                "constraints": [
                    "Route delay < 2 days",
                    "Notify residents"
                ],
                "expected_outcome": "Alternative route proposed"
            })
        
        elif intent == "emergency_collection":
            plans.append({
                "id": "plan_emergency_immediate",
                "name": "Immediate emergency collection",
                "steps": [
                    "check_truck_availability",
                    "check_landfill_capacity",
                    "estimate_waste_volume",
                    "check_equipment_status"
                ],
                "priority": "critical",
                "expected_outcome": "Emergency collection team mobilized"
            })
        
        elif intent == "coordinate_maintenance":
            plans.append({
                "id": "plan_maintenance_window",
                "name": "Schedule equipment maintenance",
                "steps": [
                    "check_equipment_status",
                    "check_route_capacity",
                    "check_budget_availability"
                ],
                "expected_outcome": "Maintenance scheduled with minimal disruption"
            })
        
        elif intent == "adjust_schedule":
            plans.append({
                "id": "plan_schedule_adjust",
                "name": "Adjust collection schedule",
                "steps": [
                    "check_truck_availability",
                    "check_route_capacity",
                    "assess_collection_delay"
                ],
                "expected_outcome": "Schedule adjusted optimally"
            })
        
        elif intent == "optimize_landfill_routing":
            plans.append({
                "id": "plan_landfill_optimize",
                "name": "Optimize landfill routing",
                "steps": [
                    "check_landfill_capacity",
                    "check_route_capacity",
                    "estimate_waste_volume",
                    "check_truck_availability"
                ],
                "expected_outcome": "Optimized routing to available landfills"
            })
        
        elif intent == "respond_to_complaint":
            plans.append({
                "id": "plan_complaint_response",
                "name": "Respond to sanitation complaint",
                "steps": [
                    "get_complaint_history",
                    "check_route_capacity",
                    "assess_collection_delay",
                    "check_truck_availability"
                ],
                "expected_outcome": "Complaint addressed with action plan"
            })
        
        elif intent == "assess_capacity":
            plans.append({
                "id": "plan_capacity_assess",
                "name": "Assess sanitation capacity",
                "steps": [
                    "check_landfill_capacity",
                    "check_truck_availability",
                    "check_recycling_center_availability",
                    "estimate_waste_volume"
                ],
                "expected_outcome": "Capacity report generated"
            })
        
        else:
            # Default plan
            plans.append({
                "id": "plan_default",
                "name": "Standard sanitation evaluation",
                "steps": [
                    "check_truck_availability",
                    "check_route_capacity",
                    "check_budget_availability"
                ],
                "expected_outcome": "Evaluation complete"
            })
        
        return plans


def planner_node(state: DepartmentState) -> DepartmentState:
    """Planner node that generates plans"""
    
    planner = SanitationPlanner()
    plan_result = planner.generate_plan(state)
    
    state["plan"] = plan_result.get("primary_plan", {})
    state["alternative_plans"] = plan_result.get("alternative_plans", [])
    
    return state
