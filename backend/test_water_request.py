"""
Send a test request to the running server to trigger Water Agent logs
"""
import requests
import json

print("\n" + "="*80)
print("🧪 SENDING TEST REQUEST TO WATER AGENT")
print("="*80)

# The request payload
payload = {
    "type": "water_quality_test",
    "department": "water",
    "location": "Main Street Water Treatment Plant",
    "reason": "What is the current water quality status?",
    "urgency": "normal",
    "user_id": "test_user_123",
    "details": {
        "test_type": "standard_quality"
    }
}

print("\n📋 Request:")
print(json.dumps(payload, indent=2))
print("\n" + "="*80)
print("🌐 Sending POST to http://localhost:8000/api/v1/query")
print("="*80)

try:
    response = requests.post(
        "http://localhost:8000/api/v1/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    print("\n📊 Response:")
    print(json.dumps(response.json(), indent=2))
    
    job_id = response.json().get("job_id")
    if job_id:
        print(f"\n🔑 Job ID: {job_id}")
        print(f"\n💡 Check the server console - you should see detailed Water Agent logs!")
        print(f"   Look for emojis like: 🛠️ 🔮 🌐 🧹 ✅")
    
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to server!")
    print("   Make sure the server is running: python main.py")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
