"""
REAL GROQ API TEST
This test actually calls Groq API - you should see it in your dashboard

Run: python test_groq_real_call.py
"""

import logging
from datetime import datetime
from coordination_agent import CoordinationAgent
from coordination_agent.state import CoordinationState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_complex_conflict_needs_llm():
    """
    Create a conflict complex enough to trigger LLM
    
    This will make REAL Groq API call
    """
    print("\n" + "="*80)
    print("TESTING REAL GROQ API CALL")
    print("="*80 + "\n")
    
    coordinator = CoordinationAgent()
    
    # Create COMPLEX multi-criteria conflict that CANNOT be solved by rules
    # High complexity score, multiple trade-offs, political considerations
    
    decisions = [
        {
            "agent_id": "water_agent",
            "agent_type": "water",
            "decision": "recommend",
            "request": {
                "type": "major_infrastructure",
                "description": "Build new water treatment plant in North District",
                "stakeholders": ["north_residents", "environmentalists", "farmers"]
            },
            "confidence": 0.85,
            "constraints": {
                "environmental_impact": "moderate",
                "political_sensitivity": "high",
                "public_opinion": "mixed"
            },
            "resources_needed": ["budget_capital", "land_north", "workers_skilled"],
            "location": "North_District",
            "estimated_cost": 50000000,  # 50M - very high
            "priority": "strategic",
            "rationale": "Long-term water security for growing population",
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent_id": "health_agent",
            "agent_type": "health",
            "decision": "recommend",
            "request": {
                "type": "healthcare_facility",
                "description": "Build regional hospital in North District",
                "stakeholders": ["north_residents", "medical_community", "elderly"]
            },
            "confidence": 0.88,
            "constraints": {
                "urgency": "high",
                "political_sensitivity": "high",
                "public_opinion": "strongly_positive"
            },
            "resources_needed": ["budget_capital", "land_north", "workers_skilled"],
            "location": "North_District",
            "estimated_cost": 80000000,  # 80M - even higher
            "priority": "public_health_critical",
            "rationale": "Nearest hospital is 50km away, emergency response times critical",
            "timestamp": datetime.now().isoformat()
        },
        {
            "agent_id": "finance_agent",
            "agent_type": "finance",
            "decision": "conditional",
            "request": {
                "type": "budget_allocation",
                "description": "Annual capital budget allocation",
                "stakeholders": ["city_council", "taxpayers", "all_departments"]
            },
            "confidence": 0.75,
            "constraints": {
                "total_budget": 100000000,  # Only 100M available
                "fiscal_responsibility": "high",
                "political_pressure": "high",
                "economic_uncertainty": "moderate"
            },
            "resources_needed": ["budget_capital"],
            "location": "Citywide",
            "estimated_cost": 0,
            "priority": "fiduciary_duty",
            "rationale": "Both projects exceed available budget, both have strong political support, difficult trade-offs",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    print("🔍 Created complex conflict scenario:")
    print(f"  - Water wants: Rs.50M for water treatment plant")
    print(f"  - Health wants: Rs.80M for hospital")
    print(f"  - Finance has: Rs.100M total budget")
    print(f"  - Conflict: Both high priority, both politically sensitive")
    print(f"  - Trade-offs: Public health vs infrastructure vs fiscal responsibility")
    print(f"\n💡 This requires LLM reasoning - should call Groq!\n")
    
    # Run coordination with decision list
    print("⏳ Running coordination workflow...")
    print("   (Watch your Groq dashboard for API call)\n")
    
    try:
        result = coordinator.coordinate(decisions)
    

        
        print("\n" + "="*80)
        print("RESULT")
        print("="*80)
        print(f"\nResolution method used: {result.get('resolution_method', 'unknown')}")
        print(f"Coordination status: {result.get('coordination_status', 'unknown')}")
        
        if "resolutions" in result and result["resolutions"]:
            resolution = result["resolutions"][0]
            print(f"\nResolution:")
            print(f"  Method: {resolution.get('method', 'unknown')}")
            print(f"  Decision: {resolution.get('decision', 'unknown')}")
            print(f"  Confidence: {resolution.get('confidence', 0):.0%}")
            print(f"  Rationale: {resolution.get('rationale', 'N/A')[:200]}")
            print(f"  Requires human: {resolution.get('requires_human', 'unknown')}")
        
        print("\n" + "="*80)
        
        if result.get('resolution_method') == 'llm':
            print("✅ SUCCESS: LLM was used (check Groq dashboard!)")
        else:
            print(f"⚠️  WARNING: Used {result.get('resolution_method')} instead of LLM")
        
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nCheck:")
        print("  1. Is GROQ_API_KEY set in .env?")
        print("  2. Is Groq API accessible?")
        print("  3. Check error details above")
        raise
    finally:
        coordinator.close()


if __name__ == "__main__":
    test_complex_conflict_needs_llm()
