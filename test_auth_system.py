"""
Test Authentication System
Quick verification script for the authentication endpoints
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1/auth"

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_test(name, success, message=""):
    """Print test result"""
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {name}")
    if message:
        print(f"    {message}")


def test_register():
    """Test user registration"""
    print(f"\n{BLUE}=== Testing Registration ==={RESET}")
    
    test_email = f"test_{datetime.now().timestamp()}@example.com"
    
    data = {
        "email": test_email,
        "password": "Test1234!",
        "full_name": "Test User",
        "role": "citizen"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=data)
        
        if response.status_code == 201:
            result = response.json()
            print_test("User Registration", True, f"User created: {result['user']['email']}")
            return result
        else:
            print_test("User Registration", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        print_test("User Registration", False, str(e))
        return None


def test_login(email, password):
    """Test user login"""
    print(f"\n{BLUE}=== Testing Login ==={RESET}")
    
    data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_test("User Login", True, f"Token received, expires in {result['token']['expires_in']}s")
            return result
        else:
            print_test("User Login", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        print_test("User Login", False, str(e))
        return None


def test_get_current_user(token):
    """Test getting current user info"""
    print(f"\n{BLUE}=== Testing Get Current User ==={RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_test("Get Current User", True, f"User: {result['email']}, Role: {result['role']}")
            return result
        else:
            print_test("Get Current User", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        print_test("Get Current User", False, str(e))
        return None


def test_verify_token(token):
    """Test token verification"""
    print(f"\n{BLUE}=== Testing Token Verification ==={RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/verify", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_test("Token Verification", True, result['message'])
            return True
        else:
            print_test("Token Verification", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Token Verification", False, str(e))
        return False


def test_refresh_token(refresh_token):
    """Test token refresh"""
    print(f"\n{BLUE}=== Testing Token Refresh ==={RESET}")
    
    data = {
        "refresh_token": refresh_token
    }
    
    try:
        response = requests.post(f"{BASE_URL}/refresh", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_test("Token Refresh", True, "New tokens generated")
            return result
        else:
            print_test("Token Refresh", False, f"Status: {response.status_code}")
            return None
    except Exception as e:
        print_test("Token Refresh", False, str(e))
        return None


def test_logout(token):
    """Test user logout"""
    print(f"\n{BLUE}=== Testing Logout ==={RESET}")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print_test("User Logout", True, result['message'])
            return True
        else:
            print_test("User Logout", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("User Logout", False, str(e))
        return False


def test_admin_login():
    """Test login with pre-configured admin account"""
    print(f"\n{BLUE}=== Testing Admin Login ==={RESET}")
    
    data = {
        "email": "admin@citygovernance.in",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print_test("Admin Login", True, f"Admin user: {result['user']['email']}, Role: {result['user']['role']}")
            return result
        else:
            print_test("Admin Login", False, f"Status: {response.status_code}, Error: {response.text}")
            return None
    except Exception as e:
        print_test("Admin Login", False, str(e))
        return None


def run_all_tests():
    """Run all authentication tests"""
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}   City Governance Authentication System Test Suite{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000")
        print(f"{GREEN}✓ Backend is running{RESET}")
    except:
        print(f"{RED}✗ Backend is not running. Please start the backend first:{RESET}")
        print(f"  python -m uvicorn backend.app.server:app --reload --port 8000")
        return
    
    # Test 1: Register new user
    register_result = test_register()
    if not register_result:
        print(f"\n{RED}Registration failed. Stopping tests.{RESET}")
        return
    
    # Extract credentials
    test_email = register_result['user']['email']
    test_password = "Test1234!"
    access_token = register_result['token']['access_token']
    refresh_token = register_result['token']['refresh_token']
    
    # Test 2: Login with created user
    login_result = test_login(test_email, test_password)
    if login_result:
        access_token = login_result['token']['access_token']
    
    # Test 3: Get current user
    test_get_current_user(access_token)
    
    # Test 4: Verify token
    test_verify_token(access_token)
    
    # Test 5: Refresh token
    test_refresh_token(refresh_token)
    
    # Test 6: Admin login
    test_admin_login()
    
    # Test 7: Logout
    test_logout(access_token)
    
    # Test 8: Verify token after logout (should fail)
    print(f"\n{BLUE}=== Testing Token After Logout ==={RESET}")
    if not test_verify_token(access_token):
        print_test("Token Invalid After Logout", True, "Token correctly invalidated")
    else:
        print_test("Token Invalid After Logout", False, "Token should be invalid")
    
    # Summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{GREEN}✓ All authentication tests completed!{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    print(f"\n{BLUE}Next Steps:{RESET}")
    print(f"  1. Open browser: http://localhost:5173/login.html")
    print(f"  2. Test login with: admin@citygovernance.in / admin123")
    print(f"  3. Try registration: http://localhost:5173/register.html")
    print(f"  4. Configure Google OAuth (optional)")
    print(f"\n{BLUE}See AUTH_SETUP_GUIDE.md for detailed setup instructions.{RESET}\n")


if __name__ == "__main__":
    run_all_tests()
