"""Budget feasibility evaluator (scaffold)."""

from typing import Dict
from ..tools import create_tools
from ..config import settings
from .llm_helper import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)


def budget_feasibility_node(state: Dict) -> Dict:
    tools = create_tools(settings)
    estimates = state.get("cost_estimates", {})
    total = float(estimates.get("total_estimated_cost", 0))

    # Basic budget check via tools
    budget_check = tools.check_budget_availability(total)
    state["fiscal_feasible"] = budget_check.get("can_afford", False)
    state["fiscal_impact"] = {
        "total_budget": budget_check.get("total_budget"),
        "remaining": budget_check.get("remaining"),
        "estimated_cost": total,
    }

    # Use LLM for advanced suggestions if available
    client = get_llm_client()
    if client:
        try:
            prompt = (
                "Given the current budget and estimated cost, suggest funding strategies or reallocations. Return JSON: {\"can_afford\":bool, \"recommendations\": [string], \"reasoning\": string}.\n"
                f"BUDGET: {budget_check}\nESTIMATED_COST: {total}"
            )

            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a municipal finance advisor. Return only JSON."},
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
            # Merge results
            state["fiscal_feasible"] = bool(parsed.get("can_afford", state.get("fiscal_feasible", False)))
            recs = parsed.get("recommendations", []) or []
            state["recommendations"] = recs
            state["fiscal_reasoning"] = parsed.get("reasoning")
            return state

        except Exception as e:
            logger.warning(f"LLM budget feasibility check failed, using basic checks: {e}")

    # Deterministic fallback recommendations
    if not state["fiscal_feasible"]:
        state["recommendations"] = [
            "Consider phasing the project",
            "Reallocate non-essential funds",
            "Request external funding or escalate"
        ]

    return state
