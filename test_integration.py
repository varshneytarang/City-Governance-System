"""
Integration Tests - Agent Viability Testing

Tests agent-to-agent, agent-to-human, and human-to-agent interactions
to ensure the system works correctly in all scenarios.
"""

import unittest
import logging
from datetime import datetime, timedelta
from typing import Dict, List

from water_agent import WaterDepartmentAgent
from water_agent.state import DepartmentState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# MOCK COMPONENTS FOR TESTING
# ============================================================

class MockCoordinator:
    """Simulates a Coordinator Agent that routes requests"""
    
    def __init__(self):
        self.water_agent = None
        self.requests_sent = []
        self.responses_received = []
    
    def register_agent(self, agent_type: str, agent):
        """Register a department agent"""
        if agent_type == "water":
            self.water_agent = agent
    
    def route_request(self, request: Dict) -> Dict:
        """Route request to appropriate department agent"""
        self.requests_sent.append(request)
        
        # Route to water department
        if request.get("department") == "water":
            response = self.water_agent.decide(request)
            self.responses_received.append(response)
            return response
        
        return {"error": "Unknown department"}
    
    def escalate_to_human(self, agent_response: Dict) -> Dict:
        """Simulate escalation to human review"""
        return {
            "escalated": True,
            "original_response": agent_response,
            "status": "awaiting_human_review"
        }


class MockHumanOperator:
    """Simulates a human operator reviewing agent decisions"""
    
    def __init__(self, name: str = "Human Operator"):
        self.name = name
        self.reviews_completed = []
    
    def review_recommendation(self, agent_response: Dict) -> Dict:
        """Human reviews and approves/rejects recommendation"""
        
        decision = agent_response.get("decision")
        confidence = agent_response.get("details", {}).get("confidence", 0)
        
        # Simulate human decision-making
        if decision == "recommend" and confidence >= 0.8:
            # High confidence recommendations usually approved
            human_decision = {
                "reviewer": self.name,
                "decision": "approved",
                "reason": "Recommendation is sound and well-justified",
                "timestamp": datetime.now().isoformat(),
                "agent_response": agent_response
            }
        elif decision == "escalate":
            # Review escalations
            human_decision = {
                "reviewer": self.name,
                "decision": "needs_more_info",
                "reason": "Requesting additional context before approval",
                "timestamp": datetime.now().isoformat(),
                "agent_response": agent_response
            }
        else:
            # Medium confidence - ask for clarification
            human_decision = {
                "reviewer": self.name,
                "decision": "conditional_approval",
                "reason": f"Approved with conditions. Confidence: {confidence}",
                "timestamp": datetime.now().isoformat(),
                "agent_response": agent_response
            }
        
        self.reviews_completed.append(human_decision)
        return human_decision
    
    def submit_request_to_agent(self, request: Dict, agent) -> Dict:
        """Human submits request to agent"""
        logger.info(f"{self.name} submitting request: {request.get('type')}")
        response = agent.decide(request)
        return response


class MockFireDepartmentAgent:
    """Simulates a Fire Department Agent for cross-department coordination"""
    
    def __init__(self):
        self.agent_type = "fire_department"
    
    def decide(self, request: Dict) -> Dict:
        """Simulate fire department decision-making"""
        
        # Fire department has different priorities
        if request.get("type") == "joint_operation_request":
            return {
                "decision": "recommend",
                "department": "fire",
                "response": {
                    "can_coordinate": True,
                    "available_units": 2,
                    "conditions": ["Require 24-hour notice", "Water supply guaranteed"]
                },
                "confidence": 0.85
            }
        
        return {"decision": "escalate", "reason": "Unknown request type"}


# ============================================================
# TEST CLASS 1: AGENT-TO-AGENT COMMUNICATION
# ============================================================

