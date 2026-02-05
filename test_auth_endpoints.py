"""
Quick Test Script for Authentication Endpoints
Run this to verify backend auth is working before testing frontend
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_register():
    print_section("TEST 1: Register New User")
    url = f"{BASE_URL}/register"
    payload = {
        "email": "test.user@example.com",
        "password": "TestPass123!",
        "full_name": "Test User",
        "role": "citizen"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            return response.json()
        else:
            print("⚠️ Registration failed (may already exist)")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_login():
    print_section("TEST 2: Login with Test Account")
    url = f"{BASE_URL}/login"
    payload = {
        "email": "admin@citygovernance.in",
        "password": "admin123"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            return response.json()
        else:
            print("❌ Login failed")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_get_user(token):
    print_section("TEST 3: Get Current User Info")
    url = f"{BASE_URL}/me"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ User info retrieved!")
        else:
            print("❌ Failed to get user info")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_verify_token(token):
    print_section("TEST 4: Verify Token")
    url = f"{BASE_URL}/verify"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Token is valid!")
        else:
            print("❌ Token verification failed")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_invalid_login():
    print_section("TEST 5: Invalid Login (Should Fail)")
    url = f"{BASE_URL}/login"
    payload = {
        "email": "wrong@email.com",
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [400, 401]:
            print("✅ Correctly rejected invalid credentials!")
        else:
            print("⚠️ Unexpected response")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "🔐 AUTHENTICATION ENDPOINT TEST SUITE" + "\n")
    print("Testing backend at: " + BASE_URL)
    print("Make sure backend is running on http://localhost:8000")
    print("\n" + "-"*60)
    
    # Test 1: Register (optional, may fail if user exists)
    test_register()
    
    # Test 2: Login with test account
    login_result = test_login()
    
    if login_result and "token" in login_result:
        token = login_result["token"]["access_token"]
        
        # Test 3: Get user info
        test_get_user(token)
        
        # Test 4: Verify token
        test_verify_token(token)
    else:
        print("\n⚠️ Cannot proceed with authenticated tests - login failed")
    
    # Test 5: Invalid login
    test_invalid_login()
    
    print("\n" + "="*60)
    print("  TEST SUITE COMPLETED")
    print("="*60)
    print("\n✅ If all tests passed, your backend auth is working!")
    print("📱 Now you can test the frontend at: http://localhost:3000/#login")
    print("\nTest Accounts:")
    print("  Email: admin@citygovernance.in")
    print("  Password: admin123")
    print("\n")

if __name__ == "__main__":
    main()
