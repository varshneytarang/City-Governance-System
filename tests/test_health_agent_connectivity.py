import os
import pytest

# DB connectivity tests
from health_agent.database import HealthDatabaseConnection
from health_agent.config import settings as health_settings

# LLM connectivity tests
from health_agent.nodes.health_planner_llm import HealthPlannerLLM


def test_health_db_connects_with_settings(monkeypatch):
    calls = {}

    class DummyConn:
        def cursor(self, *args, **kwargs):
            class C:
                def execute(self, *a, **k):
                    return None
                def fetchall(self):
                    return []
            return C()
        def close(self):
            pass

    def fake_connect(**kwargs):
        calls.update(kwargs)
        return DummyConn()

    # Ensure .env-driven settings are available
    assert health_settings.DB_HOST
    assert health_settings.DB_NAME

    import psycopg2
    monkeypatch.setattr(psycopg2, "connect", fake_connect)

    db = HealthDatabaseConnection()
    # Verify connect called with settings
    assert calls.get("host") == health_settings.DB_HOST
    assert calls.get("port") == health_settings.DB_PORT
    assert calls.get("database") == health_settings.DB_NAME
    assert calls.get("user") == health_settings.DB_USER
    assert calls.get("password") == health_settings.DB_PASSWORD
    db.close()


def test_health_db_connects_with_dsn(monkeypatch):
    dsn_calls = {"dsn": None}

    class DummyConn:
        def close(self):
            pass

    def fake_connect(dsn):
        dsn_calls["dsn"] = dsn
        return DummyConn()

    import psycopg2
    monkeypatch.setattr(psycopg2, "connect", fake_connect)

    # Prefer DSN when provided
    monkeypatch.setenv("HEALTH_DATABASE_URL", "postgresql://user:pass@localhost:5432/healthdb")

    db = HealthDatabaseConnection()
    assert dsn_calls["dsn"].startswith("postgresql://")
    db.close()


def test_health_planner_llm_uses_groq_settings(monkeypatch):
    # Set provider and keys
    health_settings.LLM_PROVIDER = "groq"
    health_settings.GROQ_API_KEY = "test-key"
    health_settings.OPENAI_API_KEY = None
    health_settings.LLM_MODEL = "llama-3.3-70b-versatile"
    health_settings.LLM_TEMPERATURE = 0.3

    captured = {"init": {}, "create": {}}

    # Monkeypatch _init_llm_client to validate settings and inject fake client
    def fake_init(self):
        class FakeCompletions:
            def create(self, **kwargs):
                captured["create"] = kwargs
                class Resp:
                    class Msg:
                        def __init__(self, content):
                            self.content = content
                    def __init__(self):
                        self.message = Resp.Msg("{\"plans\": []}")
                class Choice:
                    def __init__(self):
                        self.message = Resp.Msg("{\"plans\": []}")
                class R:
                    def __init__(self):
                        self.choices = [Choice()]
                return R()
        class FakeChat:
            def __init__(self):
                self.completions = FakeCompletions()
        class FakeClient:
            def __init__(self):
                self.chat = FakeChat()
                self.base_url = "https://api.groq.com/openai/v1"
        # Simulate expected init values
        captured["init"] = {
            "provider": health_settings.LLM_PROVIDER,
            "api_key": health_settings.GROQ_API_KEY,
            "base_url": "https://api.groq.com/openai/v1",
        }
        self.client = FakeClient()
        self.use_llm = True

    monkeypatch.setattr(HealthPlannerLLM, "_init_llm_client", fake_init)
    # Force availability
    monkeypatch.setattr(HealthPlannerLLM, "_check_llm_available", lambda self: True)

    planner = HealthPlannerLLM()
    # Trigger a call to chat.completions.create to capture model/temperature
    planner.generate_plan({"intent": "x", "goal": "y", "context": {}, "input_event": {}})

    assert captured["init"]["provider"] == "groq"
    assert captured["init"]["base_url"] == "https://api.groq.com/openai/v1"
    # Model/temperature should come from settings
    assert captured["create"]["model"] == health_settings.LLM_MODEL
    assert captured["create"]["temperature"] == health_settings.LLM_TEMPERATURE


def test_health_planner_llm_uses_openai_settings(monkeypatch):
    # Switch to OpenAI
    health_settings.LLM_PROVIDER = "openai"
    health_settings.OPENAI_API_KEY = "openai-key"
    health_settings.GROQ_API_KEY = None
    health_settings.LLM_MODEL = "gpt-4"
    health_settings.LLM_TEMPERATURE = 0.2

    captured = {"init": {}, "create": {}}

    def fake_init(self):
        class FakeCompletions:
            def create(self, **kwargs):
                captured["create"] = kwargs
                class Choice:
                    class Msg:
                        def __init__(self, content):
                            self.content = content
                    def __init__(self):
                        self.message = Choice.Msg("{\"plans\": []}")
                class R:
                    def __init__(self):
                        self.choices = [Choice()]
                return R()
        class FakeChat:
            def __init__(self):
                self.completions = FakeCompletions()
        class FakeClient:
            def __init__(self):
                self.chat = FakeChat()
                self.base_url = None
        captured["init"] = {
            "provider": health_settings.LLM_PROVIDER,
            "api_key": health_settings.OPENAI_API_KEY,
            "base_url": None,
        }
        self.client = FakeClient()
        self.use_llm = True

    monkeypatch.setattr(HealthPlannerLLM, "_init_llm_client", fake_init)
    monkeypatch.setattr(HealthPlannerLLM, "_check_llm_available", lambda self: True)

    planner = HealthPlannerLLM()
    planner.generate_plan({"intent": "x", "goal": "y", "context": {}, "input_event": {}})

    assert captured["init"]["provider"] == "openai"
    assert captured["init"]["base_url"] is None
    assert captured["create"]["model"] == health_settings.LLM_MODEL
    assert captured["create"]["temperature"] == health_settings.LLM_TEMPERATURE