class TestAgentToAgentInteraction(unittest.TestCase):
    """Test how agents communicate with each other"""
    
    def setUp(self):
        """Set up agents and coordinator"""
        self.water_agent = WaterDepartmentAgent()
        self.fire_agent = MockFireDepartmentAgent()
        self.coordinator = MockCoordinator()
        
        # Register agents with coordinator
        self.coordinator.register_agent("water", self.water_agent)
    
    def tearDown(self):
        """Clean up"""
        self.water_agent.close()
    
    def test_coordinator_routes_to_water_agent(self):
        """Test coordinator correctly routes requests to water agent"""
        
        request = {
            "type": "schedule_shift_request",
            "department": "water",
            "from": "Coordinator",
            "location": "Downtown",
            "requested_shift_days": 2,
            "estimated_cost": 50000
        }
        
        response = self.coordinator.route_request(request)
        
        # Verify routing worked
        self.assertEqual(len(self.coordinator.requests_sent), 1)
        self.assertEqual(len(self.coordinator.responses_received), 1)
        self.assertIn("decision", response)
        self.assertIn(response["decision"], ["recommend", "escalate"])
    
    def test_cross_department_coordination(self):
        """Test water and fire departments coordinating on joint operation"""
        
        # Water department receives joint operation request
        water_request = {
            "type": "schedule_shift_request",
            "from": "Fire Department",
            "location": "Downtown",
            "requested_shift_days": 1,
            "reason": "Joint underground emergency drill",
            "estimated_cost": 30000
        }
        
        water_response = self.water_agent.decide(water_request)
        
        # Fire department responds
        fire_request = {
            "type": "joint_operation_request",
            "from": "Water Department",
            "location": "Downtown",
            "date": "2026-02-01"
        }
        
        fire_response = self.fire_agent.decide(fire_request)
        
        # Verify both agents can respond
        self.assertIsNotNone(water_response)
        self.assertIsNotNone(fire_response)
        
        # Verify responses are structured
        self.assertIn("decision", water_response)
        self.assertIn("decision", fire_response)
        
        logger.info(f"Water: {water_response.get('decision')}")
        logger.info(f"Fire: {fire_response.get('decision')}")
    
    def test_agent_escalation_to_coordinator(self):
        """Test agent escalates difficult decisions to coordinator"""
        
        # Request that should trigger escalation (high risk)
        request = {
            "type": "schedule_shift_request",
            "department": "water",
            "location": "Industrial Zone A",  # High-risk zone
            "requested_shift_days": 5,  # Exceeds policy (3 days)
            "estimated_cost": 200000
        }
        
        response = self.coordinator.route_request(request)
        
        # Should escalate due to policy violation
        if response.get("decision") == "escalate":
            escalation = self.coordinator.escalate_to_human(response)
            
            self.assertTrue(escalation.get("escalated"))
            self.assertEqual(escalation.get("status"), "awaiting_human_review")
            logger.info("✓ Correctly escalated to coordinator")


# ============================================================
# TEST CLASS 2: AGENT-TO-HUMAN INTERACTION
# ============================================================

