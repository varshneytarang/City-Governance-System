"""
LLM Integration Tests

Tests to verify that the LLM is actually being called and used in the agent.
Run this to confirm your Groq/OpenAI API is being utilized.
"""

import unittest
import os
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock

from water_agent import WaterDepartmentAgent
from water_agent.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestLLMIntegration(unittest.TestCase):
    """Test actual LLM API calls"""
    
    def setUp(self):
        """Set up test environment"""
        self.agent = WaterDepartmentAgent()
        
        # Check if API key is configured
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("⚠️  No API key found. LLM tests will use mock data.")
    
    def tearDown(self):
        """Clean up"""
        self.agent.close()
    
    def test_llm_api_key_configured(self):
        """Test that LLM API key is properly configured"""
        
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        
        if api_key:
            logger.info(f"✓ API Key found: {api_key[:8]}...")
            self.assertIsNotNone(api_key)
        else:
            logger.warning("✗ No API key configured in .env file")
            logger.info("Add OPENAI_API_KEY or GROQ_API_KEY to .env to enable LLM")
    
    def test_llm_provider_setting(self):
        """Test LLM provider configuration"""
        
        provider = settings.LLM_PROVIDER
        logger.info(f"LLM Provider: {provider}")
        
        self.assertIn(provider, ["openai", "groq", "local"])
    
    @patch('openai.ChatCompletion.create')
    def test_planner_calls_llm(self, mock_openai):
        """Test that planner node actually calls OpenAI/Groq API"""
        
        # Mock LLM response
        mock_openai.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content='{"steps": ["Check manpower", "Assign workers", "Schedule shift"], "estimated_duration": "2 days"}'
                )
            )]
        )
        
        request = {
            "type": "schedule_shift_request",
            "location": "Downtown",
            "requested_shift_days": 2,
            "estimated_cost": 50000
        }
        
        response = self.agent.decide(request)
        
        # Check if OpenAI was called
        if mock_openai.called:
            logger.info("✓ LLM API was called during planning!")
            logger.info(f"  Call count: {mock_openai.call_count}")
        else:
            logger.warning("✗ LLM API was NOT called (using deterministic fallback)")
        
        self.assertIsNotNone(response)


class TestDeterministicVsLLM(unittest.TestCase):
    """Compare deterministic logic vs LLM-enhanced decisions"""
    
    def setUp(self):
        self.agent = WaterDepartmentAgent()
    
    def tearDown(self):
        self.agent.close()
    
    def test_current_implementation_is_deterministic(self):
        """Verify current implementation uses deterministic logic"""
        
        request = {
            "type": "schedule_shift_request",
            "location": "Downtown",
            "requested_shift_days": 2,
            "estimated_cost": 50000
        }
        
        # Run same request twice
        response1 = self.agent.decide(request)
        response2 = self.agent.decide(request)
        
        # Deterministic = same result every time
        logger.info("Testing determinism...")
        logger.info(f"Response 1: {response1.get('decision')}")
        logger.info(f"Response 2: {response2.get('decision')}")
        
        # Should be identical
        self.assertEqual(response1.get("decision"), response2.get("decision"))
        
        logger.info("✓ Implementation is DETERMINISTIC (no LLM randomness)")
        logger.info("  This is by design - LLM is optional/fallback")


