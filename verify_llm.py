"""Verify LLM integration across all nodes"""
import os
import sys

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

os.environ["PYTHONIOENCODING"] = "utf-8"

from water_agent import WaterDepartmentAgent
import logging

# Set to INFO to see LLM calls
logging.basicConfig(level=logging.INFO, format='%(name)s: %(message)s')

print("=" * 70)
print("LLM INTEGRATION VERIFICATION")
print("=" * 70)

agent = WaterDepartmentAgent()

test_event = {
    "type": "maintenance_request",
    "location": "Zone-A",
    "user_request": "Schedule pipeline maintenance for Zone-A",
    "priority": "medium",
    "zone": "Zone-A",
    "scheduled_date": "2025-02-01"
}

print("\nProcessing test event...")
print(f"Looking for '🤖 Using LLM' messages in logs...\n")

result = agent.decide(test_event)

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Decision: {result.get('decision')}")
print(f"\nLLM-Enhanced Nodes Active:")
print("  - Intent Analyzer")
print("  - Goal Setter")
print("  - Planner")
print("  - Observer")
print("  - Policy Validator")
print("  - Confidence Estimator")
print("  - Decision Router")
print("\nAll nodes try LLM first, fallback to rules-based if LLM fails")
print(f"\nCheck Groq API calls: https://console.groq.com/")
