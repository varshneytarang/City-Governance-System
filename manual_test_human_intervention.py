"""
Manual Test Script - Terminal-Based Human Intervention

This script demonstrates the terminal-based human intervention
feature of the coordination agent.

Run this WITHOUT the auto-approve environment variable to test
real human input via terminal.

Usage:
    python manual_test_human_intervention.py
"""

from datetime import datetime
from coordination_agent import CoordinationAgent

def test_human_intervention_manual():
    """
    Manual test for terminal-based human intervention.
    
    This creates a high-cost, low-confidence scenario that
    triggers human escalation.
    """
    print("="*70)
    print("MANUAL TEST: Terminal-Based Human Intervention")
    print("="*70)
    print()
    print("This test will trigger human escalation and wait for your input.")
    print("You will see:")
    print("  - Escalation details")
    print("  - Conflict information")
    print("  - Decision options")
    print()
    print("Make sure COORDINATION_AUTO_APPROVE is NOT set to 'true'")
    print("="*70)
    print()
    
    import os
    if os.environ.get("COORDINATION_AUTO_APPROVE", "false").lower() == "true":
        print("[WARNING] Auto-approve is enabled!")
        print("Set: $env:COORDINATION_AUTO_APPROVE=\"false\" (PowerShell)")
        print("Or: unset COORDINATION_AUTO_APPROVE (bash)")
        print()
        proceed = input("Continue anyway? [y/n]: ").strip().lower()
        if proceed != 'y':
            print("Exiting...")
            return
    
    # Initialize coordinator
    coordinator = CoordinationAgent()
    
    print("\nInitializing scenario: High-cost city-wide infrastructure project")
    print("This will trigger human escalation due to high cost and low confidence.")
    print()
    
    # Create a scenario that triggers escalation
    decisions = [
        {
            "agent_id": "water_dept",
            "agent_type": "water",
            "decision": "recommend",
            "request": {
                "type": "major_infrastructure",
                "reason": "City-wide water pipeline replacement",
                "location": "City-Wide"
            },
            "confidence": 0.60,  # Below threshold (0.7)
            "constraints": {},
            "resources_needed": ["budget_capital", "workers_citywide"],
            "location": "City-Wide",
            "estimated_cost": 90000000,  # ₹9 crore (exceeds ₹50L limit)
            "priority": "expansion",
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent_id": "engineering_dept",
            "agent_type": "engineering",
            "decision": "recommend",
            "request": {
                "type": "infrastructure_upgrade",
                "reason": "Roads need expansion for water pipeline work",
                "location": "City-Wide"
            },
            "confidence": 0.65,
            "constraints": {},
            "resources_needed": ["budget_capital", "workers_citywide"],
            "location": "City-Wide",
            "estimated_cost": 70000000,  # ₹7 crore
            "priority": "maintenance",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("Scenario Details:")
    print("  - Water Department: ₹9 crore pipeline replacement (confidence: 0.60)")
    print("  - Engineering: ₹7 crore road expansion (confidence: 0.65)")
    print("  - Total Cost: ₹16 crore")
    print("  - Resource Conflict: Both need workers_citywide and budget_capital")
    print()
    print("This should trigger:")
    print("  1. High cost escalation (₹16 crore > ₹50L limit)")
    print("  2. Low confidence escalation (0.60 and 0.65 < 0.7 threshold)")
    print("  3. Resource conflict (same resources needed)")
    print()
    print("-"*70)
    print()
    
    input("Press ENTER to trigger coordination (you will be asked for approval)...")
    print()
    
    # Coordinate - this should trigger human intervention
    result = coordinator.coordinate(decisions)
    
    # Show result
    print()
    print("="*70)
    print("COORDINATION RESULT")
    print("="*70)
    print(f"Decision: {result['decision']}")
    print(f"Conflicts Detected: {result['conflicts_detected']}")
    print(f"Resolution Method: {result['resolution_method']}")
    print(f"Requires Human: {result['requires_human']}")
    print(f"Processing Time: {result['processing_time']:.2f}s")
    
    if 'human_escalation' in result:
        escalation = result['human_escalation']
        print(f"\nEscalation ID: {escalation.get('escalation_id', 'N/A')}")
        print(f"Approver: {escalation.get('approver', 'N/A')}")
        print(f"Status: {escalation.get('status', 'N/A')}")
        print(f"Notes: {escalation.get('approval_notes', 'N/A')}")
    
    execution_plan = result.get('execution_plan', {})
    if execution_plan:
        print("\nExecution Plan:")
        for key, value in execution_plan.items():
            if isinstance(value, list):
                print(f"  {key}: {', '.join(str(v) for v in value)}")
            else:
                print(f"  {key}: {value}")
    
    print("="*70)
    print("\n✓ Test complete. Check the output above to verify human decision was applied.")
    
    coordinator.close()


def test_multiple_escalations():
    """Test multiple escalations in sequence"""
    print("\n\n")
    print("="*70)
    print("MANUAL TEST: Multiple Escalations")
    print("="*70)
    print()
    print("This will trigger 3 escalation scenarios in sequence.")
    print("You will be asked to make decisions for each one.")
    print()
    
    proceed = input("Continue? [y/n]: ").strip().lower()
    if proceed != 'y':
        print("Skipping multiple escalations test.")
        return
    
    coordinator = CoordinationAgent()
    
    scenarios = [
        {
            "name": "Budget Conflict",
            "decisions": [
                {
                    "agent_id": "water_dept",
                    "agent_type": "water",
                    "decision": "recommend",
                    "request": {"type": "expansion"},
                    "confidence": 0.55,
                    "constraints": {},
                    "resources_needed": ["budget_capital"],
                    "location": "Zone-A",
                    "estimated_cost": 60000000,  # ₹6 crore
                    "priority": "expansion",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        },
        {
            "name": "Emergency Response",
            "decisions": [
                {
                    "agent_id": "health_dept",
                    "agent_type": "health",
                    "decision": "recommend",
                    "request": {"type": "epidemic_response"},
                    "confidence": 0.92,
                    "constraints": {},
                    "resources_needed": ["medical_supplies", "workers_citywide"],
                    "location": "City-Wide",
                    "estimated_cost": 80000000,  # ₹8 crore
                    "priority": "public_health",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        },
        {
            "name": "Routine Maintenance",
            "decisions": [
                {
                    "agent_id": "engineering_dept",
                    "agent_type": "engineering",
                    "decision": "recommend",
                    "request": {"type": "routine_maintenance"},
                    "confidence": 0.62,
                    "constraints": {},
                    "resources_needed": ["workers_zone_b"],
                    "location": "Zone-B",
                    "estimated_cost": 55000000,  # ₹5.5 crore
                    "priority": "routine",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}/3] Scenario: {scenario['name']}")
        print("-"*70)
        input("Press ENTER to proceed...")
        
        result = coordinator.coordinate(scenario['decisions'])
        results.append({
            "scenario": scenario['name'],
            "decision": result['decision'],
            "approver": result.get('human_escalation', {}).get('approver', 'N/A')
        })
        
        print(f"  Result: {result['decision']}")
        print()
    
    print("="*70)
    print("SUMMARY OF DECISIONS")
    print("="*70)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['scenario']}: {r['decision']} (by {r['approver']})")
    print("="*70)
    
    coordinator.close()


if __name__ == "__main__":
    print()
    print("=" * 70)
    print(" " * 15 + "COORDINATION AGENT - HUMAN INTERVENTION TEST")
    print("=" * 70)
    print()
    
    try:
        # Test 1: Single escalation
        test_human_intervention_manual()
        
        # Test 2: Multiple escalations (optional)
        test_multiple_escalations()
        
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("="*70)
    print("Test session complete.")
    print("="*70)
