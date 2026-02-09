"""
Integration-style test: LLM-generated plan triggers DB-backed tools.

This test monkeypatches the LLM client to return a plan containing exact tool
names (e.g., "get_active_projects"), then verifies that the Water agent's tool
executor calls the corresponding DB query methods.
"""

import json
import pytest

from agents.water_agent.agent import WaterDepartmentAgent


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


def test_water_agent_llm_triggers_db_queries(monkeypatch):
    # 1) Patch planner to force LLM usage and return a plan with DB-backed steps
    from water_agent.nodes import planner as planner_module
    plan_payload = {
        "plans": [
            {
                "name": "Plan A",
                "steps": [
                    "get_active_projects",
                    "check_manpower_availability",
                    "check_pipeline_health",
                    "check_reservoir_levels",
                    "assess_zone_risk",
                    "check_budget_availability"
                ],
                "estimated_duration": "2 days",
                "estimated_cost": 50000,
                "resources_needed": ["team", "equipment"],
                "risk_level": "low"
            }
        ]
    }

    def fake_check(self):
        return True

    def fake_init(self):
        self.client = _MockClient(plan_payload)
        self.use_llm = True

    monkeypatch.setattr(planner_module.WaterPlanner, "_check_llm_available", fake_check)
    monkeypatch.setattr(planner_module.WaterPlanner, "_init_llm_client", fake_init)

    # 2) Patch DB queries to record calls and return sample data
    # IMPORTANT: WaterDepartmentAgent imports get_queries into its module namespace,
    # so patch the symbol in water_agent.agent, not only water_agent.database.
    import agents.water_agent.database as db_module
    import agents.water_agent.agent as agent_module

    calls = {
        "get_active_projects": 0,
        "get_available_workers": 0,
        "get_pipeline_status": 0,
        "get_reservoir_status": 0,
        "get_recent_incidents": 0,
        "get_budget_status": 0,
    }

    class QueriesMock:
        def __init__(self, *_):
            pass
        def get_active_projects(self, location=None):
            calls["get_active_projects"] += 1
            return [{"project_id": 1, "project_name": "A", "location": location, "status": "approved"}]
        def get_available_workers(self, location=None, role=None):
            calls["get_available_workers"] += 1
            return [{"worker_id": 1, "worker_name": "W", "role": role or "tech", "status": "active", "skills": []}]
        def get_pipeline_status(self, location=None, zone=None):
            calls["get_pipeline_status"] += 1
            return [{"pipeline_id": 1, "location": location, "zone": zone, "condition": "good", "operational_status": "ok", "pressure_psi": 50}]
        def get_reservoir_status(self):
            calls["get_reservoir_status"] += 1
            return [{"reservoir_id": 1, "name": "R1", "location": "X", "capacity_liters": 1000, "current_level_liters": 800, "level_percentage": 80, "operational_status": "ok", "last_reading_time": "now"}]
        def get_recent_incidents(self, location=None, days=30):
            calls["get_recent_incidents"] += 1
            return []
        def get_budget_status(self):
            calls["get_budget_status"] += 1
            return {"total_budget": 100000, "spent": 20000, "remaining": 80000, "utilization_percent": 20, "status": "healthy"}

    # Replace factories to return our mock in both modules
    monkeypatch.setattr(db_module, "get_queries", lambda db: QueriesMock(db))
    monkeypatch.setattr(agent_module, "get_queries", lambda db: QueriesMock(db))

    # 2b) Prevent external LLM calls for non-planner nodes
    from water_agent.nodes import intent_analyzer, goal_setter, observer, policy_validator, confidence_estimator, decision_router
    monkeypatch.setattr(intent_analyzer, "_get_llm_client", lambda: None)
    monkeypatch.setattr(goal_setter, "get_llm_client", lambda: None)
    monkeypatch.setattr(observer, "get_llm_client", lambda: None)
    monkeypatch.setattr(policy_validator, "get_llm_client", lambda: None)
    # confidence_estimator and decision_router also use get_llm_client
    monkeypatch.setattr(confidence_estimator, "get_llm_client", lambda: None)
    monkeypatch.setattr(decision_router, "get_llm_client", lambda: None)

    # 3) Run agent end-to-end on a sample request
    agent = WaterDepartmentAgent()
    request = {"type": "maintenance_request", "location": "Zone-1", "estimated_cost": 50000, "required_workers": 5, "requested_date": "2026-02-01"}
    resp = agent.decide(request)

    # 4) Assert DB-backed steps were executed via tool executor
    assert resp and isinstance(resp, dict)
    assert calls["get_active_projects"] >= 1
    assert calls["get_pipeline_status"] >= 1
    assert calls["get_reservoir_status"] >= 1
    assert calls["get_budget_status"] >= 1

    agent.close()
