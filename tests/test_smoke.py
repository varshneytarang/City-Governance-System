"""
Quick Smoke Test - Verify tests run without rate limit issues
"""

import pytest
from unittest.mock import patch, MagicMock
import json


def create_mock_llm_response(content_dict):
    """Helper to create mock LLM responses"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(content_dict)
    return mock_response


@patch('water_agent.nodes.intent_analyzer._get_llm_client')
def test_intent_analyzer_mocked(mock_llm):
    """Test intent analyzer with mocked LLM (no API call)"""
    from water_agent.nodes import intent_analyzer
    
    # Mock the LLM response
    mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
        "intent": "emergency_response",
        "risk_level": "high",
        "confidence": 0.95
    })
    
    state = {
        "input_event": {
            "type": "emergency_response",
            "severity": "critical"
        }
    }
    
    result = intent_analyzer.intent_analyzer_node(state, tools=[])
    
    assert result["intent"] == "emergency_response"
    assert result["risk_level"] == "high"
    print("✅ Intent Analyzer test passed (mocked)")


@patch('water_agent.nodes.llm_helper.get_llm_client')
def test_goal_setter_mocked(mock_llm):
    """Test goal setter with mocked LLM (no API call)"""
    from water_agent.nodes import goal_setter
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = create_mock_llm_response({
        "goal": "Fix water main break immediately",
        "success_criteria": ["leak stopped"],
        "timeline": "2 hours"
    })
    mock_llm.return_value = mock_client
    
    state = {
        "intent": "emergency_response",
        "risk_level": "high",
        "input_event": {"type": "emergency_response"}
    }
    
    result = goal_setter.goal_setter_node(state)
    
    assert "goal" in result
    assert result["goal"] is not None
    print("✅ Goal Setter test passed (mocked)")


@patch('water_agent.nodes.llm_helper.get_llm_client')
def test_planner_mocked(mock_llm):
    """Test planner with mocked LLM (no API call)"""
    from water_agent.nodes import planner
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = create_mock_llm_response({
        "plan": {
            "actions": [{"step": 1, "action": "Dispatch crew"}],
            "estimated_cost": 5000,
            "resources_needed": ["crew", "equipment"],
            "timeline": "3 hours"
        }
    })
    mock_llm.return_value = mock_client
    
    state = {
        "intent": "emergency_response",
        "goal": "Fix water main break",
        "context": {},
        "input_event": {"type": "emergency_response"}
    }
    
    result = planner.planner_node(state)
    
    assert "plan" in result
    assert result["plan"] is not None
    print("✅ Planner test passed (mocked)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
