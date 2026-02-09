"""
Integration Tests with Rate Limiting

Tests complete workflows while respecting API rate limits (30 req/min).
"""

import pytest
import time
from agents.water_agent.agent import WaterDepartmentAgent

# Rate limiting configuration - Groq allows 30 requests per minute
RATE_LIMIT_DELAY = 2.1  # Seconds between requests (30/60 = 0.5, use 2.1 for safety)


@pytest.mark.integration
@pytest.mark.slow
class TestWorkflowIntegration:
    """Integration tests for complete workflows"""
    
    def test_simple_maintenance_request(self):
        """Test end-to-end maintenance workflow"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "maintenance_request",
            "description": "Routine pipe inspection in sector 5",
            "priority": "low",
            "location": "sector_5"
        }
        
        result = agent.decide(request)
        
        assert result is not None
        assert "decision" in result
        assert result["decision"] in ["execute", "escalate", "replan"]
    
    def test_emergency_response_workflow(self):
        """Test emergency handling workflow"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "emergency_response",
            "description": "Major water main break on Oak Street",
            "severity": "critical",
            "urgency": "immediate",
            "location": "oak_street"
        }
        
        result = agent.decide(request)
        
        assert result is not None
        assert "decision" in result
        # Emergency should either execute immediately or escalate if too complex
        assert result["decision"] in ["execute", "escalate"]
    
    def test_high_cost_escalation(self):
        """Test that high-cost requests get escalated"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "infrastructure_upgrade",
            "description": "Replace all pipes in downtown district",
            "estimated_cost": 5000000,  # Very high cost
            "priority": "medium"
        }
        
        result = agent.decide(request)
        
        assert result is not None
        assert "decision" in result
        # High-cost projects should escalate
        assert result["decision"] == "escalate"
    
    def test_low_confidence_escalation(self):
        """Test that unclear requests get escalated"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "unknown_request",
            "description": "Something unclear happening",
            "data": "incomplete information"
        }
        
        result = agent.decide(request)
        
        assert result is not None
        assert "decision" in result
        # Unclear requests should escalate or ask for clarification
        assert result["decision"] in ["escalate", "replan"]
    
    def test_policy_violation_handling(self):
        """Test handling of policy violations"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "maintenance_request",
            "description": "Unauthorized modification to water main",
            "priority": "high",
            "policy_override": True  # Attempting to override policy
        }
        
        result = agent.decide(request)
        
        assert result is not None
        # Policy violations should escalate
        if "policy_compliant" in result:
            if result["policy_compliant"] == False:
                assert result["decision"] == "escalate"


@pytest.mark.integration
@pytest.mark.slow
class TestErrorHandling:
    """Test error handling in workflows"""
    
    def test_malformed_request(self):
        """Test handling of malformed requests"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {}  # Empty request
        
        result = agent.decide(request)
        
        # Should handle gracefully, not crash
        assert result is not None
    
    def test_missing_required_fields(self):
        """Test handling of incomplete requests"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "maintenance_request"
            # Missing description, priority, etc.
        }
        
        result = agent.decide(request)
        
        # Should still process
        assert result is not None
    
    def test_invalid_data_types(self):
        """Test handling of invalid data types"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "maintenance_request",
            "description": 12345,  # Should be string
            "priority": ["invalid"],  # Should be string
        }
        
        result = agent.decide(request)
        
        # Should handle gracefully
        assert result is not None


@pytest.mark.integration
class TestWorkflowPaths:
    """Test different workflow execution paths"""
    
    def test_execute_path(self):
        """Test workflow that leads to execution"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "maintenance_request",
            "description": "Replace valve at intersection A",
            "priority": "medium",
            "estimated_cost": 500,  # Low cost
            "location": "intersection_a"
        }
        
        result = agent.decide(request)
        
        assert result is not None
        # Low-cost, clear request should execute
        assert result["decision"] in ["execute", "replan"]
    
    def test_replan_path(self):
        """Test workflow that requires replanning"""
        time.sleep(RATE_LIMIT_DELAY)  # Respect rate limit
        
        agent = WaterDepartmentAgent()
        request = {
            "type": "maintenance_request",
            "description": "Complex multi-phase infrastructure project",
            "priority": "medium",
            "phases": 10,  # Complex
            "dependencies": ["phase1", "phase2", "phase3"]
        }
        
        result = agent.decide(request)
        
        assert result is not None
        # Complex requests might need replanning
        assert result["decision"] in ["replan", "escalate", "execute"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
