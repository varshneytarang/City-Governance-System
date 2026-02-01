"""
Confidence Calculator

Multi-factor confidence scoring algorithm (reusable across departments).
"""

import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """Calculate confidence score for decisions"""
    
    def calculate(self, feasible: bool, policy_ok: bool, risk_level: str,
                  attempts: int, observations: Dict[str, Any],
                  feasibility_details: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate confidence score (0.0 - 1.0).
        
        Returns: (confidence: float, factors: dict)
        """
        
        logger.info("Calculating confidence score")
        
        # Start with base score
        confidence = 0.5
        factors = {}
        
        # Factor 1: Feasibility (+0.3 if feasible)
        if feasible:
            feasibility_boost = 0.3
            confidence += feasibility_boost
            factors['feasibility'] = feasibility_boost
        else:
            feasibility_penalty = -0.3
            confidence += feasibility_penalty
            factors['feasibility'] = feasibility_penalty
        
        # Factor 2: Policy compliance (+0.2 if compliant)
        if policy_ok:
            policy_boost = 0.2
            confidence += policy_boost
            factors['policy_compliance'] = policy_boost
        else:
            policy_penalty = -0.2
            confidence += policy_penalty
            factors['policy_compliance'] = policy_penalty
        
        # Factor 3: Risk level adjustment
        risk_adjustments = {
            'low': 0.15,
            'medium': 0.0,
            'high': -0.15,
            'critical': -0.3
        }
        
        risk_adjustment = risk_adjustments.get(risk_level, 0.0)
        confidence += risk_adjustment
        factors['risk_level'] = risk_adjustment
        
        # Factor 4: Retry penalty (-0.1 per retry attempt)
        if attempts > 0:
            retry_penalty = -0.1 * attempts
            confidence += retry_penalty
            factors['retry_penalty'] = retry_penalty
        
        # Factor 5: Data completeness/quality
        extracted = observations.get('extracted_facts', {})
        data_quality = self._assess_data_quality(extracted)
        
        confidence += data_quality
        factors['data_completeness'] = data_quality
        
        # Clamp to [0.0, 1.0]
        confidence = max(0.0, min(1.0, confidence))
        
        logger.info(f"→ Final confidence: {confidence:.2f}")
        
        return (confidence, factors)
    
    def _assess_data_quality(self, extracted: Dict[str, Any]) -> float:
        """Assess quality and completeness of data"""
        
        # Count total facts extracted (similar to water/sanitation agents)
        fact_count = len(extracted)
        
        if fact_count >= 6:
            return 0.10
        elif fact_count >= 3:
            return 0.05
        else:
            return -0.05
