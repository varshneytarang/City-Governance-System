"""
Quick test script to verify Water Agent logging

This script directly invokes the Water Agent to test if logs are showing up.
"""

import sys
import os
import logging

# Setup logging to see all output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Add backend to path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("\n" + "="*80)
print("🧪 TESTING WATER AGENT LOGGING")
print("="*80)
print("\nThis will test if the Water Agent logs are working...")
print("You should see detailed logs with emojis like 🛠️ 🔮 🌐 etc.\n")
print("="*80 + "\n")

# Import Water Agent
try:
    from agents.water_agent.agent import WaterDepartmentAgent
    print("✅ Water Agent imported successfully\n")
except ImportError as e:
    print(f"❌ Failed to import Water Agent: {e}")
    sys.exit(1)

# Create test request
test_request = {
    "type": "water_quality_test",
    "location": "Main Street Water Treatment Plant",
    "reason": "What is the current water quality status at Main Street treatment plant?",
    "urgency": "normal",
    "details": {
        "test_type": "standard_quality",
        "requested_by": "Test User"
    }
}

print("📋 Test Request:")
print(f"   Type: {test_request['type']}")
print(f"   Location: {test_request['location']}")
print(f"   Query: {test_request['reason']}")
print("\n" + "="*80)
print("🚀 INVOKING WATER AGENT...")
print("="*80 + "\n")

# Create agent and process request
try:
    agent = WaterDepartmentAgent()
    print("\n✅ Agent created\n")
    
    result = agent.process_request(test_request)
    
    print("\n" + "="*80)
    print("✅ AGENT PROCESSING COMPLETE")
    print("="*80)
    print("\n📊 Result:")
    print(f"   Decision: {result.get('decision', 'N/A')}")
    print(f"   Confidence: {result.get('confidence', 0):.2%}")
    print(f"   \n💬 Response: {result.get('reason', 'N/A')[:200]}...")
    print("\n" + "="*80)
    
except Exception as e:
    print(f"\n❌ Error processing request: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test complete! If you saw detailed logs above, logging is working.")
print("If you only see this message, there's a logging configuration issue.\n")
