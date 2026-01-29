"""
PHASE 10: Policy Validator Node

Ensure allowed by department rules.
"""

import logging

from ..state import DepartmentState
from ..rules.policy_rules import PolicyValidator

logger = logging.getLogger(__name__)


def policy_validator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 10: Policy Validator
    
    Purpose: Ensure allowed by department rules.
    
    Checks:
    - max delay allowed
    - service continuity
    - SOPs
    
    Output:
    - policy_ok: bool
    - policy_violations: list
    """
    
    logger.info("📋 [NODE: Policy Validator]")
    
    try:
        intent = state.get("intent", "")
        input_event = state.get("input_event", {})
        observations = state.get("observations", {})
        
        # Validate against policies
        validator = PolicyValidator()
        policy_ok, violations = validator.validate(intent, input_event, observations)
        
        state["policy_ok"] = policy_ok
        state["policy_violations"] = violations
        
        logger.info(f"  → Policy compliant: {policy_ok}")
        
        if violations:
            logger.warning(f"  → Violations: {len(violations)}")
            for v in violations:
                logger.warning(f"    - {v}")
        
        # If policy failed, escalate
        if not policy_ok:
            state["escalate"] = True
            state["escalation_reason"] = (
                f"Policy violations: {'; '.join(violations)}"
            )
            logger.warning(f"⚠️  Policy violation - escalating")
        
    except Exception as e:
        logger.error(f"✗ Policy validator error: {e}")
        state["policy_ok"] = False
        state["policy_violations"] = [f"Validation error: {str(e)}"]
    
    return state
