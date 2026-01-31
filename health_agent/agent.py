"""
Health Department Agent - Orchestrator (scaffold)

This is a lightweight scaffold that reuses `water_agent` patterns and imports
common utilities when appropriate. Nodes and rules are implemented in the
`health_agent.nodes` and `health_agent.rules` packages.
"""

import logging
from datetime import datetime
from typing import Dict

from langgraph.graph import StateGraph, START, END

# Reuse DepartmentState type from water_agent for compatibility
from water_agent.state import DepartmentState
from water_agent.config import settings as global_settings

from .nodes import (
    health_context_loader,
    health_risk_estimator,
    health_planner_node,
    health_policy_node,
    health_confidence_node,
    output_generator_node
)

logger = logging.getLogger(__name__)


class HealthDepartmentAgent:
    """Health Department Agent - scaffolding for the real implementation."""

    def __init__(self):
        self.settings = global_settings
        self.agent_version = "0.1-health"
        self.graph = self._build_graph()
        logger.info("✓ HealthDepartmentAgent initialized")

    def _build_graph(self):
        builder = StateGraph(DepartmentState)

        builder.add_node("health_context_loader", health_context_loader)
        builder.add_node("health_risk_estimator", health_risk_estimator)
        builder.add_node("health_planner", health_planner_node)
        builder.add_node("health_policy", health_policy_node)
        builder.add_node("health_confidence", health_confidence_node)
        builder.add_node("output_generator", output_generator_node)

        # Wiring
        builder.add_edge(START, "health_context_loader")
        builder.add_edge("health_context_loader", "health_risk_estimator")
        builder.add_edge("health_risk_estimator", "health_planner")
        builder.add_edge("health_planner", "health_policy")
        builder.add_edge("health_policy", "health_confidence")
        builder.add_edge("health_confidence", "output_generator")
        builder.add_edge("output_generator", END)

        return builder.compile()

    def decide(self, request: Dict) -> Dict:
        start_time = datetime.now()

        initial_state: DepartmentState = {
            "input_event": request,
            "context": {},
            "intent": "",
            "risk_level": "low",
            "goal": "",
            "plan": {},
            "alternative_plans": [],
            "tool_results": {},
            "observations": {},
            "feasible": False,
            "policy_ok": False,
            "confidence": 0.0,
            "response": {},
            "escalate": False,
            "attempts": 0,
            "max_attempts": self.settings.MAX_PLANNING_ATTEMPTS,
            "started_at": start_time,
            "completed_at": None,
            "agent_version": self.agent_version,
            "execution_time_ms": 0,
        }

        result = self.graph.invoke(initial_state)
        result["completed_at"] = datetime.now()
        result["execution_time_ms"] = int((result["completed_at"] - start_time).total_seconds() * 1000)

        return result.get("response", {})

    def close(self):
        logger.info("✓ HealthDepartmentAgent closed")
