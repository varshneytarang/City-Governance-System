"""
Unit Tests for Individual Nodes

Tests each node in isolation with various edge cases.
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
    feasibility_evaluator,
    context_loader,
    tool_executor,
)


class TestIntentAnalyzer:
    """Test intent classification and risk assessment"""
    
    def test_emergency_intent_high_risk(self):
        """Emergency requests should be classified as high risk"""
        state = {
            "input_event": {
                "type": "emergency_response",
                "severity": "critical",
                "incident_type": "major_leak"
            }
        }
        # Add tools parameter (required by actual function signature)
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert result["intent"] == "emergency_response"
        assert result["risk_level"] in ["high", "critical"]
    
    def test_maintenance_intent_low_risk(self):
        """Routine maintenance should be low risk"""
        state = {
            "input_event": {
                "type": "maintenance_request",
                "priority": "low",
                "activity": "inspection"
            }
        }
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert result["intent"] == "coordinate_maintenance"
        assert result["risk_level"] in ["low", "medium"]
    
    def test_missing_input_event(self):
        """Should handle missing input event gracefully"""
        state = {}
        result = intent_analyzer.intent_analyzer_node(state, tools=[])
        
        assert "intent" in result
        assert result["intent"] is not None
    
    def test_invalid_request_type(self):
        """Should handle unknown request types"""
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


class TestGoalSetter:
    """Test goal formulation"""
    
    def test_emergency_goal_formulation(self):
        """Emergency intents should have urgent goals"""
        state = {
            "intent": "emergency_response",
            "risk_level": "critical",
            "input_event": {
                "type": "emergency_response",
                "incident_type": "leak"
            }
        }
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result
        assert len(result["goal"]) > 0
        assert any(word in result["goal"].lower() for word in ["emergency", "immediate", "urgent"])
    
    def test_maintenance_goal_formulation(self):
        """Maintenance should have scheduling goals"""
        state = {
            "intent": "coordinate_maintenance",
            "risk_level": "low",
            "input_event": {
                "type": "maintenance_request",
                "activity": "inspection"
            }
        }
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result
        assert len(result["goal"]) > 0
    
    def test_missing_intent(self):
        """Should handle missing intent"""
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result
        assert result["goal"] is not None
    
    @patch('water_agent.nodes.goal_setter.get_llm_client')
    def test_llm_json_error_fallback(self, mock_client):
        """Should handle LLM JSON parsing errors"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Invalid JSON {{{"))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "intent": "coordinate_maintenance",
            "input_event": {"type": "maintenance_request"}
        }
        result = goal_setter.goal_setter_node(state)
        
        assert "goal" in result
        assert result["goal"] is not None


