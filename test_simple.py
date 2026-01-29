"""Simple test for LLM integration"""
import os
import sys

# Set UTF-8 encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

os.environ["PYTHONIOENCODING"] = "utf-8"

from water_agent import WaterDepartmentAgent

print("=" * 60)
print("TESTING ALL LLM NODES")
print("=" * 60)

# Create agent
agent = WaterDepartmentAgent()

# Test event
test_event = {
    "type": "maintenance_request",
    "location": "Zone-A",
    "user_request": "Schedule pipeline maintenance for Zone-A on 2025-02-01",
    "priority": "medium",
    "zone": "Zone-A",
    "scheduled_date": "2025-02-01"
}

print("\nSubmitting request...")
print(f"Request: {test_event['user_request']}\n")

# Process
try:
    result = agent.decide(test_event)
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print("=" * 60)
    print(f"Decision: {result.get('decision', 'unknown')}")
    print(f"LLM Used: {result.get('llm_used', 'unknown')}")
    
    if result.get('plan'):
        print(f"\nPlan Generated: {len(result['plan'].get('actions', []))} actions")
    
    print("\nCheck Groq Console: https://console.groq.com/")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
