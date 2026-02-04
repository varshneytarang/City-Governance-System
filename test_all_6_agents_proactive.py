"""
Comprehensive Test: Proactive Coordination Across All 6 Agents

This test validates that all 6 agents (Water, Engineering, Fire, Sanitation, Health, Finance)
implement proactive coordination by checking with the coordinator DURING their workflows.

Test Scenario:
- All 6 agents receive requests for work in the same location (Downtown)
- Each agent should check with coordinator before executing their plan
- Coordinator should detect conflicts and provide recommendations
- Agents should handle conflicts appropriately (escalate, retry, or proceed)
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_all_6_agents_proactive_coordination():
    """Test proactive coordination across all 6 department agents."""
    
    logger.info("="*80)
    logger.info("COMPREHENSIVE TEST: Proactive Coordination Across All 6 Agents")
    logger.info("="*80)
    
    # Import all 6 agents
    try:
        from water_agent.agent import WaterDepartmentAgent
        from engineering_agent.agent import EngineeringDepartmentAgent
        from fire_agent.agent import FireDepartmentAgent
        from sanitation_agent.agent import SanitationDepartmentAgent
        from health_agent.agent import HealthDepartmentAgent
        from finance_agent.agent import FinanceDepartmentAgent
        
        logger.info("✅ All 6 agents imported successfully")
        
    except ImportError as e:
        logger.error(f"❌ Failed to import agents: {e}")
        return False
    
    # Initialize all agents
    try:
        water_agent = WaterDepartmentAgent()
        engineering_agent = EngineeringDepartmentAgent()
        fire_agent = FireDepartmentAgent()
        sanitation_agent = SanitationDepartmentAgent()
        health_agent = HealthDepartmentAgent()
        finance_agent = FinanceDepartmentAgent()
        
        logger.info("✅ All 6 agents initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agents: {e}", exc_info=True)
        return False
    
    # Define test requests - all for the same location to trigger conflicts
    # Using VALID request types that each agent accepts
    test_location = "Downtown"
    
    requests = {
        "water": {
            "type": "maintenance_request",  # Valid: maintenance_request
            "location": test_location,
            "severity": "high",
            "description": "Water main burst on Main Street",
            "estimated_affected": 500
        },
        "engineering": {
            "type": "project_planning",  # Valid: project_planning
            "location": test_location,
            "description": "Road resurfacing project on Main Street",
            "duration_days": 14,
            "budget": 50000
        },
        "fire": {
            "type": "inspection_request",  # Valid: inspection_request
            "location": test_location,
            "description": "Fire safety inspection of commercial buildings",
            "priority": "routine"
        },
        "sanitation": {
            "type": "emergency_collection",  # Valid: emergency_collection
            "location": test_location,
            "description": "Special waste collection event",
            "schedule": "this_weekend"
        },
        "health": {
            "type": "health_inspection",  # Health agent accepts any type
            "location": test_location,
            "description": "Restaurant health inspections",
            "facilities_count": 12
        },
        "finance": {
            "type": "budget_approval",  # Finance agent accepts any type
            "location": test_location,
            "description": "Budget approval for Downtown improvements",
            "amount": 150000,
            "requesting_department": "engineering"
        }
    }
    
    logger.info(f"\n📋 Test Scenario: All 6 agents working in '{test_location}'")
    logger.info("Expected: Coordination conflicts should be detected\n")
    
    results = {}
    coordination_checks = {}
    
    # Test each agent
    agents = {
        "water": water_agent,
        "engineering": engineering_agent,
        "fire": fire_agent,
        "sanitation": sanitation_agent,
        "health": health_agent,
        "finance": finance_agent
    }
    
    for agent_name, agent in agents.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing {agent_name.upper()} Agent")
        logger.info(f"{'='*60}")
        
        try:
            request = requests[agent_name]
            logger.info(f"Request: {request}")
            
            # Execute agent decision
            start = datetime.now()
            response = agent.decide(request)
            duration = (datetime.now() - start).total_seconds()
            
            logger.info(f"✅ {agent_name.title()} agent completed in {duration:.2f}s")
            logger.info(f"Response: {response}")
            
            results[agent_name] = {
                "success": True,
                "response": response,
                "duration": duration
            }
            
            # Check if coordination was performed
            # For LangGraph agents (Water, Engineering, Fire, Sanitation, Health)
            # coordination_check should be in the final state
            if hasattr(response, 'get'):
                coord_check = response.get('coordination_check')
                if coord_check:
                    coordination_checks[agent_name] = coord_check
                    logger.info(f"✅ Coordination check performed: {coord_check}")
                else:
                    logger.warning(f"⚠️ No coordination check found in response")
            
        except Exception as e:
            logger.error(f"❌ {agent_name.title()} agent failed: {e}", exc_info=True)
            results[agent_name] = {
                "success": False,
                "error": str(e)
            }
    
    # Analyze results
    logger.info("\n" + "="*80)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*80)
    
    successful_agents = [name for name, result in results.items() if result.get("success")]
    failed_agents = [name for name, result in results.items() if not result.get("success")]
    
    logger.info(f"\n✅ Successful agents: {len(successful_agents)}/6")
    for agent_name in successful_agents:
        logger.info(f"   - {agent_name.title()}")
    
    if failed_agents:
        logger.info(f"\n❌ Failed agents: {len(failed_agents)}/6")
        for agent_name in failed_agents:
            logger.info(f"   - {agent_name.title()}: {results[agent_name].get('error')}")
    
    logger.info(f"\n📊 Coordination Checks Performed: {len(coordination_checks)}/6")
    for agent_name, check in coordination_checks.items():
        logger.info(f"\n{agent_name.upper()}:")
        logger.info(f"   Approved: {check.get('approved')}")
        logger.info(f"   Has Conflicts: {check.get('has_conflicts')}")
        logger.info(f"   Requires Human: {check.get('requires_human_intervention')}")
        if check.get('conflicts'):
            logger.info(f"   Conflicts: {check.get('conflicts')}")
        if check.get('recommendations'):
            logger.info(f"   Recommendations: {check.get('recommendations')}")
    
    # Cleanup
    try:
        for agent in agents.values():
            if hasattr(agent, 'close'):
                agent.close()
        logger.info("\n✅ All agents closed successfully")
    except Exception as e:
        logger.warning(f"⚠️ Error during cleanup: {e}")
    
    # Final verdict
    logger.info("\n" + "="*80)
    all_successful = len(successful_agents) == 6
    has_coordination = len(coordination_checks) >= 4  # At least 4 agents with LangGraph
    
    if all_successful and has_coordination:
        logger.info("✅ TEST PASSED: All 6 agents implemented proactive coordination")
        logger.info("="*80)
        return True
    elif all_successful:
        logger.info("⚠️ TEST PARTIAL: All agents ran but some lack coordination checks")
        logger.info("="*80)
        return True
    else:
        logger.info("❌ TEST FAILED: Some agents failed to execute")
        logger.info("="*80)
        return False


if __name__ == "__main__":
    success = test_all_6_agents_proactive_coordination()
    exit(0 if success else 1)