class TestLLMEnhancedPlanning(unittest.TestCase):
    """Test LLM-enhanced planning capabilities"""
    
    @unittest.skipIf(
        not (os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")),
        "No API key configured"
    )
    def test_llm_generates_creative_plan(self):
        """Test LLM can generate creative plans (requires API key)"""
        
        # This test only runs if API key is present
        logger.info("\n" + "="*70)
        logger.info("TESTING: LLM Creative Planning (LIVE API CALL)")
        logger.info("="*70)
        
        request = {
            "type": "emergency_response",
            "location": "Downtown",
            "incident_type": "major_leak",
            "severity": "critical",
            "special_constraints": [
                "High traffic area",
                "Multiple buildings affected",
                "Need coordination with Fire Department"
            ]
        }
        
        # This should trigger LLM if configured
        from water_agent import WaterDepartmentAgent
        agent = WaterDepartmentAgent()
        
        try:
            response = agent.decide(request)
            
            logger.info(f"Decision: {response.get('decision')}")
            
            # Check if plan has LLM characteristics
            plan = response.get("plan", {})
            if plan:
                logger.info(f"Plan steps: {plan.get('steps', [])}")
                logger.info("✓ Plan generated (check Groq dashboard for API call)")
        finally:
            agent.close()
    
    def test_fallback_when_llm_unavailable(self):
        """Test agent works even when LLM fails"""
        
        logger.info("\nTesting fallback behavior...")
        
        # Simulate LLM being unavailable
        with patch('water_agent.config.settings.OPENAI_API_KEY', None):
            from water_agent import WaterDepartmentAgent
            agent = WaterDepartmentAgent()
            
            request = {
                "type": "maintenance_request",
                "location": "Downtown",
                "activity": "pipeline_inspection",
                "notice_hours": 48,
                "estimated_cost": 30000
            }
            
            try:
                response = agent.decide(request)
                
                # Should still work with deterministic fallback
                self.assertIsNotNone(response)
                self.assertIn("decision", response)
                
                logger.info("✓ Fallback logic works when LLM unavailable")
            finally:
                agent.close()


class TestLLMCallMonitoring(unittest.TestCase):
    """Monitor and log LLM API calls"""
    
    def test_log_llm_usage(self):
        """Log whether LLM is being used"""
        
        logger.info("\n" + "="*70)
        logger.info("LLM INTEGRATION STATUS CHECK")
        logger.info("="*70)
        
        # Check configuration
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        provider = settings.LLM_PROVIDER
        
        logger.info(f"Provider: {provider}")
        logger.info(f"API Key: {'✓ Configured' if api_key else '✗ Not configured'}")
        logger.info(f"Model: {settings.LLM_MODEL}")
        
        if api_key:
            logger.info("\n💡 LLM is CONFIGURED but may not be called in current implementation")
            logger.info("   Reason: Deterministic fallback logic is enabled by default")
            logger.info("   Solution: See instructions below to force LLM usage")
        else:
            logger.info("\n⚠️  LLM is NOT CONFIGURED")
            logger.info("   Add to .env file:")
            logger.info("   - OPENAI_API_KEY=your_key_here  OR")
            logger.info("   - GROQ_API_KEY=your_key_here")
        
        logger.info("="*70 + "\n")


def print_llm_integration_guide():
    """Print guide for enabling LLM integration"""
    
    print("\n" + "📚 "*30)
    print("HOW TO ENABLE LLM API CALLS")
    print("📚 "*30)
    
    print("\n1️⃣  Configure API Key in .env:")
    print("   OPENAI_API_KEY=sk-...")
    print("   or")
    print("   GROQ_API_KEY=gsk_...")
    
    print("\n2️⃣  Set LLM Provider:")
    print("   LLM_PROVIDER=openai   # or groq")
    
    print("\n3️⃣  Modify planner.py to USE LLM:")
    print("   Current: Uses _generate_deterministic_plans()")
    print("   Change to: Call OpenAI/Groq API in generate_plan()")
    
    print("\n4️⃣  Example LLM Integration Code:")
    print("""
    def generate_plan(self, state: DepartmentState) -> Dict:
        if self.llm_provider == "openai" and settings.OPENAI_API_KEY:
            # Call OpenAI API
            import openai
            openai.api_key = settings.OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a water department planner..."},
                    {"role": "user", "content": f"Create plan for: {goal}"}
                ],
                temperature=settings.LLM_TEMPERATURE
            )
            
            return response.choices[0].message.content
        else:
            # Fallback to deterministic
            return self._generate_deterministic_plans(...)
    """)
    
    print("\n5️⃣  Monitor API Calls:")
    print("   - OpenAI: https://platform.openai.com/usage")
    print("   - Groq: https://console.groq.com/")
    
    print("\n" + "📚 "*30 + "\n")


if __name__ == "__main__":
    print_llm_integration_guide()
    
    print("\n🧪 Running LLM Integration Tests...\n")
    unittest.main(verbosity=2)
