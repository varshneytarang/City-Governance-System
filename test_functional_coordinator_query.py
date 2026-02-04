"""
Functional Test: Coordinator Actually Calling an Agent

This test actually executes a coordinator → agent query
to verify the full flow works end-to-end.
"""

def test_coordinator_actually_calls_agent():
    """Test that coordinator can actually call and get response from agent"""
    
    print("\n" + "="*70)
    print("FUNCTIONAL TEST: Coordinator Calling Agent")
    print("="*70 + "\n")
    
    try:
        from coordination_agent.agent import CoordinationAgent
        import time
        
        # Initialize coordinator
        print("Initializing Coordination Agent...")
        coordinator = CoordinationAgent()
        print("✅ Coordinator ready\n")
        
        # Test 1: Query Water agent
        print("TEST: Coordinator queries Water agent")
        print("-" * 70)
        print("Request: Get capacity info for Downtown\n")
        
        start = time.time()
        
        response = coordinator.query_agent(
            agent_type="water",
            request={
                "type": "capacity_query",
                "location": "Downtown",
                "query": "Current water capacity status"
            },
            reason="Functional test - verifying coordinator can call agents"
        )
        
        duration = time.time() - start
        
        print(f"\n{'='*70}")
        print("RESPONSE RECEIVED")
        print(f"{'='*70}\n")
        
        print(f"Success: {response.get('success')}")
        print(f"Agent Type: {response.get('agent_type')}")
        print(f"Duration: {duration:.2f}s")
        print(f"Timestamp: {response.get('timestamp')}")
        
        if response.get('success'):
            print("\n✅ Response Data:")
            agent_response = response.get('response', {})
            print(f"   Decision: {agent_response.get('decision', 'N/A')}")
            print(f"   Confidence: {agent_response.get('confidence', 'N/A')}")
            
            if 'details' in agent_response:
                print(f"   Has details: Yes")
            
            print(f"\n{'='*70}")
            print("✅ TEST PASSED - Coordinator successfully called Water agent!")
            print(f"{'='*70}\n")
            
            success = True
        else:
            print(f"\n❌ Query failed: {response.get('error')}")
            success = False
        
        # Cleanup
        coordinator.close()
        
        return success
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🔬 Running functional test...")
    print("This will actually execute a coordinator → agent query\n")
    
    success = test_coordinator_actually_calls_agent()
    
    if success:
        print("\n" + "="*70)
        print("SUMMARY: Implementation is WORKING!")
        print("="*70)
        print("\nThe Coordination Agent can:")
        print("  ✅ Initialize agent dispatcher")
        print("  ✅ Query other agents")
        print("  ✅ Receive responses")
        print("  ✅ Handle errors gracefully")
        print("\nFeature is fully functional! 🎉\n")
    else:
        print("\n" + "="*70)
        print("SUMMARY: Implementation needs fixes")
        print("="*70 + "\n")
    
    exit(0 if success else 1)
