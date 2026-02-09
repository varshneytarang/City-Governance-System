"""Finance policy validator (scaffold).

Deterministic rule: do not exceed 90% of budget without escalation.
"""

from typing import Dict
from ..config import settings
from .llm_helper import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)


def policy_validator_node(state: Dict) -> Dict:
    """Validate finance policy. Prefer LLM for nuanced assessment; fallback to simple deterministic rule."""
    estimates = state.get("cost_estimates", {})
    total = float(estimates.get("total_estimated_cost", 0))
    budget = float(settings.BUDGET_TOTAL)

    # Try LLM-based validation
    client = get_llm_client()
    if client:
        try:
            policies = (
                "FINANCE POLICIES:\n"
                "1. DO NOT EXCEED BUDGET WITHOUT APPROVAL.\n"
                "2. MAINTAIN MIN_RESERVE_PERCENT as reserves.\n"
                "3. FLAG ANY EARMARK VIOLATIONS.\n"
            )

            prompt = f"""Check if this proposed financial plan complies with policies.

INPUT:
ESTIMATED_TOTAL: {total}
CURRENT_BUDGET: {budget}
POLICIES:
{policies}

Return ONLY JSON with keys: policy_compliant (true/false), violations (list), warnings (list), reasoning (string)."""

            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a municipal finance policy compliance checker. Return only JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=300,
            )

            llm_output = resp.choices[0].message.content
            llm_text = llm_output.strip()
            if llm_text.startswith("```"):
                llm_text = llm_text.strip("`\n")

            parsed = json.loads(llm_text)
            policy_ok = bool(parsed.get("policy_compliant", False))
            violations = parsed.get("violations", []) or []

            state["policy_ok"] = policy_ok
            state["policy_violations"] = violations

            if not policy_ok:
                state["escalate"] = True
                state["escalation_reason"] = parsed.get("reasoning", "Policy violation")

            return state

        except Exception as e:
            logger.warning(f"LLM policy validation failed, falling back: {e}")

    # Deterministic fallback
    violations = []
    policy_ok = True
    if total > budget * 0.90:
        violations.append("Estimated cost exceeds 90% of budget")
        policy_ok = False

    state["policy_ok"] = policy_ok
    state["policy_violations"] = violations

    if not policy_ok:
        state["escalate"] = True
        state["escalation_reason"] = "; ".join(violations)

    return state
