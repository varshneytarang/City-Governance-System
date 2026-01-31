import json

import pytest

from finance_agent import FinanceDepartmentAgent


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
        # Return a JSON summary consistent with output_generator expectations
        payload = json.dumps({
            "summary": "Approved with minor monitoring",
            "confidence": 0.92,
            "recommended_actions": ["schedule inspection", "track expenses monthly"]
        })
        return _MockResp(payload)


class _MockChat:
    def __init__(self):
        self.completions = _MockCompletions()


class _MockClient:
    def __init__(self):
        self.chat = _MockChat()


def test_finance_agent_with_mocked_llm(monkeypatch):
    # Patch the LLM helper to return a deterministic mock client
    import finance_agent.nodes.llm_helper as llm_helper
    import finance_agent.nodes.output_generator as output_generator

    # Patch both the helper and the consumer module (output_generator) where
    # `get_llm_client` was imported at module import time.
    monkeypatch.setattr(llm_helper, "get_llm_client", lambda: _MockClient())
    monkeypatch.setattr(output_generator, "get_llm_client", lambda: _MockClient())

    agent = FinanceDepartmentAgent()
    request = {"type": "finance_assessment", "location": "CityCenter", "estimated_cost": 5000}

    resp = agent.decide(request)

    assert isinstance(resp, dict)
    # LLM output should have been parsed into the response
    assert "summary" in resp
    assert resp.get("confidence") >= 0.9
    assert isinstance(resp.get("recommended_actions"), list)
