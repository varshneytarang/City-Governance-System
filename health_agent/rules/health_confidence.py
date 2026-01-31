"""
Health confidence scoring (simple stub).
"""

from typing import Dict


def calculate_confidence(state: Dict) -> float:
    # Very simple: confidence decreases with missing context
    context = state.get('context', {})
    score = 1.0
    if not context.get('disease_incidents'):
        score -= 0.3
    if not context.get('sanitation_inspections'):
        score -= 0.2
    if not context.get('vaccination_campaigns'):
        score -= 0.1
    return max(0.0, min(1.0, score))
