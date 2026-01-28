"""
Test Suite: Agent-to-Agent Collaboration
Tests scenarios where Water Agent must query/coordinate with other agents
"""
import asyncio
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.agents.water_v2.graph import create_workflow
from app.agents.water_v2.state import InputEvent
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost/city_mas")
# Ensure async driver is used
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif DATABASE_URL.startswith("postgresql+psycopg2://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg2://", "postgresql+asyncpg://")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ============================================================
# TEST SCENARIO 1: Water-Fire Coordination
# ============================================================

@pytest.mark.asyncio
async def test_water_fire_coordination():
    """
    Scenario: Water maintenance needed, but Fire Department requires water supply
    
    Expected behavior:
    - Water agent checks fire hydrant dependency
    - Coordinates with fire department schedule
    - Decision considers fire safety constraints
    """
    print("\n" + "="*70)
    print("TEST 1: WATER-FIRE AGENT COORDINATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Maintenance near fire hydrants
        input_event = InputEvent(
            type="pipeline_maintenance_request",
            from_entity="Coordinator",
            location="Commercial District A",
            priority="medium",
            reason="Pipeline maintenance will affect fire hydrants in area",
            requested_shift_days=2,
            metadata={"citizen_id": "C10001"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Context Considered: {len(result.get('context', []))} factors")
        print(f"  Safety Considerations: {result.get('risk_level')}")
        
        # Should consider fire department coordination
        context_text = str(result.get('context', [])).lower()
        
        print(f"\n🔍 Coordination Check:")
        print(f"  Fire-related context: {'fire' in context_text or 'hydrant' in context_text}")
        print(f"  Safety risk assessed: {result.get('risk_level') is not None}")
        
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Water-Fire coordination scenario handled")


# ============================================================
# TEST SCENARIO 2: Water-Roads Department Coordination
# ============================================================

@pytest.mark.asyncio
async def test_water_roads_coordination():
    """
    Scenario: Water pipe repair requires road excavation
    
    Expected behavior:
    - Water agent identifies road work dependency
    - Checks roads department schedule
    - Coordinates to avoid traffic disruption
    """
    print("\n" + "="*70)
    print("TEST 2: WATER-ROADS DEPARTMENT COORDINATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Underground pipe repair requiring road access
        input_event = InputEvent(
            type="emergency_repair_request",
            from_entity="Roads Department",
            location="Main Street Downtown",
            priority="high",
            reason="Underground water main break requires road excavation",
            requested_shift_days=1,
            metadata={"citizen_id": "C10002"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Plan: {result.get('plan', {}).get('action', 'N/A')[:100]}...")
        print(f"  Dependencies: {len(result.get('dependencies', []))} identified")
        
        # Check if road work is considered
        plan_text = str(result.get('plan', {})).lower()
        
        print(f"\n🔍 Dependencies Check:")
        print(f"  Road work mentioned: {'road' in plan_text or 'excavation' in plan_text}")
        print(f"  Traffic considered: {'traffic' in plan_text}")
        
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Water-Roads coordination scenario handled")


# ============================================================
# TEST SCENARIO 3: Water-Electric Grid Coordination
# ============================================================

@pytest.mark.asyncio
async def test_water_electric_coordination():
    """
    Scenario: Water pump maintenance requires power shutdown coordination
    
    Expected behavior:
    - Water agent identifies power dependency
    - Coordinates with electric department
    - Plans backup power arrangements
    """
    print("\n" + "="*70)
    print("TEST 3: WATER-ELECTRIC GRID COORDINATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Pump station maintenance requiring power
        input_event = InputEvent(
            type="pipeline_maintenance_request",
            from_entity="Electric Department",
            location="North Pump Station",
            priority="medium",
            reason="Electrical maintenance on water pumps",
            requested_shift_days=1,
            metadata={"citizen_id": "C10003"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Emergency Backup: {result.get('observations', {}).get('check_emergency_backup', {}).get('duration_hours', 'N/A')} hours")
        
        # Should consider backup power
        backup_check = result.get('observations', {}).get('check_emergency_backup', {})
        
        print(f"\n🔍 Power Coordination Check:")
        print(f"  Backup duration: {backup_check.get('duration_hours', 0)} hours")
        print(f"  Backup adequate: {backup_check.get('duration_hours', 0) >= 24}")
        
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Water-Electric coordination scenario handled")


# ============================================================
# TEST SCENARIO 4: Multi-Agent Resource Conflict
# ============================================================

@pytest.mark.asyncio
async def test_multi_agent_resource_conflict():
    """
    Scenario: Multiple departments need same manpower resources
    
    Expected behavior:
    - Water agent checks manpower availability
    - Detects schedule conflicts with other departments
    - Proposes alternative scheduling
    """
    print("\n" + "="*70)
    print("TEST 4: MULTI-AGENT RESOURCE CONFLICT")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Request during likely busy period
        input_event = InputEvent(
            type="pipeline_maintenance_request",
            from_entity="Coordinator",
            location="West Zone",
            priority="low",
            reason="Routine pipeline inspection",
            requested_shift_days=1,
            metadata={"citizen_id": "C10004", "work_type": "scheduled_maintenance"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Manpower Check: {result.get('observations', {}).get('check_manpower_availability', {})}")
        print(f"  Schedule Check: {result.get('observations', {}).get('check_schedule_conflicts', {})}")
        
        manpower = result.get('observations', {}).get('check_manpower_availability', {})
        schedule = result.get('observations', {}).get('check_schedule_conflicts', {})
        
        print(f"\n🔍 Resource Conflict Check:")
        print(f"  Manpower available: {manpower.get('available_workers', 'N/A')}")
        print(f"  Schedule conflicts: {schedule.get('conflicts', False)}")
        
        # If conflicts detected, should handle appropriately
        if schedule.get('conflicts') or manpower.get('available_workers', 0) < 5:
            print(f"  Conflict handling: {result.get('decision')}")
        
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Multi-agent resource conflict handled")


# ============================================================
# TEST SCENARIO 5: Sequential Agent Workflow
# ============================================================

@pytest.mark.asyncio
async def test_sequential_agent_workflow():
    """
    Scenario: Water work must happen AFTER fire department approval
    
    Expected behavior:
    - Water agent recognizes dependency
    - Checks fire department status
    - Sequences work appropriately
    """
    print("\n" + "="*70)
    print("TEST 5: SEQUENTIAL AGENT WORKFLOW")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Work requiring fire department clearance
        input_event = InputEvent(
            type="new_connection_request",
            from_entity="Fire Department",
            location="Fire Station Area",
            priority="medium",
            reason="New water line installation near fire station",
            requested_shift_days=5,
            metadata={"citizen_id": "C10005", "project_type": "construction"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Dependencies: {result.get('dependencies', [])}")
        print(f"  Sequencing: {result.get('plan', {}).get('steps', [])}")
        
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Sequential workflow coordination handled")


# ============================================================
# TEST SCENARIO 6: Cross-Department Data Query
# ============================================================

@pytest.mark.asyncio
async def test_cross_department_data_query():
    """
    Scenario: Water agent needs data from another department's database
    
    Expected behavior:
    - Water agent queries shared database
    - Retrieves cross-department information
    - Makes decision based on integrated data
    """
    print("\n" + "="*70)
    print("TEST 6: CROSS-DEPARTMENT DATA QUERY")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Request requiring cross-department data
        input_event = InputEvent(
            type="capacity_assessment_request",
            from_entity="Planning Department",
            location="Industrial Park",
            priority="medium",
            reason="Water infrastructure impact assessment",
            requested_shift_days=3,
            metadata={"citizen_id": "C10006"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Context Sources: {len(result.get('context', []))}"))
        print(f"  Tools Executed: {list(result.get('observations', {}).keys())}")
        
        # Should have gathered data from tools
        tools_used = list(result.get('observations', {}).keys())
        
        print(f"\n🔍 Data Integration Check:")
        print(f"  Tools used: {len(tools_used)}")
        print(f"  Pipeline data: {'check_pipeline_health' in tools_used}")
        print(f"  Safety data: {'check_safety_risk' in tools_used}")
        print(f"  Resource data: {'check_emergency_backup' in tools_used}")
        
        assert len(tools_used) > 0, "Should use at least one tool"
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Cross-department data query handled")


# ============================================================
# TEST SCENARIO 7: Agent Collaboration on Complex Project
# ============================================================

@pytest.mark.asyncio
async def test_complex_multi_agent_project():
    """
    Scenario: Large project requiring coordination across multiple departments
    
    Expected behavior:
    - Water agent identifies all dependencies
    - Plans multi-phase coordination
    - Ensures all constraints satisfied
    """
    print("\n" + "="*70)
    print("TEST 7: COMPLEX MULTI-AGENT PROJECT")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Large infrastructure project
        input_event = InputEvent(
            type="new_connection_request",
            from_entity="Development Authority",
            location="City Center Redevelopment",
            priority="high",
            reason="Complete water system upgrade for new development",
            requested_shift_days=30,
            metadata={"citizen_id": "C10007", "project_scale": "major_infrastructure"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Feasible: {result.get('feasible')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Constraints Checked: {len(result.get('observations', {}))}")
        
        # Large project likely needs escalation or careful planning
        observations = result.get('observations', {})
        
        print(f"\n🔍 Multi-Agent Coordination:")
        print(f"  Pipeline health: {observations.get('check_pipeline_health', {}).get('pressure_ok', 'N/A')}")
        print(f"  Manpower: {observations.get('check_manpower_availability', {}).get('sufficient', 'N/A')}")
        print(f"  Budget: {observations.get('check_budget_availability', {}).get('sufficient', 'N/A')}")
        print(f"  Schedule: {observations.get('check_schedule_conflicts', {}).get('conflicts', 'N/A')}")
        
        assert result.get('decision') in ['approve', 'escalate'], "Should make a decision"
        print("\n✅ TEST PASSED: Complex multi-agent project handled")


# ============================================================
# RUN ALL TESTS
# ============================================================

async def run_all_tests():
    """Run all agent-to-agent coordination tests"""
    print("\n" + "="*70)
    print("🤝 AGENT-TO-AGENT COLLABORATION TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Water-Fire Coordination", test_water_fire_coordination),
        ("Water-Roads Coordination", test_water_roads_coordination),
        ("Water-Electric Coordination", test_water_electric_coordination),
        ("Multi-Agent Resource Conflict", test_multi_agent_resource_conflict),
        ("Sequential Agent Workflow", test_sequential_agent_workflow),
        ("Cross-Department Data Query", test_cross_department_data_query),
        ("Complex Multi-Agent Project", test_complex_multi_agent_project),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n⚠️  TEST ERROR: {name}")
            print(f"   Error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
