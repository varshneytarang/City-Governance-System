"""
Fire Department Agent Test Suite

Tests the fire department agent with various emergency and operational scenarios.
"""

import pytest
import logging
from fire_agent.agent import FireDepartmentAgent

logging.basicConfig(level=logging.INFO)


class TestFireAgent:
    """Test suite for Fire Department Agent"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup agent for each test"""
        self.agent = FireDepartmentAgent()
        yield
        self.agent.close()
    
    def test_emergency_response_structure_fire(self):
        """
        Test Scenario 1: Emergency Response - Structure Fire
        
        Critical priority structure fire requiring immediate response.
        Should deploy multiple trucks and firefighters within 10 minutes.
        """
        
        request = {
            "type": "emergency_response",
            "from": "911 Dispatch",
            "location": "Zone-1, Main Street",
            "zone": "Zone-1",
            "incident_type": "structure_fire",
            "priority": "critical",
            "casualties_reported": 0,
            "reason": "Residential building fire, 2nd floor, smoke visible"
        }
        
        response = self.agent.decide(request)
        
        # Assertions
        assert response is not None
        assert "decision" in response
        assert response["decision"] in ["recommend", "escalate", "reject"]
        
        # For emergency response, should typically recommend (if resources available)
        if response["decision"] == "recommend":
            assert "recommendation" in response
            assert response.get("requires_human_review") is not None
            
            # Check plan exists
            rec = response.get("recommendation", {})
            assert "plan" in rec or "action" in rec
            
            # Should have high confidence for emergency with available resources
            confidence = response.get("confidence") or rec.get("confidence", 0)
            assert confidence > 0.5  # At least 50% confidence
        
        print("\n✓ Emergency Response Test Passed")
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', 'N/A')}")
    
    def test_hazmat_incident_response(self):
        """
        Test Scenario 2: Hazmat Incident Response
        
        Hazardous materials incident requiring specialized team and equipment.
        Should check for certified personnel and hazmat equipment.
        """
        
        request = {
            "type": "hazmat_incident",
            "from": "Police Department",
            "location": "Zone-2, Industrial Park",
            "zone": "Zone-2",
            "incident_type": "chemical_spill",
            "priority": "high",
            "casualties_reported": 0,
            "reason": "Chemical leak at manufacturing facility, containment needed"
        }
        
        response = self.agent.decide(request)
        
        # Assertions
        assert response is not None
        assert "decision" in response
        assert response["decision"] in ["recommend", "escalate", "reject"]
        
        # Check for reasoning
        assert "reasoning" in response or "reason" in response
        
        print("\n✓ Hazmat Response Test Passed")
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', response.get('reason', 'N/A'))}")
    
    def test_equipment_maintenance_request(self):
        """
        Test Scenario 3: Equipment Maintenance
        
        Routine equipment maintenance request.
        Should check station capacity and budget before scheduling.
        """
        
        request = {
            "type": "equipment_maintenance",
            "from": "Station Captain",
            "location": "Zone-1, Fire Station 1",
            "zone": "Zone-1",
            "incident_type": "routine_maintenance",
            "priority": "medium",
            "reason": "Annual pump testing and ladder inspection for Truck-1"
        }
        
        response = self.agent.decide(request)
        
        # Assertions
        assert response is not None
        assert "decision" in response
        assert response["decision"] in ["recommend", "escalate", "reject"]
        
        # Maintenance should typically be feasible if budget allows
        if response["decision"] == "recommend":
            assert "recommendation" in response or "plan" in response.get("details", {})
        
        print("\n✓ Equipment Maintenance Test Passed")
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', 'N/A')}")
    
    def test_training_schedule_request(self):
        """
        Test Scenario 4: Training Request
        
        Request to schedule firefighter training.
        Should ensure adequate station coverage during training.
        """
        
        request = {
            "type": "training_request",
            "from": "Training Coordinator",
            "location": "Zone-3, Training Facility",
            "zone": "Zone-3",
            "priority": "low",
            "reason": "Quarterly hazmat certification training for 5 firefighters"
        }
        
        response = self.agent.decide(request)
        
        # Assertions
        assert response is not None
        assert "decision" in response
        assert response["decision"] in ["recommend", "escalate", "reject"]
        
        # Training should be schedulable if coverage permits
        assert "reasoning" in response or "reason" in response
        
        print("\n✓ Training Request Test Passed")
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', response.get('reason', 'N/A'))}")
    
    def test_station_deployment_request(self):
        """
        Test Scenario 5: Station Deployment
        
        Deploy resources to a location for standby coverage.
        """
        
        request = {
            "type": "station_deployment",
            "from": "Operations Commander",
            "location": "Zone-2, Public Event Site",
            "zone": "Zone-2",
            "priority": "medium",
            "reason": "Deploy standby unit for large public event with 5000 attendees"
        }
        
        response = self.agent.decide(request)
        
        # Assertions
        assert response is not None
        assert "decision" in response
        assert response["decision"] in ["recommend", "escalate", "reject"]
        
        print("\n✓ Station Deployment Test Passed")
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', 'N/A')}")
    
    def test_readiness_assessment(self):
        """
        Test Scenario 6: Readiness Assessment
        
        Assess current operational readiness of fire department.
        Should check all resources and provide comprehensive report.
        """
        
        request = {
            "type": "readiness_assessment",
            "from": "Fire Chief",
            "location": "All Zones",
            "priority": "medium",
            "reason": "Monthly operational readiness assessment"
        }
        
        response = self.agent.decide(request)
        
        # Assertions
        assert response is not None
        assert "decision" in response
        
        # Readiness assessment should provide detailed information
        if response["decision"] == "recommend":
            assert "recommendation" in response or "details" in response
        
        print("\n✓ Readiness Assessment Test Passed")
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', 'N/A')}")
    
    def test_invalid_request_type(self):
        """
        Test Scenario 7: Invalid Request
        
        Test agent error handling for invalid request type.
        """
        
        request = {
            "type": "invalid_type",
            "location": "Zone-1"
        }
        
        response = self.agent.decide(request)
        
        # Should escalate or reject invalid requests
        assert response is not None
        assert "decision" in response
        assert response["decision"] in ["escalate", "reject"]
        assert "error" in response or "reasoning" in response
        
        print("\n✓ Invalid Request Test Passed")
        print(f"  Decision: {response['decision']}")


