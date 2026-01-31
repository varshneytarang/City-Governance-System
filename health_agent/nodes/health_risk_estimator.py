"""
Node: health_risk_estimator
Compute a health_risk_score from context and input_event and set `state['risk_level']`.
"""

import logging
from typing import Dict

from ..config import settings

logger = logging.getLogger(__name__)


def _normalize_incidence(incidents_list):
    if not incidents_list:
        return 0.0
    return min(1.0, len(incidents_list) / 50.0)  # simple scaling


def _vulnerability_index(vulnerable_entries):
    if not vulnerable_entries:
        return 0.0
    # average vulnerability_index when present
    vals = [e.get('vulnerability_index', 0) for e in vulnerable_entries if e.get('vulnerability_index') is not None]
    if not vals:
        return 0.0
    return min(1.0, sum(vals) / len(vals) / 10.0)


def health_risk_estimator(state: Dict) -> Dict:
    context = state.get('context', {})
    incidents = context.get('disease_incidents', [])
    vuln = context.get('vulnerable_populations', [])
    sanitation = context.get('sanitation_inspections', [])

    incidence_score = _normalize_incidence(incidents)
    vuln_score = _vulnerability_index(vuln)
    sanitation_risk = min(1.0, len([s for s in sanitation if s.get('outcome') in ('fail','critical')]) / 5.0)

    # weights (configurable in health config later)
    w_incidence = 0.5
    w_vuln = 0.3
    w_san = 0.2

    health_risk_score = incidence_score * w_incidence + vuln_score * w_vuln + sanitation_risk * w_san

    # Map to level
    if health_risk_score >= 0.7:
        level = 'high'
    elif health_risk_score >= 0.4:
        level = 'medium'
    else:
        level = 'low'

    state['health_risk_score'] = round(health_risk_score, 3)
    state['risk_level'] = level

    logger.info(f"✓ Health risk estimated: {state['health_risk_score']} ({level})")
    return state
