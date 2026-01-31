"""
DIAGNOSTIC TEST - Check What's Actually Working

This test verifies:
1. Can we connect to the database?
2. Do database queries work?
3. Does the agent use real database data?
4. Is LLM actually being called?
5. Are constraints enforced?
"""

import os
import sys
from datetime import datetime

print("="*80)
print("DIAGNOSTIC TEST - CHECKING WHAT ACTUALLY WORKS")
print("="*80)

# Test 1: Database Connection
print("\n[TEST 1] Database Connection")
print("-"*80)
try:
    from water_agent.database import DatabaseConnection, WaterDepartmentQueries
    
    db = DatabaseConnection()
    print("✓ DatabaseConnection class imported")
    
    # Try to connect
    conn = db.get_connection()
    if conn:
        print("✓ Database connection established")
        
        # Try a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM workers")
        count = cursor.fetchone()[0]
        print(f"✓ Database query works - Found {count} workers in DB")
        cursor.close()
    else:
        print("✗ Database connection FAILED - Connection is None")
        
except Exception as e:
    print(f"✗ Database test FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Tool Queries
print("\n[TEST 2] Tool Database Queries")
print("-"*80)
try:
    from water_agent.tools import WaterDepartmentTools
    from water_agent.database import DatabaseConnection, WaterDepartmentQueries
    
    db = DatabaseConnection()
    queries = WaterDepartmentQueries(db)
    tools = WaterDepartmentTools(db, queries)
    
    print("✓ Tools initialized with database")
    
    # Test manpower check
    result = tools.check_manpower_availability(location="Zone-A", required_count=5)
    print(f"✓ Manpower check executed")
    print(f"  Result: {result}")
    
    if "error" in result:
        print(f"  ✗ Query returned error: {result['error']}")
    else:
        print(f"  ✓ Found {result.get('available_count', 0)} workers")
    
    # Test pipeline check
    result = tools.check_pipeline_health(location="Zone-A")
    print(f"✓ Pipeline health check executed")
    print(f"  Result: {result.get('overall_condition', 'unknown')}")
    
    # Test budget check
    result = tools.check_budget_availability(estimated_cost=50000)
    print(f"✓ Budget check executed")
    print(f"  Result: {result}")
    
except Exception as e:
    print(f"✗ Tool queries FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Agent with Real Database
print("\n[TEST 3] Agent Using Real Database Data")
print("-"*80)
try:
    from water_agent import WaterDepartmentAgent
    
    agent = WaterDepartmentAgent()
    print("✓ Agent initialized")
    
    # Make a request
    request = {
        "type": "maintenance_request",
        "location": "Zone-A",
        "user_request": "Schedule pipeline inspection",
        "activity": "inspection",
        "priority": "medium"
    }
    
    print("  Submitting request...")
    result = agent.decide(request)
    
    print(f"✓ Agent processed request")
    print(f"  Decision: {result.get('decision')}")
    
    # Check if tool results were used
    if result.get("details"):
        print(f"  Tool results available: {bool(result['details'].get('tool_results'))}")
    
    agent.close()
    
except Exception as e:
    print(f"✗ Agent test FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 4: LLM Integration
print("\n[TEST 4] LLM Integration Status")
print("-"*80)
try:
    from water_agent.config import settings
    
    # Check settings object (proper way - loads from .env)
    if settings.LLM_PROVIDER == "groq":
        api_key = settings.GROQ_API_KEY
    elif settings.LLM_PROVIDER == "openai":
        api_key = settings.OPENAI_API_KEY
    else:
        api_key = None
    
    print(f"  LLM Provider: {settings.LLM_PROVIDER}")
    print(f"  LLM Model: {settings.LLM_MODEL}")
    print(f"  API Key Configured: {'✓ YES' if api_key else '✗ NO'}")
    
    if api_key:
        print(f"  API Key: {api_key[:8]}..." if len(api_key) > 8 else api_key)
        print("\n  ✓ LLM is configured and ready!")
        print("  To verify LLM is called, run:")
        print("    python test_groq_live.py")
        print("  Then check: https://console.groq.com/")
    else:
        print("\n  ⚠️  No API key found!")
        print("  Add to .env file:")
        print("    GROQ_API_KEY=your_key_here")
        
except Exception as e:
    print(f"✗ LLM config check FAILED: {e}")

# Test 5: Database Constraints
print("\n[TEST 5] Database Constraints Check")
print("-"*80)
try:
    from water_agent.database import DatabaseConnection
    
    db = DatabaseConnection()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Check if constraints exist
    print("  Checking database constraints...")
    
    # Check budget table
    cursor.execute("SELECT COUNT(*) FROM budget")
    budget_count = cursor.fetchone()[0]
    print(f"  Budget entries: {budget_count}")
    
    # Check workers table
    cursor.execute("SELECT COUNT(*) FROM workers WHERE status = 'available'")
    available_workers = cursor.fetchone()[0]
    print(f"  Available workers: {available_workers}")
    
    # Check pipelines table
    cursor.execute("SELECT COUNT(*) FROM pipelines WHERE condition = 'good'")
    good_pipelines = cursor.fetchone()[0]
    print(f"  Pipelines in good condition: {good_pipelines}")
    
    if budget_count > 0 and available_workers > 0:
        print("  ✓ Database has data for constraints")
    else:
        print("  ⚠️  Database may be empty - constraints won't work")
    
    cursor.close()
    
except Exception as e:
    print(f"✗ Constraint check FAILED: {e}")

# Summary
print("\n" + "="*80)
print("DIAGNOSTIC SUMMARY")
print("="*80)
print("""
Next Steps:
1. If database tests failed → Check database connection settings
2. If tool queries failed → Check database schema and data
3. If agent test failed → Check logs for errors
4. If LLM not configured → Add API key to .env
5. Run actual tests: python -m pytest tests/test_integration_workflow.py -v

To verify LLM is being used:
  python test_groq_live.py
  Then check Groq console: https://console.groq.com/
""")
print("="*80)
