"""
PHASE 13: Decision Router (LLM-Enhanced)

Uses LLM to make intelligent routing decisions.
"""

import logging
import json

from ..state import DepartmentState
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)

# Compatibility alias for tests
_get_llm_client = get_llm_client


def decision_router_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 13: Decision Router (LLM-Enhanced)
    
    Uses LLM to intelligently route to RECOMMEND or ESCALATE.
    """
    
    logger.info("🔀 [NODE: Decision Router]")
    
    try:
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        confidence = state.get("confidence", 0.0)
        risk_level = state.get("risk_level", "low")
        escalate_flag = state.get("escalate", False)
        
        # Already escalated?
        if escalate_flag:
            logger.info("→ Already marked for escalation")
            return state
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for routing decision...")
            should_escalate, reason = _route_with_llm(
                llm_client, feasible, policy_ok, confidence, 
                risk_level, state
            )
            
            if should_escalate is not None:
                if should_escalate:
                    logger.warning(f"⚠️ ESCALATE: {reason}")
                    state["escalate"] = True
                    state["escalation_reason"] = reason
                else:
                    logger.info("✓ RECOMMEND: All checks passed")
                    state["escalate"] = False
                return state
        
        # Fallback to rules-based
        logger.info("Using rules-based fallback")
        should_escalate = False
        escalation_reason = None
        
        # Rule 1: Policy compliance
        if not policy_ok:
            should_escalate = True
            escalation_reason = "Policy violations detected"
        
        # Rule 2: High risk
        elif risk_level in ["high", "critical"]:
            should_escalate = True
            escalation_reason = f"Risk level too high: {risk_level}"
        
        # Rule 3: Confidence threshold
        threshold = settings.CONFIDENCE_THRESHOLD
        if confidence < threshold:
            should_escalate = True
            escalation_reason = f"Confidence {confidence:.2f} below threshold {threshold}"
        
        # Rule 4: Not feasible
        elif not feasible:
            should_escalate = True
            escalation_reason = state.get("feasibility_reason", "Plan not feasible")
        
        if should_escalate:
            logger.warning(f"⚠️ ESCALATE: {escalation_reason}")
            state["escalate"] = True
            state["escalation_reason"] = escalation_reason
        else:
            logger.info("✓ RECOMMEND: All checks passed")
            state["escalate"] = False
        
    except Exception as e:
        logger.error(f"✗ Decision router error: {e}")
        state["escalate"] = True
        state["escalation_reason"] = f"Router error: {str(e)}"
    
    return state


def _route_with_llm(client, feasible: bool, policy_ok: bool, confidence: float,
                    risk_level: str, state: dict) -> tuple[bool, str]:
    """Use LLM to make routing decision"""
    try:
        prompt = f"""Make a routing decision for this Water Department case.

FEASIBLE: {feasible}
POLICY COMPLIANT: {policy_ok}
CONFIDENCE: {confidence:.2f} (threshold: {settings.CONFIDENCE_THRESHOLD})
RISK LEVEL: {risk_level}

FULL STATE CONTEXT:
{json.dumps({k: v for k, v in state.items() if k not in ['messages', 'tool_results']}, indent=2, default=str)}

Return ONLY valid JSON:
{{
  "decision": "RECOMMEND" or "ESCALATE",
  "reasoning": "brief explanation",
  "confidence_in_decision": 0.95
}}

ESCALATE if:
- Policy violations exist
- Risk is high/critical
- Confidence < {settings.CONFIDENCE_THRESHOLD}
- Not feasible
- Any safety concerns

RECOMMEND if:
- All checks pass
- Confidence >= {settings.CONFIDENCE_THRESHOLD}
- Low/medium risk
- Feasible and policy compliant"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department routing AI. Decide RECOMMEND vs ESCALATE. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startswith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        result = json.loads(llm_output.strip())
        decision = result.get("decision", "ESCALATE").upper()
        reasoning = result.get("reasoning", "LLM routing decision")
        
        should_escalate = (decision == "ESCALATE")
        
        return should_escalate, reasoning
        
    except Exception as e:
        logger.warning(f"LLM routing failed: {e}")
        return None, ""
