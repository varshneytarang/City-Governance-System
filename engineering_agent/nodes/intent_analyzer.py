"""
PHASE 4: Intent + Risk Analyzer Node

Classify the request and assess immediate risk using LLM.

Rule: If risk == high → escalate immediately.
"""

from typing import Dict, List
import logging
import json

from ..state import EngineeringState
from ..database import EngineeringDepartmentQueries
from ..tools import EngineeringDepartmentTools
from ..config import settings

logger = logging.getLogger(__name__)

# Initialize LLM client if available
def _get_llm_client():
    """Get LLM client for intent analysis"""
    try:
        if settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
            import openai
            return openai.OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
        elif settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            import openai
            return openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    except:
        return None
    return None


# Intent classification mapping
INTENT_MAPPING = {
    "schedule_shift_request": "negotiate_schedule",
    "emergency_response": "emergency_response",
    "maintenance_request": "coordinate_maintenance",
    "capacity_query": "assess_capacity",
    "incident_report": "respond_to_incident",
    "project_planning": "plan_project"
}


def intent_analyzer_node(state: EngineeringState, 
                        tools: EngineeringDepartmentTools) -> EngineeringState:
    """
    PHASE 4: Intent + Risk Analysis Node (LLM-Enhanced)
    
    Uses LLM to classify intent and assess risk, with deterministic fallback.
    """
    
    logger.info("🔍 [NODE: Intent + Risk Analysis]")
    
    try:
        input_event = state.get("input_event", {})
        request_type = input_event.get("type", "unknown")
        location = input_event.get("location")
        context = state.get("context", {})
        
        # Try LLM first
        llm_client = _get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for intent analysis...")
            llm_result = _analyze_with_llm(llm_client, input_event, context)
            
            if llm_result:
                intent = llm_result.get("intent", "unknown_request")
                risk_level = llm_result.get("risk_level", "low")
                safety_concerns = llm_result.get("safety_concerns", [])
                logger.info(f"  → LLM: {request_type} → Intent: {intent}, Risk: {risk_level}")
                
                return {
                    **state,
                    "intent": intent,
                    "risk_level": risk_level,
                    "safety_concerns": safety_concerns
                }
        
        # Fallback to deterministic
        logger.info("Using deterministic fallback")
        intent = INTENT_MAPPING.get(request_type, "unknown_request")
        logger.info(f"  → Request: {request_type} → Intent: {intent}")
        
        # ========== RISK ASSESSMENT ==========
        risk_level = "low"
        safety_concerns = []
        
        # Check 1: Location-based risk
        if context.get("is_high_risk_zone"):
            safety_concerns.append("Location is a known high-risk zone")
            risk_level = "high"
        
        # Check 2: Critical incidents
        critical_incidents = context.get("incident_severity", {}).get("critical", 0)
        if critical_incidents > 0:
            safety_concerns.append(f"Critical incidents in area: {critical_incidents}")
            risk_level = "critical"
        
        # Check 3: Pipeline status
        pipeline_status = context.get("pipelines_status", {})
        poor_pipelines = pipeline_status.get("poor", 0) + pipeline_status.get("critical", 0)
        if poor_pipelines > 0:
            safety_concerns.append(f"Infrastructure issues: {poor_pipelines} pipelines")
            if risk_level != "critical":
                risk_level = "high"
        
        # Check 4: Reservoir levels (drought conditions)
        avg_reservoir = context.get("avg_reservoir_level", 100)
        if avg_reservoir < 20:
            safety_concerns.append(f"Critical water shortage: {avg_reservoir:.1f}%")
            risk_level = "critical"
        elif avg_reservoir < 40:
            safety_concerns.append(f"Low water levels: {avg_reservoir:.1f}%")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 5: Emergency request type
        if request_type == "emergency_response":
            safety_concerns.append("Emergency request detected")
            if risk_level != "critical":
                risk_level = "high"
        
        # Check 6: Recent incidents in location
        recent_incidents = context.get("recent_incidents", 0)
        if recent_incidents > 5:
            safety_concerns.append(f"Multiple recent incidents: {recent_incidents}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 7: Budget constraints
        budget = context.get("budget", {})
        utilization = budget.get("utilization_percent", 0)
        if utilization > 90:
            safety_concerns.append(f"Budget nearly exhausted: {utilization:.1f}%")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 8: Assess zone risk using tools
        logger.info(f"  → Assessing zone risk for {location}")
        zone_risk_result = tools.assess_zone_risk(location) if location else {}
        zone_risk_level = zone_risk_result.get("risk_level", "low")
        
        # Escalate risk if tool reports high
        if zone_risk_level in ["high", "critical"]:
            for factor in zone_risk_result.get("contributing_factors", []):
                if factor not in safety_concerns:
                    safety_concerns.append(factor)
            if zone_risk_level == "critical":
                risk_level = "critical"
            elif zone_risk_level == "high" and risk_level != "critical":
                risk_level = "high"
        
        logger.info(f"  → Risk Level: {risk_level}")
        logger.info(f"  → Safety Concerns: {len(safety_concerns)}")
        
        # Update state
        state["intent"] = intent
        state["risk_level"] = risk_level
        state["safety_concerns"] = safety_concerns
        
        # ========== IMMEDIATE ESCALATION RULE ==========
        if risk_level == "critical":
            logger.warning(f"⚠️  CRITICAL RISK DETECTED - Automatic escalation")
            state["escalate"] = True
            state["escalation_reason"] = f"Critical risk level: {'; '.join(safety_concerns)}"
        
    except Exception as e:
        logger.error(f"✗ Intent analysis error: {e}")
        state["intent"] = "unknown"
        state["risk_level"] = "unknown"
        state["safety_concerns"] = [f"Analysis error: {str(e)}"]
    
    return state


def _analyze_with_llm(client, input_event: Dict, context: Dict) -> Dict:
    """Use LLM to analyze intent and assess risk"""
    try:
        prompt = f"""Analyze this Water Department request and classify its intent and risk level.

REQUEST:
{json.dumps(input_event, indent=2)}

CONTEXT:
- Active Projects: {len(context.get('active_projects', []))}
- Available Workers: {context.get('worker_info', {}).get('available_count', 'unknown')}
- High Risk Zone: {context.get('is_high_risk_zone', False)}
- Recent Incidents: {len(context.get('incidents', []))}

Return ONLY valid JSON with this exact structure:
{{
  "intent": "negotiate_schedule | emergency_response | coordinate_maintenance | assess_capacity | respond_to_incident | plan_project",
  "risk_level": "low | medium | high | critical",
  "safety_concerns": ["specific concern 1", "specific concern 2"],
  "reasoning": "brief explanation of the classification"
}}

Consider:
1. Emergency indicators (severity, incident type)
2. Location risk factors
3. Time constraints and urgency
4. Resource availability
5. Potential safety issues

Choose risk level:
- low: routine operation, no safety concerns
- medium: some complexity, manageable risks
- high: significant risks, careful planning needed
- critical: immediate safety threat, escalation required"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Water Department risk analysis AI. Analyze requests and classify intent and risk levels accurately. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=500
        )
        
        llm_output = response.choices[0].message.content
        logger.info(f"LLM output: {llm_output[:150]}...")
        
        # Clean JSON (handle markdown wrapping)
        llm_output_clean = llm_output.strip()
        if llm_output_clean.startswith("```json"):
            llm_output_clean = llm_output_clean[7:]
        elif llm_output_clean.startswith("```"):
            llm_output_clean = llm_output_clean[3:]
        if llm_output_clean.endswith("```"):
            llm_output_clean = llm_output_clean[:-3]
        
        # Parse JSON
        result = json.loads(llm_output_clean.strip())
        return result
        
    except json.JSONDecodeError as e:
        logger.warning(f"LLM returned invalid JSON: {e}")
        return None
    except Exception as e:
        logger.warning(f"LLM analysis failed: {e}")
        return None
