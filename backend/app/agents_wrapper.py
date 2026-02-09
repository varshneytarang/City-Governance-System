import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def _import_agent_module(agent_id: str):
    """Try to import an agent package like `water_agent` or `fire_agent`.

    Returns the module package or raises ImportError.
    """
    module_name = f"{agent_id}_agent"
    try:
        module = __import__(module_name, fromlist=["*"])
        return module
    except Exception as e:
        logger.debug(f"Failed to import {module_name}: {e}")
        raise


def run_agent_sync(agent_id: str, input_event: Dict[str, Any]) -> Dict[str, Any]:
    """Run an agent synchronously and return a normalized DecisionResponse dict.

    Supports packages named `<agent>_agent` that expose a class with a `.decide()` method.
    Currently this will work with `water_agent` (WaterDepartmentAgent).
    """
    try:
        # Prefer explicit mapping for known agents
        if agent_id == "water":
            from agents.water_agent.agent import WaterDepartmentAgent

            agent = WaterDepartmentAgent()
            result = agent.decide(input_event)
            return result

        # Try dynamic import for other agent packages
        module = _import_agent_module(agent_id)

        # Heuristic: find any attribute ending with 'Agent' and instantiate
        agent_cls = None
        for name in dir(module):
            if name.lower().endswith("agent") and name[0].isupper():
                agent_cls = getattr(module, name)
                break

        if agent_cls is None:
            raise ImportError(f"No Agent class found in module {module.__name__}")

        agent = agent_cls()
        if hasattr(agent, "decide"):
            return agent.decide(input_event)
        elif hasattr(agent, "coordinate"):
            # some agents may expose `coordinate` for multi-agent input
            return agent.coordinate(input_event)
        else:
            raise AttributeError("Agent has no decide/coordinate method")

    except Exception as e:
        logger.exception("Agent execution failed")
        return {
            "decision": "error",
            "reason": str(e),
            "error": str(e),
            "confidence": 0.0,
        }
    finally:
        # Attempt to persist the decision for water agent and others via local storage if available
        try:
            from . import storage
            # only persist if result present and agent known
            if agent_id and isinstance(locals().get('result', None), dict):
                storage.log_decision(agent_id, input_event, locals().get('result'))
        except Exception:
            # non-fatal: storage is best-effort
            logger.debug("Local storage not available or failed to log decision")
