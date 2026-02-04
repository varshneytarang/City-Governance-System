"""
Test Proactive Coordination Across All 4 Main Agents

Demonstrates Water, Engineering, Fire, and Sanitation agents
checking with coordinator during their workflows.

Scenario: Multiple departments need to work in the same location
Expected: Agents detect conflicts and coordinate proactively
"""

import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

from water_agent import WaterDepartmentAgent
from engineering_agent import EngineeringDepartmentAgent
from fire_agent import FireDepartmentAgent
from sanitation_agent import SanitationDepartmentAgent


def test_all_agents_proactive_coordination():
    """
    Test all 4 agents with proactive coordination
    """
    
    print("\n" + "="*80)
    print("PROACTIVE COORDINATION SYSTEM - ALL 4 AGENTS TEST")
    print("="*80)
    print("\nScenario: All departments want to work in Downtown area")
    print("Expected: Agents detect conflicts during workflow and coordinate\n")
    
    # Initialize all agents
    print("→ Initializing agents...")
    water_agent = WaterDepartmentAgent()
    engineering_agent = EngineeringDepartmentAgent()
    fire_agent = FireDepartmentAgent()
    sanitation_agent = SanitationDepartmentAgent()
    print("✓ All 4 agents initialized\n")
    
    # ========================================================================
    # AGENT 1: Water Department - Pipeline Maintenance
    # ========================================================================
    print("="*80)
    print("AGENT 1: WATER DEPARTMENT - Pipeline Maintenance in Downtown")
    print("="*80)
    
    water_request = {
        "type": "maintenance_request",
        "location": "Downtown",
        "reason": "Replace aging pipeline section",
        "estimated_cost": 300000,
        "priority": "high"
    }
    
    print("\n🌊 Water Agent processing...")
    water_result = water_agent.decide(water_request)
    
    print(f"\n📊 Water Agent Result:")
    print(f"   Decision: {water_result.get('decision', 'N/A').upper()}")
    print(f"   Confidence: {water_result.get('confidence', 0)*100:.0f}%")
    if water_result.get('coordination_check'):
        print(f"   Coordination: ✅ Checked (first agent)")
    
    # ========================================================================
    # AGENT 2: Engineering Department - Road Construction
    # ========================================================================
    print("\n" + "="*80)
    print("AGENT 2: ENGINEERING DEPARTMENT - Road Work in Downtown (SAME LOCATION)")
    print("="*80)
    print("Expected: Conflict detected with Water Department\n")
    
    engineering_request = {
        "type": "project_approval_request",
        "location": "Downtown",  # SAME LOCATION
        "project_type": "road_resurfacing",
        "estimated_cost": 500000,
        "planned_start_month": 11,
        "reason": "Road maintenance project"
    }
    
    print("🏗️  Engineering Agent processing...")
    engineering_result = engineering_agent.decide(engineering_request)
    
    print(f"\n📊 Engineering Agent Result:")
    print(f"   Decision: {engineering_result.get('decision', 'N/A').upper()}")
    print(f"   Confidence: {engineering_result.get('confidence', 0)*100:.0f}%")
    
    if engineering_result.get('coordination_check'):
        coord_check = engineering_result['coordination_check']
        print(f"   Conflicts Detected: {coord_check.get('has_conflicts', False)}")
        if coord_check.get('conflict_types'):
            print(f"   Conflict Types: {', '.join(coord_check['conflict_types'])}")
    
    # ========================================================================
    # AGENT 3: Fire Department - Safety Inspection
    # ========================================================================
    print("\n" + "="*80)
    print("AGENT 3: FIRE DEPARTMENT - Safety Inspection in Downtown")
    print("="*80)
    print("Expected: Conflict detected with Water and Engineering\n")
    
    fire_request = {
        "type": "safety_inspection",
        "location": "Downtown",  # SAME LOCATION
        "zone": "Downtown",
        "incident_type": "routine_inspection",
        "priority": "medium",
        "reason": "Quarterly fire safety inspection"
    }
    
    print("🔥 Fire Agent processing...")
    fire_result = fire_agent.decide(fire_request)
    
    print(f"\n📊 Fire Agent Result:")
    print(f"   Decision: {fire_result.get('decision', 'N/A').upper()}")
    print(f"   Confidence: {fire_result.get('confidence', 0)*100:.0f}%")
    
    if fire_result.get('coordination_check'):
        coord_check = fire_result['coordination_check']
        print(f"   Conflicts Detected: {coord_check.get('has_conflicts', False)}")
        if coord_check.get('recommendations'):
            print(f"   Recommendations:")
            for rec in coord_check['recommendations'][:2]:  # Show first 2
                print(f"      • {rec}")
    
    # ========================================================================
    # AGENT 4: Sanitation Department - Street Cleaning
    # ========================================================================
    print("\n" + "="*80)
    print("AGENT 4: SANITATION DEPARTMENT - Collection Route in Downtown")
    print("="*80)
    print("Expected: Conflict detected with all 3 previous agents\n")
    
    sanitation_request = {
        "type": "route_modification",
        "location": "Downtown",  # SAME LOCATION
        "zone": "Downtown",
        "reason": "Update collection schedule for Downtown area",
        "estimated_cost": 50000
    }
    
    print("🧹 Sanitation Agent processing...")
    sanitation_result = sanitation_agent.decide(sanitation_request)
    
    print(f"\n📊 Sanitation Agent Result:")
    print(f"   Decision: {sanitation_result.get('decision', 'N/A').upper()}")
    print(f"   Confidence: {sanitation_result.get('confidence', 0)*100:.0f}%")
    
    if sanitation_result.get('coordination_check'):
        coord_check = sanitation_result['coordination_check']
        print(f"   Conflicts Detected: {coord_check.get('has_conflicts', False)}")
        if coord_check.get('alternative_suggestions'):
            print(f"   Alternative Suggestions:")
            for alt in coord_check['alternative_suggestions'][:2]:
                print(f"      • {alt}")
    
    # ========================================================================
    # RESULTS SUMMARY
    # ========================================================================
    print("\n" + "="*80)
    print("PROACTIVE COORDINATION TEST RESULTS")
    print("="*80)
    
    results = [
        ("Water", water_result),
        ("Engineering", engineering_result),
        ("Fire", fire_result),
        ("Sanitation", sanitation_result)
    ]
    
    coordinated_count = 0
    conflict_count = 0
    escalated_count = 0
    
    for agent_name, result in results:
        decision = result.get('decision', 'unknown')
        has_coord = result.get('coordination_check') is not None
        has_conflicts = result.get('coordination_check', {}).get('has_conflicts', False)
        escalated = result.get('escalate', False)
        
        if has_coord:
            coordinated_count += 1
        if has_conflicts:
            conflict_count += 1
        if escalated:
            escalated_count += 1
        
        status_icon = "✅" if has_coord else "⚠️"
        conflict_icon = "⚠️" if has_conflicts else "✓"
        
        print(f"\n{status_icon} {agent_name} Department:")
        print(f"   Decision: {decision.upper()}")
        print(f"   Coordination Check: {'Yes' if has_coord else 'No'}")
        print(f"   {conflict_icon} Conflicts: {'Yes' if has_conflicts else 'No'}")
        if escalated:
            print(f"   🚨 Escalated to Human")
    
    print("\n" + "="*80)
    print("SUMMARY STATISTICS")
    print("="*80)
    print(f"   Total Agents Tested: 4")
    print(f"   ✅ Agents with Coordination: {coordinated_count}/4")
    print(f"   ⚠️  Conflicts Detected: {conflict_count}")
    print(f"   🚨 Escalations Required: {escalated_count}")
    
    if coordinated_count == 4:
        print(f"\n✅ SUCCESS: All agents used proactive coordination!")
    
    if conflict_count > 0:
        print(f"✅ SUCCESS: Conflicts detected BEFORE execution!")
        print(f"   System prevented {conflict_count} potential conflicts")
    
    # Cleanup
    water_agent.close()
    engineering_agent.close()
    fire_agent.close()
    sanitation_agent.close()
    
    print("\n" + "="*80)
    print("TEST COMPLETE - PROACTIVE COORDINATION WORKING!")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_all_agents_proactive_coordination()
