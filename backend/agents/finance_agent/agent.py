"""Finance Department Agent - scaffolded implementation."""

import logging
from datetime import datetime
from typing import Dict

from .config import settings
from .state import FinanceAgentState
from .tools import create_tools
from .database import get_finance_queries
from .nodes.finance_context_loader import finance_context_loader
from .nodes.revenue_forecaster import revenue_forecaster_node
from .nodes.cost_estimator import cost_estimator_node
from .nodes.coordination_checkpoint import coordination_checkpoint_node
from .nodes.budget_feasibility import budget_feasibility_node
from .nodes.policy_validator import policy_validator_node
from .nodes.output_generator import output_generator_node

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

        state: FinanceAgentState = {
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
            # Proactive coordination fields
            "coordination_check": None,
            "coordination_approved": False,
            "coordination_recommendations": [],
        }

        # Sequential pipeline with proactive coordination checkpoint
        # (context -> forecast -> cost -> COORDINATION -> feasibility -> policy -> output)
        try:
            state = finance_context_loader(state)
            state = revenue_forecaster_node(state)
            state = cost_estimator_node(state)
            
            # Proactive coordination checkpoint
            state = coordination_checkpoint_node(state)
            
            # Check if we should escalate based on coordination
            if state.get("escalate"):
                end_time = datetime.now()
                state["completed_at"] = end_time.isoformat()
                state["execution_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
                if "started_at" in state and isinstance(state["started_at"], datetime):
                    state["started_at"] = state["started_at"].isoformat()
                return state.get("response", {
                    "decision": "escalate",
                    "reason": state.get("escalation_reason", "Coordination required human intervention"),
                    "coordination_check": state.get("coordination_check"),
                    "execution_time_ms": state["execution_time_ms"]
                })
            
            state = budget_feasibility_node(state)
            state = policy_validator_node(state)
            state = output_generator_node(state)

            end_time = datetime.now()
            state["completed_at"] = end_time.isoformat()
            state["execution_time_ms"] = int((end_time - start_time).total_seconds() * 1000)
            if "started_at" in state and isinstance(state["started_at"], datetime):
                state["started_at"] = state["started_at"].isoformat()

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
