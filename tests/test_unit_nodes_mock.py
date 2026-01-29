"""
Unit Tests for Individual Nodes (Mocked - No API Calls)

Tests each node in isolation with mocked LLM responses to avoid rate limits.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from water_agent.state import DepartmentState
from water_agent.nodes import (
    intent_analyzer,
    goal_setter,
    planner,
    observer,
    policy_validator,
    confidence_estimator,
    decision_router,
)


def create_mock_llm_response(content_dict):
    """Helper to create consistent mock LLM responses"""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(content_dict)
    return mock_response


class TestIntentAnalyzer:
    """Test intent classification and risk assessment"""
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_emergency_intent_high_risk(self, mock_llm):
        """Emergency requests should be classified as high risk"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "intent": "emergency_response",
            "risk_level": "high",
            "confidence": 0.95
        })
        
        state = {
            "input_event": {
                "type": "emergency_response",
                "severity": "critical",
                "incident_type": "major_leak"
            }
        }
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert result["intent"] == "emergency_response"
        assert result["risk_level"] == "high"
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_maintenance_intent_low_risk(self, mock_llm):
        """Routine maintenance should be low risk"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "intent": "coordinate_maintenance",
            "risk_level": "low",
            "confidence": 0.88
        })
        
        state = {
            "input_event": {
                "type": "maintenance_request",
                "priority": "low",
                "activity": "inspection"
            }
        }
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert result["intent"] == "coordinate_maintenance"
        assert result["risk_level"] == "low"
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_missing_input_event(self, mock_llm):
        """Should handle missing input event gracefully"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "intent": "unknown",
            "risk_level": "low",
            "confidence": 0.50
        })
        
        state = {}
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert "intent" in result
        assert result["intent"] is not None
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_invalid_request_type(self, mock_llm):
        """Should handle unknown request types"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "intent": "unknown",
            "risk_level": "low",
            "confidence": 0.45
        })
        
        state = {
            "input_event": {
                "type": "unknown_type_xyz",
                "data": "random"
            }
        }
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert "intent" in result
        assert "risk_level" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_llm_failure_fallback(self, mock_llm):
        """Should fallback to deterministic when LLM fails"""
        mock_llm.return_value = None
        
        state = {
            "input_event": {
                "type": "emergency_response",
                "severity": "high"
            }
        }
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert "intent" in result
        assert result["intent"] is not None
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_malformed_llm_response(self, mock_llm):
        """Should handle malformed JSON from LLM"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "INVALID JSON {{"
        mock_llm.return_value.chat.completions.create.return_value = mock_response
        
        state = {"input_event": {"type": "test"}}
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        # Should fallback gracefully
        assert "intent" in result


class TestGoalSetter:
    """Test goal formulation"""
    
    @patch('water_agent.nodes.goal_setter._get_llm_client')
    def test_emergency_goal_formulation(self, mock_llm):
        """Emergency intents should have urgent goals"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "goal": "Immediately contain and repair water main break to prevent further damage",
            "success_criteria": ["leak stopped", "service restored"],
            "timeline": "2 hours"
        })
        
        state = {
            "intent": "emergency_response",
            "risk_level": "high",
            "input_event": {"type": "emergency_response"}
        }
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result
        assert len(result["goal"]) > 0
    
    @patch('water_agent.nodes.goal_setter._get_llm_client')
    def test_maintenance_goal_formulation(self, mock_llm):
        """Maintenance intents should have structured goals"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "goal": "Schedule and complete routine pipe inspection in sector A",
            "success_criteria": ["inspection completed", "report generated"],
            "timeline": "1 week"
        })
        
        state = {
            "intent": "coordinate_maintenance",
            "risk_level": "low",
            "input_event": {"type": "maintenance_request"}
        }
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result
        assert result["goal"] is not None
    
    @patch('water_agent.nodes.goal_setter._get_llm_client')
    def test_missing_intent(self, mock_llm):
        """Should handle missing intent gracefully"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "goal": "Assess situation and determine appropriate action",
            "success_criteria": ["situation assessed"],
            "timeline": "1 hour"
        })
        
        state = {"input_event": {"type": "test"}}
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result


class TestPlanner:
    """Test action planning"""
    
    @patch('water_agent.nodes.planner._get_llm_client')
    def test_creates_action_plan(self, mock_llm):
        """Should create structured action plans"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "plan": {
                "actions": [
                    {"step": 1, "action": "Dispatch crew", "duration": "30min"},
                    {"step": 2, "action": "Assess damage", "duration": "1hour"}
                ],
                "estimated_cost": 5000,
                "resources_needed": ["crew", "equipment"],
                "timeline": "3 hours"
            }
        })
        
        state = {
            "intent": "emergency_response",
            "goal": "Fix water main break",
            "context": {},
            "input_event": {"type": "emergency_response"}
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        assert result["plan"] is not None
    
    @patch('water_agent.nodes.planner._get_llm_client')
    def test_plan_includes_cost_estimate(self, mock_llm):
        """Plans should include cost estimates"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "plan": {
                "actions": [{"step": 1, "action": "test"}],
                "estimated_cost": 2500,
                "resources_needed": ["staff"],
                "timeline": "1 day"
            }
        })
        
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Schedule maintenance",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        if result["plan"]:
            assert "estimated_cost" in result["plan"]
            assert result["plan"]["estimated_cost"] > 0
    
    @patch('water_agent.nodes.planner._get_llm_client')
    def test_plan_includes_resources(self, mock_llm):
        """Plans should specify resource needs"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "plan": {
                "actions": [{"step": 1, "action": "test"}],
                "estimated_cost": 1000,
                "resources_needed": ["trucks", "tools", "staff"],
                "timeline": "2 days"
            }
        })
        
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Schedule maintenance",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        if result["plan"]:
            assert "resources_needed" in result["plan"]
            assert isinstance(result["plan"]["resources_needed"], list)


