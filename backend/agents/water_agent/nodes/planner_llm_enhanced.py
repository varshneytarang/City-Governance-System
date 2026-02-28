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
        print("="*60)
        print("🛠️ WATER PLANNER INITIALIZATION")
        print("="*60)
        self.llm_provider = settings.LLM_PROVIDER
        print(f"📌 LLM Provider: {self.llm_provider}")
        print(f"📌 LLM Model: {settings.LLM_MODEL}")
        print(f"📌 Temperature: {settings.LLM_TEMPERATURE}")
        
        self.use_llm = self._check_llm_available()
        print(f"📌 Will use LLM: {self.use_llm}")
        
        if self.use_llm:
            self._init_llm_client()
        else:
            print("⚠️  Using DETERMINISTIC FALLBACK mode")
        print("="*60)
    
    def _check_llm_available(self) -> bool:
        """Check if LLM is configured"""
        openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
        groq_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
        
        if self.llm_provider == "openai" and openai_key:
            logger.info("✓ OpenAI LLM configured")
            return True
        elif self.llm_provider == "groq" and groq_key:
            logger.info("✓ Groq LLM configured")
            return True
        else:
            logger.warning("⚠️  No LLM configured, using deterministic fallback")
            logger.warning(f"   Provider: {self.llm_provider}")
            logger.warning(f"   GROQ_API_KEY from env: {'Set' if os.getenv('GROQ_API_KEY') else 'Not set'}")
            logger.warning(f"   GROQ_API_KEY from settings: {'Set' if settings.GROQ_API_KEY else 'Not set'}")
            return False
    
    def _init_llm_client(self):
        """Initialize LLM client (OpenAI or Groq)"""
        try:
            if self.llm_provider == "groq":
                # Groq uses OpenAI-compatible API
                import openai
                groq_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
                self.client = openai.OpenAI(
                    api_key=groq_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                logger.info("✓ Groq client initialized")
            else:
                # Standard OpenAI
                import openai
                openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
                self.client = openai.OpenAI(api_key=openai_key)
                logger.info("✓ OpenAI client initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize LLM client: {e}")
            self.use_llm = False
    
    def generate_plan(self, state: DepartmentState) -> Dict:
        """
        PHASE 6: Planner Node (LLM)
        
        This version ACTUALLY calls your LLM API!
        """
        
        print("\n" + "="*60)
        print("📋 [WATER PLANNER - GENERATING PLAN]")
        print("="*60)
        
        try:
            goal = state.get("goal", "")
            intent = state.get("intent", "")
            context = state.get("context", {})
            input_event = state.get("input_event", {})
            
            print(f"📥 Input Event: {json.dumps(input_event, indent=2)}")
            print(f"🎯 Goal: {goal}")
            print(f"💡 Intent: {intent}")
            print(f"📊 Context Keys: {list(context.keys())}")
            print(f"🤖 Use LLM: {self.use_llm}")
            
            if self.use_llm:
                # 🔥 ACTUAL LLM CALL HERE 🔥
                print("\n🔥 CALLING LLM API...")
                print(f"   Provider: {self.llm_provider}")
                print(f"   Model: {self._get_model_name()}")
                plans = self._generate_llm_plans(
                    intent=intent,
                    goal=goal,
                    context=context,
                    input_event=input_event
                )
                print("✅ LLM response received and parsed")
            else:
                # Fallback to deterministic
                print("⚠️  Using deterministic fallback (no LLM)")
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
        
        print("\n" + "-"*60)
        print("🔮 Building LLM Prompt...")
        # Build prompt for LLM
        prompt = self._build_planning_prompt(intent, goal, context, input_event)
        print(f"📝 Prompt length: {len(prompt)} characters")
        print(f"📝 Prompt preview:\n{prompt[:300]}...")
        
        try:
            print("\n🌐 Making API call to LLM...")
            print(f"   Client type: {type(self.client)}")
            print(f"   Model: {self._get_model_name()}")
            print(f"   Temperature: {settings.LLM_TEMPERATURE}")
            
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
            print("\n✅ LLM API call successful!")
            print(f"📤 Raw LLM output ({len(llm_output)} chars):\n{llm_output[:500]}...")
            
            # Clean markdown code fences (LLMs often wrap JSON in ```json ... ```)
            print("\n🧹 Cleaning markdown code fences...")
            llm_output_clean = llm_output.strip()
            if llm_output_clean.startswith("```json"):
                print("   Removed ```json prefix")
                llm_output_clean = llm_output_clean[7:]
            elif llm_output_clean.startswith("```"):
                print("   Removed ``` prefix")
                llm_output_clean = llm_output_clean[3:]
            if llm_output_clean.endswith("```"):
                print("   Removed ``` suffix")
                llm_output_clean = llm_output_clean[:-3]
            llm_output_clean = llm_output_clean.strip()
            print(f"📤 Cleaned output ({len(llm_output_clean)} chars)")
            
            # Parse JSON response
            try:
                print("\n🔍 Parsing JSON...")
                parsed = json.loads(llm_output_clean)
                plans = parsed.get("plans", [])
                print(f"✅ JSON parsed successfully! Found {len(plans)} plan(s)")
                
                if plans:
                    for i, plan in enumerate(plans):
                        print(f"\n   Plan {i+1}: {plan.get('name', 'Unnamed')}")
                        print(f"      Steps: {len(plan.get('steps', []))}")
                        print(f"      Duration: {plan.get('estimated_duration', 'N/A')}")
                        print(f"      Cost: ${plan.get('estimated_cost', 0):,}")
                
                if not plans:
                    print("⚠️  LLM returned no plans, using fallback")
                    return self._generate_deterministic_plans(intent, goal, context, input_event)
                
                return plans
            
            except json.JSONDecodeError as e:
                print(f"❌ JSON PARSE ERROR: {e}")
                print(f"   Failed to parse: {llm_output_clean[:200]}...")
                print("🔄 Falling back to deterministic plans")
                # Fallback to deterministic
                return self._generate_deterministic_plans(intent, goal, context, input_event)
        
        except Exception as e:
            print(f"❌ LLM API CALL FAILED: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            print("🔄 Falling back to deterministic plans")
            # Fallback to deterministic
            return self._generate_deterministic_plans(intent, goal, context, input_event)
    
    def _get_model_name(self) -> str:
        """Get the appropriate model name for the provider"""
        if self.llm_provider == "groq":
            # Groq models: llama3-70b-8192, llama-3.3-70b-versatile, mixtral-8x7b-32768
            return os.getenv("LLM_MODEL") or settings.LLM_MODEL
        else:
            # OpenAI models
            return os.getenv("LLM_MODEL") or settings.LLM_MODEL
    
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
