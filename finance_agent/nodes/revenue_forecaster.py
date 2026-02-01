"""Revenue forecaster (scaffold).

Simple deterministic forecasting based on a percentage of budget.
"""

from typing import Dict
from .llm_helper import get_llm_client
from finance_agent.config import settings
import logging
import json

logger = logging.getLogger(__name__)


def revenue_forecaster_node(state: Dict) -> Dict:
    """Generate a revenue forecast. Use LLM if available, otherwise deterministic fallback."""
    context = state.get("context", {})
    budget_total = context.get("budget_total", 0)

    # Try LLM
    client = get_llm_client()
    if client:
        try:
            prompt = f"""You are a municipal finance forecaster.

CURRENT BUDGET: {float(budget_total)}

Produce a JSON object with the field `next_period_revenue` (number) and `method` (string).
Return only JSON."""

            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a municipal finance forecasting assistant. Return only JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=settings.LLM_TEMPERATURE,
                max_tokens=200,
            )

            llm_output = resp.choices[0].message.content
            llm_text = llm_output.strip()
            if llm_text.startswith("```"):
                llm_text = llm_text.strip("`\n")

            parsed = json.loads(llm_text)
            # ensure numeric
            parsed["next_period_revenue"] = float(parsed.get("next_period_revenue", 0))
            state["revenue_forecast"] = parsed
            return state

        except Exception as e:
            logger.warning(f"LLM revenue forecast failed, falling back: {e}")

    # Deterministic fallback
    forecast = {"next_period_revenue": float(budget_total) * 0.10, "method": "simple_percent"}
    state["revenue_forecast"] = forecast
    return state
