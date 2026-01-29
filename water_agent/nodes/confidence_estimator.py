"""
PHASE 12: Confidence Estimator Node

Quantify uncertainty.
"""

import logging

from ..state import DepartmentState
from ..rules.confidence_calculator import ConfidenceCalculator

logger = logging.getLogger(__name__)


def confidence_estimator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 12: Confidence Estimator
    
    Purpose: Quantify uncertainty.
    
    Based on:
    - data completeness
    - risk level
    - number of retries
    - feasibility
    - policy compliance
    """
    
    logger.info("🎯 [NODE: Confidence Estimator]")
    
    try:
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        risk_level = state.get("risk_level", "low")
        attempts = state.get("attempts", 0)
        observations = state.get("observations", {})
        feasibility_details = state.get("feasibility_details", {})
        
        # Calculate confidence
        calculator = ConfidenceCalculator()
        confidence, factors = calculator.calculate(
            feasible=feasible,
            policy_ok=policy_ok,
            risk_level=risk_level,
            attempts=attempts,
            observations=observations,
            feasibility_details=feasibility_details
        )
        
        state["confidence"] = confidence
        state["confidence_factors"] = factors
        
        logger.info(f"  → Confidence: {confidence:.2f} (0.0-1.0)")
        logger.info(f"    Feasibility: +{factors.get('feasibility', 0):.2f}")
        logger.info(f"    Policy: +{factors.get('policy_compliance', 0):.2f}")
        logger.info(f"    Risk: {factors.get('risk_level', 0):+.2f}")
        logger.info(f"    Data: {factors.get('data_completeness', 0):+.2f}")
        
    except Exception as e:
        logger.error(f"✗ Confidence estimator error: {e}")
        state["confidence"] = 0.0
        state["confidence_factors"] = {"error": str(e)}
    
    return state
