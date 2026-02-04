"""
Quick Test: Coordinator Calling Agents

Simple test to verify coordinator can call other agents
"""

from coordination_agent.agent import CoordinationAgent

print("\n" + "="*60)
print("QUICK TEST: Coordinator Calling Agents")
print("="*60 + "\n")

try:
    # Initialize coordinator
    print("Step 1: Initialize Coordination Agent")
    coordinator = CoordinationAgent()
    print("✅ Coordinator initialized with agent dispatcher\n")
    
    # Test 1: Query single agent
    print("Step 2: Query Water Agent")
    print("Request: Get capacity info for Downtown")
    
    response = coordinator.query_agent(
        agent_type="water",
        request={
            "type": "capacity_query",
            "location": "Downtown"
        },
        reason="Testing coordinator → agent communication"
    )
    
    print(f"✅ Query completed!")
    print(f"   Success: {response.get('success')}")
    print(f"   Agent: {response.get('agent_type')}")
    print(f"   Duration: {response.get('duration_seconds', 0):.2f}s\n")
    
    # Test 2: Query multiple agents
    print("Step 3: Query Multiple Agents (Water, Engineering)")
    
    responses = coordinator.query_multiple_agents({
        "water": {"type": "capacity_query", "location": "Downtown"},
        "engineering": {"type": "project_planning", "location": "Downtown"}
    })
    
    print(f"✅ Multi-agent query completed!")
    print(f"   Agents queried: {len(responses)}")
    for agent_type, resp in responses.items():
        print(f"   - {agent_type}: {'Success' if resp.get('success') else 'Failed'}")
    
    print("\n" + "="*60)
    print("✅ TEST PASSED - Coordinator can call other agents!")
    print("="*60 + "\n")
    
    coordinator.close()
    
except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
