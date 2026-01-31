"""
Node: output_generator
Format the final structured response for the Health department.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def output_generator_node(state: Dict) -> Dict:
    response = {
        'department': 'Health',
        'impact_assessment': {
            'health_risk_score': state.get('health_risk_score'),
            'risk_level': state.get('risk_level'),
            'sanitation_issues': len(state.get('context', {}).get('sanitation_inspections', []))
        },
        'recommendations': [],
        'confidence': state.get('confidence', 0.0),
        'requires_human_review': False
    }

    plan = state.get('plan')
    if plan:
        response['recommendations'].append(plan.get('name'))
        response['recommendations'].extend(plan.get('steps', []))

    # Escalate if risk is high or confidence low
    if state.get('risk_level') == 'high' or state.get('confidence', 0.0) < 0.5:
        response['requires_human_review'] = True

    state['response'] = response
    logger.info('✓ Health response generated')
    return state
