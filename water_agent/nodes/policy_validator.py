"""
PHASE 10: Policy Validator Node (LLM-Enhanced)

Uses LLM to check policy compliance with nuanced understanding.
"""

import logging
import json

from ..state import DepartmentState
from ..rules.policy_rules import PolicyValidator
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)

# Compatibility alias for tests
_get_llm_client = get_llm_client


def policy_validator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 10: Policy Validator (LLM-Enhanced)
    
    Uses LLM to understand policy compliance with context awareness.
    """
    
    logger.info("📋 [NODE: Policy Validator]")
    
    try:
        intent = state.get("intent", "")
        input_event = state.get("input_event", {})
        observations = state.get("observations", {})
        plan = state.get("plan", {})
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for policy validation...")
            policy_ok, violations = _validate_with_llm(llm_client, intent, input_event, observations, plan)
            
            if policy_ok is not None:
                state["policy_ok"] = policy_ok
                state["policy_violations"] = violations
                logger.info(f"✓ LLM policy check: {'PASS' if policy_ok else 'FAIL'}")
                
                if not policy_ok:
                    state["escalate"] = True
                    state["escalation_reason"] = f"Policy violations: {'; '.join(violations)}"
                    logger.warning("⚠️ Policy violation - escalating")
                
                return state
        
        # Fallback to rules-based
        logger.info("Using rules-based fallback")
        validator = PolicyValidator()
        policy_ok, violations = validator.validate(intent, input_event, observations)
        
        state["policy_ok"] = policy_ok
        state["policy_violations"] = violations
        
        logger.info(f"→ Policy compliant: {policy_ok}")
        
        if violations:
            logger.warning(f"→ Violations: {len(violations)}")
            for v in violations:
                logger.warning(f"  - {v}")
        
        if not policy_ok:
            state["escalate"] = True
            state["escalation_reason"] = f"Policy violations: {'; '.join(violations)}"
            logger.warning("⚠️ Policy violation - escalating")
        
    except Exception as e:
        logger.error(f"✗ Policy validator error: {e}")
        state["policy_ok"] = False
        state["policy_violations"] = [f"Validation error: {str(e)}"]
    
    return state


def _validate_with_llm(client, intent: str, input_event: dict, observations: dict, plan: dict) -> tuple[bool, list]:
    """Use LLM to validate policy compliance"""
    try:
        policies = """
WATER DEPARTMENT POLICIES:
1. MAX_SHIFT_DELAY_DAYS = 3 (maximum allowed delay for shift assignments)
2. MIN_MAINTENANCE_NOTICE_HOURS = 24 (minimum notice for maintenance)
3. EMERGENCY_OVERRIDE_ALLOWED = True (emergencies can bypass certain rules)
4. MAX_BUDGET_OVERAGE_PERCENT = 10 (max budget overage allowed)
5. REQUIRE_SUPERVISOR_FOR_EMERGENCY = True (supervisor approval needed)
"""

        prompt = f"""Check if this plan complies with Water Department policies.

INTENT: {intent}
INPUT EVENT: {json.dumps(input_event, indent=2)}
OBSERVATIONS: {json.dumps(observations, indent=2)}
PLAN: {json.dumps(plan, indent=2)}

{policies}

Return ONLY valid JSON:
{{
  "policy_compliant": true/false,
  "violations": ["violation 1", "violation 2", ...],
  "warnings": ["warning 1", ...],
  "reasoning": "brief explanation"
}}

Be strict but context-aware. Consider emergency situations."""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department policy compliance AI. Evaluate plans against policies. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=500
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
        policy_ok = result.get("policy_compliant", False)
        violations = result.get("violations", [])
        
        return policy_ok, violations
        
    except Exception as e:
        logger.warning(f"LLM policy validation failed: {e}")
        return None, []
