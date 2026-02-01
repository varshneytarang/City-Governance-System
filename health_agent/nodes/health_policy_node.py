"""
Node: health_policy_node
Run deterministic health policy checks and set `state['policy_ok']` and `state['policy_violations']`.
"""

import logging
from typing import Dict

from ..rules import health_policy_rules

logger = logging.getLogger(__name__)


def health_policy_node(state: Dict) -> Dict:
    violations = []

    ok, reason = health_policy_rules.must_maintain_surveillance(state)
    if not ok:
        violations.append(reason)

    # Example additional policy: vaccination campaigns should not be interrupted
    campaigns = state.get('context', {}).get('vaccination_campaigns', [])
    if campaigns:
        # if any campaign is ongoing (end_date is null or in future), flag
        ongoing = [c for c in campaigns if not c.get('end_date') or str(c.get('end_date')) >= str(state.get('started_at', ''))]
        if ongoing:
            violations.append('Active vaccination campaign in area')

    state['policy_violations'] = violations
    state['policy_ok'] = len(violations) == 0
    if not state['policy_ok']:
        state['escalate'] = True
        state['escalation_reason'] = '; '.join(violations)

    logger.info(f"✓ Policy check complete: ok={state['policy_ok']}")
    return state
