"""
LLM-Enhanced Planner Node

This version ACTUALLY calls your Groq/OpenAI API.
Replace the existing planner.py with this to enable LLM.
"""

import logging
import json
import os
from typing import Dict, List, Any

from ..state import DepartmentState
from ..config import settings

logger = logging.getLogger(__name__)


class WaterPlannerWithLLM:
    """LLM-powered planner that actually makes API calls"""
    
    def __init__(self):
        """Initialize planner with LLM client"""
        self.llm_provider = settings.LLM_PROVIDER
        self.use_llm = self._check_llm_available()
        
        if self.use_llm:
            self._init_llm_client()
    
    def _check_llm_available(self) -> bool:
        """Check if LLM is configured"""
        openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        groq_key = os.getenv("GROQ_API_KEY")
        
        if self.llm_provider == "openai" and openai_key:
            logger.info("✓ OpenAI LLM configured")
            return True
        elif self.llm_provider == "groq" and groq_key:
            logger.info("✓ Groq LLM configured")
            return True
        else:
            logger.warning("⚠️  No LLM configured, using deterministic fallback")
            return False
    
    def _init_llm_client(self):
        """Initialize LLM client (OpenAI or Groq)"""
        try:
            if self.llm_provider == "groq":
                # Groq uses OpenAI-compatible API
                import openai
                self.client = openai.OpenAI(
                    api_key=os.getenv("GROQ_API_KEY"),
                    base_url="https://api.groq.com/openai/v1"
                )
                logger.info("✓ Groq client initialized")
            else:
                # Standard OpenAI
                import openai
                openai.api_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
                self.client = openai.OpenAI()
                logger.info("✓ OpenAI client initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize LLM client: {e}")
            self.use_llm = False
    
    def generate_plan(self, state: DepartmentState) -> Dict:
        """
        PHASE 6: Planner Node (LLM)
        
        This version ACTUALLY calls your LLM API!
        """
        
        logger.info("📋 [NODE: Planner (LLM)]")
        
        try:
            goal = state.get("goal", "")
            intent = state.get("intent", "")
            context = state.get("context", {})
            input_event = state.get("input_event", {})
            
            if self.use_llm:
                # 🔥 ACTUAL LLM CALL HERE 🔥
                logger.info("🤖 Calling LLM API...")
                plans = self._generate_llm_plans(
                    intent=intent,
                    goal=goal,
                    context=context,
                    input_event=input_event
                )
                logger.info("✓ LLM response received")
            else:
                # Fallback to deterministic
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
        """
        Generate plans using LLM (OpenAI/Groq)
        
        THIS IS WHERE THE ACTUAL API CALL HAPPENS! 🚀
        """
        
        # Build prompt for LLM
        prompt = self._build_planning_prompt(intent, goal, context, input_event)
        
        try:
            # Make API call
            response = self.client.chat.completions.create(
                model=self._get_model_name(),
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
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=1000
            )
            
            # Extract response
            llm_output = response.choices[0].message.content
            logger.info(f"LLM raw output: {llm_output[:200]}...")
            
            # Parse JSON response
            try:
                parsed = json.loads(llm_output)
                plans = parsed.get("plans", [])
                
                if not plans:
                    logger.warning("LLM returned no plans, using fallback")
                    return self._generate_deterministic_plans(intent, goal, context, input_event)
                
                return plans
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM JSON: {e}")
                # Fallback to deterministic
                return self._generate_deterministic_plans(intent, goal, context, input_event)
        
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            # Fallback to deterministic
            return self._generate_deterministic_plans(intent, goal, context, input_event)
    
    def _get_model_name(self) -> str:
        """Get the appropriate model name for the provider"""
        if self.llm_provider == "groq":
            # Groq models: llama3-70b-8192, mixtral-8x7b-32768, gemma-7b-it
            return os.getenv("LLM_MODEL", "llama3-70b-8192")
        else:
            # OpenAI models
            return settings.LLM_MODEL
    
    def _build_planning_prompt(self, intent: str, goal: str, 
                              context: Dict, input_event: Dict) -> str:
        """Build detailed prompt for LLM"""
        
        prompt = f"""Generate a detailed operational plan for the Water Department.

INTENT: {intent}
GOAL: {goal}

REQUEST DETAILS:
{json.dumps(input_event, indent=2)}

CURRENT CONTEXT:
- Active Projects: {context.get('active_projects', [])}
- Available Workers: {context.get('worker_info', {}).get('available_count', 'unknown')}
- Budget Status: ${context.get('budget_status', {}).get('available', 0):,}

REQUIREMENTS:
1. Generate 1-2 alternative plans
2. Each plan must include:
   - Clear step-by-step actions
   - Estimated duration
   - Resource requirements
   - Estimated costs
   - Risk assessment

Return ONLY valid JSON following this structure:
{{
  "plans": [
    {{
      "name": "Plan A: Quick Response",
      "steps": ["Step 1 description", "Step 2 description", ...],
      "estimated_duration": "2 days",
      "estimated_cost": 50000,
      "resources_needed": ["5 workers", "2 vehicles", "equipment"],
      "risk_level": "low",
      "pros": ["Fast", "Efficient"],
      "cons": ["Higher cost"]
    }}
  ]
}}
"""
        return prompt
    
    def _generate_deterministic_plans(self, intent: str, goal: str,
                                     context: Dict, input_event: Dict) -> List[Dict]:
        """
        Deterministic fallback when LLM is unavailable
        """
        
        request_type = input_event.get("type", "")
        location = input_event.get("location", "Unknown")
        
        plans = []
        
        if request_type == "schedule_shift_request":
            days = input_event.get("requested_shift_days", 1)
            cost = input_event.get("estimated_cost", 50000)
            
            plans.append({
                "name": "Standard Shift Adjustment",
                "steps": [
                    "1. Review current work schedule",
                    "2. Identify affected workers and tasks",
                    f"3. Shift work by {days} day(s)",
                    "4. Notify all stakeholders",
                    "5. Update project timelines"
                ],
                "estimated_duration": f"{days + 1} days",
                "estimated_cost": cost,
                "resources_needed": [
                    "Administrative staff for notifications",
                    "Project coordinators for timeline updates"
                ],
                "risk_level": "low" if days <= 2 else "medium"
            })
        
        elif request_type == "emergency_response":
            severity = input_event.get("severity", "medium")
            incident_type = input_event.get("incident_type", "leak")
            
            plans.append({
                "name": "Emergency Response Protocol",
                "steps": [
                    "1. Dispatch emergency response team immediately",
                    f"2. Assess {incident_type} severity at {location}",
                    "3. Isolate affected area",
                    "4. Deploy repair equipment",
                    "5. Coordinate with other departments if needed",
                    "6. Restore service and monitor"
                ],
                "estimated_duration": "4-8 hours",
                "estimated_cost": 75000,
                "resources_needed": [
                    "Emergency response team (6-8 workers)",
                    "2 emergency vehicles",
                    "Repair equipment and materials"
                ],
                "risk_level": severity
            })
        
        elif request_type == "maintenance_request":
            activity = input_event.get("activity", "inspection")
            notice_hours = input_event.get("notice_hours", 24)
            
            plans.append({
                "name": "Scheduled Maintenance Plan",
                "steps": [
                    f"1. Schedule {activity} for {location}",
                    f"2. Provide {notice_hours}h advance notice to residents",
                    "3. Assign qualified maintenance crew",
                    "4. Prepare equipment and materials",
                    "5. Execute maintenance work",
                    "6. Conduct post-work inspection",
                    "7. Update maintenance records"
                ],
                "estimated_duration": "1-2 days",
                "estimated_cost": input_event.get("estimated_cost", 30000),
                "resources_needed": [
                    "Maintenance crew (3-4 workers)",
                    "Inspection equipment",
                    "Safety gear"
                ],
                "risk_level": "low"
            })
        
        else:
            # Generic plan
            plans.append({
                "name": "General Assessment Plan",
                "steps": [
                    "1. Review request details",
                    "2. Assess resource availability",
                    "3. Evaluate feasibility",
                    "4. Prepare recommendation"
                ],
                "estimated_duration": "1 day",
                "estimated_cost": 10000,
                "resources_needed": ["Administrative review"],
                "risk_level": "low"
            })
        
        return plans


# Node function for LangGraph
def planner_node(state: DepartmentState) -> DepartmentState:
    """
    Planner node that uses LLM when available
    """
    planner = WaterPlannerWithLLM()
    result = planner.generate_plan(state)
    
    return {
        **state,
        "plan": result.get("primary_plan"),
        "alternative_plans": result.get("alternative_plans", []),
        "llm_used": result.get("llm_used", False)
    }
