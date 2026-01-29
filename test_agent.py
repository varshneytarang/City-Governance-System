"""
Unit tests for Water Department Agent

Tests each phase of the agent workflow.
"""

import unittest
import logging
from datetime import datetime

from water_agent.state import DepartmentState
from water_agent.database import DatabaseConnection, WaterDepartmentQueries
from water_agent.tools import WaterDepartmentTools
from water_agent.nodes.context_loader import context_loader_node
from water_agent.nodes.intent_analyzer import intent_analyzer_node
from water_agent.nodes.goal_setter import goal_setter_node
from water_agent.nodes.planner import planner_node
from water_agent.nodes.tool_executor import tool_executor_node
from water_agent.nodes.observer import observer_node
from water_agent.nodes.feasibility_evaluator import feasibility_evaluator_node
from water_agent.nodes.policy_validator import policy_validator_node
from water_agent.nodes.confidence_estimator import confidence_estimator_node
from water_agent.nodes.decision_router import decision_router_node
from water_agent.nodes.output_generator import output_generator_node
from water_agent.rules.feasibility_rules import FeasibilityEvaluator
from water_agent.rules.policy_rules import PolicyValidator
from water_agent.rules.confidence_calculator import ConfidenceCalculator


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAgentState(unittest.TestCase):
    """Test agent state definition"""
    
    def test_state_structure(self):
        """Test that DepartmentState has required fields"""
        state: DepartmentState = {
            "input_event": {"type": "test"},
            "context": {},
            "intent": "test",
            "risk_level": "low",
            "safety_concerns": [],
            "goal": "test goal",
            "plan": {},
            "alternative_plans": [],
            "tool_results": {},
            "observations": {},
            "feasible": False,
            "feasibility_reason": "",
            "feasibility_details": {},
            "policy_ok": False,
            "policy_violations": [],
            "decision_id": None,
            "confidence": 0.0,
            "confidence_factors": {},
            "response": {},
            "escalate": False,
            "escalation_reason": None,
            "attempts": 0,
            "max_attempts": 3,
            "started_at": datetime.now(),
            "completed_at": None,
            "agent_version": "1.0",
            "execution_time_ms": 0,
            "retry_needed": False
        }
        
        self.assertEqual(state["intent"], "test")
        self.assertFalse(state["feasible"])
        self.assertEqual(state["risk_level"], "low")


class TestFeasibilityRules(unittest.TestCase):
    """Test feasibility evaluation"""
    
    def setUp(self):
        self.evaluator = FeasibilityEvaluator()
    
    def test_schedule_shift_sufficient_manpower(self):
        """Test schedule shift with sufficient manpower"""
        observations = {
            "extracted_facts": {
                "manpower_sufficient": True,
                "available_workers": 6,
                "required_workers": 5,
                "schedule_conflict": False,
                "pipeline_condition": "good",
                "critical_pipeline_issues": 0,
                "budget_available": True,
                "zone_risk_level": "low",
                "active_projects_count": 2
            }
        }
        
        feasible, reason, details = self.evaluator.evaluate(
            "negotiate_schedule",
            observations,
            {"requested_shift_days": 2}
        )
        
        self.assertTrue(feasible)
        self.assertIn("satisfied", reason.lower())
    
    def test_schedule_shift_insufficient_manpower(self):
        """Test schedule shift with insufficient manpower"""
        observations = {
            "extracted_facts": {
                "manpower_sufficient": False,
                "available_workers": 2,
                "required_workers": 5,
                "schedule_conflict": False,
                "pipeline_condition": "good",
                "critical_pipeline_issues": 0,
                "budget_available": True,
                "zone_risk_level": "low",
                "active_projects_count": 2
            }
        }
        
        feasible, reason, details = self.evaluator.evaluate(
            "negotiate_schedule",
            observations,
            {"requested_shift_days": 2}
        )
        
        self.assertFalse(feasible)
        self.assertIn("insufficient", reason.lower())
    
    def test_emergency_always_feasible(self):
        """Test emergency is always feasible"""
        observations = {
            "extracted_facts": {
                "available_workers": 5
            }
        }
        
        feasible, reason, details = self.evaluator.evaluate(
            "emergency_response",
            observations,
            {}
        )
        
        self.assertTrue(feasible)


