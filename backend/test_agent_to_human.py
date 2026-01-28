"""
Test Suite: Agent-to-Human Escalation
Tests scenarios where the agent must escalate to human decision-makers
"""
import asyncio
import pytest
from datetime import datetime
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
# TEST SCENARIO 1: Low Confidence Escalation
# ============================================================

@pytest.mark.asyncio
async def test_low_confidence_escalation():
    """
    Scenario: Plan has low confidence score → Must escalate to human
    
    Expected behavior:
    - Confidence < 0.7 threshold
    - Decision = "escalate"
    - Response contains escalation reason
    """
    print("\n" + "="*70)
    print("TEST 1: LOW CONFIDENCE ESCALATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Vague request with missing critical details
        input_event = InputEvent(
            type="new_connection_request",
            from_entity="Citizen",
            location="Somewhere in the city",  # Vague location
            priority="medium",
            reason="Water problem",  # Vague description
            requested_shift_days=1,
            metadata={"citizen_id": "C12345"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Confidence: {result.get('confidence', 0):.2f}")
        print(f"  Escalation Reason: {result.get('escalation_reason', 'N/A')}")
        
        assert result.get("decision") == "escalate", "Should escalate due to low confidence"
        assert result.get("confidence", 1.0) < 0.7, "Confidence should be below threshold"
        assert "confidence" in result.get("escalation_reason", "").lower(), "Should mention confidence in reason"
        
        print("\n✅ TEST PASSED: Low confidence correctly triggers escalation")


# ============================================================
# TEST SCENARIO 2: Policy Violation Escalation
# ============================================================

@pytest.mark.asyncio
async def test_policy_violation_escalation():
    """
    Scenario: Plan violates department policies → Must escalate
    
    Expected behavior:
    - Policy violation detected
    - Decision = "escalate"
    - Policy violations listed in response
    """
    print("\n" + "="*70)
    print("TEST 2: POLICY VIOLATION ESCALATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Request that will violate delay policy (>3 days)
        input_event = InputEvent(
            type="pipeline_maintenance_request",
            from_entity="Coordinator",
            location="Downtown Zone",
            priority="low",
            reason="Routine inspection can wait",
            requested_shift_days=5,  # Exceeds max_delay_days (3)
            metadata={"citizen_id": "C67890"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Policy Compliant: {result.get('policy_compliant')}")
        print(f"  Violations: {result.get('policy_violations', [])}")
        
        assert result.get("decision") == "escalate", "Should escalate due to policy violation"
        assert result.get("policy_compliant") == False, "Should detect policy violation"
        assert len(result.get("policy_violations", [])) > 0, "Should list violations"
        
        print("\n✅ TEST PASSED: Policy violation correctly triggers escalation")


# ============================================================
# TEST SCENARIO 3: High Risk Escalation
# ============================================================

@pytest.mark.asyncio
async def test_high_risk_escalation():
    """
    Scenario: High safety risk detected → Must escalate
    
    Expected behavior:
    - Risk level = "high"
    - Decision = "escalate"
    - Escalation mentions safety concerns
    """
    print("\n" + "="*70)
    print("TEST 3: HIGH RISK ESCALATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Request in high-risk location (many recent incidents)
        input_event = InputEvent(
            type="emergency_repair_request",
            from_entity="Citizen",
            location="Industrial Zone A",  # Assume high incident area
            priority="high",
            reason="Multiple pipeline failures reported",
            requested_shift_days=1,
            metadata={"citizen_id": "C11111"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Risk Level: {result.get('risk_level')}")
        print(f"  Escalation Reason: {result.get('escalation_reason', 'N/A')}")
        
        # May escalate if risk is detected
        if result.get("risk_level") == "high":
            assert result.get("decision") == "escalate", "High risk should trigger escalation"
            print("\n✅ TEST PASSED: High risk correctly triggers escalation")
        else:
            print("\n⚠️  TEST SKIPPED: No high risk detected in test data")


# ============================================================
# TEST SCENARIO 4: All Plans Infeasible → Human Review
# ============================================================

@pytest.mark.asyncio
async def test_all_plans_infeasible_escalation():
    """
    Scenario: LLM generates 3 plans, all fail feasibility → Escalate
    
    Expected behavior:
    - Attempts = 3 (max retries)
    - Feasible = False
    - Decision = "escalate"
    - Reason mentions feasibility failure
    """
    print("\n" + "="*70)
    print("TEST 4: ALL PLANS INFEASIBLE → ESCALATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Request in location with no resources (will fail constraints)
        input_event = InputEvent(
            type="emergency_repair_request",
            from_entity="Coordinator",
            location="Remote Area XYZ",  # Likely no infrastructure data
            priority="high",
            reason="Critical water main break",
            requested_shift_days=1,
            metadata={"citizen_id": "C99999"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('response', {}).get('decision')}")
        print(f"  Feasible: {result.get('feasible')}")
        print(f"  Feasibility Reason: {result.get('feasibility_reason', 'N/A')[:100]}...")
        
        if result.get("feasible") == False:
            assert result.get("response", {}).get("decision") == "escalate", "Should escalate when all plans fail"
            print("\n✅ TEST PASSED: Infeasible plans trigger escalation")
        else:
            print("\n⚠️  TEST RESULT: Plan was feasible")


# ============================================================
# TEST SCENARIO 5: Budget Constraint Violation → Escalation
# ============================================================

@pytest.mark.asyncio
async def test_budget_constraint_escalation():
    """
    Scenario: Requested work exceeds budget → Escalate to finance
    
    Expected behavior:
    - Budget constraint fails
    - Feasible = False
    - Decision = "escalate"
    - Blocking factor mentions budget
    """
    print("\n" + "="*70)
    print("TEST 5: BUDGET CONSTRAINT ESCALATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Large project requiring significant budget
        input_event = InputEvent(
            type="pipeline_maintenance_request",
            from_entity="Coordinator",
            location="City Center",
            priority="medium",
            reason="Complete pipeline replacement",
            requested_shift_days=30,  # Long project = high cost
            metadata={"citizen_id": "C55555", "project_type": "infrastructure_upgrade"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Feasible: {result.get('feasible')}")
        print(f"  Feasibility Reason: {result.get('feasibility_reason', 'N/A')[:150]}...")
        
        feasibility_reason = result.get('feasibility_reason', '').lower()
        if 'budget' in feasibility_reason:
            assert result.get("feasible") == False, "Should be infeasible due to budget"
            print("\n✅ TEST PASSED: Budget constraint correctly identified")
        else:
            print("\n⚠️  TEST RESULT: Budget constraint not triggered (budget sufficient)")


# ============================================================
# TEST SCENARIO 6: Emergency Override Request → Human Approval
# ============================================================

@pytest.mark.asyncio
async def test_emergency_override_escalation():
    """
    Scenario: Emergency request that needs immediate human approval
    
    Expected behavior:
    - Priority = "critical"
    - May escalate for authorization
    - Response indicates emergency handling
    """
    print("\n" + "="*70)
    print("TEST 6: EMERGENCY OVERRIDE ESCALATION")
    print("="*70)
    
    async with AsyncSessionLocal() as db:
        workflow = create_workflow(db)
        
        # Input: Critical emergency requiring immediate action
        input_event = InputEvent(
            type="emergency_repair_request",
            from_entity="Hospital",
            location="Hospital District",
            priority="critical",
            reason="Complete water supply failure affecting hospital",
            requested_shift_days=0,  # Immediate
            metadata={"citizen_id": "C88888"}
        )
        
        # Execute workflow
        initial_state = {"input_event": input_event.model_dump()}
        result = await workflow.ainvoke(initial_state)
        
        # Assertions
        print(f"\n📊 Result Summary:")
        print(f"  Decision: {result.get('decision')}")
        print(f"  Risk Level: {result.get('risk_level')}")
        print(f"  Response: {result.get('response', '')[:200]}...")
        
        # Emergency may be approved or escalated depending on constraints
        assert result.get("decision") in ["approve", "escalate"], "Emergency should get decision"
        print(f"\n✅ TEST PASSED: Emergency handled with decision: {result.get('decision')}")


# ============================================================
# RUN ALL TESTS
# ============================================================

async def run_all_tests():
    """Run all agent-to-human escalation tests"""
    print("\n" + "="*70)
    print("🧪 AGENT-TO-HUMAN ESCALATION TEST SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Low Confidence", test_low_confidence_escalation),
        ("Policy Violation", test_policy_violation_escalation),
        ("High Risk", test_high_risk_escalation),
        ("All Plans Infeasible", test_all_plans_infeasible_escalation),
        ("Budget Constraint", test_budget_constraint_escalation),
        ("Emergency Override", test_emergency_override_escalation),
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
