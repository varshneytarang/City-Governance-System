"""
Multi-Agent Integration Example

Demonstrates Water Agent + Engineering Agent + Coordination Agent
working together on a joint infrastructure project.
"""

from water_agent import WaterDepartmentAgent
from engineering_agent import EngineeringDepartmentAgent
from coordination_agent import CoordinationAgent


def main():
    print("\n" + "="*70)
    print("MULTI-AGENT CITY GOVERNANCE SYSTEM - INTEGRATION DEMO")
    print("="*70)
    
    # Initialize all agents
    print("\n→ Initializing agents...")
    water_agent = WaterDepartmentAgent()
    engineering_agent = EngineeringDepartmentAgent()
    coordinator = CoordinationAgent()
    print("✓ All agents initialized")
    
    # Scenario: New pipeline construction in Zone-A
    # - Water department needs new pipeline
    # - Engineering department must build infrastructure
    # - Both need same workers and budget
    
    print("\n" + "="*70)
    print("SCENARIO: New Pipeline Construction Project")
    print("="*70)
    
    # Step 1: Water agent evaluates need
    print("\n[1] Water Department: Assessing pipeline need...")
    water_request = {
        "type": "project_planning",
        "location": "Zone-A",
        "project_type": "new_pipeline",
        "estimated_cost": 400000,
        "reason": "Expand water supply to Zone-A"
    }
    
    water_decision = water_agent.decide(water_request)
    print(f"   Water Decision: {water_decision['decision']}")
    print(f"   Confidence: {water_decision.get('confidence', 'N/A')}")
    
    # Step 2: Engineering agent evaluates construction
    print("\n[2] Engineering Department: Assessing construction feasibility...")
    engineering_request = {
        "type": "project_approval_request",
        "location": "Zone-A",
        "project_type": "pipeline_construction",
        "estimated_cost": 500000,
        "planned_start_month": 11,  # November (post-monsoon)
        "reason": "Pipeline infrastructure for water department"
    }
    
    engineering_decision = engineering_agent.decide(engineering_request)
    print(f"   Engineering Decision: {engineering_decision['decision']}")
    print(f"   Confidence: {engineering_decision.get('confidence', 'N/A')}")
    
    # Step 3: Coordination agent resolves potential conflicts
    print("\n[3] Coordination Agent: Coordinating both departments...")
    
    # Format decisions for coordinator
    coordination_input = [
        {
            "agent_id": "water_dept",
            "agent_type": "water",
            "decision": water_decision["decision"],
            "request": water_request,
            "confidence": water_decision.get("confidence", 0.8),
            "constraints": {},
            "resources_needed": ["workers_zone_a", "budget_capital"],
            "location": "Zone-A",
            "estimated_cost": 400000,
            "priority": "expansion",
            "timestamp": water_decision.get("timestamp", "")
        },
        {
            "agent_id": "engineering_dept",
            "agent_type": "engineering",
            "decision": engineering_decision["decision"],
            "request": engineering_request,
            "confidence": engineering_decision.get("confidence", 0.8),
            "constraints": {},
            "resources_needed": ["workers_zone_a", "budget_capital"],
            "location": "Zone-A",
            "estimated_cost": 500000,
            "priority": "expansion",
            "timestamp": engineering_decision.get("timestamp", "")
        }
    ]
    
    coordination_result = coordinator.coordinate(coordination_input)
    
    print(f"   Coordination Decision: {coordination_result['decision']}")
    print(f"   Conflicts Detected: {coordination_result['conflicts_detected']}")
    print(f"   Resolution Method: {coordination_result['resolution_method']}")
    print(f"   Processing Time: {coordination_result['processing_time']:.2f}s")
    
    # Step 4: Show execution plan
    print("\n[4] Execution Plan:")
    execution_plan = coordination_result.get("execution_plan", {})
    
    if "sequence" in execution_plan:
        print("   Sequential Execution:")
        for step in execution_plan["sequence"]:
            print(f"     {step['order']}. {step['agent']}: {step.get('action', 'proceed')}")
    elif "approved" in execution_plan:
        print(f"   Approved: {', '.join(execution_plan['approved'])}")
        if "queued" in execution_plan:
            print(f"   Queued: {', '.join(execution_plan['queued'])}")
    
    print(f"\n   Rationale: {coordination_result.get('rationale', 'N/A')}")
    
    # Summary
    print("\n" + "="*70)
    print("INTEGRATION SUMMARY")
    print("="*70)
    print("✓ Water Agent: Autonomous decision-making")
    print("✓ Engineering Agent: Autonomous decision-making")
    print("✓ Coordination Agent: Multi-agent orchestration")
    print("\n✓ Workflow Log:")
    for i, log_entry in enumerate(coordination_result.get("workflow_log", []), 1):
        print(f"   {i}. {log_entry}")
    
    print("\n✅ MULTI-AGENT COORDINATION SUCCESSFUL")
    print("="*70)
    
    # Cleanup
    water_agent.close()
    engineering_agent.close()
    coordinator.close()


if __name__ == "__main__":
    main()