class TestPolicyRules(unittest.TestCase):
    """Test policy validation"""
    
    def setUp(self):
        self.validator = PolicyValidator()
    
    def test_schedule_within_max_delay(self):
        """Test schedule within max delay policy"""
        compliant, violations = self.validator.validate(
            "negotiate_schedule",
            {"requested_shift_days": 2},
            {"extracted_facts": {"active_projects_count": 2}}
        )
        
        self.assertTrue(compliant)
    
    def test_schedule_exceeds_max_delay(self):
        """Test schedule exceeds max delay policy"""
        compliant, violations = self.validator.validate(
            "negotiate_schedule",
            {"requested_shift_days": 10},  # Exceeds MAX_SHIFT_DELAY_DAYS (3)
            {"extracted_facts": {}}
        )
        
        self.assertFalse(compliant)
        self.assertTrue(any("delay" in str(v).lower() for v in violations))


class TestConfidenceCalculation(unittest.TestCase):
    """Test confidence scoring"""
    
    def test_high_confidence(self):
        """Test high confidence scenario"""
        observations = {
            "extracted_facts": {"fact1": "value", "fact2": "value"}
        }
        feasibility_details = {"violations": []}
        
        confidence, factors = ConfidenceCalculator.calculate(
            feasible=True,
            policy_ok=True,
            risk_level="low",
            attempts=0,
            observations=observations,
            feasibility_details=feasibility_details
        )
        
        self.assertGreater(confidence, 0.7)
    
    def test_low_confidence(self):
        """Test low confidence scenario"""
        observations = {
            "extracted_facts": {}
        }
        feasibility_details = {"violations": ["violation1", "violation2"]}
        
        confidence, factors = ConfidenceCalculator.calculate(
            feasible=False,
            policy_ok=False,
            risk_level="high",
            attempts=3,
            observations=observations,
            feasibility_details=feasibility_details
        )
        
        self.assertLess(confidence, 0.5)


class TestNodeExecution(unittest.TestCase):
    """Test individual node execution"""
    
    def setUp(self):
        """Set up test state"""
        self.state: DepartmentState = {
            "input_event": {
                "type": "schedule_shift_request",
                "location": "Downtown",
                "requested_shift_days": 2
            },
            "context": {},
            "intent": "",
            "risk_level": "low",
            "safety_concerns": [],
            "goal": "",
            "plan": {},
            "alternative_plans": [],
            "tool_results": {},
            "observations": {},
            "feasible": False,
            "feasibility_reason": "",
            "feasibility_details": {},
            "policy_ok": False,
            "policy_violations": [],
            "decision_id": None,
            "confidence": 0.0,
            "confidence_factors": {},
            "response": {},
            "escalate": False,
            "escalation_reason": None,
            "attempts": 0,
            "max_attempts": 3,
            "started_at": datetime.now(),
            "completed_at": None,
            "agent_version": "1.0",
            "execution_time_ms": 0,
            "retry_needed": False
        }
    
    def test_goal_setter_node(self):
        """Test goal setter produces goal"""
        result = goal_setter_node(self.state)
        
        self.assertIsNotNone(result.get("goal"))
        self.assertGreater(len(result.get("goal", "")), 0)
    
    def test_planner_node(self):
        """Test planner produces plan"""
        self.state["goal"] = "test goal"
        self.state["intent"] = "negotiate_schedule"
        
        result = planner_node(self.state)
        
        self.assertIsNotNone(result.get("plan"))
    
    def test_observer_node(self):
        """Test observer normalizes tool results"""
        self.state["tool_results"] = {
            "manpower": {"sufficient": True, "available_count": 5}
        }
        
        result = observer_node(self.state)
        
        self.assertIn("extracted_facts", result.get("observations", {}))
    
    def test_confidence_estimator_node(self):
        """Test confidence estimator"""
        self.state["feasible"] = True
        self.state["policy_ok"] = True
        self.state["risk_level"] = "low"
        self.state["observations"] = {"extracted_facts": {}}
        self.state["feasibility_details"] = {"violations": []}
        
        result = confidence_estimator_node(self.state)
        
        confidence = result.get("confidence", 0)
        self.assertGreater(confidence, 0)
        self.assertLessEqual(confidence, 1.0)
    
    def test_decision_router_node(self):
        """Test decision router"""
        self.state["feasible"] = True
        self.state["policy_ok"] = True
        self.state["confidence"] = 0.85
        self.state["risk_level"] = "low"
        
        result = decision_router_node(self.state)
        
        # Should not escalate when all conditions met
        self.assertFalse(result.get("escalate"))
    
    def test_output_generator_node(self):
        """Test output generator"""
        self.state["escalate"] = False
        self.state["confidence"] = 0.85
        self.state["feasible"] = True
        self.state["policy_ok"] = True
        
        result = output_generator_node(self.state)
        
        response = result.get("response", {})
        self.assertEqual(response.get("decision"), "recommend")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("WATER DEPARTMENT AGENT - TEST SUITE")
    print("="*70 + "\n")
    
    unittest.main(verbosity=2)
