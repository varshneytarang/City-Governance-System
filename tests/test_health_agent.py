import pytest
from agents.health_agent import HealthDepartmentAgent


def test_health_agent_smoke():
    agent = HealthDepartmentAgent()
    request = {'type': 'sanitation_work_schedule', 'location': 'TestZone'}
    resp = agent.decide(request)
    # The scaffold returns a response dict (may be empty); assert keys exist when present
    assert isinstance(resp, dict)
    agent.close()
