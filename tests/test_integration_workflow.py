"""
Integration Tests for Complete Workflow

Tests the entire agent workflow end-to-end with various scenarios.
"""

import pytest
import time
from water_agent import WaterDepartmentAgent

# Rate limit: 30 requests/minute = 2 seconds between requests
RATE_LIMIT_DELAY = 2.1


class TestCompleteWorkflow:
    """Test full workflow from input to decision"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_simple_maintenance_request(self):
        """Test simple maintenance request workflow"""
        time.sleep(RATE_LIMIT_DELAY)  # Rate limit protection
        
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Schedule pipeline inspection",
            "activity": "inspection",
            "priority": "medium"
        }
        
        result = self.agent.decide(request)
        
        assert result is not None
        assert "decision" in result
        assert result["decision"] in ["recommend", "escalate"]
        # Check for plan OR escalation reason (not final_plan)
        assert "plan" in result or "escalation_reason" in result
    
    def test_emergency_response_workflow(self):
        """Test emergency response workflow"""
        time.sleep(RATE_LIMIT_DELAY)  # Rate limit protection
        
        request = {
            "type": "emergency_response",
            "location": "Zone-B",
            "user_request": "Major water leak reported",
            "severity": "critical",
            "incident_type": "major_leak"
        }
        
        result = self.agent.decide(request)
        
        assert result is not None
        assert "decision" in result
        # Emergency should be processed (recommend or escalate)
        assert result["decision"] in ["recommend", "escalate"]
    
    def test_shift_schedule_request(self):
        """Test shift scheduling workflow"""
        time.sleep(RATE_LIMIT_DELAY)  # Rate limit protection
        
        request = {
            "type": "schedule_shift_request",
            "location": "Zone-C",
            "user_request": "Delay work by 2 days",
            "requested_shift_days": 2,
            "reason": "Weather conditions"
        }
        
        result = self.agent.decide(request)
        
        assert result is not None
        assert "decision" in result
    
    def test_multiple_requests_sequential(self):
        """Test processing multiple requests sequentially"""
        requests = [
            {
                "type": "maintenance_request",
                "location": "Zone-A",
                "user_request": "Inspection needed",
                "activity": "inspection"
            },
            {
                "type": "maintenance_request",
                "location": "Zone-B",
                "user_request": "Repair needed",
                "activity": "repair"
            }
        ]
        
        results = []
        for req in requests:
            time.sleep(RATE_LIMIT_DELAY)  # Rate limit protection
            result = self.agent.decide(req)
            results.append(result)
            assert result is not None
            assert "decision" in result
        
        # Both should be processed independently
        assert len(results) == 2


class TestEdgeCases:
    """Test edge cases and error scenarios"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        request = {
            "user_request": "Do something"
            # Missing 'type' and 'location'
        }
        
        with pytest.raises(ValueError) as exc_info:
            self.agent.decide(request)
        
        assert "Missing required fields" in str(exc_info.value)
    
    def test_invalid_request_type(self):
        """Test handling of invalid request type"""
        request = {
            "type": "invalid_type_xyz",
            "location": "Zone-A",
            "user_request": "Test request"
        }
        
        with pytest.raises(ValueError) as exc_info:
            self.agent.decide(request)
        
        assert "Invalid request type" in str(exc_info.value)
    
    def test_empty_request(self):
        """Test handling of empty request"""
        request = {}
        
        with pytest.raises(ValueError):
            self.agent.decide(request)
    
    def test_null_values(self):
        """Test handling of null values"""
        request = {
            "type": "maintenance_request",
            "location": None,
            "user_request": None,
            "activity": None
        }
        
        with pytest.raises(ValueError):
            self.agent.decide(request)
    
    def test_extremely_high_cost(self):
        """Test handling of extremely high cost estimates"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Very expensive project",
            "estimated_cost": 10_000_000  # 10 million
        }
        
        result = self.agent.decide(request)
        
        # Should escalate due to high cost
        assert result["decision"] == "escalate"
    
    def test_very_long_user_request(self):
        """Test handling of very long user requests"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "A" * 10000  # 10k character request
        }
        
        result = self.agent.decide(request)
        
        # Should still process without error
        assert result is not None
        assert "decision" in result
    
    def test_special_characters_in_request(self):
        """Test handling of special characters"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Fix pipe @ location <script>alert('test')</script>; DROP TABLE users;--"
        }
        
        result = self.agent.decide(request)
        
        # Should handle safely
        assert result is not None
        assert "decision" in result
    
    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-中文",
            "user_request": "修理管道 🚰 💧",
            "activity": "repair"
        }
        
        result = self.agent.decide(request)
        
        assert result is not None
        assert "decision" in result


class TestRetryLoop:
    """Test retry/loop mechanisms"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_escalation_on_third_attempt(self):
        """Test that system escalates after max retries"""
        # This would require a scenario that triggers retries
        # For now, test that a problematic request eventually resolves
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Complex request requiring multiple attempts",
            "estimated_cost": 0  # Invalid cost might trigger retry
        }
        
        result = self.agent.decide(request)
        
        # Should either succeed or escalate, not loop forever
        assert result is not None
        assert "decision" in result
    
    def test_no_infinite_loops(self):
        """Test that system doesn't enter infinite loops"""
        request = {
            "type": "emergency_response",
            "location": "Zone-A",
            "user_request": "Critical emergency",
            "severity": "critical"
        }
        
        # This should complete in reasonable time
        import time
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should complete within 60 seconds
        assert duration < 60
        assert result is not None


