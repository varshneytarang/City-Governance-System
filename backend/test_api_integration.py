"""
API Integration Test - Testing Fire and Water Agent Endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("🚀 API INTEGRATION TESTING")
print("=" * 80)

# Test 1: Fire Agent - Emergency Response
print("\n" + "=" * 80)
print("🔥 TEST 1: Fire Agent - Building Fire Emergency")
print("=" * 80)

fire_request = {
    "user_id": 1,  # Added required user_id
    "request_type": "emergency_response",
    "emergency_type": "fire",
    "location": {
        "address": "Test Building, Delhi",
        "latitude": 28.6139,
        "longitude": 77.2090
    },
    "description": "Major fire in commercial building",
    "casualties": 3,
    "building_type": "commercial",
    "fire_intensity": "major",
    "priority": "critical"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/fire/emergency",
        json=fire_request,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response Received")
        print(f"📋 Request ID: {data.get('request_id', 'N/A')}")
        print(f"✅ Decision: {data.get('decision', 'N/A')}")
        print(f"💭 Reasoning: {data.get('reasoning', 'N/A')}")
        print(f"🎯 Risk Level: {data.get('risk_level', 'N/A')}")
        print(f"💰 Estimated Cost: ₹{data.get('estimated_cost', 0):,.2f}")
        print(f"⏱️  Estimated Duration: {data.get('estimated_duration', 0)} minutes")
        
        # Check coordination
        coordination = data.get('next_steps', [])
        if coordination:
            print(f"🤝 Coordination: {len(coordination)} departments")
            for step in coordination:
                print(f"   - {step}")
    else:
        print(f"❌ Error: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ ERROR: Backend server not running!")
    print("💡 Start server: D:\\City-Governance-System\\backend\\venv\\Scripts\\python.exe D:\\City-Governance-System\\backend\\main.py")
    exit(1)
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 2: Water Agent - Road Digging Request
print("\n" + "=" * 80)
print("💧 TEST 2: Water Agent - Road Digging Permission")
print("=" * 80)

water_request = {
    "request_type": "road_digging",
    "location": "Main Street, Block A",
    "priority": "medium",
    "description": "Road widening project",
    "details": {
        "purpose": "Infrastructure upgrade",
        "depth": 2.0,
        "duration": 14
    }
}

try:
    response = requests.post(
        f"{BASE_URL}/api/water/request",
        json=water_request,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response Received")
        print(f"📋 Request ID: {data.get('request_id', 'N/A')}")
        print(f"✅ Decision: {data.get('decision', 'N/A')}")
        print(f"💭 Reasoning: {data.get('reasoning', 'N/A')}")
        print(f"🎯 Risk Score: {data.get('risk_score', 0)}")
        print(f"💰 Estimated Cost: ₹{data.get('estimated_cost', 0):,.2f}")
        print(f"⏱️  Estimated Duration: {data.get('estimated_duration', 0)} days")
        
        # Check affected infrastructure
        affected = data.get('affected_infrastructure', [])
        if affected:
            print(f"🚧 Affected Infrastructure: {len(affected)} items")
            for item in affected:
                print(f"   - {item.get('infrastructure_type', 'N/A')}: {item.get('condition', 'N/A')}")
    else:
        print(f"❌ Error: Status {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 3: Fire Agent - Inspection Request
print("\n" + "=" * 80)
print("🏢 TEST 3: Fire Agent - Building Inspection")
print("=" * 80)

inspection_request = {
    "user_id": 1,  # Added required user_id
    "request_type": "fire_inspection",
    "location": {
        "address": "Commercial Complex, South Delhi",
        "latitude": 28.5355,
        "longitude": 77.3910
    },
    "description": "Annual fire safety inspection",
    "priority": "medium",
    "inspection_type": "routine"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/fire/inspection",
        json=inspection_request,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response Received")
        print(f"📋 Request ID: {data.get('request_id', 'N/A')}")
        print(f"✅ Decision: {data.get('decision', 'N/A')}")
        print(f"💭 Reasoning: {data.get('reasoning', 'N/A')}")
        print(f"💰 Estimated Cost: ₹{data.get('estimated_cost', 0):,.2f}")
    else:
        print(f"❌ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Test 4: Water Agent - Leakage Report
print("\n" + "=" * 80)
print("💧 TEST 4: Water Agent - Water Leakage Report")
print("=" * 80)

leakage_request = {
    "request_type": "leakage",
    "location": "Downtown Area",
    "priority": "high",
    "description": "Major water leakage affecting traffic",
    "details": {
        "severity": "high",
        "flow_rate": "heavy"
    }
}

try:
    response = requests.post(
        f"{BASE_URL}/api/water/request",
        json=leakage_request,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API Response Received")
        print(f"📋 Request ID: {data.get('request_id', 'N/A')}")
        print(f"✅ Decision: {data.get('decision', 'N/A')}")
        print(f"💭 Reasoning: {data.get('reasoning', 'N/A')}")
        print(f"⏱️  Estimated Duration: {data.get('estimated_duration', 0)} days")
    else:
        print(f"❌ Error: Status {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")

# Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print("✅ Fire Agent - Emergency Response: Tested")
print("✅ Water Agent - Road Digging: Tested")
print("✅ Fire Agent - Inspection: Tested")
print("✅ Water Agent - Leakage: Tested")
print("\n🎉 API Integration Tests Complete!")
print("=" * 80)
