"""Cost estimator (scaffold).

Aggregates proposed actions into a total estimated cost.
"""

from typing import Dict
from .llm_helper import get_llm_client
from finance_agent.config import settings
import logging
import json

logger = logging.getLogger(__name__)


def cost_estimator_node(state: Dict) -> Dict:
    """Estimate cost per proposed action. Use LLM for nuanced estimates, fallback to deterministic sums."""
    input_event = state.get("input_event", {})
    proposed = input_event.get("proposed_actions") or []

    # Direct provided estimate takes precedence
    if input_event.get("estimated_cost") is not None:
        total = float(input_event.get("estimated_cost"))
        state["cost_estimates"] = {"total_estimated_cost": total, "by_item": proposed}
        return state

    # Try LLM to estimate costs per item
    client = get_llm_client()
    if client and proposed:
        try:
            prompt = (
                "Estimate costs for the following proposed actions. Return JSON: {\"total_estimated_cost\": number, \"by_item\": [{\"name\":string, \"cost\":number}]}\n\n"
                f"ACTIONS: {json.dumps(proposed)}"
            )

            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a municipal finance cost estimator. Return only JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=400,
            )

            llm_output = resp.choices[0].message.content
            llm_text = llm_output.strip()
            if llm_text.startswith("```"):
                llm_text = llm_text.strip("`\n")

            parsed = json.loads(llm_text)
            parsed["total_estimated_cost"] = float(parsed.get("total_estimated_cost", 0))
            state["cost_estimates"] = parsed
            return state
        except Exception as e:
            logger.warning(f"LLM cost estimation failed, falling back: {e}")

    # Deterministic fallback: simple sum of provided item costs
    total = 0.0
    by_item = []
    for p in proposed:
        name = p.get("name") or p.get("id") or "item"
        try:
            cost = float(p.get("cost", 0))
        except Exception:
            cost = 0.0
        by_item.append({"name": name, "cost": cost})
        total += cost

    state["cost_estimates"] = {"total_estimated_cost": total, "by_item": by_item}
    return state
