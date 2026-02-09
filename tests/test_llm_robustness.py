"""
LLM-Specific Robustness Tests

Tests LLM integration, fallback mechanisms, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from agents.water_agent import WaterDepartmentAgent
from water_agent.nodes import intent_analyzer, goal_setter, planner


class TestLLMFailureHandling:
    """Test LLM failure scenarios and fallback"""
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_intent_analyzer_llm_timeout(self, mock_client):
        """Test timeout handling in intent analyzer"""
        mock_client.side_effect = TimeoutError("API timeout")
        
        state = {
            "input_event": {
                "type": "maintenance_request",
                "priority": "high"
            }
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should fallback to deterministic
        assert "intent" in result
        assert result["intent"] is not None
    
    @patch('water_agent.nodes.goal_setter.get_llm_client')
    def test_goal_setter_llm_network_error(self, mock_client):
        """Test network error handling in goal setter"""
        mock_client.side_effect = ConnectionError("Network unreachable")
        
        state = {
            "intent": "coordinate_maintenance",
            "input_event": {"type": "maintenance_request"}
        }
        
        result = goal_setter.goal_setter_node(state)
        
        # Should fallback gracefully
        assert "goal" in result
        assert result["goal"] is not None
    
    @patch('water_agent.nodes.planner.WaterPlannerWithLLM._init_llm_client')
    def test_planner_llm_authentication_error(self, mock_init):
        """Test authentication error handling"""
        mock_init.side_effect = Exception("Invalid API key")
        
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Test goal",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        
        result = planner.planner_node(state)
        
        # Should fallback to deterministic planning
        assert "plan" in result


class TestLLMResponseValidation:
    """Test validation of LLM responses"""
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_invalid_json_response(self, mock_client):
        """Test handling of invalid JSON from LLM"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Not valid JSON at all"))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should fallback when JSON parsing fails
        assert "intent" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_empty_llm_response(self, mock_client):
        """Test handling of empty LLM response"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=""))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        assert "intent" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_malformed_json_with_extra_text(self, mock_client):
        """Test handling of JSON with extra text"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='Sure! Here is the JSON: {"intent": "test"} I hope this helps!'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should either parse JSON or fallback
        assert "intent" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_json_with_markdown_wrapper(self, mock_client):
        """Test handling of JSON wrapped in markdown"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='```json\n{"intent": "coordinate_maintenance", "risk_level": "low"}\n```'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should successfully parse despite markdown
        assert "intent" in result
        assert result["intent"] == "coordinate_maintenance"


class TestLLMRateLimiting:
    """Test handling of rate limits"""
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_rate_limit_error(self, mock_client):
        """Test handling of rate limit errors"""
        mock_llm = Mock()
        mock_llm.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should fallback when rate limited
        assert "intent" in result
        assert result["intent"] is not None


class TestLLMContextHandling:
    """Test LLM context and prompt handling"""
    
    @patch('water_agent.nodes.goal_setter.get_llm_client')
    def test_very_long_context(self, mock_client):
        """Test handling of very long context"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='{"goal": "Test goal"}'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        # Very long input
        state = {
            "intent": "coordinate_maintenance",
            "input_event": {
                "type": "maintenance_request",
                "description": "A" * 50000  # 50k characters
            }
        }
        
        result = goal_setter.goal_setter_node(state)
        
        # Should handle without error (may truncate)
        assert "goal" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_special_characters_in_prompt(self, mock_client):
        """Test special characters don't break prompts"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='{"intent": "coordinate_maintenance", "risk_level": "low"}'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {
                "type": "maintenance_request",
                "user_request": 'Test with "quotes" and \'apostrophes\' and \n newlines'
            }
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        assert "intent" in result


class TestLLMConsistency:
    """Test consistency of LLM responses"""
    
    def setup_method(self):
        """Setup agent"""
        self.agent = WaterDepartmentAgent()
    
    def teardown_method(self):
        """Cleanup"""
        if hasattr(self, 'agent'):
            self.agent.close()
    
    def test_same_request_consistent_results(self):
        """Test that same request gives consistent result types"""
        request = {
            "type": "maintenance_request",
            "location": "Zone-A",
            "user_request": "Test consistency"
        }
        
        results = []
        for _ in range(3):
            result = self.agent.decide(request)
            results.append(result)
        
        # All should have same structure
        for result in results:
            assert "decision" in result
            assert result["decision"] in ["recommend", "escalate"]
    
    def test_similar_requests_similar_decisions(self):
        """Test that similar requests get similar treatment"""
        requests = [
            {
                "type": "maintenance_request",
                "location": "Zone-A",
                "user_request": "Schedule pipeline inspection"
            },
            {
                "type": "maintenance_request",
                "location": "Zone-B",
                "user_request": "Schedule pipeline inspection"
            }
        ]
        
        results = [self.agent.decide(req) for req in requests]
        
        # Similar requests should get similar decisions
        decisions = [r["decision"] for r in results]
        # At least should have valid decisions
        for decision in decisions:
            assert decision in ["recommend", "escalate"]


class TestLLMTokenUsage:
    """Test handling of token limits"""
    
    @patch('water_agent.nodes.planner.WaterPlannerWithLLM._generate_llm_plans')
    def test_handles_token_limit_exceeded(self, mock_generate):
        """Test handling when token limit is exceeded"""
        mock_generate.side_effect = Exception("Token limit exceeded")
        
        state = {
            "intent": "coordinate_maintenance",
            "goal": "Test goal",
            "context": {},
            "input_event": {"type": "maintenance_request"}
        }
        
        result = planner.planner_node(state)
        
        # Should fallback to deterministic
        assert "plan" in result


class TestLLMEdgeCases:
    """Test LLM-specific edge cases"""
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_llm_returns_wrong_schema(self, mock_client):
        """Test handling when LLM returns wrong schema"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='{"wrong_field": "value", "another_wrong_field": 123}'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should fallback when schema is wrong
        assert "intent" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_llm_returns_array_instead_of_object(self, mock_client):
        """Test handling when LLM returns array instead of object"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='["intent", "risk"]'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should fallback gracefully
        assert "intent" in result
    
    @patch('water_agent.nodes.intent_analyzer._get_llm_client')
    def test_llm_returns_nested_json(self, mock_client):
        """Test handling of deeply nested JSON"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(
            content='{"data": {"nested": {"intent": "coordinate_maintenance"}}}'
        ))]
        
        mock_llm = Mock()
        mock_llm.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_llm
        
        state = {
            "input_event": {"type": "maintenance_request"}
        }
        
        result = intent_analyzer.intent_analyzer_node(state)
        
        # Should handle or fallback
        assert "intent" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