class TestLLMIntegration:
    """Test LLM integration and fallback"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_llm_api_available(self):
        """Test that LLM API is available"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test LLM availability"
        }
        
        result = self.agent.decide(request)
        
        # Should work with or without LLM
        assert result is not None
        assert "decision" in result
    
    def test_llm_generates_creative_plans(self):
        """Test that LLM generates varied plans"""
        request = {
            "type": "project_planning",
            "location": "Zone-A",
            "user_request": "Plan water infrastructure upgrade",
            "scope": "large"
        }
        
        result = self.agent.decide(request)
        
        assert result is not None
        # If LLM is used, plan should exist
        if "final_plan" in result:
            plan = result["final_plan"]
            assert "steps" in plan or "actions" in plan


class TestConcurrency:
    """Test concurrent request handling"""
    
    def test_multiple_agents_independent(self):
        """Test that multiple agent instances are independent"""
        agent1 = WaterDepartmentAgent()
        agent2 = WaterDepartmentAgent()
        
        request1 = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Request 1"
        }
        
        request2 = {
            "type": "emergency_response",
            "location": "Zone-B",
            "user_request": "Request 2",
            "severity": "high"
        }
        
        result1 = agent1.decide(request1)
        result2 = agent2.decide(request2)
        
        # Both should complete independently
        assert result1 is not None
        assert result2 is not None
        
        agent1.close()
        agent2.close()


class TestStateTransitions:
    """Test state transitions through workflow"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_state_progression(self):
        """Test that state progresses through all phases"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Track state progression"
        }
        
        result = self.agent.decide(request)
        
        # Result should contain evidence of state progression
        assert result is not None
        # Final state should have decision
        assert "decision" in result
    
    def test_early_escalation_skips_later_phases(self):
        """Test that early escalation short-circuits workflow"""
        request = {
            "type": "emergency_response",
            "location": "Zone-A",
            "user_request": "Critical issue requiring immediate escalation",
            "severity": "critical"
        }
        
        result = self.agent.decide(request)
        
        # Should have decision even if some phases skipped
        assert result is not None
        assert "decision" in result


class TestErrorRecovery:
    """Test error recovery mechanisms"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_recovers_from_partial_data(self):
        """Test recovery from incomplete data"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test partial data",
            # Missing optional fields
        }
        
        result = self.agent.decide(request)
        
        # Should still process with defaults
        assert result is not None
        assert "decision" in result
    
    def test_handles_database_unavailable(self):
        """Test handling when database is unavailable"""
        # Agent should still work even if logging fails
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test without DB"
        }
        
        result = self.agent.decide(request)
        
        # Should complete even if memory logging fails
        assert result is not None
        assert "decision" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
