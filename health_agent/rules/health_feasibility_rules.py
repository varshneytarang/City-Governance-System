"""
Health feasibility rules (stubs).
"""

from typing import Dict


def can_deploy_mobile_unit(state: Dict) -> (bool, str):
    # Simplified check: require at least one available unit
    tools = state.get('tool_results', {})
    mobile = tools.get('mobile_unit_availability')
    if mobile and mobile.get('available_units', 0) > 0:
        return True, 'Mobile unit available'
    return False, 'No mobile units available'
