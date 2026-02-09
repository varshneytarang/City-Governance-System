"""Load finance context (scaffold).

Populate `state['context']` with simple budget snapshot.
"""

from typing import Dict
from ..config import settings
from .llm_helper import get_llm_client
import logging
import json

logger = logging.getLogger(__name__)


def finance_context_loader(state: Dict) -> Dict:
    # Minimal context: budget totals and reserve percent
    state_context = state.get("context", {})
    state_context.update({
        "budget_total": float(settings.BUDGET_TOTAL),
        "reserve_percent": float(settings.MIN_RESERVE_PERCENT),
    })
    # If the agent provided a DB queries object (via state), prefer using it
    # to enrich context deterministically for integration tests.
    queries = state.get("queries")
    if queries:
        try:
            db_ctx = queries.fetch_budget_context(location=state.get("input_event", {}).get("location"))
            if db_ctx:
                state_context["budget_total"] = float(db_ctx.get("total_budget", state_context["budget_total"]))
                state_context["budget_summary"] = db_ctx
        except Exception as e:
            logger.warning(f"Finance context DB enrich failed: {e}")
    else:
        # Optionally enrich context with an LLM-generated summary
        client = get_llm_client()
        if client:
            try:
                prompt = (
                    f"Summarize this municipal finance context as JSON.\n"
                    f"BUDGET_TOTAL: {state_context['budget_total']}\n"
                    f"RESERVE_PERCENT: {state_context['reserve_percent']}\n\n"
                    "Return JSON: {\"summary\":string, \"confidence\":number}"
                )

                resp = client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a municipal finance assistant. Return only JSON."},
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
                state_context["summary"] = parsed.get("summary")
                state_context["summary_confidence"] = float(parsed.get("confidence", 0.0))
            except Exception as e:
                logger.warning(f"Finance context LLM enrich failed: {e}")

    state["context"] = state_context
    return state
