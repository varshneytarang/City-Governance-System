"""
Integration-style test: Finance agent LLM + DB integration.

This test patches the finance LLM helper to return a sequence of controlled
JSON responses (for `revenue_forecaster` and `cost_estimator`), and patches
`get_finance_queries()` (both in `finance_agent.database` and
`finance_agent.agent`) to return a `QueriesMock` that records calls. The test
then runs `FinanceDepartmentAgent.decide()` and asserts the DB query methods
were invoked.
"""

import json
import pytest

from finance_agent.agent import FinanceDepartmentAgent


class _MockMessage:
    def __init__(self, content: str):
        self.content = content


class _MockChoice:
    def __init__(self, content: str):
        self.message = _MockMessage(content)


class _MockResp:
    def __init__(self, content: str):
        self.choices = [_MockChoice(content)]


class _SequenceCompletions:
    def __init__(self, payloads):
        self._payloads = list(payloads)

    def create(self, **kwargs):
        if not self._payloads:
            # default safe response
            return _MockResp(json.dumps({}))
        return _MockResp(json.dumps(self._payloads.pop(0)))


class _MockChat:
    def __init__(self, payloads):
        self.completions = _SequenceCompletions(payloads)


class _MockClient:
    def __init__(self, payloads):
        self.chat = _MockChat(payloads)


def test_finance_agent_llm_triggers_db_queries(monkeypatch):
    # Prepare payloads for LLM calls in order they are expected to occur.
    # finance_context_loader (LLM summary) may be skipped if queries present.
    # revenue_forecaster -> expects {"next_period_revenue": number, "method": "..."}
    # cost_estimator -> expects {"total_estimated_cost": number, "by_item": [...]}
    revenue_payload = {"next_period_revenue": 15000, "method": "model_based"}
    cost_payload = {"total_estimated_cost": 12000, "by_item": [{"name": "repair", "cost": 12000}]}
    budget_feas_payload = {"can_afford": True, "recommendations": [], "reasoning": "OK"}
    policy_payload = {"policy_compliant": True, "violations": [], "warnings": []}
    output_payload = {"summary": "Approved", "confidence": 0.9, "recommended_actions": []}

    payloads = [revenue_payload, cost_payload, budget_feas_payload, policy_payload, output_payload]

    # Patch the LLM client factory to return our mock client (sequence)
    import finance_agent.nodes.llm_helper as llm_module
    monkeypatch.setattr(llm_module, "get_llm_client", lambda: _MockClient(payloads))

    # Patch DB queries factory in both modules
    import finance_agent.database as db_module
    import finance_agent.agent as agent_module

    calls = {"fetch_budget_context": 0, "fetch_audit_log": 0}

    class QueriesMock:
        def __init__(self, *_, **__):
            pass

        def fetch_budget_context(self, location=None):
            calls["fetch_budget_context"] += 1
            return {"total_budget": 100000, "remaining": 80000}

        def fetch_audit_log(self, limit=10):
            calls["fetch_audit_log"] += 1
            return [{"timestamp": "now", "event": "test"}]

        def close(self):
            pass

    monkeypatch.setattr(db_module, "get_finance_queries", lambda: QueriesMock())
    monkeypatch.setattr(agent_module, "get_finance_queries", lambda: QueriesMock())

    # Run agent end-to-end
    agent = FinanceDepartmentAgent()
    request = {"type": "maintenance_request", "location": "District-9", "proposed_actions": [{"name": "repair", "cost": 12000}]}
    resp = agent.decide(request)

    # Assertions: agent returns a dict response and DB queries were used
    assert isinstance(resp, dict)
    assert calls["fetch_budget_context"] >= 1

    agent.close()
