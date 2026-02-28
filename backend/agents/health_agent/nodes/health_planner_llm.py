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
        # Extract richer context details
        disease_incidents = context.get('disease_incidents', [])
        vaccination_campaigns = context.get('vaccination_campaigns', [])
        sanitation_inspections = context.get('sanitation_inspections', [])
        health_facilities = context.get('health_facilities', [])
        budget_info = context.get('budget_status', {})
        
        # Format critical incidents
        critical_incidents = [i for i in disease_incidents if i.get('severity') == 'critical']
        
        return f"""Generate a detailed operational plan for the Health Department.

INTENT: {intent}
GOAL: {goal}

REQUEST DETAILS:
{json.dumps(input_event, indent=2)}

CURRENT CONTEXT:
- Recent Disease Incidents: {len(disease_incidents)} ({len(critical_incidents)} critical)
- Active Vaccination Campaigns: {len(vaccination_campaigns)}
- Recent Sanitation Inspections: {len(sanitation_inspections)}
- Available Health Facilities: {len(health_facilities)}
- Budget Status: ${budget_info.get('available', 0):,}

AVAILABLE TOOLS (use these exact names in steps):
- disease_surveillance_tool: Get disease incident data for location
- vaccination_status_tool: Check vaccination coverage in location
- sanitation_inspection_tool: Get sanitation inspection results
- mobile_unit_availability: Check available mobile health units
- public_messaging_capacity: Check public messaging capabilities

REQUIREMENTS:
1. Generate 1-2 alternative plans
2. Each plan must include:
   - Clear step-by-step actions
   - Estimated duration
   - Resource requirements (staff, equipment, facilities)
   - Estimated costs
   - Health impact assessment
   - Risk level with justification

Return ONLY valid JSON following this structure:
{{
  "plans": [
    {{
      "name": "Plan A: Rapid Response",
      "steps": ["Step 1 description", "Step 2 description", ...],
      "estimated_duration": "2-3 days",
      "estimated_cost": 15000,
      "resources_needed": ["mobile unit", "5 health workers", "testing kits"],
      "risk_level": "medium",
      "health_impact": "High - immediate intervention",
      "pros": ["Fast deployment", "Targeted response"],
      "cons": ["Resource intensive"]
    }}
  ]
}}
"""

    def _generate_llm_plans(self, intent: str, goal: str, context: Dict, input_event: Dict) -> List[Dict]:
        prompt = self._build_prompt(intent, goal, context, input_event)
        try:
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a Health Department planning AI. Generate structured plans "
                            "for public health operations. Return ONLY valid JSON with this structure: "
                            '{"plans": [{"name": "Plan A", "steps": ["step1", "step2"], '
                            '"estimated_duration": "X days", "estimated_cost": 15000, '
                            '"resources_needed": ["resource1"], "risk_level": "medium", '
                            '"health_impact": "description"}]}'
                        )
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=1000,
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
        """Generate request-type specific fallback plans"""
        plans = []
        location = input_event.get("location", "Unknown")
        request_type = input_event.get("type", "")
        severity = input_event.get("severity", "medium")
        
        if "outbreak" in request_type.lower() or "disease" in request_type.lower():
            # Disease outbreak response
            plans.append({
                "name": "Disease Outbreak Response Protocol",
                "steps": [
                    f"Deploy rapid response team to {location}",
                    "Conduct disease surveillance and contact tracing",
                    "Set up mobile testing facility",
                    "Coordinate with epidemiology team",
                    "Launch public health advisory",
                    "Monitor outbreak evolution"
                ],
                "estimated_duration": "3-7 days",
                "estimated_cost": 25000,
                "resources_needed": ["mobile unit", "testing kits", "8-10 health workers", "contact tracing team"],
                "risk_level": severity,
                "health_impact": "High - Contains disease spread"
            })
        
        elif "vaccination" in request_type.lower() or "immunization" in request_type.lower():
            # Vaccination campaign
            plans.append({
                "name": "Vaccination Campaign Deployment",
                "steps": [
                    f"Schedule vaccination drive in {location}",
                    "Mobilize vaccination teams and supplies",
                    "Set up vaccination stations",
                    "Conduct community outreach",
                    "Monitor coverage and adverse events",
                    "Submit coverage reports"
                ],
                "estimated_duration": "5-10 days",
                "estimated_cost": 18000,
                "resources_needed": ["vaccine doses", "cold storage", "6 vaccinators", "registration staff"],
                "risk_level": "low",
                "health_impact": "High - Improves community immunity"
            })
        
        elif "inspection" in request_type.lower() or "sanitation" in request_type.lower():
            # Sanitation inspection
            plans.append({
                "name": "Sanitation Inspection and Remediation",
                "steps": [
                    f"Conduct sanitation inspection at {location}",
                    "Document violations and health hazards",
                    "Issue compliance notice to facility",
                    "Schedule follow-up inspection",
                    "Coordinate remediation with sanitation dept"
                ],
                "estimated_duration": "2-4 days",
                "estimated_cost": 8000,
                "resources_needed": ["inspection team", "testing equipment", "documentation tools"],
                "risk_level": "medium",
                "health_impact": "Medium - Prevents foodborne illness"
            })
        
        else:
            # Generic health response
            plans.append({
                "name": "Standard Health Response Plan",
                "steps": [
                    f"Assess health situation in {location}",
                    "Deploy mobile health unit",
                    "Coordinate with sanitation department",
                    "Launch public health messaging campaign",
                    "Monitor and report outcomes"
                ],
                "estimated_duration": "2-5 days",
                "estimated_cost": 12000,
                "resources_needed": ["mobile unit", "health workers", "messaging resources"],
                "risk_level": "medium",
                "health_impact": "Medium - Addresses health concern"
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
