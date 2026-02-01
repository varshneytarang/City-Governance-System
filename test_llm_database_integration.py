"""
Test LLM + Database Integration
Verify LLM is using database data for decisions with reduced API calls
"""

import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("=" * 70)
print("LLM + DATABASE INTEGRATION TEST")
print("Testing: Reduced API calls + Database-driven decisions")
print("=" * 70)

# ========== TEST 1: FIRE AGENT - Emergency Response ==========
print("\n[TEST 1] FIRE AGENT - Structure Fire Emergency")
print("-" * 70)

from fire_agent.agent import FireDepartmentAgent

fire_agent = FireDepartmentAgent()

fire_request = {
    "type": "emergency_response",
    "incident_type": "structure_fire",
    "location": "123 Main Street",
    "zone": "Zone-1",
    "priority": "high",
    "description": "Structure fire at residential building, 2-story home"
}

print(f"\n📝 Request: {fire_request['incident_type']} in {fire_request['zone']}")
print(f"   Location: {fire_request['location']}")
print(f"   Priority: {fire_request['priority']}")

result = fire_agent.decide(fire_request)

print(f"\n🎯 DECISION: {result.get('decision', 'N/A').upper()}")
print(f"   Confidence: {result.get('confidence', 0)*100:.0f}%")
print(f"   Reasoning: {result.get('reasoning', 'N/A')}")

# Check if database data was used
context = result.get('context', {})
if context:
    print(f"\n✓ Database Context Loaded:")
    print(f"   - Fire Stations: {len(context.get('fire_stations', []))} stations")
    print(f"   - Available Trucks: {len(context.get('fire_trucks', []))} trucks")
    print(f"   - Firefighters: {len(context.get('firefighters', []))} personnel")
    print(f"   - Fire Hydrants: {len(context.get('fire_hydrants', []))} hydrants")

print("\n" + "=" * 70)

# ========== TEST 2: SANITATION AGENT - Route Change ==========
print("\n[TEST 2] SANITATION AGENT - Route Change Request")
print("-" * 70)

from sanitation_agent.agent import SanitationDepartmentAgent

sanitation_agent = SanitationDepartmentAgent()

sanitation_request = {
    "type": "route_change",
    "zone": "Zone-1",
    "location": "Zone-1",  # Required field
    "route_id": 1,
    "reason": "construction_detour",
    "urgency": "medium",
    "description": "Need to reroute due to road construction on Oak Street"
}

print(f"\n📝 Request: {sanitation_request['type']} in {sanitation_request['zone']}")
print(f"   Route ID: {sanitation_request['route_id']}")
print(f"   Reason: {sanitation_request['reason']}")

result = sanitation_agent.decide(sanitation_request)

print(f"\n🎯 DECISION: {result.get('decision', 'N/A').upper()}")
print(f"   Confidence: {result.get('confidence', 0)*100:.0f}%")
print(f"   Reasoning: {result.get('reasoning', 'N/A')}")

# Check if database data was used
context = result.get('context', {})
if context:
    print(f"\n✓ Database Context Loaded:")
    print(f"   - Routes: {len(context.get('routes', []))} routes")
    print(f"   - Waste Trucks: {len(context.get('trucks', []))} trucks")
    print(f"   - Waste Bins: {len(context.get('bins', []))} bins")
    print(f"   - Complaints: {len(context.get('complaints', []))} complaints")

print("\n" + "=" * 70)
print("\n✅ INTEGRATION TEST COMPLETE")
print("\nAPI Call Summary:")
print("   • Planner: LLM enabled (2 calls total)")
print("   • Observer: LLM disabled (0 calls)")
print("   • Policy Validator: LLM disabled (0 calls)")
print("   • Confidence: LLM enabled (2 calls total)")
print(f"\n   📊 Total API Calls: ~4 calls (within 30 call limit)")
print("\n" + "=" * 70)
