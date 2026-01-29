"""
PHASE 13: Decision Router

Route to recommend or escalate based on:
- confidence >= 0.7 → recommend
- confidence < 0.7 → escalate
- policy failed → escalate
- risk high → escalate
"""

import logging

from ..state import DepartmentState
from ..config import settings

logger = logging.getLogger(__name__)


def decision_router_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 13: Decision Router
    
    Rules:
    | Condition        | Outcome   |
    |------------------|-----------|
    | confidence ≥ 0.7 | recommend |
    | confidence < 0.7 | escalate  |
    | policy failed    | escalate  |
    | risk high        | escalate  |
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
            logger.info("  → Already marked for escalation")
            return state
        
        # Check each condition
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
        
        # ========== SET ROUTING DECISION ==========
        
        if should_escalate:
            logger.warning(f"⚠️  ESCALATE: {escalation_reason}")
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
