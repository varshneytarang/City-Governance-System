"""
Node: health_confidence_node
Compute and set `state['confidence']` using `health_agent.rules.health_confidence`.
"""

import logging
from typing import Dict

from ..rules import health_confidence

logger = logging.getLogger(__name__)


def health_confidence_node(state: Dict) -> Dict:
    conf = health_confidence.calculate_confidence(state)
    state['confidence'] = round(conf, 3)
    logger.info(f"✓ Confidence estimated: {state['confidence']}")
    return state
