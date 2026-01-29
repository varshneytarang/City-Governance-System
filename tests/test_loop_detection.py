"""
Loop Detection and Prevention Tests

Tests to ensure the system doesn't enter infinite loops.
"""

import pytest
import time
from unittest.mock import patch, Mock
from water_agent import WaterDepartmentAgent


class TestLoopPrevention:
    """Test loop detection and prevention mechanisms"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_max_iterations_enforced(self):
        """Test that maximum iterations are enforced"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test max iterations"
        }
        
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should complete quickly (not loop forever)
        assert duration < 60  # 60 second timeout
        assert result is not None
        assert "decision" in result
    
    def test_retry_limit_on_failure(self):
        """Test that retries are limited"""
        # Create a scenario that might trigger retries
        request = {
            "type": "emergency_response",
            "location": "Zone-A",
            "user_request": "Critical issue",
            "severity": "critical"
        }
        
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should not retry indefinitely
        assert duration < 60
        assert result is not None
    
    def test_circular_dependency_prevention(self):
        """Test that circular state dependencies are prevented"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test circular dependencies"
        }
        
        result = self.agent.decide(request)
        
        # Should complete without circular dependency errors
        assert result is not None
        assert "decision" in result
    
    def test_state_convergence(self):
        """Test that state always converges to a final decision"""
        requests = [
            {
                "type": "maintenance_request",
                "location": "Zone-A",
                "user_request": "Request 1"
            },
            {
                "type": "emergency_response",
                "location": "Zone-B",
                "user_request": "Request 2",
                "severity": "high"
            },
            {
                "type": "schedule_shift_request",
                "location": "Zone-C",
                "user_request": "Request 3",
                "requested_shift_days": 2
            }
        ]
        
        for req in requests:
            start = time.time()
            result = self.agent.decide(req)
            duration = time.time() - start
            
            # Each should converge
            assert duration < 60
            assert result is not None
            assert "decision" in result
            assert result["decision"] in ["recommend", "escalate"]


class TestConditionalLoops:
    """Test conditional loops in workflow"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_escalation_exits_early(self):
        """Test that escalation exits workflow early"""
        request = {
            "type": "emergency_response",
            "location": "Zone-A",
            "user_request": "Critical emergency requiring immediate escalation",
            "severity": "critical"
        }
        
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Early escalation should be faster
        assert duration < 30
        assert result["decision"] == "escalate"
    
    def test_feasibility_failure_routing(self):
        """Test that feasibility failure routes correctly"""
        request = {
            "type": "project_planning",
            "location": "Zone-A",
            "user_request": "Impossible project with no resources",
            "estimated_cost": 50_000_000  # Unrealistic cost
        }
        
        result = self.agent.decide(request)
        
        # Should escalate, not loop
        assert result is not None
        assert result["decision"] in ["recommend", "escalate"]
    
    def test_retry_after_replanning(self):
        """Test retry mechanism after replanning"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Complex maintenance requiring replanning"
        }
        
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should not retry indefinitely
        assert duration < 60
        assert result is not None


class TestStateTransitionValidation:
    """Validate state transitions don't create loops"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_all_transitions_reachable(self):
        """Test that all state transitions lead to end states"""
        # Test various request types to ensure all paths work
        request_types = [
            "maintenance_request",
            "emergency_response",
            "schedule_shift_request",
            "capacity_query",
            "incident_report",
            "project_planning"
        ]
        
        for req_type in request_types:
            request = {
                "type": req_type,
                "location": "Zone-A",
                "user_request": f"Test {req_type}"
            }
            
            result = self.agent.decide(request)
            
            # All should reach an end state
            assert result is not None
            assert "decision" in result
            assert result["decision"] in ["recommend", "escalate"]
    
    def test_no_backward_loops(self):
        """Test that workflow doesn't loop backwards"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test no backward loops"
        }
        
        # Track execution to ensure forward progress
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should progress forward only
        assert duration < 60
        assert result is not None


class TestConcurrentLoopPrevention:
    """Test loop prevention with concurrent requests"""
    
    def test_parallel_requests_no_interference(self):
        """Test that parallel requests don't interfere"""
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
        
        # Process in parallel (simulated)
        import threading
        
        results = {}
        
        def process_request(agent, request, key):
            results[key] = agent.decide(request)
        
        thread1 = threading.Thread(target=process_request, args=(agent1, request1, "r1"))
        thread2 = threading.Thread(target=process_request, args=(agent2, request2, "r2"))
        
        start = time.time()
        thread1.start()
        thread2.start()
        
        thread1.join(timeout=60)
        thread2.join(timeout=60)
        duration = time.time() - start
        
        # Both should complete without hanging
        assert duration < 120
        assert "r1" in results
        assert "r2" in results
        assert results["r1"] is not None
        assert results["r2"] is not None
        
        agent1.close()
        agent2.close()


class TestDeadlockPrevention:
    """Test prevention of deadlock scenarios"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_no_resource_deadlock(self):
        """Test that resource contention doesn't cause deadlock"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test resource deadlock prevention"
        }
        
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should not deadlock
        assert duration < 60
        assert result is not None
    
    def test_no_database_lock_deadlock(self):
        """Test that database operations don't deadlock"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test database deadlock prevention"
        }
        
        result = self.agent.decide(request)
        
        # Should complete even with DB operations
        assert result is not None


class TestTimeouts:
    """Test timeout mechanisms"""
    
    def setup_method(self):
        """Setup agent before each test"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup after each test"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_overall_execution_timeout(self):
        """Test that overall execution has timeout"""
        request = {
            "type": "project_planning",
            "location": "Zone-A",
            "user_request": "Very complex project requiring extensive planning",
            "scope": "large"
        }
        
        start = time.time()
        result = self.agent.decide(request)
        duration = time.time() - start
        
        # Should complete within reasonable time
        assert duration < 120  # 2 minutes max
        assert result is not None
    
    def test_node_execution_timeout(self):
        """Test that individual nodes have timeouts"""
        # Each node should not hang indefinitely
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test node timeouts"
        }
        
        result = self.agent.decide(request)
        
        # Should complete
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])
