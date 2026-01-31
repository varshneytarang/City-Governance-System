"""Compose final finance response (scaffold)."""

from typing import Dict
from .llm_helper import get_llm_client
from finance_agent.config import settings
import logging
import json

logger = logging.getLogger(__name__)


def output_generator_node(state: Dict) -> Dict:
    estimates = state.get("cost_estimates", {})
    fiscal = state.get("fiscal_impact", {})
    recommendations = state.get("recommendations", [])

    # Basic response
    response = {
        "decision": "approve" if state.get("fiscal_feasible") and state.get("policy_ok", True) else "escalate",
        "fiscal_feasible": state.get("fiscal_feasible", False),
        "cost_summary": {
            "total_estimated_cost": estimates.get("total_estimated_cost", 0),
            "by_item": estimates.get("by_item", [])
        },
        "fiscal_impact": fiscal,
        "recommendations": recommendations,
        "confidence": 0.75 if state.get("fiscal_feasible") else 0.4,
        "escalate": state.get("escalate", False),
        "escalation_reason": state.get("escalation_reason")
    }

    # Optionally ask LLM to produce a polished summary and confidence
    client = get_llm_client()
    if client:
        try:
            # build the input state JSON separately to avoid f-string parsing issues
            input_state = {
                'decision': response['decision'],
                'cost_summary': response['cost_summary'],
                'fiscal_impact': response['fiscal_impact'],
                'recommendations': response['recommendations']
            }
            json_state = json.dumps(input_state)
            prompt = (
                "Produce a concise JSON summary for this finance decision with keys: summary (string), confidence (number), recommended_actions (list).\n\n"
                + "INPUT_STATE: "
                + json_state
            )

            resp = client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a municipal finance communicator. Return only JSON."},
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
            response["summary"] = parsed.get("summary")
            response["confidence"] = float(parsed.get("confidence", response.get("confidence", 0.5)))
            response["recommended_actions"] = parsed.get("recommended_actions", response.get("recommendations", []))

        except Exception as e:
            logger.warning(f"LLM output generation failed, using basic response: {e}")

    state["response"] = response
    return state
