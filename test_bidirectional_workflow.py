"""
Test Complete Bidirectional Workflow

This test verifies the complete loop:
1. Backend → Coordinator → Agent (query_agent)
2. Agent → Coordinator → Agent (coordination checkpoint during workflow)
3. Response back through the chain

This ensures there are no circular dependency issues or infinite loops.
"""

import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_complete_bidirectional_workflow():
    """
    Test the complete workflow:
    
    Backend → Coordinator.query_agent("water", request)
        ↓
    Coordinator → AgentDispatcher → WaterAgent.decide(request)
        ↓
    WaterAgent workflow → coordination_checkpoint_node
        ↓
    Creates NEW Coordinator → coordinator.check_plan_conflicts()
        ↓
    Checks database for conflicts
        ↓
    Returns conflict check result to Agent
        ↓
    Agent continues workflow
        ↓
    Returns decision to Coordinator
        ↓
    Returns response to Backend
    """
    
    print("\n" + "=" * 80)
    print("TEST: Complete Bidirectional Workflow")
    print("=" * 80)
    print("\nWorkflow:")
    print("  Backend")
    print("    ↓ coordinator.query_agent()")
    print("  Coordinator")
    print("    ↓ agent.decide()")
    print("  Water Agent")
    print("    ↓ coordination_checkpoint")
    print("  NEW Coordinator instance")
    print("    ↓ check_plan_conflicts()")
    print("  Database (check conflicts)")
    print("    ↓ return conflicts")
    print("  Agent continues")
    print("    ↓ return decision")
    print("  Response back to caller")
    print("\n" + "=" * 80)
    
    # Simulate backend calling coordinator
    print("\n1️⃣ Backend: Initializing Coordinator...")
    from coordination_agent.agent import CoordinationAgent
    
    coordinator = CoordinationAgent()
    print("   ✅ Coordinator initialized")
    
    # Simulate backend query
    print("\n2️⃣ Backend: Calling coordinator.query_agent()...")
    print("   Request: Water capacity query for Downtown")
    
    request = {
        "type": "capacity_query",
        "location": "Downtown",
        "query": "Check water pressure",
        "from": "Backend"
    }
    
    print("\n" + "-" * 80)
    print("STARTING AGENT WORKFLOW...")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        response = coordinator.query_agent(
            agent_type="water",
            request=request,
            reason="Backend bidirectional workflow test"
        )
        
        duration = time.time() - start_time
        
        print("\n" + "-" * 80)
        print("WORKFLOW COMPLETE")
        print("-" * 80)
        
        print(f"\n3️⃣ Response Received (took {duration:.2f}s):")
        print(f"   Success: {response.get('success')}")
        print(f"   Agent Type: {response.get('agent_type')}")
        
        if response['success']:
            agent_response = response['response']
            print(f"\n   Agent Decision:")
            print(f"   • Decision: {agent_response.get('decision', 'N/A')}")
            print(f"   • Requires Human: {agent_response.get('requires_human_review', False)}")
            
            details = agent_response.get('details', {})
            if details:
                print(f"\n   Details:")
                print(f"   • Feasible: {details.get('feasible', 'N/A')}")
                print(f"   • Policy Compliant: {details.get('policy_compliant', 'N/A')}")
                print(f"   • Confidence: {details.get('confidence', 0):.2f}")
        else:
            print(f"\n   ❌ Query failed: {response.get('error')}")
        
        print("\n" + "=" * 80)
        print("4️⃣ Analysis: Checking for Issues")
        print("=" * 80)
        
        # Check logs for coordination checkpoint execution
        print("\nLook in the logs above for:")
        print("  ✅ Should see: 'PHASE 6.5: Coordination Checkpoint'")
        print("  ✅ Should see: 'PROACTIVE CONFLICT CHECK - WATER'")
        print("  ✅ Should see: 'No conflicts detected' or 'CONFLICTS DETECTED'")
        print("  ❌ Should NOT see: Infinite loops, circular imports, or stack overflow")
        
        # Potential issues to watch for
        print("\nPotential Issues to Check:")
        print("  1. Multiple Coordinator Instances:")
        print("     • Agent creates NEW coordinator in checkpoint")
        print("     • This is OK if it closes properly")
        print("     • Check: Database connection warnings")
        
        print("\n  2. Circular Calls:")
        print("     • Coordinator → Agent → Coordinator → Agent (infinite loop)")
        print("     • This is PREVENTED because:")
        print("       - checkpoint only calls check_plan_conflicts() (not query_agent)")
        print("       - check_plan_conflicts() queries database (doesn't call agents)")
        
        print("\n  3. Resource Leaks:")
        print("     • Each checkpoint creates coordinator instance")
        print("     • Must call coordinator.close() after use")
        print("     • Check: Look for 'Database connection closed' messages")
        
        if response['success']:
            print("\n✅ WORKFLOW SUCCESSFUL")
            print("   • No infinite loops detected")
            print("   • Agent completed full workflow")
            print("   • Response returned successfully")
            return True
        else:
            print("\n⚠️  WORKFLOW FAILED")
            return False
        
    except RecursionError as e:
        print("\n❌ RECURSION ERROR - INFINITE LOOP DETECTED!")
        print(f"   Error: {e}")
        print("\n   This means:")
        print("   • Coordinator is calling agent")
        print("   • Agent is calling coordinator")
        print("   • Coordinator is calling agent again (loop)")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\n5️⃣ Cleanup...")
        coordinator.close()
        print("   ✅ Coordinator closed")


def test_potential_circular_issue():
    """
    Test if there's a circular dependency issue
    """
    
    print("\n" + "=" * 80)
    print("TEST: Circular Dependency Check")
    print("=" * 80)
    
    print("\n1️⃣ Testing Coordinator imports Agent classes...")
    try:
        from coordination_agent.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        print("   ✅ AgentDispatcher created successfully")
        
        # Try to get water agent class (lazy load)
        water_class = dispatcher._get_agent_class("water")
        print(f"   ✅ Water agent class loaded: {water_class.__name__}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n2️⃣ Testing Agent imports Coordinator...")
    try:
        # Simulate what coordination checkpoint does
        from coordination_agent import CoordinationAgent
        coord = CoordinationAgent()
        print("   ✅ Coordinator created from agent context")
        coord.close()
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n✅ NO CIRCULAR IMPORT ISSUES")
    return True


if __name__ == "__main__":
    print("\n🧪 TESTING: Complete Bidirectional Workflow")
    print("=" * 80)
    
    # Test 1: Circular imports
    test1 = test_potential_circular_issue()
    
    # Test 2: Full workflow
    test2 = test_complete_bidirectional_workflow()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Circular Dependency Check: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Complete Workflow:         {'✅ PASS' if test2 else '❌ FAIL'}")
    print("=" * 80)
    
    if test1 and test2:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nThe bidirectional workflow is working correctly:")
        print("  • Backend → Coordinator → Agent")
        print("  • Agent → Coordinator (checkpoint) → Database")
        print("  • Response flows back correctly")
        print("  • No circular dependencies")
        print("  • No infinite loops")
    else:
        print("\n⚠️  ISSUES DETECTED - See output above")
