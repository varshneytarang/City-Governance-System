"""
PHASE 9: Feasibility Evaluator Node

MOST IMPORTANT: Decide if plan is feasible — deterministically.

NOT an agent. NOT an LLM. Pure Python rules.
"""

import logging

from ..state import EngineeringState
from ..rules.feasibility_rules import FeasibilityEvaluator

logger = logging.getLogger(__name__)


def feasibility_evaluator_node(state: EngineeringState) -> EngineeringState:
    """
    PHASE 9: Feasibility Evaluator
    
    Purpose: Decide if plan is feasible — deterministically.
    
    NOT an agent. NOT an LLM. Pure Python rules.
    
    This is the most important validation step.
    """
    
    logger.info("⚖️  [NODE: Feasibility Evaluator]")
    
    try:
        intent = state.get("intent", "")
        observations = state.get("observations", {})
        input_event = state.get("input_event", {})
        attempts = state.get("attempts", 0)
        max_attempts = state.get("max_attempts", 3)
        
        # Evaluate feasibility using rules
        evaluator = FeasibilityEvaluator()
        feasible, reason, details = evaluator.evaluate(intent, observations, input_event)
        
        # Update state
        state["feasible"] = feasible
        state["feasibility_reason"] = reason
        state["feasibility_details"] = details
        
        logger.info(f"  → Feasible: {feasible}")
        logger.info(f"  → Reason: {reason}")
        
        # ========== LOOP CONTROL ==========
        
        if feasible:
            logger.info(f"✓ Plan is feasible - proceeding")
        else:
            logger.warning(f"✗ Plan not feasible")
            
            # Try alternatives if available
            alternatives = state.get("alternative_plans", [])
            attempts = state.get("attempts", 0)
            
            if attempts < max_attempts and alternatives:
                logger.info(f"  → Trying alternative plan ({attempts + 1}/{max_attempts})")
                
                # Switch to next alternative plan
                state["attempts"] = attempts + 1
                state["plan"] = alternatives[0]
                state["alternative_plans"] = alternatives[1:]
                
                # Mark this as requiring retry
                state["retry_needed"] = True
                
            elif attempts >= max_attempts:
                logger.warning(f"✗ Max retry attempts ({max_attempts}) reached")
                state["escalate"] = True
                state["escalation_reason"] = f"No feasible plan found after {max_attempts} attempts"
    
    except Exception as e:
        logger.error(f"✗ Feasibility evaluator error: {e}")
        state["feasible"] = False
        state["feasibility_reason"] = f"Evaluation error: {str(e)}"
        state["feasibility_details"] = {"error": str(e)}
    
    return state
