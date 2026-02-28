"""
PHASE 11: Memory Logger Node

Persist decision trail to agent_decisions table.

This enables full audit trail.
"""

import logging
from datetime import datetime

from ..state import DepartmentState
from ..database import SanitationDepartmentQueries

logger = logging.getLogger(__name__)


def memory_logger_node(state: DepartmentState, queries: SanitationDepartmentQueries) -> DepartmentState:
    """
    PHASE 11: Memory Logger
    
    Purpose: Persist decision trail.
    
    Stores to agent_decisions table:
    - input
    - plan
    - feasibility
    - outcome
    
    This enables audit and historical analysis.
    """
    
    logger.info("💾 [NODE: Memory Logger]")
    
    try:
        # Build decision record
        decision_record = {
            "request_type": state.get("input_event", {}).get("type", "unknown"),
            "request_data": state.get("input_event", {}),
            "context": state.get("context", {}),
            "plan": state.get("plan", {}),
            "tool_results": state.get("tool_results", {}),
            "feasible": state.get("feasible", False),
            "feasibility_reason": state.get("feasibility_reason", ""),
            "policy_ok": state.get("policy_ok", False),
            "policy_violations": state.get("policy_violations", []),
            "confidence": state.get("confidence", 0.0),
            "confidence_factors": state.get("confidence_factors", {}),
            "decision": state.get("response", {}).get("decision", "escalate"),
            "reasoning": state.get("response", {}).get("reasoning", ""),
            "escalation_reason": state.get("escalation_reason"),
            "response": state.get("response", {}),
            "execution_time_ms": state.get("execution_time_ms", 0)
        }
        
        # Sanitizer to convert dates/decimals and non-JSON types
        def _sanitize(obj):
            from datetime import date, datetime
            from decimal import Decimal

            if obj is None:
                return None
            if isinstance(obj, (str, int, float, bool)):
                return obj
            if isinstance(obj, (date, datetime)):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                try:
                    return float(obj)
                except Exception:
                    return str(obj)
            if isinstance(obj, dict):
                return {k: _sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_sanitize(v) for v in obj]
            try:
                return str(obj)
            except Exception:
                return None

        # Sanitize record for DB insertion
        decision_record_sanitized = _sanitize(decision_record)

        # Log to database
        decision_id = queries.log_decision(decision_record_sanitized)
        
        state["decision_id"] = decision_id
        
        logger.info(f"✓ Decision logged: {decision_id}")
        
    except Exception as e:
        logger.error(f"✗ Memory logger error: {e}")
        state["decision_id"] = None
    
    return state