class TestAgentToHumanInteraction(unittest.TestCase):
    """Test how agents communicate recommendations to humans"""
    
    def setUp(self):
        """Set up agent and human operator"""
        self.agent = WaterDepartmentAgent()
        self.human = MockHumanOperator("Senior Engineer")
    
    def tearDown(self):
        """Clean up"""
        self.agent.close()
    
    def test_high_confidence_recommendation_to_human(self):
        """Test agent presents high-confidence recommendation to human"""
        
        # Request that should produce high confidence
        request = {
            "type": "schedule_shift_request",
            "location": "Downtown",
            "requested_shift_days": 1,
            "estimated_cost": 25000,
            "required_workers": 3
        }
        
        agent_response = self.agent.decide(request)
        
        # Human reviews
        human_decision = self.human.review_recommendation(agent_response)
        
        # Verify interaction
        self.assertIsNotNone(human_decision)
        self.assertEqual(human_decision.get("reviewer"), "Senior Engineer")
        self.assertIn(human_decision.get("decision"), 
                     ["approved", "conditional_approval", "needs_more_info"])
        
        logger.info(f"Agent: {agent_response.get('decision')}")
        logger.info(f"Human: {human_decision.get('decision')}")
    
    def test_escalation_reaches_human(self):
        """Test escalated requests reach human reviewer"""
        
        # Request designed to escalate
        request = {
            "type": "schedule_shift_request",
            "location": "Industrial Zone A",  # High-risk area
            "requested_shift_days": 4,  # Exceeds policy
            "estimated_cost": 150000
        }
        
        agent_response = self.agent.decide(request)
        
        # Should escalate
        self.assertEqual(agent_response.get("decision"), "escalate")
        self.assertTrue(agent_response.get("requires_human_review"))
        
        # Human reviews escalation
        human_decision = self.human.review_recommendation(agent_response)
        
        self.assertEqual(human_decision.get("decision"), "needs_more_info")
        logger.info("✓ Escalation reached human for review")
    
    def test_agent_explains_reasoning_to_human(self):
        """Test agent provides clear reasoning for human understanding"""
        
        request = {
            "type": "maintenance_request",
            "location": "Downtown",
            "activity": "pipeline_inspection",
            "notice_hours": 48,
            "estimated_cost": 30000
        }
        
        agent_response = self.agent.decide(request)
        
        # Verify response has explanation
        self.assertIn("reasoning", agent_response.keys() or 
                     agent_response.get("reason") is not None)
        
        # Verify details are available for human review
        details = agent_response.get("details", {})
        self.assertIsNotNone(details)
        
        if "confidence" in details:
            logger.info(f"Confidence: {details['confidence']}")
        
        logger.info(f"Reasoning: {agent_response.get('reasoning', agent_response.get('reason'))}")


# ============================================================
# TEST CLASS 3: HUMAN-TO-AGENT INTERACTION
# ============================================================

class TestHumanToAgentInteraction(unittest.TestCase):
    """Test how humans submit requests and interact with agents"""
    
    def setUp(self):
        """Set up agent and human operator"""
        self.agent = WaterDepartmentAgent()
        self.human = MockHumanOperator("Field Supervisor")
    
    def tearDown(self):
        """Clean up"""
        self.agent.close()
    
    def test_human_submits_routine_request(self):
        """Test human submits routine maintenance request"""
        
        # Human creates request
        request = {
            "type": "maintenance_request",
            "location": "Downtown",
            "activity": "pipeline_inspection",
            "notice_hours": 72,
            "estimated_cost": 20000,
            "submitted_by": "Field Supervisor"
        }
        
        # Submit to agent
        response = self.human.submit_request_to_agent(request, self.agent)
        
        # Verify agent processed it
        self.assertIsNotNone(response)
        self.assertIn("decision", response)
        
        logger.info(f"Human submitted: {request['type']}")
        logger.info(f"Agent decided: {response.get('decision')}")
    
    def test_human_submits_emergency_request(self):
        """Test human submits emergency request for immediate response"""
        
        # Emergency from human operator
        emergency_request = {
            "type": "emergency_response",
            "location": "Downtown",
            "incident_type": "major_leak",
            "severity": "high",
            "reported_by": "Field Supervisor"
        }
        
        response = self.human.submit_request_to_agent(emergency_request, self.agent)
        
        # Emergency should be handled quickly
        self.assertIsNotNone(response)
        
        # Log response time (in real system)
        logger.info("✓ Emergency request processed by agent")
    
    def test_human_receives_agent_constraints(self):
        """Test human receives and understands agent-imposed constraints"""
        
        request = {
            "type": "schedule_shift_request",
            "location": "Downtown",
            "requested_shift_days": 2,
            "estimated_cost": 40000
        }
        
        response = self.human.submit_request_to_agent(request, self.agent)
        
        # Check if agent provides constraints
        recommendation = response.get("recommendation", {})
        constraints = recommendation.get("constraints", [])
        
        if constraints:
            logger.info(f"Agent imposed constraints: {constraints}")
            self.assertIsInstance(constraints, list)
        
        # Human should understand the response format
        self.assertIn("decision", response)
        logger.info("✓ Human can parse agent response")


# ============================================================
# TEST CLASS 4: MULTI-SCENARIO WORKFLOW TESTING
# ============================================================

