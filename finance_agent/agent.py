"""Finance Department Agent - scaffolded implementation."""

import logging
from datetime import datetime
from typing import Dict

from finance_agent.config import settings
from finance_agent.tools import create_tools
from finance_agent.database import get_finance_queries
from finance_agent.nodes.finance_context_loader import finance_context_loader
from finance_agent.nodes.revenue_forecaster import revenue_forecaster_node
from finance_agent.nodes.cost_estimator import cost_estimator_node
from finance_agent.nodes.budget_feasibility import budget_feasibility_node
from finance_agent.nodes.policy_validator import policy_validator_node
from finance_agent.nodes.output_generator import output_generator_node

logger = logging.getLogger(__name__)


class FinanceDepartmentAgent:
    """Finance Agent with DB/LLM integration (mirrors water_agent pattern)."""

    def __init__(self):
        self.settings = settings
        self.tools = create_tools(settings)
        self.queries = get_finance_queries()
        self.agent_version = "0.2-finance"
        logger.info("✓ FinanceDepartmentAgent initialized")

    def decide(self, request: Dict) -> Dict:
        start_time = datetime.now()

        state = {
            "input_event": request,
            "context": {},
            "revenue_forecast": {},
            "cost_estimates": {},
            "fiscal_feasible": False,
            "policy_ok": True,
            "response": {},
            "escalate": False,
            "escalation_reason": None,
            "started_at": start_time,
            "completed_at": None,
            "agent_version": self.agent_version,
            "execution_time_ms": 0,
            "queries": self.queries,  # Pass DB queries to nodes if needed
        }

        # Sequential pipeline (context -> forecast -> cost -> feasibility -> policy -> output)
        try:
            state = finance_context_loader(state)
            state = revenue_forecaster_node(state)
            state = cost_estimator_node(state)
            state = budget_feasibility_node(state)
            state = policy_validator_node(state)
            state = output_generator_node(state)

            state["completed_at"] = datetime.now()
            state["execution_time_ms"] = int((state["completed_at"] - start_time).total_seconds() * 1000)

            return state.get("response", {})

        except Exception as e:
            logger.error(f"Finance agent error: {e}", exc_info=True)
            return {
                "decision": "escalate",
                "reason": str(e),
                "execution_time_ms": int((datetime.now() - start_time).total_seconds() * 1000)
            }

    def close(self):
        self.queries.close()
        logger.info("✓ FinanceDepartmentAgent closed")
