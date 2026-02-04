"""
LLM-enabled planner for Health Agent. Uses `health_agent.config.settings` (HEALTH_ env
prefix) so the Health Agent can be configured independently from Water Agent.

This mirrors the behavior of the water planner but is fully self-contained.
"""

import logging
import json
import os
from typing import Dict, List

from ..config import settings

logger = logging.getLogger(__name__)


class HealthPlannerLLM:
    def __init__(self):
        self.llm_provider = settings.LLM_PROVIDER
        self.use_llm = self._check_llm_available()
        if self.use_llm:
            self._init_llm_client()

    def _check_llm_available(self) -> bool:
        openai_key = settings.OPENAI_API_KEY
        groq_key = settings.GROQ_API_KEY

        if self.llm_provider == "groq" and groq_key:
            logger.info("✓ HealthPlanner: Groq LLM configured")
            return True
        if self.llm_provider == "openai" and openai_key:
            logger.info("✓ HealthPlanner: OpenAI LLM configured")
            return True
        logger.warning("⚠️  HealthPlanner: No LLM configured, using deterministic fallback")
        return False

    def _init_llm_client(self):
        try:
            import openai
            if self.llm_provider == "groq":
                self.client = openai.OpenAI(api_key=settings.GROQ_API_KEY,
                                            base_url="https://api.groq.com/openai/v1")
                logger.info("✓ HealthPlanner: Groq client initialized")
            else:
                self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✓ HealthPlanner: OpenAI client initialized")
        except Exception as e:
            logger.error(f"✗ HealthPlanner: Failed to initialize LLM client: {e}")
            self.use_llm = False

    def generate_plan(self, state: Dict) -> Dict:
        logger.info("📋 [HEALTH NODE: Planner (LLM)]")
        intent = state.get("intent", "")
        goal = state.get("goal", "")
        context = state.get("context", {})
        input_event = state.get("input_event", {})

        if self.use_llm:
            plans = self._generate_llm_plans(intent, goal, context, input_event)
        else:
            plans = self._generate_deterministic_plans(intent, goal, context, input_event)

        return {
            "primary_plan": plans[0] if plans else None,
            "alternative_plans": plans[1:] if len(plans) > 1 else [],
            "total_plans": len(plans),
            "llm_used": self.use_llm,
        }

    def _build_prompt(self, intent: str, goal: str, context: Dict, input_event: Dict) -> str:
        return f"""You are a Public Health planning assistant for a municipal health department.

INTENT: {intent}
GOAL: {goal}

REQUEST:
{json.dumps(input_event, indent=2)}

CONTEXT SUMMARY:
- recent incidents: {len(context.get('disease_incidents', []))}
- vaccination campaigns: {len(context.get('vaccination_campaigns', []))}
- sanitation inspections: {len(context.get('sanitation_inspections', []))}

AVAILABLE TOOLS (use these exact names in steps):
- disease_surveillance_tool: Get disease incident data for location
- vaccination_status_tool: Check vaccination coverage in location
- sanitation_inspection_tool: Get sanitation inspection results
- mobile_unit_availability: Check available mobile health units
- public_messaging_capacity: Check public messaging capabilities

Produce 1-2 alternative plans as JSON with this structure:
{{"plans": [{{"name":"...","steps":[...],"estimated_duration":"X days","estimated_cost":0,"resources_needed":[],"risk_level":"low|medium|high"}}]}}
"""

    def _generate_llm_plans(self, intent: str, goal: str, context: Dict, input_event: Dict) -> List[Dict]:
        prompt = self._build_prompt(intent, goal, context, input_event)
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a municipal public health planner. Return only JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=800,
            )
            llm_output = response.choices[0].message.content
            # Clean markdown code fences like water planner
            llm_output_clean = llm_output.strip()
            if llm_output_clean.startswith("```json"):
                llm_output_clean = llm_output_clean[7:]
            elif llm_output_clean.startswith("```"):
                llm_output_clean = llm_output_clean[3:]
            if llm_output_clean.endswith("```"):
                llm_output_clean = llm_output_clean[:-3]
            parsed = json.loads(llm_output_clean.strip())
            return parsed.get("plans", [])
        except Exception as e:
            logger.error(f"✗ HealthPlanner LLM call failed: {e}")
            return self._generate_deterministic_plans(intent, goal, context, input_event)

    def _generate_deterministic_plans(self, intent: str, goal: str, context: Dict, input_event: Dict) -> List[Dict]:
        plans = []
        location = input_event.get("location", "Unknown")
        plans.append({
            "name": "Deploy sanitation + mobile clinic",
            "steps": [
                f"Increase street cleaning in {location}",
                f"Deploy mobile health unit to {location}",
                "Coordinate with sanitation department",
                "Launch public messaging campaign"
            ],
            "estimated_duration": "1-3 days",
            "estimated_cost": 12000,
            "resources_needed": ["mobile_unit", "sanitation_team", "messaging"],
            "risk_level": "medium"
        })
        return plans


# Thin wrapper used by LangGraph node
def health_planner_llm_node(state: Dict) -> Dict:
    planner = HealthPlannerLLM()
    result = planner.generate_plan(state)
    state["plan"] = result.get("primary_plan")
    state["alternative_plans"] = result.get("alternative_plans", [])
    state["llm_used"] = result.get("llm_used", False)
    return state


# Export a common name expected by other modules
health_planner_node = health_planner_llm_node
