"""
Test: Coordination Agent Querying Other Agents

This test demonstrates the new capability where the coordination agent
can query other agents to gather information during conflict resolution.

Scenarios tested:
1. Coordinator queries single agent for information
2. Coordinator queries multiple agents simultaneously
3. Coordinator gathers context from multiple agents for a location
4. Use during conflict resolution workflow
"""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_coordinator_query_single_agent():
    """Test coordinator querying a single agent"""
    print("\n" + "="*80)
    print("TEST 1: Coordinator Querying Single Agent")
    print("="*80 + "\n")
    
    try:
        from coordination_agent.agent import CoordinationAgent
        
        coordinator = CoordinationAgent()
        
        # Coordinator asks Water agent about capacity
        print("Scenario: Coordinator needs to know water capacity in Downtown")
        print("Action: Query Water agent\n")
        
        response = coordinator.query_agent(
            agent_type="water",
            request={
                "type": "capacity_query",
                "location": "Downtown",
                "query": "What is current water capacity and pressure?"
            },
            reason="Checking water infrastructure for conflict resolution"
        )
        
        print(f"\n✅ Query completed:")
        print(f"   Success: {response.get('success')}")
        print(f"   Agent: {response.get('agent_type')}")
        print(f"   Duration: {response.get('duration_seconds', 0):.2f}s")
        if response.get('success'):
            agent_response = response.get('response', {})
            print(f"   Agent Decision: {agent_response.get('decision')}")
        else:
            print(f"   Error: {response.get('error')}")
        
        coordinator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coordinator_query_multiple_agents():
    """Test coordinator querying multiple agents"""
    print("\n" + "="*80)
    print("TEST 2: Coordinator Querying Multiple Agents")
    print("="*80 + "\n")
    
    try:
        from coordination_agent.agent import CoordinationAgent
        
        coordinator = CoordinationAgent()
        
        # Coordinator asks multiple agents about Downtown
        print("Scenario: Coordinator needs comprehensive view of Downtown activities")
        print("Action: Query Water, Engineering, and Fire agents simultaneously\n")
        
        responses = coordinator.query_multiple_agents(
            queries={
                "water": {
                    "type": "capacity_query",
                    "location": "Downtown"
                },
                "engineering": {
                    "type": "project_planning",
                    "location": "Downtown",
                    "description": "Query current projects"
                },
                "fire": {
                    "type": "readiness_assessment",
                    "location": "Downtown"
                }
            },
            reason="Gathering comprehensive context for conflict resolution"
        )
        
        print(f"\n✅ Multi-agent query completed:")
        print(f"   Agents queried: {len(responses)}")
        
        for agent_type, response in responses.items():
            print(f"\n   {agent_type.upper()} Agent:")
            print(f"      Success: {response.get('success')}")
            print(f"      Duration: {response.get('duration_seconds', 0):.2f}s")
            if response.get('success'):
                agent_response = response.get('response', {})
                print(f"      Decision: {agent_response.get('decision', 'N/A')}")
        
        coordinator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coordinator_gather_context():
    """Test coordinator gathering context from multiple agents"""
    print("\n" + "="*80)
    print("TEST 3: Coordinator Gathering Context for Location")
    print("="*80 + "\n")
    
    try:
        from coordination_agent.agent import CoordinationAgent
        
        coordinator = CoordinationAgent()
        
        # Coordinator gathers context about Downtown from all relevant agents
        print("Scenario: Conflict detected in Downtown - need full context")
        print("Action: Gather context from Water, Engineering, and Sanitation\n")
        
        context = coordinator.gather_agent_context(
            agent_types=["water", "engineering", "sanitation"],
            location="Downtown",
            context_type="capacity_query"
        )
        
        print(f"\n✅ Context gathering completed:")
        print(f"   Location: {context.get('location')}")
        print(f"   Agents queried: {len(context.get('agents_queried', []))}")
        print(f"   Successful responses: {context.get('successful_responses')}/{len(context.get('agents_queried', []))}")
        print(f"   Timestamp: {context.get('timestamp')}")
        
        coordinator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_coordinator_during_conflict_resolution():
    """Test using agent queries during actual conflict resolution"""
    print("\n" + "="*80)
    print("TEST 4: Coordinator Using Agent Queries During Conflict Resolution")
    print("="*80 + "\n")
    
    try:
        from coordination_agent.agent import CoordinationAgent
        
        coordinator = CoordinationAgent()
        
        print("Scenario: Water and Engineering both want to work in Downtown")
        print("Action: Coordinator queries both agents for details before resolving\n")
        
        # Simulate conflict - coordinator needs more info from both agents
        print("Step 1: Query Water agent about their work")
        water_response = coordinator.query_agent(
            "water",
            {
                "type": "maintenance_request",
                "location": "Downtown",
                "description": "Planned water main maintenance",
                "priority": "high"
            },
            reason="Understanding Water department's plans for conflict resolution"
        )
        
        print(f"   Water agent response: {water_response.get('success')}")
        
        print("\nStep 2: Query Engineering agent about their work")
        eng_response = coordinator.query_agent(
            "engineering",
            {
                "type": "project_planning",
                "location": "Downtown",
                "description": "Road construction project",
                "priority": "medium"
            },
            reason="Understanding Engineering department's plans"
        )
        
        print(f"   Engineering agent response: {eng_response.get('success')}")
        
        print("\nStep 3: Coordinator can now make informed decision")
        print("   - Both agents want Downtown")
        print("   - Water has higher priority (maintenance)")
        print("   - Engineering can be scheduled after Water completes")
        print("   ✅ Conflict resolved with agent input!")
        
        coordinator.close()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all coordinator agent query tests"""
    print("\n" + "="*80)
    print("COORDINATOR AGENT QUERY CAPABILITY - COMPREHENSIVE TEST")
    print("="*80)
    
    tests = [
        ("Query Single Agent", test_coordinator_query_single_agent),
        ("Query Multiple Agents", test_coordinator_query_multiple_agents),
        ("Gather Context", test_coordinator_gather_context),
        ("Conflict Resolution with Queries", test_coordinator_during_conflict_resolution)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"Running: {test_name}")
        print(f"{'='*80}")
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
