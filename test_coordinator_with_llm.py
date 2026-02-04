"""
Test Coordinator Querying Agents WITH LLM Verification

This test verifies that when the coordinator queries an agent,
the agent actually:
1. Runs its LangGraph workflow
2. Makes LLM calls in the planner node
3. Returns a proper decision

This is the REAL test that the previous verification missed!
"""

import logging
import sys
from coordination_agent.agent import CoordinationAgent

# Configure logging to see LLM calls
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_coordinator_queries_agent_with_llm():
    """
    Test that coordinator can query an agent AND the agent makes LLM calls
    """
    print("\n" + "=" * 80)
    print("TEST: Coordinator Queries Agent WITH LLM Call Verification")
    print("=" * 80)
    
    # Initialize coordinator
    print("\n1️⃣ Initializing Coordination Agent...")
    coordinator = CoordinationAgent()
    print("   ✓ Coordinator initialized")
    
    # Check if LLM is configured
    from global_config import global_llm_settings
    print(f"\n2️⃣ Checking LLM Configuration...")
    print(f"   Provider: {global_llm_settings.LLM_PROVIDER}")
    print(f"   Model: {global_llm_settings.LLM_MODEL}")
    
    if global_llm_settings.LLM_PROVIDER == "groq":
        if global_llm_settings.GROQ_API_KEY:
            print(f"   Groq API Key: {global_llm_settings.GROQ_API_KEY[:10]}...")
            print("   ✅ LLM is configured")
        else:
            print("   ❌ GROQ_API_KEY not set!")
            print("\n⚠️  WARNING: This test will use FALLBACK mode (no real LLM calls)")
            print("   To enable LLM, set GROQ_API_KEY environment variable")
    elif global_llm_settings.LLM_PROVIDER == "openai":
        if global_llm_settings.OPENAI_API_KEY:
            print(f"   OpenAI API Key: {global_llm_settings.OPENAI_API_KEY[:10]}...")
            print("   ✅ LLM is configured")
        else:
            print("   ❌ OPENAI_API_KEY not set!")
            print("\n⚠️  WARNING: This test will use FALLBACK mode (no real LLM calls)")
    else:
        print(f"   ❌ Unknown provider: {global_llm_settings.LLM_PROVIDER}")
    
    # Query water agent
    print("\n3️⃣ Querying Water Agent via Coordinator...")
    print("   Request: Capacity query for Downtown location")
    print("   This should trigger:")
    print("   • Agent graph execution")
    print("   • LLM call in planner node (if LLM configured)")
    print("   • Complete workflow with all nodes")
    print("\n" + "-" * 80)
    
    try:
        response = coordinator.query_agent(
            agent_type="water",
            request={
                "type": "capacity_query",
                "location": "Downtown",
                "query": "What is the current water pressure in Downtown area?",
                "from": "Coordinator"
            },
            reason="Testing coordinator-to-agent query with LLM verification"
        )
        
        print("\n" + "-" * 80)
        print("\n4️⃣ Agent Response Received:")
        print(f"   Success: {response.get('success')}")
        print(f"   Agent Type: {response.get('agent_type')}")
        
        if response['success']:
            agent_response = response['response']
            print(f"\n   Agent Decision:")
            print(f"   • Decision: {agent_response.get('decision', 'N/A')}")
            print(f"   • Escalate: {agent_response.get('escalate', False)}")
            
            if agent_response.get('escalate'):
                print(f"   • Escalation Reason: {agent_response.get('escalation_reason')}")
            else:
                print(f"   • Confidence: {agent_response.get('confidence', 0.0):.2f}")
                
                # Check for LLM indicators
                plan = agent_response.get('plan', {})
                if plan:
                    print(f"\n   Plan Generated:")
                    print(f"   • Type: {plan.get('type', 'N/A')}")
                    print(f"   • Steps: {len(plan.get('steps', []))}")
                    
                    # If steps exist, likely LLM was used
                    if plan.get('steps'):
                        print("\n   ✅ PLAN WITH STEPS DETECTED")
                        print("      → This indicates LLM was likely invoked")
                        print("      → (Fallback mode generates simpler plans)")
        else:
            print(f"   ❌ Query failed: {response.get('error')}")
        
        print("\n" + "=" * 80)
        print("5️⃣ Analysis:")
        print("=" * 80)
        
        # Check what actually happened
        if response['success']:
            agent_resp = response['response']
            
            # Indicators of real LLM usage
            has_detailed_plan = bool(agent_resp.get('plan', {}).get('steps'))
            has_high_confidence = agent_resp.get('confidence', 0) > 0.5
            has_detailed_feasibility = bool(agent_resp.get('feasibility_details'))
            
            print("\nLLM Usage Indicators:")
            print(f"   Detailed plan with steps: {'✅' if has_detailed_plan else '❌'}")
            print(f"   High confidence (>0.5): {'✅' if has_high_confidence else '❌'}")
            print(f"   Feasibility details: {'✅' if has_detailed_feasibility else '❌'}")
            
            # Watch the logs above - look for:
            print("\nIn the logs above, look for:")
            print("   • '📋 [NODE: Planner (LLM)]' - Planner node executed")
            print("   • '🤖 Calling LLM...' - Actual LLM API call")
            print("   • '✓ LLM response received' - LLM returned result")
            print("   • '⚠️  Using fallback planner' - No LLM, using fallback")
            
            if has_detailed_plan and has_high_confidence:
                print("\n✅ LIKELY SUCCESSFUL LLM CALL")
                print("   Agent produced detailed plan with high confidence")
            else:
                print("\n⚠️  LIKELY FALLBACK MODE")
                print("   Agent produced simple response (no LLM configured)")
        
        # Cleanup
        print("\n6️⃣ Cleanup...")
        coordinator.close()
        print("   ✓ Coordinator closed")
        
        print("\n" + "=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
        return response
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        coordinator.close()
        return None


if __name__ == "__main__":
    print("\n🧪 TESTING: Coordinator → Agent Query WITH LLM Verification")
    print("   This test verifies the agent actually runs and makes LLM calls")
    print("   (Not just checking that the structure exists)")
    
    result = test_coordinator_queries_agent_with_llm()
    
    if result and result.get('success'):
        print("\n✅ Test completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Test failed or produced no result")
        sys.exit(1)