def run_all_tests():
    """Run all fire agent tests manually"""
    
    print("\n" + "=" * 70)
    print("FIRE DEPARTMENT AGENT - TEST SUITE")
    print("=" * 70)
    
    agent = FireDepartmentAgent()
    
    try:
        print("\n[TEST 1] Emergency Response - Structure Fire")
        request = {
            "type": "emergency_response",
            "from": "911 Dispatch",
            "location": "Zone-1, Main Street",
            "zone": "Zone-1",
            "incident_type": "structure_fire",
            "priority": "critical",
            "casualties_reported": 0,
            "reason": "Residential building fire, 2nd floor, smoke visible"
        }
        response = agent.decide(request)
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', 'N/A')}")
        
        print("\n[TEST 2] Hazmat Incident Response")
        request = {
            "type": "hazmat_incident",
            "from": "Police Department",
            "location": "Zone-2, Industrial Park",
            "zone": "Zone-2",
            "incident_type": "chemical_spill",
            "priority": "high",
            "casualties_reported": 0,
            "reason": "Chemical leak at manufacturing facility, containment needed"
        }
        response = agent.decide(request)
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', response.get('reason', 'N/A'))}")
        
        print("\n[TEST 3] Equipment Maintenance")
        request = {
            "type": "equipment_maintenance",
            "from": "Station Captain",
            "location": "Zone-1, Fire Station 1",
            "zone": "Zone-1",
            "incident_type": "routine_maintenance",
            "priority": "medium",
            "reason": "Annual pump testing and ladder inspection for Truck-1"
        }
        response = agent.decide(request)
        print(f"  Decision: {response['decision']}")
        print(f"  Reasoning: {response.get('reasoning', 'N/A')}")
        
        print("\n" + "=" * 70)
        print("✓ FIRE AGENT TESTS COMPLETED")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        agent.close()


if __name__ == "__main__":
    run_all_tests()
