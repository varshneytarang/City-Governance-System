import json

from agents.health_agent.agent import HealthDepartmentAgent


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
        # Return a plans JSON as expected by HealthPlannerLLM
        payload = json.dumps({
            "plans": [
                {
                    "name": "Mock Rapid Response",
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


def test_health_agent_planner_llm_monkeypatch(monkeypatch):
    # Patch HealthPlannerLLM methods to force LLM usage and inject mock client
    from health_agent.nodes import health_planner_llm as planner_module
    import agents.health_agent.database as db_module

    def fake_check(self):
        return True

    def fake_init(self):
        self.client = _MockClient()
        self.use_llm = True

    monkeypatch.setattr(planner_module.HealthPlannerLLM, "_check_llm_available", fake_check)
    monkeypatch.setattr(planner_module.HealthPlannerLLM, "_init_llm_client", fake_init)

    # Mock DB queries so the health_context_loader does not attempt a real DB connection
    class HealthQueriesMock:
        def get_disease_incidents(self, location=None, days=30):
            return []

        def get_vaccination_campaigns(self, location=None):
            return []

        def get_sanitation_inspections(self, location=None):
            return []

        def get_vulnerable_populations(self, location=None):
            return []

        def get_health_facilities(self, location=None):
            return []

    monkeypatch.setattr(db_module, "get_health_queries", lambda: HealthQueriesMock())

    agent = HealthDepartmentAgent()
    request = {"type": "health_assessment", "location": "Industrial Zone A"}

    resp = agent.decide(request)

    assert isinstance(resp, dict)
    # Expect the runner to include recommendations from the plan
    assert "recommendations" in resp
    assert len(resp["recommendations"]) >= 1
