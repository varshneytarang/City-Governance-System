import pytest

from agents.finance_agent import FinanceDepartmentAgent


def test_finance_agent_basic_approve():
    agent = FinanceDepartmentAgent()

    request = {
        "type": "finance_assessment",
        "location": "CityCenter",
        "estimated_cost": 5000
    }

    response = agent.decide(request)

    assert isinstance(response, dict)
    assert "decision" in response
    # For scaffold budget 100000, 5000 should be affordable
    assert response["decision"] in ("approve", "escalate")


def test_finance_agent_escalate_high_cost():
    agent = FinanceDepartmentAgent()

    request = {
        "type": "finance_assessment",
        "location": "CityCenter",
        "estimated_cost": 1000000
    }

    response = agent.decide(request)
    assert response["decision"] == "escalate"
