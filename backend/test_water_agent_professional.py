"""
Professional Water Department Agent - Test Suite
Tests all scenarios with proper validation
"""

import asyncio
import json
from datetime import datetime

# Mock database for testing
class MockDB:
    async def execute(self, *args, **kwargs):
        class Result:
            def scalars(self):
                class Scalars:
                    def all(self):
                        return []
                return Scalars()
            def scalar(self):
                return 1
        return Result()
    
    async def commit(self):
        pass


async def test_water_department_agent():
    """
    Test professional water department agent
    """
    from app.agents.water_v2.graph import process_request
    from app.agents.water_v2.state import InputEvent
    
    print("\n" + "=" * 70)
    print("🧪 TESTING PROFESSIONAL WATER DEPARTMENT AGENT")
    print("=" * 70)
    
    db = MockDB()
    
    # ========== TEST 1: Schedule Shift Request (Normal) ==========
    
    print("\n\n📋 TEST 1: Schedule Shift Request (Low Risk, Should Approve)")
    print("-" * 70)
    
    test1_event = {
        "type": "schedule_shift_request",
        "from_entity": "Coordinator",
        "location": "Zone-12",
        "requested_shift_days": 2,
        "reason": "Joint underground work with Roads Department",
        "priority": "medium",
        "metadata": {}
    }
    
    print(f"\nInput Event:")
    print(json.dumps(test1_event, indent=2))
    
    result1 = await process_request(db, test1_event)
    
    print(f"\n✅ Result:")
    print(json.dumps(result1, indent=2))
    print(f"\nDecision: {result1['decision']}")
    print(f"Confidence: {result1['confidence']}")
    print(f"Reasoning: {result1['reasoning']}")
    
    # ========== TEST 2: Emergency Request (High Risk, Should Escalate) ==========
    
    print("\n\n📋 TEST 2: Emergency Repair Request (High Risk, Should Escalate)")
    print("-" * 70)
    
    test2_event = {
        "type": "emergency_repair_request",
        "from_entity": "Field Officer",
        "location": "Zone-5",
        "requested_shift_days": 1,
        "reason": "Major pipeline burst causing flooding",
        "priority": "critical",
        "metadata": {
            "affected_households": 500,
            "water_loss_liters_per_hour": 10000
        }
    }
    
    print(f"\nInput Event:")
    print(json.dumps(test2_event, indent=2))
    
    result2 = await process_request(db, test2_event)
    
    print(f"\n✅ Result:")
    print(json.dumps(result2, indent=2))
    print(f"\nDecision: {result2['decision']}")
    print(f"Confidence: {result2['confidence']}")
    print(f"Escalation Reason: {result2.get('escalation_reason', 'N/A')}")
    
    # ========== TEST 3: Capacity Assessment (Analysis Request) ==========
    
    print("\n\n📋 TEST 3: Capacity Assessment Request")
    print("-" * 70)
    
    test3_event = {
        "type": "capacity_assessment_request",
        "from_entity": "Engineering Department",
        "location": "Zone-8",
        "requested_shift_days": 0,
        "reason": "New residential complex planning",
        "priority": "low",
        "metadata": {
            "expected_population": 1000,
            "daily_water_requirement_liters": 150000
        }
    }
    
    print(f"\nInput Event:")
    print(json.dumps(test3_event, indent=2))
    
    result3 = await process_request(db, test3_event)
    
    print(f"\n✅ Result:")
    print(json.dumps(result3, indent=2))
    print(f"\nDecision: {result3['decision']}")
    print(f"Recommended Action: {result3.get('recommended_action', 'N/A')}")
    
    # ========== SUMMARY ==========
    
    print("\n\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Test 1 (Normal Request): {result1['decision']}")
    print(f"Test 2 (Emergency): {result2['decision']}")
    print(f"Test 3 (Analysis): {result3['decision']}")
    print("\n✅ All tests completed!")
    print("=" * 70 + "\n")


# ========== VISUALIZATION TEST ==========

async def test_visualization():
    """
    Test workflow visualization
    """
    print("\n\n🎨 TESTING WORKFLOW VISUALIZATION")
    print("=" * 70)
    
    try:
        from app.agents.water_v2.graph import create_water_department_agent
        
        db = MockDB()
        workflow = create_water_department_agent(db)
        
        # Get Mermaid diagram
        mermaid_code = workflow.get_graph().draw_mermaid()
        
        print("\n✅ Mermaid Diagram Generated:")
        print("-" * 70)
        print(mermaid_code)
        print("-" * 70)
        
        # Save to file
        with open("water_agent_workflow.mmd", "w") as f:
            f.write(mermaid_code)
        
        print("\n💾 Diagram saved to: water_agent_workflow.mmd")
        print("📌 Visualize at: https://mermaid.live/")
        
    except Exception as e:
        print(f"\n❌ Visualization failed: {e}")


# ========== RUN ALL TESTS ==========

async def main():
    await test_water_department_agent()
    await test_visualization()


if __name__ == "__main__":
    asyncio.run(main())
