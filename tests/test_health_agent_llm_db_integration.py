"""
Integration-style test for Health agent: ensure workflow uses DB and LLM.

While the Health agent does not have a tool executor, its context loader
performs DB queries, and the planner uses LLM. This test forces LLM usage and
verifies DB queries were invoked during decision processing.
"""

import json
import pytest

from health_agent.agent import HealthDepartmentAgent


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
    def __init__(self, payload: dict):
        self._payload = json.dumps(payload)

    def create(self, **kwargs):
        return _MockResp(self._payload)


class _MockChat:
    def __init__(self, payload: dict):
        self.completions = _MockCompletions(payload)


class _MockClient:
    def __init__(self, payload: dict):
        self.chat = _MockChat(payload)


def test_health_agent_llm_and_db(monkeypatch):
    # 1) Patch HealthPlannerLLM to force LLM and return a basic plan
    from health_agent.nodes import health_planner_llm as planner_module
    plan_payload = {
        "plans": [
            {
                "name": "Health Assessment Plan",
                "steps": ["Review incidents", "Coordinate sanitation"],
                "estimated_duration": "2 days",
                "estimated_cost": 8000,
                "resources_needed": ["mobile_unit"],
                "risk_level": "medium"
            }
        ]
    }

    def fake_check(self):
        return True

    def fake_init(self):
        self.client = _MockClient(plan_payload)
        self.use_llm = True

    monkeypatch.setattr(planner_module.HealthPlannerLLM, "_check_llm_available", fake_check)
    monkeypatch.setattr(planner_module.HealthPlannerLLM, "_init_llm_client", fake_init)

    # 2) Patch health DB queries to record calls and return sample data
    import health_agent.database as db_module
    import importlib
    hcl_module = importlib.import_module('health_agent.nodes.health_context_loader')

    calls = {
        "get_disease_incidents": 0,
        "get_vaccination_campaigns": 0,
        "get_sanitation_inspections": 0,
        "get_vulnerable_populations": 0,
        "get_health_facilities": 0,
    }

    class HealthQueriesMock:
        def get_disease_incidents(self, location=None, days=30):
            calls["get_disease_incidents"] += 1
            return []
        def get_vaccination_campaigns(self, location=None):
            calls["get_vaccination_campaigns"] += 1
            return []
        def get_sanitation_inspections(self, location=None, recent_days=90):
            calls["get_sanitation_inspections"] += 1
            return []
        def get_vulnerable_populations(self, location=None):
            calls["get_vulnerable_populations"] += 1
            return []
        def get_health_facilities(self, location=None):
            calls["get_health_facilities"] += 1
            return []

    # Patch both the database module and the imported symbol in health_context_loader
    monkeypatch.setattr(db_module, "get_health_queries", lambda: HealthQueriesMock())
    monkeypatch.setattr(hcl_module, "get_health_queries", lambda: HealthQueriesMock())

    # 3) Run agent end-to-end on a sample request
    agent = HealthDepartmentAgent()
    request = {"type": "health_assessment", "location": "Zone H"}
    resp = agent.decide(request)

    # 4) Assert response and DB calls occurred
    assert isinstance(resp, dict)
    assert sum(calls.values()) >= 1  # at least one DB query was made by context loader
