"""
Fire Agent Test Script

Test the Fire Agent with different emergency scenarios
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_async_db
from app.agents.fire.graph import create_fire_agent_workflow
from app.agents.fire.state import FireState


async def test_scenario(scenario_name: str, initial_state: FireState):
    """Test a single scenario"""
    print(f"\n{'='*80}")
    print(f"Testing Scenario: {scenario_name}")
    print(f"{'='*80}\n")
    
    try:
        # Get database session
        async for db in get_async_db():
            # Create workflow
            workflow = create_fire_agent_workflow(db)
            
            # Execute workflow
            result = await workflow.ainvoke(initial_state)
            
            # Display results
            print(f"📍 Location: {result['location'].get('address', 'Unknown')}")
            print(f"🔥 Emergency Type: {result.get('emergency_type', result.get('request_type'))}")
            print(f"⚠️  Priority: {result.get('priority', 'N/A')}")
            
            if result.get('casualties'):
                print(f"🚨 Casualties: {result['casualties']}")
            
            print(f"\n📊 Severity Assessment:")
            severity = result.get("severity_assessment", {})
            if severity:
                print(f"   Level: {severity.get('level', 'N/A')}")
                print(f"   Score: {severity.get('score', 0)}/100")
            
            print(f"\n🚒 Nearby Stations: {len(result.get('nearby_stations', []))}")
            for station in result.get('nearby_stations', [])[:3]:
                print(f"   - {station['name']}: {station['distance_km']}km, "
                      f"{station['personnel_count']} personnel, {station['vehicle_count']} vehicles")
            
            dispatch_plan = result.get('dispatch_plan', {})
            if dispatch_plan:
                print(f"\n🚨 Dispatch Plan:")
                print(f"   Total Personnel: {dispatch_plan.get('total_personnel', 0)}")
                print(f"   Total Vehicles: {dispatch_plan.get('total_vehicles', 0)}")
                print(f"   Estimated ETA: {dispatch_plan.get('estimated_eta', 0)} minutes")
                
                for station_dispatch in dispatch_plan.get('stations', []):
                    print(f"   → {station_dispatch['station_name']}: "
                          f"{station_dispatch['personnel']} personnel, "
                          f"{station_dispatch['vehicles']} vehicles, "
                          f"ETA {station_dispatch['eta_minutes']} min")
                
                if dispatch_plan.get('mutual_aid_needed'):
                    print(f"   ⚠️  Mutual aid requested")
            
            print(f"\n🎯 Risk Level: {result.get('risk_level', 'N/A').upper()}")
            
            risk_factors = result.get('risk_factors', [])
            if risk_factors:
                print(f"\n⚠️  Risk Factors:")
                for factor in risk_factors:
                    print(f"   - {factor}")
            
            print(f"\n✅ Decision: {result.get('decision', 'N/A')}")
            print(f"💭 Reasoning: {result.get('reasoning', 'N/A')}")
            
            conditions = result.get('conditions', [])
            if conditions:
                print(f"\n📋 Conditions:")
                for condition in conditions:
                    print(f"   - {condition}")
            
            print(f"\n💰 Estimated Cost: ₹{result.get('estimated_cost', 0):,.2f}")
            print(f"⏱️  Estimated Duration: {result.get('estimated_duration', 0)} minutes")
            
            if result.get('coordination_required'):
                print(f"\n🤝 Coordination Required:")
                for dept in result.get('departments_to_notify', []):
                    print(f"   - {dept}")
            
            print(f"\n✨ Workflow Status: {result.get('workflow_status', 'unknown')}")
            
            break  # Exit after first iteration
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Run all test scenarios"""
    
    # Scenario 1: Building Fire with Casualties
    scenario1: FireState = {
        "request_id": "test-fire-001",
        "request_type": "emergency_response",
        "department_id": 2,
        "user_id": 1,
        "location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "address": "Connaught Place, Central Delhi"
        },
        "description": "Large fire in commercial building, multiple people trapped on upper floors",
        "priority": "critical",
        "timestamp": datetime.utcnow().isoformat(),
        "emergency_type": "fire",
        "casualties": 5,
        "building_type": "commercial",
        "fire_intensity": "major",
        "validation_status": "",
        "validation_errors": [],
        "nearby_stations": [],
        "available_stations": [],
        "station_distances": {},
        "active_incidents": [],
        "historical_incidents": [],
        "incident_patterns": {},
        "station_resources": {},
        "total_personnel": 0,
        "available_personnel": 0,
        "total_vehicles": 0,
        "available_vehicles": 0,
        "llm_analysis": "",
        "severity_assessment": {},
        "response_requirements": {},
        "risk_level": "",
        "risk_factors": [],
        "estimated_response_time": 0,
        "recommended_stations": [],
        "dispatch_plan": {},
        "backup_required": False,
        "mutual_aid_needed": False,
        "decision": "",
        "reasoning": "",
        "conditions": [],
        "estimated_cost": 0.0,
        "estimated_duration": 0,
        "safety_check_passed": False,
        "resource_check_passed": False,
        "coordination_required": False,
        "coordination_needed": False,
        "departments_to_notify": [],
        "coordination_messages": [],
        "coordination_status": "",
        "response": {},
        "action_items": [],
        "next_steps": [],
        "workflow_status": "in_progress",
        "current_node": "",
        "errors": [],
        "execution_time": 0.0
    }
    
    # Scenario 2: High-Rise Fire
    scenario2: FireState = {
        "request_id": "test-fire-002",
        "request_type": "emergency_response",
        "department_id": 2,
        "user_id": 1,
        "location": {
            "latitude": 28.6280,
            "longitude": 77.2200,
            "address": "Nehru Place High-Rise, South Delhi"
        },
        "description": "Fire on 15th floor of high-rise building, smoke spreading",
        "priority": "high",
        "timestamp": datetime.utcnow().isoformat(),
        "emergency_type": "fire",
        "casualties": 0,
        "building_type": "high-rise",
        "fire_intensity": "moderate",
        "validation_status": "",
        "validation_errors": [],
        "nearby_stations": [],
        "available_stations": [],
        "station_distances": {},
        "active_incidents": [],
        "historical_incidents": [],
        "incident_patterns": {},
        "station_resources": {},
        "total_personnel": 0,
        "available_personnel": 0,
        "total_vehicles": 0,
        "available_vehicles": 0,
        "llm_analysis": "",
        "severity_assessment": {},
        "response_requirements": {},
        "risk_level": "",
        "risk_factors": [],
        "estimated_response_time": 0,
        "recommended_stations": [],
        "dispatch_plan": {},
        "backup_required": False,
        "mutual_aid_needed": False,
        "decision": "",
        "reasoning": "",
        "conditions": [],
        "estimated_cost": 0.0,
        "estimated_duration": 0,
        "safety_check_passed": False,
        "resource_check_passed": False,
        "coordination_required": False,
        "coordination_needed": False,
        "departments_to_notify": [],
        "coordination_messages": [],
        "coordination_status": "",
        "response": {},
        "action_items": [],
        "next_steps": [],
        "workflow_status": "in_progress",
        "current_node": "",
        "errors": [],
        "execution_time": 0.0
    }
    
    # Scenario 3: Medical Emergency
    scenario3: FireState = {
        "request_id": "test-fire-003",
        "request_type": "emergency_response",
        "department_id": 2,
        "user_id": 1,
        "location": {
            "latitude": 28.6500,
            "longitude": 77.2300,
            "address": "Civil Lines, North Delhi"
        },
        "description": "Medical emergency, cardiac arrest reported",
        "priority": "high",
        "timestamp": datetime.utcnow().isoformat(),
        "emergency_type": "medical",
        "casualties": 1,
        "building_type": "residential",
        "fire_intensity": None,
        "validation_status": "",
        "validation_errors": [],
        "nearby_stations": [],
        "available_stations": [],
        "station_distances": {},
        "active_incidents": [],
        "historical_incidents": [],
        "incident_patterns": {},
        "station_resources": {},
        "total_personnel": 0,
        "available_personnel": 0,
        "total_vehicles": 0,
        "available_vehicles": 0,
        "llm_analysis": "",
        "severity_assessment": {},
        "response_requirements": {},
        "risk_level": "",
        "risk_factors": [],
        "estimated_response_time": 0,
        "recommended_stations": [],
        "dispatch_plan": {},
        "backup_required": False,
        "mutual_aid_needed": False,
        "decision": "",
        "reasoning": "",
        "conditions": [],
        "estimated_cost": 0.0,
        "estimated_duration": 0,
        "safety_check_passed": False,
        "resource_check_passed": False,
        "coordination_required": False,
        "coordination_needed": False,
        "departments_to_notify": [],
        "coordination_messages": [],
        "coordination_status": "",
        "response": {},
        "action_items": [],
        "next_steps": [],
        "workflow_status": "in_progress",
        "current_node": "",
        "errors": [],
        "execution_time": 0.0
    }
    
    # Scenario 4: Industrial Hazmat Incident
    scenario4: FireState = {
        "request_id": "test-fire-004",
        "request_type": "emergency_response",
        "department_id": 2,
        "user_id": 1,
        "location": {
            "latitude": 28.6700,
            "longitude": 77.1800,
            "address": "Industrial Area, Wazirpur"
        },
        "description": "Chemical spill in industrial facility, toxic fumes detected",
        "priority": "critical",
        "timestamp": datetime.utcnow().isoformat(),
        "emergency_type": "hazmat",
        "casualties": 2,
        "building_type": "industrial",
        "fire_intensity": None,
        "validation_status": "",
        "validation_errors": [],
        "nearby_stations": [],
        "available_stations": [],
        "station_distances": {},
        "active_incidents": [],
        "historical_incidents": [],
        "incident_patterns": {},
        "station_resources": {},
        "total_personnel": 0,
        "available_personnel": 0,
        "total_vehicles": 0,
        "available_vehicles": 0,
        "llm_analysis": "",
        "severity_assessment": {},
        "response_requirements": {},
        "risk_level": "",
        "risk_factors": [],
        "estimated_response_time": 0,
        "recommended_stations": [],
        "dispatch_plan": {},
        "backup_required": False,
        "mutual_aid_needed": False,
        "decision": "",
        "reasoning": "",
        "conditions": [],
        "estimated_cost": 0.0,
        "estimated_duration": 0,
        "safety_check_passed": False,
        "resource_check_passed": False,
        "coordination_required": False,
        "coordination_needed": False,
        "departments_to_notify": [],
        "coordination_messages": [],
        "coordination_status": "",
        "response": {},
        "action_items": [],
        "next_steps": [],
        "workflow_status": "in_progress",
        "current_node": "",
        "errors": [],
        "execution_time": 0.0
    }
    
    # Run scenarios
    await test_scenario("Building Fire with Casualties", scenario1)
    await test_scenario("High-Rise Fire", scenario2)
    await test_scenario("Medical Emergency", scenario3)
    await test_scenario("Industrial Hazmat Incident", scenario4)
    
    print(f"\n{'='*80}")
    print("All scenarios tested!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    asyncio.run(main())
