"""
Test Backend Integration with Coordination Agent

This script tests the complete flow:
  Client → Backend → Coordinator → Department Agent → Response
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"


def test_backend_coordinator_integration():
    """Test that backend routes requests through coordinator to agents"""
    
    print("\n" + "=" * 80)
    print("TEST: Backend → Coordinator → Agent Integration")
    print("=" * 80)
    
    # Test 1: Health check
    print("\n1️⃣ Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/health")
        health = response.json()
        print(f"   Status: {health.get('status')}")
        print(f"   Coordinator: {health.get('coordinator')}")
        print(f"   Version: {health.get('version')}")
        
        if health.get('coordinator') != 'initialized':
            print("   ❌ Coordinator not initialized!")
            return False
        print("   ✅ Backend healthy and coordinator ready")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        print("   Make sure backend is running: uvicorn backend.app.server:app --reload")
        return False
    
    # Test 2: Submit query (Water department)
    print("\n2️⃣ Submitting Water Department Query...")
    print("   Request: Capacity query for Downtown")
    
    query_payload = {
        "type": "capacity_query",
        "location": "Downtown",
        "reason": "Testing backend integration",
        "from": "TestClient"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/query",
            json=query_payload
        )
        
        if response.status_code != 200:
            print(f"   ❌ Query submission failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        submit_result = response.json()
        job_id = submit_result.get("job_id")
        agent_type = submit_result.get("agent_type")
        
        print(f"   ✅ Query submitted successfully")
        print(f"   Job ID: {job_id}")
        print(f"   Routed to: {agent_type} agent")
        print(f"   Status: {submit_result.get('status')}")
    except Exception as e:
        print(f"   ❌ Failed to submit query: {e}")
        return False
    
    # Test 3: Poll for results
    print("\n3️⃣ Polling for Results...")
    print(f"   Job ID: {job_id}")
    
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        time.sleep(2)  # Wait 2 seconds between polls
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/query/{job_id}")
            job = response.json()
            status = job.get("status")
            
            print(f"   Attempt {attempt}/{max_attempts}: Status = {status}")
            
            if status == "succeeded":
                print("\n   ✅ Job completed successfully!")
                result = job.get("result", {})
                
                print("\n   Agent Decision:")
                print(f"   • Decision: {result.get('decision', 'N/A')}")
                print(f"   • Reason: {result.get('reason', 'N/A')}")
                
                if result.get('decision') == 'escalate':
                    print(f"   • Requires Human Review: {result.get('requires_human_review', False)}")
                    details = result.get('details', {})
                    print(f"   • Feasible: {details.get('feasible', 'N/A')}")
                    print(f"   • Policy Compliant: {details.get('policy_compliant', 'N/A')}")
                    print(f"   • Confidence: {details.get('confidence', 0):.2f}")
                else:
                    recommendation = result.get('recommendation', {})
                    print(f"   • Confidence: {recommendation.get('confidence', 0):.2f}")
                    print(f"   • Action: {recommendation.get('action', 'N/A')}")
                
                return True
                
            elif status == "failed":
                print(f"\n   ❌ Job failed!")
                print(f"   Error: {job.get('error', 'Unknown error')}")
                return False
            
            elif status in ["queued", "running"]:
                # Continue polling
                continue
            else:
                print(f"\n   ⚠️  Unknown status: {status}")
                
        except Exception as e:
            print(f"   ❌ Error polling job: {e}")
            return False
    
    print(f"\n   ⏱️  Timeout: Job did not complete in {max_attempts * 2} seconds")
    return False


def test_engineering_query():
    """Test routing to Engineering department"""
    
    print("\n" + "=" * 80)
    print("TEST: Engineering Department Query")
    print("=" * 80)
    
    query_payload = {
        "type": "project_planning",
        "location": "Main Street",
        "reason": "Road repair needed",
        "estimated_cost": 50000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/query", json=query_payload)
        result = response.json()
        
        print(f"✅ Query submitted")
        print(f"   Job ID: {result.get('job_id')}")
        print(f"   Agent: {result.get('agent_type')}")
        
        if result.get('agent_type') == 'engineering':
            print("   ✅ Correctly routed to Engineering agent")
            return True
        else:
            print(f"   ❌ Wrong routing: Expected 'engineering', got '{result.get('agent_type')}'")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def test_fire_query():
    """Test routing to Fire department"""
    
    print("\n" + "=" * 80)
    print("TEST: Fire Department Query")
    print("=" * 80)
    
    query_payload = {
        "type": "fire_inspection",
        "location": "Industrial Zone",
        "reason": "Routine fire safety inspection"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/query", json=query_payload)
        result = response.json()
        
        print(f"✅ Query submitted")
        print(f"   Job ID: {result.get('job_id')}")
        print(f"   Agent: {result.get('agent_type')}")
        
        if result.get('agent_type') == 'fire':
            print("   ✅ Correctly routed to Fire agent")
            return True
        else:
            print(f"   ❌ Wrong routing: Expected 'fire', got '{result.get('agent_type')}'")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🧪 TESTING: Backend → Coordinator → Agent Integration")
    print("=" * 80)
    print("\nPrerequisites:")
    print("  1. Backend must be running: uvicorn backend.app.server:app --reload")
    print("  2. Database must be accessible")
    print("  3. GROQ_API_KEY must be set (for LLM calls)")
    print("\n" + "=" * 80)
    
    # Run tests
    test1_passed = test_backend_coordinator_integration()
    test2_passed = test_engineering_query()
    test3_passed = test_fire_query()
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Water Department Query:       {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Engineering Department Route: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    print(f"Fire Department Route:        {'✅ PASS' if test3_passed else '❌ FAIL'}")
    print("=" * 80)
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nBackend is successfully routing requests through Coordinator to Agents!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
