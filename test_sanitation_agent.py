"""
Sanitation Agent - Simple Test

Test the sanitation department agent with various request types.
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sanitation_agent.agent import SanitationDepartmentAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_route_change_request():
    """Test route change request"""
    
    print("\n" + "="*70)
    print("TEST 1: Route Change Request")
    print("="*70)
    
    agent = SanitationDepartmentAgent()
    
    request = {
        "type": "route_change_request",
        "from": "Operations Coordinator",
        "location": "Zone-1",
        "route_id": 1,
        "new_route": "Alternative North Route",
        "reason": "Road construction blocking main route"
    }
    
    response = agent.decide(request)
    
    print("\n📊 Response:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reason: {response.get('reason', response.get('reasoning', 'N/A'))}")
    
    if response.get('decision') == 'recommend':
        rec = response.get('recommendation', {})
        print(f"  Action: {rec.get('action')}")
        print(f"  Confidence: {rec.get('confidence', 0):.2%}")
    
    agent.close()


def test_emergency_collection():
    """Test emergency collection request"""
    
    print("\n" + "="*70)
    print("TEST 2: Emergency Collection")
    print("="*70)
    
    agent = SanitationDepartmentAgent()
    
    request = {
        "type": "emergency_collection",
        "from": "Public Health Department",
        "location": "Zone-3",
        "route_id": 5,
        "urgency": "high",
        "reason": "Multiple overflowing bins causing health hazard"
    }
    
    response = agent.decide(request)
    
    print("\n📊 Response:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reason: {response.get('reason', response.get('reasoning', 'N/A'))}")
    
    agent.close()


def test_equipment_maintenance():
    """Test equipment maintenance request"""
    
    print("\n" + "="*70)
    print("TEST 3: Equipment Maintenance")
    print("="*70)
    
    agent = SanitationDepartmentAgent()
    
    request = {
        "type": "equipment_maintenance",
        "from": "Fleet Manager",
        "location": "Central Depot",
        "equipment_type": "compactor_truck",
        "truck_id": 2,
        "reason": "Scheduled maintenance",
        "estimated_downtime_hours": 4
    }
    
    response = agent.decide(request)
    
    print("\n📊 Response:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reason: {response.get('reason', response.get('reasoning', 'N/A'))}")
    
    agent.close()


def test_complaint_response():
    """Test complaint response request"""
    
    print("\n" + "="*70)
    print("TEST 4: Complaint Response")
    print("="*70)
    
    agent = SanitationDepartmentAgent()
    
    request = {
        "type": "complaint_response",
        "from": "Citizen Services",
        "location": "Zone-2",
        "route_id": 3,
        "complaint_type": "missed_collection",
        "complaint_count": 5,
        "reason": "Multiple residents reporting missed pickups"
    }
    
    response = agent.decide(request)
    
    print("\n📊 Response:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reason: {response.get('reason', response.get('reasoning', 'N/A'))}")
    
    agent.close()


def main():
    """Run all tests"""
    
    print("\n")
    print("🗑️  " + "="*66)
    print("🗑️   SANITATION DEPARTMENT AGENT - TEST SUITE")
    print("🗑️  " + "="*66)
    
    try:
        test_route_change_request()
        test_emergency_collection()
        test_equipment_maintenance()
        test_complaint_response()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        print("\n" + "="*70)
        print("❌ TESTS FAILED")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
