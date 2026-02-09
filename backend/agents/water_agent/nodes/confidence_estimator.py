"""
PHASE 12: Confidence Estimator Node (LLM-Enhanced)

Uses LLM to assess confidence with nuanced understanding of risk factors.
"""

import logging
import json

from ..state import DepartmentState
from ..rules.confidence_calculator import ConfidenceCalculator
from ..config import settings
from .llm_helper import get_llm_client

logger = logging.getLogger(__name__)

# Compatibility alias for tests
_get_llm_client = get_llm_client


def confidence_estimator_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 12: Confidence Estimator (LLM-Enhanced)
    
    Uses LLM to assess confidence with nuanced risk understanding.
    """
    
    logger.info("🎯 [NODE: Confidence Estimator]")
    
    try:
        feasible = state.get("feasible", False)
        policy_ok = state.get("policy_ok", False)
        risk_level = state.get("risk_level", "low")
        attempts = state.get("attempts", 0)
        observations = state.get("observations", {})
        feasibility_details = state.get("feasibility_details", {})
        
        # Try LLM first
        llm_client = get_llm_client()
        if llm_client:
            logger.info("🤖 Using LLM for confidence estimation...")
            confidence, factors = _estimate_with_llm(
                llm_client, feasible, policy_ok, risk_level, 
                attempts, observations, feasibility_details
            )
            
            if confidence is not None:
                state["confidence"] = confidence
                state["confidence_factors"] = factors
                logger.info(f"✓ LLM confidence: {confidence:.2f}")
                return state
        
        # Fallback to rules-based
        logger.info("Using rules-based fallback")
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
        
        logger.info(f"→ Confidence: {confidence:.2f} (0.0-1.0)")
        logger.info(f"  Feasibility: +{factors.get('feasibility', 0):.2f}")
        logger.info(f"  Policy: +{factors.get('policy_compliance', 0):.2f}")
        logger.info(f"  Risk: {factors.get('risk_level', 0):+.2f}")
        logger.info(f"  Data: {factors.get('data_completeness', 0):+.2f}")
        
    except Exception as e:
        logger.error(f"✗ Confidence estimator error: {e}")
        state["confidence"] = 0.0
        state["confidence_factors"] = {"error": str(e)}
    
    return state


def _estimate_with_llm(client, feasible: bool, policy_ok: bool, risk_level: str, 
                       attempts: int, observations: dict, feasibility_details: dict) -> tuple[float, dict]:
    """Use LLM to estimate confidence score"""
    try:
        prompt = f"""Assess confidence in this Water Department decision.

FEASIBLE: {feasible}
POLICY COMPLIANT: {policy_ok}
RISK LEVEL: {risk_level}
ATTEMPTS: {attempts}
OBSERVATIONS: {json.dumps(observations, indent=2)}
FEASIBILITY: {json.dumps(feasibility_details, indent=2)}

Return ONLY valid JSON with confidence score (0.0 - 1.0):
{{
  "confidence_score": 0.85,
  "factors": {{
    "feasibility_impact": 0.3,
    "policy_impact": 0.2,
    "risk_impact": -0.1,
    "data_quality_impact": 0.15
  }},
  "reasoning": "brief explanation"
}}

Consider:
1. Feasibility pass/fail → high impact
2. Policy compliance → critical
3. Risk level → higher risk = lower confidence
4. Data completeness → missing data reduces confidence
5. Multiple attempts → retries reduce confidence"""

        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a Water Department confidence assessment AI. Score confidence 0.0-1.0. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=400
        )
        
        llm_output = response.choices[0].message.content.strip()
        
        # Clean markdown
        if llm_output.startswith("```json"):
            llm_output = llm_output[7:]
        elif llm_output.startswith("```"):
            llm_output = llm_output[3:]
        if llm_output.endswith("```"):
            llm_output = llm_output[:-3]
        
        result = json.loads(llm_output.strip())
        confidence = result.get("confidence_score", 0.5)
        factors = result.get("factors", {})
        
        # Clamp to valid range
        confidence = max(0.0, min(1.0, confidence))
        
        return confidence, factors
        
    except Exception as e:
        logger.warning(f"LLM confidence estimation failed: {e}")
        return None, {}
