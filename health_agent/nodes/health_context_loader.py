"""
Node: health_context_loader
Populates `state['context']` with health-related context using `health_agent.database`.
"""

import logging
from typing import Dict

from ..database import get_health_queries

logger = logging.getLogger(__name__)


def health_context_loader(state: Dict) -> Dict:
    input_event = state.get('input_event', {})
    location = input_event.get('location')

    queries = get_health_queries()

    context = {}
    if location:
        context['disease_incidents'] = queries.get_disease_incidents(location=location, days=30)
        context['vaccination_campaigns'] = queries.get_vaccination_campaigns(location=location)
        context['sanitation_inspections'] = queries.get_sanitation_inspections(location=location)
        context['vulnerable_populations'] = queries.get_vulnerable_populations(location=location)
        context['health_facilities'] = queries.get_health_facilities(location=location)

    state['context'] = context
    logger.info('✓ Health context loaded')
    return state
