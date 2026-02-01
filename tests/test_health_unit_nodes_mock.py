"""
Unit Tests for Health Agent Nodes (Mocked - No external calls)

Mirrors water agent node tests with health-specific nodes.
"""

import json
import pytest
from unittest.mock import MagicMock

# Import health nodes
from health_agent.nodes.health_context_loader import health_context_loader
from health_agent.nodes.health_planner_llm import HealthPlannerLLM
from health_agent.nodes.health_policy_node import health_policy_node
from health_agent.nodes.health_confidence_node import health_confidence_node
from health_agent.nodes.health_risk_estimator import health_risk_estimator
from health_agent.nodes.output_generator import output_generator_node


# ---------- Helpers ----------
class _MockMessage:
    def __init__(self, content: str):
        self.content = content


class _MockChoice:
    def __init__(self, content: str):
        self.message = _MockMessage(content)


class _MockResp:
    def __init__(self, content: str):
        self.choices = [_MockChoice(content)]


class _MockCompletions:
    def create(self, **kwargs):
        payload = json.dumps({
            "plans": [
                {
                    "name": "Mock Health Rapid Response",
                    "steps": ["Inspect area", "Deploy mobile clinic"],
                    "estimated_duration": "2 days",
                    "estimated_cost": 8000,
                    "resources_needed": ["mobile_unit"],
                    "risk_level": "medium"
                }
            ]
        })
        return _MockResp(payload)


class _MockChat:
    def __init__(self):
        self.completions = _MockCompletions()


class _MockClient:
    def __init__(self):
        self.chat = _MockChat()


# ---------- Tests ----------

def test_health_context_loader_populates(monkeypatch):
    # Mock DB queries to avoid real Postgres
    import health_agent.database as db_module

    class HealthQueriesMock:
        def get_disease_incidents(self, location=None, days=30):
            return [{"incident_id": 1, "severity": "low"}]
        def get_vaccination_campaigns(self, location=None):
            return [{"campaign_id": 1, "end_date": None}]
        def get_sanitation_inspections(self, location=None):
            return [{"inspection_id": 1, "outcome": "pass"}]
        def get_vulnerable_populations(self, location=None):
            return [{"population_group": "elderly", "vulnerability_index": 5}]
        def get_health_facilities(self, location=None):
            return [{"facility_id": 1, "status": "open"}]

    monkeypatch.setattr(db_module, "get_health_queries", lambda: HealthQueriesMock())

    state = {"input_event": {"location": "ZoneX"}}
    result = health_context_loader(state)
    ctx = result.get("context", {})

    assert "disease_incidents" in ctx
    assert "vaccination_campaigns" in ctx
    assert "sanitation_inspections" in ctx
    assert "vulnerable_populations" in ctx
    assert "health_facilities" in ctx


def test_health_planner_llm_mock_client(monkeypatch):
    # Force LLM path and inject mock client
    def fake_check(self):
        return True
    def fake_init(self):
        self.client = _MockClient()
        self.use_llm = True

    monkeypatch.setattr(HealthPlannerLLM, "_check_llm_available", fake_check)
    monkeypatch.setattr(HealthPlannerLLM, "_init_llm_client", fake_init)

    planner = HealthPlannerLLM()
    state = {"intent": "health_assessment", "goal": "Reduce incidence", "context": {}, "input_event": {"location": "ZoneX"}}
    res = planner.generate_plan(state)

    assert res.get("llm_used") is True
    assert res.get("primary_plan") is not None
    assert isinstance(res.get("alternative_plans", []), list)


def test_health_policy_node_flags_campaign():
    # Active campaign should add a violation
    state = {
        "started_at": "2026-01-31T00:00:00",
        "context": {
            "vaccination_campaigns": [
                {"campaign_id": 1, "end_date": None}
            ]
        }
    }
    result = health_policy_node(state)
    assert result["policy_ok"] is False
    assert result["escalate"] is True
    assert any("Active vaccination campaign" in v for v in result.get("policy_violations", []))


def test_health_confidence_node_produces_score():
    state = {"plan": {"name": "Plan"}, "observations": {}}
    out = health_confidence_node(state)
    assert "confidence" in out
    assert 0.0 <= out["confidence"] <= 1.0


def test_health_risk_estimator_levels():
    # Low risk
    state_low = {"context": {
        "disease_incidents": [],
        "vulnerable_populations": [],
        "sanitation_inspections": []
    }}
    out_low = health_risk_estimator(state_low)
    assert out_low["risk_level"] in ("low", "medium", "high")

    # High risk: many incidents, failures
    state_high = {"context": {
        "disease_incidents": [{"id": i} for i in range(60)],
        "vulnerable_populations": [{"vulnerability_index": 9} for _ in range(5)],
        "sanitation_inspections": [{"outcome": "fail"} for _ in range(5)]
    }}
    out_high = health_risk_estimator(state_high)
    assert out_high["risk_level"] == "high"


def test_output_generator_escalation_logic():
    # High risk → requires human review
    state = {
        "risk_level": "high",
        "confidence": 0.9,
        "context": {"sanitation_inspections": [{"outcome": "fail"}]},
        "plan": {"name": "Mock Plan", "steps": ["Step1"]}
    }
    out = output_generator_node(state)
    resp = out.get("response", {})
    assert resp.get("requires_human_review") is True
    assert "recommendations" in resp
    assert len(resp["recommendations"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])