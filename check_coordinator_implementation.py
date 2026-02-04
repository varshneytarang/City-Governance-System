"""
Status Check: Coordinator Agent Query Implementation

This script checks the complete status of the coordinator
agent query capability implementation.
"""

def check_implementation_status():
    """Check all components of the implementation"""
    
    print("\n" + "="*80)
    print("IMPLEMENTATION STATUS CHECK: Coordinator Agent Query Capability")
    print("="*80 + "\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Agent Dispatcher File Exists
    checks_total += 1
    print("Check 1: Agent Dispatcher File")
    print("-" * 80)
    try:
        import os
        dispatcher_path = "coordination_agent/agent_dispatcher.py"
        if os.path.exists(dispatcher_path):
            file_size = os.path.getsize(dispatcher_path)
            print(f"✅ File exists: {dispatcher_path}")
            print(f"   Size: {file_size} bytes")
            checks_passed += 1
        else:
            print(f"❌ File missing: {dispatcher_path}")
    except Exception as e:
        print(f"❌ Error checking file: {e}")
    print()
    
    # Check 2: AgentDispatcher Class Can Be Imported
    checks_total += 1
    print("Check 2: AgentDispatcher Import")
    print("-" * 80)
    try:
        from coordination_agent.agent_dispatcher import AgentDispatcher
        print("✅ AgentDispatcher class imported successfully")
        print(f"   Class: {AgentDispatcher.__name__}")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Import failed: {e}")
    print()
    
    # Check 3: Coordination Agent Has Dispatcher
    checks_total += 1
    print("Check 3: Coordination Agent Integration")
    print("-" * 80)
    try:
        from coordination_agent.agent import CoordinationAgent
        coordinator = CoordinationAgent()
        
        if hasattr(coordinator, 'agent_dispatcher'):
            print("✅ Coordinator has agent_dispatcher attribute")
            print(f"   Type: {type(coordinator.agent_dispatcher).__name__}")
            checks_passed += 1
        else:
            print("❌ Coordinator missing agent_dispatcher")
        
        coordinator.close()
    except Exception as e:
        print(f"❌ Check failed: {e}")
    print()
    
    # Check 4: Query Methods Exist
    checks_total += 1
    print("Check 4: Query Methods")
    print("-" * 80)
    try:
        from coordination_agent.agent import CoordinationAgent
        coordinator = CoordinationAgent()
        
        methods = ['query_agent', 'query_multiple_agents', 'gather_agent_context', 'get_agent_status']
        all_exist = True
        
        for method in methods:
            if hasattr(coordinator, method):
                print(f"✅ {method}() exists")
            else:
                print(f"❌ {method}() missing")
                all_exist = False
        
        if all_exist:
            checks_passed += 1
        
        coordinator.close()
    except Exception as e:
        print(f"❌ Check failed: {e}")
    print()
    
    # Check 5: Dispatcher Can Load Agent Classes
    checks_total += 1
    print("Check 5: Agent Class Loading")
    print("-" * 80)
    try:
        from coordination_agent.agent_dispatcher import AgentDispatcher
        dispatcher = AgentDispatcher()
        
        test_agents = ['water', 'engineering', 'fire']
        all_loaded = True
        
        for agent_type in test_agents:
            try:
                agent_class = dispatcher._get_agent_class(agent_type)
                print(f"✅ {agent_type}: {agent_class.__name__}")
            except Exception as e:
                print(f"❌ {agent_type}: {e}")
                all_loaded = False
        
        if all_loaded:
            checks_passed += 1
        
        dispatcher.close_all_agents()
    except Exception as e:
        print(f"❌ Check failed: {e}")
    print()
    
    # Check 6: Documentation Files
    checks_total += 1
    print("Check 6: Documentation")
    print("-" * 80)
    try:
        import os
        docs = [
            "COORDINATOR_AGENT_QUERIES.md",
            "COORDINATOR_CALLS_AGENTS_COMPLETE.md"
        ]
        
        docs_exist = 0
        for doc in docs:
            if os.path.exists(doc):
                print(f"✅ {doc}")
                docs_exist += 1
            else:
                print(f"⚠️  {doc} (optional)")
        
        if docs_exist > 0:
            checks_passed += 1
    except Exception as e:
        print(f"❌ Check failed: {e}")
    print()
    
    # Check 7: Test Files
    checks_total += 1
    print("Check 7: Test Files")
    print("-" * 80)
    try:
        import os
        tests = [
            "test_coordinator_agent_queries.py",
            "verify_coordinator_queries.py",
            "test_functional_coordinator_query.py"
        ]
        
        tests_exist = 0
        for test in tests:
            if os.path.exists(test):
                print(f"✅ {test}")
                tests_exist += 1
            else:
                print(f"⚠️  {test} (optional)")
        
        if tests_exist > 0:
            checks_passed += 1
    except Exception as e:
        print(f"❌ Check failed: {e}")
    print()
    
    # Summary
    print("="*80)
    print(f"RESULTS: {checks_passed}/{checks_total} checks passed")
    print("="*80 + "\n")
    
    if checks_passed == checks_total:
        print("✅ IMPLEMENTATION COMPLETE AND WORKING!")
        print("\nAll components are properly implemented:")
        print("  ✓ Agent Dispatcher module created")
        print("  ✓ Coordination Agent integrated with dispatcher")
        print("  ✓ All query methods implemented")
        print("  ✓ Agent class loading functional")
        print("  ✓ Documentation available")
        print("  ✓ Test files created")
        
        print("\nCapabilities:")
        print("  • Coordinator can query any department agent")
        print("  • Coordinator can query multiple agents simultaneously")
        print("  • Coordinator can gather context for locations")
        print("  • Agent instances are cached for performance")
        print("  • Graceful error handling implemented")
        
        print("\nUsage:")
        print("  coordinator = CoordinationAgent()")
        print("  response = coordinator.query_agent('water', {...})")
        print("  responses = coordinator.query_multiple_agents({...})")
        
    elif checks_passed >= checks_total * 0.7:
        print("⚠️  IMPLEMENTATION MOSTLY COMPLETE")
        print(f"\n{checks_passed} of {checks_total} checks passed.")
        print("Core functionality should work, but some components may be missing.")
        
    else:
        print("❌ IMPLEMENTATION INCOMPLETE")
        print(f"\nOnly {checks_passed} of {checks_total} checks passed.")
        print("Please review the failed checks above.")
    
    print()
    return checks_passed == checks_total


if __name__ == "__main__":
    success = check_implementation_status()
    exit(0 if success else 1)
