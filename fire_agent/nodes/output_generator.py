"""
PHASE 14: Output Generation Node

Generate either a recommendation or escalation request.
"""

import logging
import json

from ..state import DepartmentState

logger = logging.getLogger(__name__)


def output_generator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 14: Output Generation
    
    Generates final response in standardized format.
    """
    
    logger.info("📤 [NODE: Output Generator]")
    
    try:
        escalate = state.get("escalate", False)
        confidence = state.get("confidence", 0.0)
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        
        response = {}
        
        if escalate:
            # ESCALATION RESPONSE
            response = {
                "decision": "escalate",
                "reason": state.get("escalation_reason", "Escalation required"),
                "requires_human_review": True,
                "details": {
                    "feasible": feasible,
                    "policy_compliant": policy_ok,
                    "confidence": confidence,
                    "risk_level": state.get("risk_level", "unknown"),
                    "plan": state.get("plan", {})
                }
            }
            logger.info("  → Escalation response generated")
        
        else:
            # RECOMMENDATION RESPONSE
            response = {
                "decision": "recommend",
                "reasoning": f"All criteria satisfied. Confidence: {confidence:.2%}",
                "requires_human_review": False,
                "recommendation": {
                    "action": "proceed",
                    "plan": state.get("plan", {}),
                    "constraints": state.get("plan", {}).get("constraints", []),
                    "confidence": confidence
                },
                "details": {
                    "feasible": feasible,
                    "policy_compliant": policy_ok,
                    "risk_level": state.get("risk_level", "unknown"),
                    "feasibility_reason": state.get("feasibility_reason", ""),
                    "safety_concerns": state.get("safety_concerns", [])
                }
            }
            logger.info("  → Recommendation response generated")
        
        state["response"] = response
        
        # Log response
        logger.info(f"✓ Response ready")
        logger.info(f"  Decision: {response.get('decision')}")
        logger.info(f"  Confidence: {confidence:.2%}")
        
    except Exception as e:
        logger.error(f"✗ Output generator error: {e}")
        state["response"] = {
            "decision": "escalate",
            "reason": f"Output generation error: {str(e)}",
            "error": str(e)
        }
    
    return state
