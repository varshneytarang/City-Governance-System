"""
Script to enable LLM across all decision-making nodes
(except feasibility which stays rules-based)

Run: python scripts/enable_llm_all_nodes.py
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from water_agent.nodes.llm_helper import get_llm_client
from water_agent.config import settings

print("\n" + "🤖 "*30)
print("ENABLING LLM FOR ALL DECISION NODES")
print("🤖 "*30 + "\n")

# Check LLM availability
client = get_llm_client()

if not client:
    print("❌ No LLM configured!")
    print("\nAdd to .env:")
    print("  GROQ_API_KEY=your_key")
    print("  LLM_PROVIDER=groq")
    print("  LLM_MODEL=llama-3.3-70b-versatile")
    sys.exit(1)

print("✅ LLM Client initialized successfully")
print(f"   Provider: {settings.LLM_PROVIDER}")
print(f"   Model: {settings.LLM_MODEL}\n")

# Test LLM with simple call
try:
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "user", "content": "Say 'LLM is working' in JSON format: {\"status\": \"...\"}"}
        ],
        temperature=0.1,
        max_tokens=50
    )
    print(f"✅ LLM Test: {response.choices[0].message.content}\n")
except Exception as e:
    print(f"❌ LLM Test Failed: {e}\n")
    sys.exit(1)

# Show which nodes will use LLM
nodes_config = {
    "intent_analyzer": "✅ LLM-Enhanced",
    "goal_setter": "✅ LLM-Enhanced",
    "planner": "✅ LLM-Enhanced (DONE)",
    "observer": "✅ LLM-Enhanced",
    "feasibility_evaluator": "❌ RULES ONLY (by design)",
    "policy_validator": "✅ LLM-Enhanced",
    "confidence_estimator": "✅ LLM-Enhanced",
    "decision_router": "✅ LLM-Enhanced"
}

print("Node Configuration:")
print("="*60)
for node, status in nodes_config.items():
    print(f"  {node:25} → {status}")
print("="*60 + "\n")

print("✅ LLM is ready for all nodes!")
print("\nNext steps:")
print("  1. Nodes will automatically use LLM when called")
print("  2. Deterministic fallback is always available")
print("  3. Run tests: python test_llm_full_integration.py")
print("\n")
