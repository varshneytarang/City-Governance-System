"""
Test script to verify Fire and Sanitation agents can query database using ACTUAL schema tables
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.agents.sanitation_agent.database import DatabaseConnection as SanitationDB, SanitationDepartmentQueries
from backend.agents.fire_agent.database import DatabaseConnection as FireDB, FireDepartmentQueries

def test_sanitation_agent():
    """Test sanitation agent database queries"""
    print("\n" + "="*60)
    print("TESTING SANITATION AGENT")
    print("="*60)
    
    try:
        db = SanitationDB()
        queries = SanitationDepartmentQueries(db)
        
        # Test 1: Get sanitation inspections
        print("\n1️⃣ Testing get_sanitation_inspections()...")
        inspections = queries.get_sanitation_inspections(days=90)
        print(f"   ✅ Retrieved {len(inspections)} sanitation inspections")
        if inspections:
            print(f"   📋 Sample: {inspections[0].get('location')} - {inspections[0].get('outcome')}")
        
        # Test 2: Get active projects
        print("\n2️⃣ Testing get_active_projects()...")
        projects = queries.get_active_projects()
        print(f"   ✅ Retrieved {len(projects)} active sanitation projects")
        if projects:
            print(f"   📋 Sample: {projects[0].get('project_name')} - {projects[0].get('status')}")
        
        # Test 3: Get work schedule
        print("\n3️⃣ Testing get_work_schedule()...")
        schedules = queries.get_work_schedule(days_ahead=7)
        print(f"   ✅ Retrieved {len(schedules)} scheduled sanitation work items")
        if schedules:
            print(f"   📋 Sample: {schedules[0].get('activity_type')} on {schedules[0].get('scheduled_date')}")
        
        # Test 4: Get available workers
        print("\n4️⃣ Testing get_available_workers()...")
        workers = queries.get_available_workers()
        print(f"   ✅ Retrieved {len(workers)} available sanitation workers")
        if workers:
            print(f"   📋 Sample: {workers[0].get('worker_name')} - {workers[0].get('role')}")
        
        # Test 5: Get recent incidents
        print("\n5️⃣ Testing get_recent_incidents()...")
        incidents = queries.get_recent_incidents(days=30)
        print(f"   ✅ Retrieved {len(incidents)} recent sanitation incidents")
        if incidents:
            print(f"   📋 Sample: {incidents[0].get('incident_type')} at {incidents[0].get('location')}")
        
        # Test 6: Get budget status
        print("\n6️⃣ Testing get_budget_status()...")
        budget = queries.get_budget_status()
        if budget:
            print(f"   ✅ Budget: ${budget.get('total_budget')} total, ${budget.get('remaining')} remaining")
        else:
            print(f"   ⚠ No budget record found for current month")
        
        db.close()
        print("\n✅ SANITATION AGENT: ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ SANITATION AGENT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fire_agent():
    """Test fire agent database queries"""
    print("\n" + "="*60)
    print("TESTING FIRE AGENT")
    print("="*60)
    
    try:
        db = FireDB()
        queries = FireDepartmentQueries(db)
        
        # Test 1: Get fire incidents
        print("\n1️⃣ Testing get_fire_incidents()...")
        incidents = queries.get_fire_incidents(days=90)
        print(f"   ✅ Retrieved {len(incidents)} fire incidents")
        if incidents:
            print(f"   📋 Sample: {incidents[0].get('incident_type')} - {incidents[0].get('severity')}")
        
        # Test 2: Get active fire incidents
        print("\n2️⃣ Testing get_active_fire_incidents()...")
        active = queries.get_active_fire_incidents()
        print(f"   ✅ Retrieved {len(active)} active fire incidents")
        if active:
            print(f"   📋 Sample: {active[0].get('incident_type')} at {active[0].get('location')}")
        
        # Test 3: Get active projects
        print("\n3️⃣ Testing get_active_projects()...")
        projects = queries.get_active_projects()
        print(f"   ✅ Retrieved {len(projects)} active fire projects")
        if projects:
            print(f"   📋 Sample: {projects[0].get('project_name')} - {projects[0].get('status')}")
        
        # Test 4: Get work schedule
        print("\n4️⃣ Testing get_work_schedule()...")
        schedules = queries.get_work_schedule(days_ahead=7)
        print(f"   ✅ Retrieved {len(schedules)} scheduled fire work items")
        if schedules:
            print(f"   📋 Sample: {schedules[0].get('activity_type')} on {schedules[0].get('scheduled_date')}")
        
        # Test 5: Get available workers
        print("\n5️⃣ Testing get_available_workers()...")
        workers = queries.get_available_workers()
        print(f"   ✅ Retrieved {len(workers)} available firefighters")
        if workers:
            print(f"   📋 Sample: {workers[0].get('worker_name')} - {workers[0].get('role')}")
        
        # Test 6: Get budget status
        print("\n6️⃣ Testing get_budget_status()...")
        budget = queries.get_budget_status()
        if budget:
            print(f"   ✅ Budget: ${budget.get('total_budget')} total, ${budget.get('remaining')} remaining")
        else:
            print(f"   ⚠ No budget record found for current month")
        
        db.close()
        print("\n✅ FIRE AGENT: ALL TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ FIRE AGENT ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "🔍 TESTING FIRE & SANITATION DATABASE CONNECTIVITY 🔍".center(60))
    
    sanitation_ok = test_sanitation_agent()
    fire_ok = test_fire_agent()
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"Sanitation Agent: {'✅ PASS' if sanitation_ok else '❌ FAIL'}")
    print(f"Fire Agent: {'✅ PASS' if fire_ok else '❌ FAIL'}")
    
    if sanitation_ok and fire_ok:
        print("\n🎉 SUCCESS: Both agents can query database using actual schema tables!")
    else:
        print("\n⚠ Some tests failed. Check errors above.")
    
    print("="*60 + "\n")
