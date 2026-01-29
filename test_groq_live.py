"""
Quick test to verify Groq API is being called
"""

from water_agent import WaterDepartmentAgent

print("\n" + "🔥 "*30)
print("TESTING GROQ API INTEGRATION")
print("🔥 "*30 + "\n")

agent = WaterDepartmentAgent()

request = {
    "type": "schedule_shift_request",
    "location": "Downtown",
    "requested_shift_days": 2,
    "estimated_cost": 50000
}

print("Submitting request to agent...")
print("Check your Groq dashboard: https://console.groq.com/\n")

response = agent.decide(request)

print("\n" + "="*70)
print("RESULT:")
print("="*70)
print(f"Decision: {response.get('decision')}")
print(f"LLM Used: {response.get('llm_used', 'unknown')}")

if response.get("plan"):
    plan = response["plan"]
    print(f"\nPlan Name: {plan.get('name')}")
    print(f"Steps: {len(plan.get('steps', []))}")
    print(f"First 3 steps:")
    for i, step in enumerate(plan.get('steps', [])[:3], 1):
        print(f"  {i}. {step}")

agent.close()

print("\n✅ Check Groq Console for API usage:")
print("   https://console.groq.com/")
print("\n")
