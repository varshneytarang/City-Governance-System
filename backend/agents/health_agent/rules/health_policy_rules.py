"""
Health policy rules (stubs).
"""

from typing import Dict


def must_maintain_surveillance(state: Dict) -> (bool, str):
    # If surveillance data is missing or recent incidents are critical, require escalation
    incidents = state.get('context', {}).get('disease_incidents', [])
    if not incidents:
        return False, 'No surveillance data available'
    critical = [i for i in incidents if i.get('severity') == 'critical']
    if critical:
        return False, 'Critical incidents present - human review required'
    return True, 'Surveillance OK'
