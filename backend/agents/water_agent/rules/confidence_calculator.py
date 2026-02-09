"""
Confidence Calculation Rules

PHASE 12: Quantify uncertainty based on:
- data completeness
- risk level
- number of retries
- historical similarity
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """Calculate confidence score for recommendations"""
    
    @staticmethod
    def calculate(
        feasible: bool,
        policy_ok: bool,
        risk_level: str,
        attempts: int,
        observations: Dict,
        feasibility_details: Dict
    ) -> Tuple[float, Dict]:
        """
        Calculate confidence score 0.0-1.0
        
        Returns: (confidence_score, factors_breakdown)
        """
        
        factors = {}
        
        # Start at neutral 0.5
        base_score = 0.5
        
        # Factor 1: Feasibility check (+0.25 if passes)
        if feasible:
            factors["feasibility"] = 0.25
            base_score += 0.25
        else:
            factors["feasibility"] = -0.15  # Strong negative if not feasible
            base_score -= 0.15
        
        # Factor 2: Policy compliance (+0.20 if passes)
        if policy_ok:
            factors["policy_compliance"] = 0.20
            base_score += 0.20
        else:
            factors["policy_compliance"] = -0.20  # Strong negative if policy fails
            base_score -= 0.20
        
        # Factor 3: Risk level (varies)
        risk_map = {
            "low": 0.15,
            "medium": 0.05,
            "high": -0.10,
            "critical": -0.25
        }
        risk_factor = risk_map.get(risk_level, 0.0)
        factors["risk_level"] = risk_factor
        base_score += risk_factor
        
        # Factor 4: Data completeness
        # Check how many observations we collected
        extracted_facts = observations.get("extracted_facts", {})
        fact_count = len(extracted_facts)
        if fact_count >= 6:
            data_factor = 0.10
        elif fact_count >= 3:
            data_factor = 0.05
        else:
            data_factor = -0.05
        
        factors["data_completeness"] = data_factor
        base_score += data_factor
        
        # Factor 5: Retry count (lower confidence if many retries)
        if attempts == 0:
            retry_factor = 0.05  # First try
        elif attempts == 1:
            retry_factor = 0.0   # Second try, neutral
        else:
            retry_factor = -0.10 * (attempts - 1)  # Penalize multiple retries
        
        factors["retry_count"] = retry_factor
        base_score += retry_factor
        
        # Factor 6: Constraint violations (from feasibility details)
        violations = feasibility_details.get("violations", [])
        if violations:
            violation_factor = -0.05 * len(violations)
            factors["constraint_violations"] = violation_factor
            base_score += violation_factor
        
        # Clamp score to [0.0, 1.0]
        confidence = max(0.0, min(1.0, base_score))
        
        factors["total_score"] = confidence
        
        return confidence, factors
