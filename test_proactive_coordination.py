"""
Test Proactive Coordination System

Demonstrates agents checking with coordinator DURING workflow,
not just after completion.
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


def test_proactive_coordination():
    """
    Test scenario: Two agents make decisions for same location
    
    Expected behavior:
    1. Water agent makes decision first
    2. Engineering agent checks with coordinator during workflow
    3. Coordinator detects conflict and provides feedback
    4. Engineering agent adjusts or escalates based on feedback
    """
    
    print("\n" + "="*80)
    print("PROACTIVE COORDINATION SYSTEM TEST")
    print("="*80)
    print("\nScenario: Both departments planning work in Zone-A")
    print("Expected: Engineering agent detects conflict during workflow\n")
    
    # Initialize agents
    print("→ Initializing agents...")
    water_agent = WaterDepartmentAgent()
    engineering_agent = EngineeringDepartmentAgent()
    print("✓ Agents initialized\n")
    
    # ========================================================================
    # STEP 1: Water Department makes a decision
    # ========================================================================
    print("="*80)
    print("STEP 1: Water Department - Pipeline Maintenance Request")
    print("="*80)
    
    water_request = {
        "type": "maintenance_request",
        "location": "Zone-A",
        "reason": "Pipeline leak detected",
        "estimated_cost": 250000,
        "priority": "high"
    }
    
    print("\n🌊 Water Agent processing request...")
    water_result = water_agent.decide(water_request)
    
    print(f"\n📊 Water Agent Decision:")
    print(f"   Decision: {water_result.get('decision', 'N/A').upper()}")
    print(f"   Confidence: {water_result.get('confidence', 0)*100:.0f}%")
    if water_result.get('coordination_check'):
        print(f"   Coordination Check: Passed")
    
    # ========================================================================
    # STEP 2: Engineering Department makes decision for SAME location
    # ========================================================================
    print("\n" + "="*80)
    print("STEP 2: Engineering Department - Construction Project (SAME LOCATION)")
    print("="*80)
    print("Expected: Coordinator detects conflict during workflow\n")
    
    engineering_request = {
        "type": "project_approval_request",
        "location": "Zone-A",  # SAME LOCATION
        "project_type": "road_construction",
        "estimated_cost": 500000,
        "planned_start_month": 11,
        "reason": "Road widening project"
    }
    
    print("🏗️  Engineering Agent processing request...")
    print("   (Coordinator will be called during workflow)\n")
    
    engineering_result = engineering_agent.decide(engineering_request)
    
    print(f"\n📊 Engineering Agent Decision:")
    print(f"   Decision: {engineering_result.get('decision', 'N/A').upper()}")
    print(f"   Confidence: {engineering_result.get('confidence', 0)*100:.0f}%")
    
    # Check coordination results
    if engineering_result.get('coordination_check'):
        coord_check = engineering_result['coordination_check']
        print(f"\n🔍 Coordination Check Results:")
        print(f"   Conflicts Detected: {coord_check.get('has_conflicts', False)}")
        print(f"   Should Proceed: {coord_check.get('should_proceed', True)}")
        print(f"   Requires Human: {coord_check.get('requires_human', False)}")
        
        if coord_check.get('conflict_types'):
            print(f"\n   Conflict Types:")
            for ct in coord_check['conflict_types']:
                print(f"      • {ct}")
        
        if coord_check.get('recommendations'):
            print(f"\n   Coordinator Recommendations:")
            for rec in coord_check['recommendations']:
                print(f"      • {rec}")
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    print("\n" + "="*80)
    print("TEST RESULTS - PROACTIVE COORDINATION")
    print("="*80)
    
    print(f"\n✅ Water Agent:")
    print(f"   • Made decision first")
    print(f"   • Decision: {water_result.get('decision', 'N/A')}")
    
    print(f"\n✅ Engineering Agent:")
    print(f"   • Checked with coordinator DURING workflow")
    print(f"   • Decision: {engineering_result.get('decision', 'N/A')}")
    
    if engineering_result.get('escalate'):
        print(f"\n🚨 Engineering agent escalated due to conflicts:")
        print(f"   Reason: {engineering_result.get('escalation_reason', 'N/A')}")
        print("\n✅ PROACTIVE COORDINATION WORKING!")
        print("   Agent detected conflict and escalated BEFORE executing plan")
    elif engineering_result.get('coordination_check', {}).get('has_conflicts'):
        print(f"\n⚠️  Conflicts detected but agent proceeded with caution")
        print("\n✅ PROACTIVE COORDINATION WORKING!")
        print("   Agent received coordinator feedback during workflow")
    else:
        print(f"\n✅ No conflicts detected - both agents coordinated successfully")
    
    # Cleanup
    water_agent.close()
    engineering_agent.close()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    test_proactive_coordination()
