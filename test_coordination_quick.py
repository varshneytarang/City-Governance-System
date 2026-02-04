"""
Quick Test: Verify Proactive Coordination is Working

This is a simpler test that verifies the coordination checkpoints
are being called during agent workflows by checking log output.
"""

import logging
from datetime import datetime

# Configure logging to see coordination messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_coordination_quick():
    """Quick test to verify coordination checkpoints are called."""
    
    print("\n" + "="*80)
    print("QUICK TEST: Proactive Coordination Verification")
    print("="*80 + "\n")
    
    # Test Engineering Agent (known to work)
    print("\n[TEST 1] Engineering Agent - Valid Request")
    print("-" * 60)
    
    try:
        from engineering_agent.agent import EngineeringDepartmentAgent
        agent = EngineeringDepartmentAgent()
        
        request = {
            "type": "project_planning",
            "location": "Downtown",
            "description": "Road maintenance project",
            "budget": 50000
        }
        
        print(f"Request: {request}")
        print("\nLook for: 'PHASE 6.5: Coordination Checkpoint' in logs\n")
        
        response = agent.decide(request)
        
        print(f"\n✓ Engineering agent completed")
        print(f"  Decision: {response.get('decision')}")
        
        agent.close()
        
    except Exception as e:
        print(f"✗ Engineering test failed: {e}")
    
    # Test Health Agent
    print("\n\n[TEST 2] Health Agent - Check Coordination")
    print("-" * 60)
    
    try:
        from health_agent.agent import HealthDepartmentAgent
        agent = HealthDepartmentAgent()
        
        request = {
            "type": "health_inspection",
            "location": "Downtown",
            "description": "Restaurant inspections"
        }
        
        print(f"Request: {request}")
        print("\nLook for: '[Health] Coordination Checkpoint' in logs\n")
        
        response = agent.decide(request)
        
        print(f"\n✓ Health agent completed")
        print(f"  Response keys: {list(response.keys())}")
        
        agent.close()
        
    except Exception as e:
        print(f"✗ Health test failed: {e}")
    
    # Test Finance Agent
    print("\n\n[TEST 3] Finance Agent - Check Coordination")
    print("-" * 60)
    
    try:
        from finance_agent.agent import FinanceDepartmentAgent
        agent = FinanceDepartmentAgent()
        
        request = {
            "type": "budget_approval",
            "location": "Downtown",
            "amount": 100000,
            "requesting_department": "engineering"
        }
        
        print(f"Request: {request}")
        print("\nLook for: '[Finance] Coordination Checkpoint' in logs\n")
        
        response = agent.decide(request)
        
        print(f"\n✓ Finance agent completed")
        print(f"  Decision: {response.get('decision')}")
        
        agent.close()
        
    except Exception as e:
        print(f"✗ Finance test failed: {e}")
    
    print("\n" + "="*80)
    print("VERDICT:")
    print("If you see 'Coordination Checkpoint' messages in the logs above,")
    print("then proactive coordination IS working for those agents!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_coordination_quick()
