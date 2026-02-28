import json
from ..schemas import PlannerOutput, IntentAnalysis


def test_planner_schema_valid():
    sample = {
        "plans": [
            {
                "name": "Plan A",
                "steps": ["step1", "step2"],
                "estimated_duration": "2 days",
                "estimated_cost": 10000,
                "resources_needed": ["workers"],
                "risk_level": "low"
            }
        ]
    }

    parsed = PlannerOutput.parse_obj(sample)
    assert len(parsed.plans) == 1
    assert parsed.plans[0].name == "Plan A"


def test_intent_schema_valid():
    sample = {
        "intent": "emergency_response",
        "risk_level": "high",
        "safety_concerns": ["pipeline leak"],
        "reasoning": "Detected critical incident"
    }

    parsed = IntentAnalysis.parse_obj(sample)
    assert parsed.intent == "emergency_response"
    assert parsed.risk_level == "high"