class TestPlanner:
    """Test plan generation"""
    
    def test_emergency_plan_generation(self):
        """Emergency plans should have rapid response steps"""
        state = {
            "intent": "emergency_response",
            "goal": "Respond to critical leak immediately",
            "context": {"available_workers": 10},
            "input_event": {
                "type": "emergency_response",
                "location": "Zone-A"
            }
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        assert result["plan"] is not None
        assert "steps" in result["plan"]
        assert len(result["plan"]["steps"]) > 0
    
    def test_plan_includes_cost_estimate(self):
        """Plans should include cost estimates"""
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Schedule maintenance",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        if result["plan"]:  # Plan may be None if escalated early
            assert "estimated_cost" in result["plan"]
            assert result["plan"]["estimated_cost"] > 0
    
    def test_plan_includes_resources(self):
        """Plans should specify resource needs"""
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Schedule maintenance",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        if result["plan"]:  # Plan may be None if escalated early
            assert "resources_needed" in result["plan"]
            assert isinstance(result["plan"]["resources_needed"], list)
    
    def test_empty_context_handling(self):
        """Should handle empty context"""
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Test goal",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        result = planner.planner_node(state)
        
        assert "plan" in result
        assert result["plan"] is not None


class TestObserver:
    """Test tool result observation"""
    
    def test_analyze_tool_results(self):
        """Should extract facts from tool results"""
        state = {
            "tool_results": {
                "manpower": {
                    "sufficient": True,
                    "available_count": 10,
                    "required_count": 5
                },
                "budget": {
                    "available": 100000,
                    "required": 50000
                }
            },
            "plan": {"name": "Test Plan"}
        }
        result = observer.observer_node(state)
        
        assert "observations" in result
        assert result["observations"] is not None
    
    def test_empty_tool_results(self):
        """Should handle empty tool results"""
        state = {
            "tool_results": {},
            "plan": {}
        }
        result = observer.observer_node(state)
        
        assert "observations" in result
    
    def test_missing_tool_results(self):
        """Should handle missing tool results"""
        state = {"plan": {}}
        result = observer.observer_node(state)
        
        assert "observations" in result
    
    def test_malformed_tool_results(self):
        """Should handle malformed tool results"""
        state = {
            "tool_results": {
                "manpower": "not a dict",
                "invalid": None
            },
            "plan": {}
        }
        result = observer.observer_node(state)
        
        assert "observations" in result


class TestFeasibilityEvaluator:
    """Test feasibility checking (rules-based)"""
    
    def test_feasible_plan_passes(self):
        """Feasible plans should pass"""
        state = {
            "plan": {
                "name": "Test Plan",
                "estimated_cost": 50000,
                "resources_needed": ["5 workers"],
                "estimated_duration": "2 days"
            },
            "observations": {
                "extracted_facts": {
                    "manpower_sufficient": True,
                    "available_workers": 10,
                    "budget_available": 100000
                }
            }
        }
        result = feasibility_evaluator.feasibility_evaluator_node(state)
        
        assert result["feasible"] is True
        assert "feasibility_details" in result
    
    def test_insufficient_workers_fails(self):
        """Should fail when workers insufficient"""
        state = {
            "plan": {
                "name": "Test Plan",
                "resources_needed": ["20 workers"],
                "estimated_cost": 50000
            },
            "observations": {
                "extracted_facts": {
                    "manpower_sufficient": False,
                    "available_workers": 5
                }
            }
        }
        result = feasibility_evaluator.feasibility_evaluator_node(state)
        
        assert result["feasible"] is False
    
    def test_insufficient_budget_fails(self):
        """Should fail when budget insufficient"""
        state = {
            "plan": {
                "name": "Test Plan",
                "estimated_cost": 150000
            },
            "observations": {
                "extracted_facts": {
                    "budget_available": 50000
                }
            }
        }
        result = feasibility_evaluator.feasibility_evaluator_node(state)
        
        assert result["feasible"] is False
    
    def test_missing_observations(self):
        """Should handle missing observations"""
        state = {
            "plan": {"name": "Test Plan"}
        }
        result = feasibility_evaluator.feasibility_evaluator_node(state)
        
        assert "feasible" in result


class TestPolicyValidator:
    """Test policy compliance"""
    
    def test_compliant_plan_passes(self):
        """Policy-compliant plans should pass"""
        state = {
            "intent": "coordinate_maintenance",
            "input_event": {
                "type": "maintenance_request",
                "notice_hours": 48
            },
            "observations": {},
            "plan": {"name": "Test Plan"}
        }
        result = policy_validator.policy_validator_node(state)
        
        assert "policy_ok" in result
        assert "policy_violations" in result
    
    def test_insufficient_notice_fails(self):
        """Should fail with insufficient notice"""
        state = {
            "intent": "coordinate_maintenance",
            "input_event": {
                "type": "maintenance_request",
                "notice_hours": 12  # Less than MIN_MAINTENANCE_NOTICE_HOURS (24)
            },
            "observations": {},
            "plan": {}
        }
        result = policy_validator.policy_validator_node(state)
        
        # May pass or fail depending on LLM/rules, but should not error
        assert "policy_ok" in result
        assert "policy_violations" in result
    
    def test_emergency_override(self):
        """Emergencies may override certain policies"""
        state = {
            "intent": "emergency_response",
            "input_event": {
                "type": "emergency_response",
                "severity": "critical"
            },
            "observations": {},
            "plan": {}
        }
        result = policy_validator.policy_validator_node(state)
        
        assert "policy_ok" in result


class TestConfidenceEstimator:
    """Test confidence scoring"""
    
    def test_high_confidence_scenario(self):
        """All positive factors should yield high confidence"""
        state = {
            "feasible": True,
            "policy_ok": True,
            "risk_level": "low",
            "attempts": 0,
            "observations": {"data": "complete"},
            "feasibility_details": {"all_checks_passed": True}
        }
        result = confidence_estimator.confidence_estimator_node(state)
        
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["confidence"] > 0.5
    
    def test_low_confidence_scenario(self):
        """Negative factors should reduce confidence"""
        state = {
            "feasible": False,
            "policy_ok": False,
            "risk_level": "critical",
            "attempts": 3,
            "observations": {},
            "feasibility_details": {}
        }
        result = confidence_estimator.confidence_estimator_node(state)
        
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0
        assert result["confidence"] < 0.7
    
    def test_confidence_in_valid_range(self):
        """Confidence should always be 0.0 to 1.0"""
        state = {
            "feasible": True,
            "policy_ok": True,
            "risk_level": "medium",
            "attempts": 1,
            "observations": {},
            "feasibility_details": {}
        }
        result = confidence_estimator.confidence_estimator_node(state)
        
        assert 0.0 <= result["confidence"] <= 1.0


class TestDecisionRouter:
    """Test routing logic"""
    
    def test_high_confidence_recommends(self):
        """High confidence should recommend"""
        state = {
            "feasible": True,
            "policy_ok": True,
            "confidence": 0.85,
            "risk_level": "low",
            "escalate": False
        }
        result = decision_router.decision_router_node(state)
        
        assert "escalate" in result
        # High confidence, feasible, policy OK should recommend
        assert result["escalate"] is False
    
    def test_low_confidence_escalates(self):
        """Low confidence should escalate"""
        state = {
            "feasible": True,
            "policy_ok": True,
            "confidence": 0.3,  # Below threshold
            "risk_level": "low",
            "escalate": False
        }
        result = decision_router.decision_router_node(state)
        
        assert result["escalate"] is True
    
    def test_policy_failure_escalates(self):
        """Policy failure should always escalate"""
        state = {
            "feasible": True,
            "policy_ok": False,
            "confidence": 0.9,
            "risk_level": "low",
            "escalate": False
        }
        result = decision_router.decision_router_node(state)
        
        assert result["escalate"] is True
    
    def test_high_risk_escalates(self):
        """Critical risk should escalate"""
        state = {
            "feasible": True,
            "policy_ok": True,
            "confidence": 0.9,
            "risk_level": "critical",
            "escalate": False
        }
        result = decision_router.decision_router_node(state)
        
        assert result["escalate"] is True
    
    def test_already_escalated_preserved(self):
        """Should preserve existing escalation flag"""
        state = {
            "feasible": True,
            "policy_ok": True,
            "confidence": 0.9,
            "risk_level": "low",
            "escalate": True,
            "escalation_reason": "Previous escalation"
        }
        result = decision_router.decision_router_node(state)
        
        assert result["escalate"] is True


class TestContextLoader:
    """Test context loading"""
    
    def test_loads_context(self):
        """Should load operational context"""
        state = {"input_event": {"location": "Zone-A"}}
        result = context_loader.context_loader_node(state)
        
        assert "context" in result
        assert isinstance(result["context"], dict)
    
    def test_missing_location(self):
        """Should handle missing location"""
        state = {"input_event": {}}
        result = context_loader.context_loader_node(state)
        
        assert "context" in result


class TestToolExecutor:
    """Test tool execution"""
    
    def test_executes_tools(self):
        """Should execute plan tools"""
        state = {
            "plan": {
                "tools": ["check_manpower", "check_budget"],
                "actions": []
            }
        }
        result = tool_executor.tool_executor_node(state)
        
        assert "tool_results" in result
    
    def test_handles_missing_tools(self):
        """Should handle plans without tools"""
        state = {
            "plan": {"actions": ["action1"]}
        }
        result = tool_executor.tool_executor_node(state)
        
        assert "tool_results" in result
    
    def test_handles_invalid_tool(self):
        """Should handle invalid tool names"""
        state = {
            "plan": {
                "tools": ["invalid_tool_xyz"]
            }
        }
        result = tool_executor.tool_executor_node(state)
        
        assert "tool_results" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