class TestObserver:
    """Test real-time observation"""
    
    @patch('water_agent.nodes.observer._get_llm_client')
    def test_observes_current_conditions(self, mock_llm):
        """Should analyze current state"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "observations": {
                "current_status": "active_leak",
                "severity": "high",
                "affected_areas": ["sector_a", "sector_b"]
            }
        })
        
        state = {
            "plan": {"actions": [{"step": 1, "action": "test"}]},
            "context": {"sensors": {"pressure": "low"}},
            "input_event": {"type": "emergency_response"}
        }
        result = observer.observer_node(state)
        
        assert "observations" in result
        assert result["observations"] is not None
    
    @patch('water_agent.nodes.observer._get_llm_client')
    def test_identifies_deviations(self, mock_llm):
        """Should detect when reality differs from plan"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "observations": {
                "current_status": "worse_than_expected",
                "deviation": "leak spreading faster",
                "needs_escalation": True
            }
        })
        
        state = {
            "plan": {"expected_duration": "1 hour"},
            "context": {"actual_duration": "3 hours"},
            "input_event": {"type": "test"}
        }
        result = observer.observer_node(state)
        
        assert "observations" in result


class TestPolicyValidator:
    """Test policy compliance checking"""
    
    @patch('water_agent.nodes.policy_validator._get_llm_client')
    def test_validates_against_policies(self, mock_llm):
        """Should check plans against policies"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "policy_compliant": True,
            "violations": [],
            "warnings": []
        })
        
        state = {
            "plan": {"estimated_cost": 5000},
            "context": {"budget_limit": 10000},
            "input_event": {"type": "test"}
        }
        result = policy_validator.policy_validator_node(state)
        
        assert "policy_compliant" in result
        assert isinstance(result["policy_compliant"], bool)
    
    @patch('water_agent.nodes.policy_validator._get_llm_client')
    def test_flags_violations(self, mock_llm):
        """Should identify policy violations"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "policy_compliant": False,
            "violations": ["budget_exceeded"],
            "warnings": []
        })
        
        state = {
            "plan": {"estimated_cost": 15000},
            "context": {"budget_limit": 10000},
            "input_event": {"type": "test"}
        }
        result = policy_validator.policy_validator_node(state)
        
        assert "policy_compliant" in result
        assert result["policy_compliant"] == False


class TestConfidenceEstimator:
    """Test confidence scoring"""
    
    @patch('water_agent.nodes.confidence_estimator._get_llm_client')
    def test_calculates_confidence(self, mock_llm):
        """Should provide confidence scores"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "confidence": 0.92,
            "factors": ["data_quality_high", "plan_feasible"],
            "uncertainty_level": "low"
        })
        
        state = {
            "plan": {"actions": [{"step": 1, "action": "test"}]},
            "observations": {"status": "normal"},
            "policy_compliant": True,
            "input_event": {"type": "test"}
        }
        result = confidence_estimator.confidence_estimator_node(state)
        
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
    
    @patch('water_agent.nodes.confidence_estimator._get_llm_client')
    def test_lower_confidence_for_uncertainty(self, mock_llm):
        """Should give lower scores when uncertain"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "confidence": 0.45,
            "factors": ["incomplete_data", "high_complexity"],
            "uncertainty_level": "high"
        })
        
        state = {
            "plan": None,
            "observations": None,
            "policy_compliant": False,
            "input_event": {"type": "test"}
        }
        result = confidence_estimator.confidence_estimator_node(state)
        
        assert "confidence" in result
        assert result["confidence"] < 0.7


class TestDecisionRouter:
    """Test decision routing logic"""
    
    @patch('water_agent.nodes.decision_router._get_llm_client')
    def test_routes_to_execution(self, mock_llm):
        """High confidence should route to execution"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "decision": "execute",
            "reasoning": "All conditions met for execution",
            "next_phase": "execution"
        })
        
        state = {
            "confidence": 0.9,
            "policy_compliant": True,
            "plan": {"actions": [{"step": 1, "action": "test"}]},
            "input_event": {"type": "test"}
        }
        result = decision_router.decision_router_node(state)
        
        assert "decision" in result
        assert result["decision"] in ["execute", "escalate", "replan"]
    
    @patch('water_agent.nodes.decision_router._get_llm_client')
    def test_escalates_low_confidence(self, mock_llm):
        """Low confidence should trigger escalation"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "decision": "escalate",
            "reasoning": "Confidence too low for autonomous execution",
            "next_phase": "escalation"
        })
        
        state = {
            "confidence": 0.3,
            "policy_compliant": True,
            "plan": {"actions": [{"step": 1, "action": "test"}]},
            "input_event": {"type": "test"}
        }
        result = decision_router.decision_router_node(state)
        
        assert "decision" in result
        assert result["decision"] == "escalate"
    
    @patch('water_agent.nodes.decision_router._get_llm_client')
    def test_escalates_policy_violations(self, mock_llm):
        """Policy violations should trigger escalation"""
        mock_llm.return_value.chat.completions.create.return_value = create_mock_llm_response({
            "decision": "escalate",
            "reasoning": "Policy violation requires human review",
            "next_phase": "escalation"
        })
        
        state = {
            "confidence": 0.8,
            "policy_compliant": False,
            "plan": {"actions": [{"step": 1, "action": "test"}]},
            "input_event": {"type": "test"}
        }
        result = decision_router.decision_router_node(state)
        
        assert "decision" in result
        assert result["decision"] == "escalate"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
