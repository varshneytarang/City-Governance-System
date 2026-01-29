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


class WaterPlanner:
    """LLM-based planner for Water Department"""
    
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
                            "You are a Water Department planning AI. Generate structured plans "
                            "for departmental operations. Return ONLY valid JSON with this structure: "
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
        return f"""Generate a detailed operational plan for the Water Department.

INTENT: {intent}
GOAL: {goal}

REQUEST DETAILS:
{json.dumps(input_event, indent=2)}

CURRENT CONTEXT:
- Active Projects: {context.get('active_projects', [])}
- Available Workers: {context.get('worker_info', {}).get('available_count', 'unknown')}
- Budget Status: ${context.get('budget_status', {}).get('available', 0):,}

Return ONLY valid JSON:
{{
  "plans": [
    {{
      "name": "Plan A",
      "steps": ["Step 1", "Step 2", ...],
      "estimated_duration": "2 days",
      "estimated_cost": 50000,
      "resources_needed": ["5 workers", "equipment"],
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
