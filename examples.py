"""
Example usage of Water Department Agent

This demonstrates how to use the agent end-to-end.
"""

import logging
from water_agent import WaterDepartmentAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def example_1_schedule_shift_request():
    """Example 1: Schedule shift request"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Schedule Shift Request")
    print("="*70)
    
    agent = WaterDepartmentAgent()
    
    request = {
        "type": "schedule_shift_request",
        "from": "Coordinator",
        "location": "Downtown",  # Must match DB location
        "requested_shift_days": 2,
        "reason": "Joint underground work",
        "estimated_cost": 50000,
        "required_workers": 5
    }
    
    response = agent.decide(request)
    
    print("\n📊 RESPONSE:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reasoning: {response.get('reasoning', response.get('reason'))}")
    print(f"  Confidence: {response.get('details', {}).get('confidence', 'N/A')}")
    
    agent.close()
    return response


def example_2_emergency_response():
    """Example 2: Emergency response"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Emergency Response")
    print("="*70)
    
    agent = WaterDepartmentAgent()
    
    request = {
        "type": "emergency_response",
        "from": "Control Center",
        "location": "Downtown",
        "incident_type": "major_leak",
        "severity": "critical"
    }
    
    response = agent.decide(request)
    
    print("\n📊 RESPONSE:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reasoning: {response.get('reasoning', response.get('reason'))}")
    
    agent.close()
    return response


def example_3_maintenance_request():
    """Example 3: Maintenance request"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Maintenance Request")
    print("="*70)
    
    agent = WaterDepartmentAgent()
    
    request = {
        "type": "maintenance_request",
        "from": "Operations",
        "location": "Downtown",
        "activity": "pipeline_inspection",
        "notice_hours": 48,
        "estimated_cost": 25000,
        "required_workers": 3
    }
    
    response = agent.decide(request)
    
    print("\n📊 RESPONSE:")
    print(f"  Decision: {response.get('decision')}")
    print(f"  Reasoning: {response.get('reasoning', response.get('reason'))}")
    print(f"  Requires Review: {response.get('requires_human_review')}")
    
    agent.close()
    return response


def example_4_visualization():
    """Example 4: Visualize agent workflow"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Agent Workflow Visualization")
    print("="*70)
    
    agent = WaterDepartmentAgent()
    
    # Generate Mermaid diagram
    mermaid = agent.visualize()
    
    if mermaid:
        print("\n🎨 Agent Graph (Mermaid):")
        print(mermaid)
    
    agent.close()


if __name__ == "__main__":
    print("\n" + "🌊 " * 20)
    print("WATER DEPARTMENT AGENT - EXAMPLES")
    print("🌊 " * 20)
    
    try:
        # Run examples
        example_1_schedule_shift_request()
        example_2_emergency_response()
        example_3_maintenance_request()
        example_4_visualization()
        
        print("\n" + "✓ " * 20)
        print("ALL EXAMPLES COMPLETED")
        print("✓ " * 20 + "\n")
    
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()