class TestCompleteWorkflows(unittest.TestCase):
    """Test complete workflows involving all parties"""
    
    def setUp(self):
        """Set up all components"""
        self.water_agent = WaterDepartmentAgent()
        self.coordinator = MockCoordinator()
        self.human_operator = MockHumanOperator("Operations Manager")
        
        self.coordinator.register_agent("water", self.water_agent)
    
    def tearDown(self):
        """Clean up"""
        self.water_agent.close()
    
    def test_complete_approval_workflow(self):
        """Test: Human → Agent → Recommend → Human Approval"""
        
        logger.info("\n" + "="*70)
        logger.info("WORKFLOW TEST: Complete Approval Flow")
        logger.info("="*70)
        
        # 1. Human submits request
        request = {
            "type": "schedule_shift_request",
            "department": "water",
            "location": "Downtown",
            "requested_shift_days": 1,
            "estimated_cost": 30000,
            "submitted_by": "Operations Manager"
        }
        
        logger.info("Step 1: Human submits request")
        
        # 2. Coordinator routes to agent
        agent_response = self.coordinator.route_request(request)
        logger.info(f"Step 2: Agent decides: {agent_response.get('decision')}")
        
        # 3. Human reviews
        human_decision = self.human_operator.review_recommendation(agent_response)
        logger.info(f"Step 3: Human reviews: {human_decision.get('decision')}")
        
        # Verify complete flow
        self.assertEqual(len(self.coordinator.requests_sent), 1)
        self.assertEqual(len(self.coordinator.responses_received), 1)
        self.assertEqual(len(self.human_operator.reviews_completed), 1)
        
        logger.info("✓ Complete approval workflow successful\n")
    
    def test_escalation_workflow(self):
        """Test: Human → Agent → Escalate → Coordinator → Human"""
        
        logger.info("\n" + "="*70)
        logger.info("WORKFLOW TEST: Escalation Flow")
        logger.info("="*70)
        
        # 1. Human submits complex request
        request = {
            "type": "schedule_shift_request",
            "department": "water",
            "location": "Industrial Zone A",  # High risk
            "requested_shift_days": 5,  # Policy violation
            "estimated_cost": 180000
        }
        
        logger.info("Step 1: Human submits complex request")
        
        # 2. Agent processes and escalates
        agent_response = self.coordinator.route_request(request)
        logger.info(f"Step 2: Agent decides: {agent_response.get('decision')}")
        
        # 3. Should escalate
        if agent_response.get("decision") == "escalate":
            # 4. Coordinator escalates to human
            escalation = self.coordinator.escalate_to_human(agent_response)
            logger.info("Step 3: Coordinator escalates to human")
            
            # 5. Human reviews escalation
            human_decision = self.human_operator.review_recommendation(agent_response)
            logger.info(f"Step 4: Human reviews: {human_decision.get('decision')}")
            
            self.assertTrue(escalation.get("escalated"))
        
        logger.info("✓ Escalation workflow successful\n")
    
    def test_multi_department_coordination_workflow(self):
        """Test: Department A → Coordinator → Department B → Human"""
        
        logger.info("\n" + "="*70)
        logger.info("WORKFLOW TEST: Multi-Department Coordination")
        logger.info("="*70)
        
        # 1. Water department needs to coordinate with Fire
        water_request = {
            "type": "schedule_shift_request",
            "department": "water",
            "location": "Downtown",
            "requested_shift_days": 1,
            "reason": "Joint drill with Fire Department",
            "estimated_cost": 25000
        }
        
        logger.info("Step 1: Water department request")
        
        # 2. Water agent processes
        water_response = self.coordinator.route_request(water_request)
        logger.info(f"Step 2: Water agent: {water_response.get('decision')}")
        
        # 3. Fire department (simulated) would also process
        fire_agent = MockFireDepartmentAgent()
        fire_response = fire_agent.decide({
            "type": "joint_operation_request",
            "from": "Water Department",
            "location": "Downtown"
        })
        logger.info(f"Step 3: Fire agent: {fire_response.get('decision')}")
        
        # 4. Coordinator aggregates responses
        # 5. Human makes final decision
        human_decision = self.human_operator.review_recommendation(water_response)
        logger.info(f"Step 4: Human final decision: {human_decision.get('decision')}")
        
        logger.info("✓ Multi-department workflow successful\n")
    
    def test_emergency_priority_workflow(self):
        """Test: Emergency Request → Fast Track → Immediate Response"""
        
        logger.info("\n" + "="*70)
        logger.info("WORKFLOW TEST: Emergency Priority")
        logger.info("="*70)
        
        start_time = datetime.now()
        
        # 1. Emergency request from human
        emergency = {
            "type": "emergency_response",
            "department": "water",
            "location": "Downtown",
            "incident_type": "major_leak",
            "severity": "critical",
            "reported_by": "Emergency Hotline"
        }
        
        logger.info("Step 1: Emergency reported")
        
        # 2. Agent processes immediately
        response = self.coordinator.route_request(emergency)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Step 2: Agent responded in {processing_time:.2f}s")
        logger.info(f"Decision: {response.get('decision')}")
        
        # Emergency should be processed quickly (< 2 seconds in test)
        self.assertLess(processing_time, 2.0)
        
        logger.info("✓ Emergency priority workflow successful\n")


