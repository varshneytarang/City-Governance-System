"""
PHASE 4: Intent + Risk Analyzer Node

Classify the request and assess immediate risk using LLM.

Rule: If risk == high → escalate immediately.
"""

from typing import Dict, List
import logging
import json

from ..state import DepartmentState
from ..database import SanitationDepartmentQueries
from ..tools import SanitationDepartmentTools
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
    "route_change_request": "negotiate_route_change",
    "emergency_collection": "emergency_collection",
    "equipment_maintenance": "coordinate_maintenance",
    "schedule_adjustment": "adjust_schedule",
    "landfill_routing": "optimize_landfill_routing",
    "complaint_response": "respond_to_complaint",
    "capacity_assessment": "assess_capacity"
}


def intent_analyzer_node(state: DepartmentState, 
                        tools: SanitationDepartmentTools) -> DepartmentState:
    """
    PHASE 4: Intent + Risk Analysis Node (LLM-Enhanced)
    
    Uses LLM to classify intent and assess risk, with deterministic fallback.
    """
    
    logger.info("🔍 [NODE: Intent + Risk Analysis]")
    
    try:
        input_event = state.get("input_event", {})
        request_type = input_event.get("type", "unknown")
        location = input_event.get("location")
        route_id = input_event.get("route_id")
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
        
        # Check 1: Route delay risk
        routes = context.get("routes", [])
        delayed_routes = sum(1 for r in routes if r.get("days_delayed", 0) > 2)
        if delayed_routes > 3:
            safety_concerns.append(f"Multiple delayed routes: {delayed_routes}")
            risk_level = "high"
        
        # Check 2: Landfill capacity
        landfills = context.get("landfills", [])
        overloaded_landfills = sum(1 for l in landfills if l.get("capacity_utilization", 0) > 90)
        if overloaded_landfills > 0:
            safety_concerns.append(f"Landfill capacity critical: {overloaded_landfills} sites")
            if risk_level != "high":
                risk_level = "high"
        
        # Check 3: Truck availability
        trucks = context.get("trucks", [])
        available_trucks = sum(1 for t in trucks if t.get("status") == "available" and t.get("fuel_percent", 0) >= 25)
        if available_trucks < 2:
            safety_concerns.append(f"Low truck availability: {available_trucks}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 4: Recent complaints
        recent_complaints = context.get("recent_complaints", 0)
        if recent_complaints > 20:
            safety_concerns.append(f"High complaint volume: {recent_complaints}")
            if risk_level != "high":
                risk_level = "high"
        elif recent_complaints > 10:
            safety_concerns.append(f"Elevated complaints: {recent_complaints}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 5: Emergency request type
        if request_type == "emergency_collection":
            safety_concerns.append("Emergency collection request")
            if risk_level != "high":
                risk_level = "high"
        
        # Check 6: Overflowing bins
        bins = context.get("bins", [])
        critical_bins = sum(1 for b in bins if b.get("fill_level", 0) >= 95)
        if critical_bins > 5:
            safety_concerns.append(f"Critical bin overflow: {critical_bins} bins")
            risk_level = "critical"
        elif critical_bins > 2:
            safety_concerns.append(f"Bins near capacity: {critical_bins}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 7: Budget constraints
        budget = context.get("budget", {})
        utilization = budget.get("utilization_percent", 0)
        if utilization > 90:
            safety_concerns.append(f"Budget nearly exhausted: {utilization:.1f}%")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 8: Assess route/zone risk using tools
        if route_id:
            logger.info(f"  → Assessing route {route_id} delay")
            delay_result = tools.assess_collection_delay(route_id)
            delay_days = delay_result.get("days_delayed", 0)
            if delay_days > 3:
                safety_concerns.append(f"Route severely delayed: {delay_days} days")
                if risk_level != "critical":
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
        prompt = f"""Analyze this Sanitation Department request and classify its intent and risk level.

REQUEST:
{json.dumps(input_event, indent=2)}

CONTEXT:
- Active Routes: {len(context.get('routes', []))}
- Available Trucks: {sum(1 for t in context.get('trucks', []) if t.get('status') == 'available')}
- Recent Complaints: {context.get('recent_complaints', 0)}
- Critical Bins: {sum(1 for b in context.get('bins', []) if b.get('fill_level', 0) >= 95)}

Return ONLY valid JSON with this exact structure:
{{
  "intent": "negotiate_route_change | emergency_collection | coordinate_maintenance | adjust_schedule | optimize_landfill_routing | respond_to_complaint | assess_capacity",
  "risk_level": "low | medium | high | critical",
  "safety_concerns": ["specific concern 1", "specific concern 2"],
  "reasoning": "brief explanation of the classification"
}}

Consider:
1. Emergency indicators (overflowing bins, health hazards)
2. Route coverage and delays
3. Time constraints and urgency
4. Resource availability (trucks, workers, landfill capacity)
5. Public health and safety issues

Choose risk level:
- low: routine operation, no safety concerns
- medium: some complexity, manageable risks
- high: significant risks, careful planning needed
- critical: immediate health/safety threat, escalation required"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a Sanitation Department risk analysis AI. Analyze requests and classify intent and risk levels accurately. Always return valid JSON."
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
