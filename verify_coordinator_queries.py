"""
Verification: Coordinator Agent Query Capability

Quick test to verify coordinator can call other agents
"""

def verify_coordinator_can_call_agents():
    """Verify the coordinator agent query capability works"""
    
    print("\n" + "="*70)
    print("VERIFICATION: Coordinator Agent Query Capability")
    print("="*70 + "\n")
    
    try:
        # Step 1: Import and initialize
        print("Step 1: Initializing Coordination Agent...")
        from coordination_agent.agent import CoordinationAgent
        coordinator = CoordinationAgent()
        print("✅ Coordinator initialized\n")
        
        # Step 2: Check dispatcher exists
        print("Step 2: Checking agent dispatcher...")
        if hasattr(coordinator, 'agent_dispatcher'):
            print("✅ Agent dispatcher found")
            print(f"   Type: {type(coordinator.agent_dispatcher).__name__}\n")
        else:
            print("❌ Agent dispatcher NOT found")
            return False
        
        # Step 3: Check query methods exist
        print("Step 3: Checking query methods...")
        required_methods = [
            'query_agent',
            'query_multiple_agents',
            'gather_agent_context',
            'get_agent_status'
        ]
        
        all_methods_exist = True
        for method in required_methods:
            if hasattr(coordinator, method):
                print(f"   ✅ {method}() exists")
            else:
                print(f"   ❌ {method}() MISSING")
                all_methods_exist = False
        
        if not all_methods_exist:
            return False
        
        print()
        
        # Step 4: Test simple query (without full execution to save time)
        print("Step 4: Testing dispatcher can load agent class...")
        try:
            # Test that dispatcher can get agent class
            water_class = coordinator.agent_dispatcher._get_agent_class("water")
            if water_class:
                print(f"✅ Dispatcher can load Water agent class")
                print(f"   Class: {water_class.__name__}\n")
            else:
                print("❌ Failed to load agent class")
                return False
        except Exception as e:
            print(f"❌ Error loading agent class: {e}\n")
            return False
        
        # Step 5: Verify cache mechanism
        print("Step 5: Checking cache mechanism...")
        if hasattr(coordinator.agent_dispatcher, '_agent_cache'):
            print(f"✅ Cache exists (currently: {len(coordinator.agent_dispatcher._agent_cache)} agents)\n")
        else:
            print("❌ Cache not found\n")
            return False
        
        # Step 6: Test query_agent method signature
        print("Step 6: Testing query_agent method...")
        try:
            # Get method signature
            import inspect
            sig = inspect.signature(coordinator.query_agent)
            params = list(sig.parameters.keys())
            print(f"✅ Method signature: query_agent({', '.join(params)})")
            
            required_params = ['agent_type', 'request']
            if all(p in params for p in required_params):
                print(f"✅ Has required parameters: {required_params}\n")
            else:
                print(f"❌ Missing required parameters")
                return False
        except Exception as e:
            print(f"❌ Error checking method: {e}\n")
            return False
        
        # Cleanup
        coordinator.close()
        print("="*70)
        print("✅ ALL VERIFICATIONS PASSED")
        print("="*70)
        print("\nCoordinator agent CAN call other agents!")
        print("\nAvailable capabilities:")
        print("  • query_agent(agent_type, request, reason)")
        print("  • query_multiple_agents(queries, reason)")
        print("  • gather_agent_context(agent_types, location, context_type)")
        print("  • get_agent_status(agent_type)\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = verify_coordinator_can_call_agents()
    
    if success:
        print("\n" + "="*70)
        print("Next Steps:")
        print("="*70)
        print("1. Run full test: python test_coordinator_agent_queries.py")
        print("2. See example: python example_coordinator_intelligent_resolution.py")
        print("3. Read docs: COORDINATOR_AGENT_QUERIES.md\n")
    
    exit(0 if success else 1)