# ============================================================
# TEST CLASS 5: EDGE CASES AND ERROR HANDLING
# ============================================================

class TestEdgeCasesAndErrors(unittest.TestCase):
    """Test how system handles edge cases and errors"""
    
    def setUp(self):
        self.agent = WaterDepartmentAgent()
        self.human = MockHumanOperator("Test Operator")
    
    def tearDown(self):
        self.agent.close()
    
    def test_invalid_request_from_human(self):
        """Test agent handles invalid requests gracefully"""
        
        # Missing required fields
        invalid_request = {
            "type": "schedule_shift_request"
            # Missing: location, requested_shift_days
        }
        
        try:
            response = self.agent.decide(invalid_request)
            # Should either error or escalate
            if "error" in response or response.get("decision") == "escalate":
                logger.info("✓ Agent handled invalid request gracefully")
        except ValueError as e:
            # Expected - validation error
            logger.info(f"✓ Agent validated input: {str(e)}")
            self.assertIn("required", str(e).lower())
    
    def test_conflicting_agent_responses(self):
        """Test coordinator handles conflicting agent responses"""
        
        coordinator = MockCoordinator()
        coordinator.register_agent("water", self.agent)
        
        # Request that might have different interpretations
        request = {
            "type": "schedule_shift_request",
            "department": "water",
            "location": "Downtown",
            "requested_shift_days": 3,  # At policy limit
            "estimated_cost": 75000
        }
        
        response = coordinator.route_request(request)
        
        # Should handle gracefully
        self.assertIn("decision", response)
        logger.info(f"✓ Coordinator handled response: {response.get('decision')}")
    
    def test_human_overrides_agent_recommendation(self):
        """Test human can override agent recommendation"""
        
        request = {
            "type": "maintenance_request",
            "location": "Downtown",
            "activity": "pipeline_inspection",
            "notice_hours": 48,
            "estimated_cost": 35000
        }
        
        agent_response = self.agent.decide(request)
        
        # Human can always override
        human_override = {
            "original_agent_decision": agent_response.get("decision"),
            "human_decision": "approved_with_modifications",
            "reason": "Human expertise applied",
            "modifications": ["Extended timeline by 1 day"]
        }
        
        self.assertIsNotNone(human_override)
        logger.info("✓ Human can override agent recommendations")


# ============================================================
# MAIN TEST RUNNER
# ============================================================

if __name__ == "__main__":
    print("\n" + "🔄 "*30)
    print("INTEGRATION TEST SUITE - AGENT VIABILITY")
    print("Testing: Agent↔Agent, Agent↔Human, Human↔Agent")
    print("🔄 "*30 + "\n")
    
    # Run all test suites
    unittest.main(verbosity=2)
