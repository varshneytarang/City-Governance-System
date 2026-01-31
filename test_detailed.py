"""
Step-by-step test to see exactly what's happening with tools
"""

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from water_agent import WaterDepartmentAgent

print("="*80)
print("DETAILED TOOL EXECUTION TEST")
print("="*80)

agent = WaterDepartmentAgent()

request = {
    "type": "maintenance_request",
    "location": "Zone-A",
    "user_request": "Schedule pipeline inspection",
    "activity": "inspection",
    "priority": "medium",
    "estimated_cost": 30000
}

print("\n📨 Request:")
print(f"   Type: {request['type']}")
print(f"   Location: {request['location']}")
print(f"   Activity: {request['activity']}")
print(f"   Cost: ${request['estimated_cost']:,}")

print("\n🚀 Processing...")
print("-"*80)

result = agent.decide(request)

print("\n" + "="*80)
print("📊 RESULTS")
print("="*80)

print(f"\n✓ Decision: {result.get('decision')}")
print(f"✓ Reason: {result.get('reason', 'N/A')}")

# Check for details
if 'details' in result:
    details = result['details']
    
    print(f"\n📋 Plan Generated:")
    plan = details.get('plan', {})
    if plan:
        print(f"   Name: {plan.get('name', 'N/A')}")
        print(f"   Steps: {len(plan.get('steps', []))} steps")
        for i, step in enumerate(plan.get('steps', []), 1):
            print(f"      {i}. {step}")
    
    print(f"\n🔧 Tool Results:")
    tool_results = details.get('tool_results', {})
    if tool_results:
        print(f"   ✓ Got {len(tool_results)} tool results:")
        for tool_name, tool_data in tool_results.items():
            print(f"      • {tool_name}: {list(tool_data.keys())}")
    else:
        print("   ✗ NO TOOL RESULTS")
    
    print(f"\n📊 Observations:")
    observations = details.get('observations', {})
    if observations:
        facts = observations.get('extracted_facts', {})
        print(f"   Facts extracted: {len(facts)}")
        for key, value in facts.items():
            print(f"      • {key}: {value}")
    else:
        print("   ✗ NO OBSERVATIONS")
    
    print(f"\n🎯 Feasibility:")
    print(f"   Feasible: {details.get('feasible', 'unknown')}")
    print(f"   Reason: {details.get('feasibility_reason', 'N/A')}")
    
    print(f"\n📜 Policy:")
    print(f"   Compliant: {details.get('policy_ok', 'unknown')}")
    violations = details.get('policy_violations', [])
    if violations:
        print(f"   Violations: {violations}")
    
    print(f"\n🎲 Confidence:")
    print(f"   Score: {details.get('confidence', 0):.2f}")
    
else:
    print("\n⚠️  No details in result")

print("\n" + "="*80)

agent.close()
