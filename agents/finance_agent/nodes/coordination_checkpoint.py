"""
Finance Agent Coordination Checkpoint Node

This node implements proactive coordination for Finance Agent:
- Occurs between cost_estimator and budget_feasibility
- Calls the coordination agent to check for conflicts
- Routes to escalate/retry/proceed based on coordinator's response
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def coordination_checkpoint_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check with coordination agent before proceeding with budget allocation.
    
    This is the proactive coordination checkpoint that enables real-time
    conflict detection across all agents in the City Governance System.
    
    Workflow:
    1. Extract cost estimates and revenue forecast from state
    2. Call coordination_agent.check_plan_conflicts()
    3. Update state with coordinator's response
    4. Set routing flags for downstream conditional edges
    
    Args:
        state: Current agent state with financial analysis
        
    Returns:
        Updated state with coordination_check, coordination_approved, and routing flags
    """
    logger.info("🔄 [Finance] Coordination Checkpoint - checking with coordinator")
    
    try:
        # Extract financial details
        cost_estimates = state.get("cost_estimates", {})
        revenue_forecast = state.get("revenue_forecast", {})
        input_event = state.get("input_event", {})
        
        location = input_event.get("location", "citywide")
        department = input_event.get("requesting_department", "unknown")
        
        # Extract resources from cost estimates
        resources = []
        if cost_estimates.get("budget_allocation"):
            resources.append("budget_allocation")
        if cost_estimates.get("funding_source"):
            resources.append(cost_estimates["funding_source"])
        
        # Get total estimated cost
        estimated_cost = cost_estimates.get("total_cost", 0)
        if not estimated_cost and cost_estimates.get("amount"):
            estimated_cost = cost_estimates["amount"]
        
        logger.info(f"📡 [Finance] Sending coordination request: location={location}, cost=${estimated_cost}")
        
        # Import and call coordination agent
        try:
            from agents.coordination_agent.agent import CoordinationAgent
            coordinator = CoordinationAgent()
            
            # Check for conflicts - pass individual arguments
            check_result = coordinator.check_plan_conflicts(
                agent_id="finance_agent",
                agent_type="finance",
                plan={
                    "cost_estimates": cost_estimates,
                    "revenue_forecast": revenue_forecast,
                    "requesting_department": department
                },
                location=location,
                resources_needed=resources,
                estimated_cost=estimated_cost,
                priority=input_event.get("priority", "normal")
            )
            
            logger.info(f"✅ [Finance] Coordinator response: {check_result}")
            
            # Update state with coordinator's response
            state["coordination_check"] = check_result
            state["coordination_approved"] = check_result.get("approved", False)
            state["coordination_recommendations"] = check_result.get("recommendations", [])
            
            # Set routing flags
            if check_result.get("requires_human_intervention"):
                state["escalate"] = True
                state["escalation_reason"] = "Coordinator requires human intervention"
                logger.warning("⚠️ [Finance] Coordinator requires human intervention - escalating")
                
            elif check_result.get("has_conflicts"):
                conflicts = check_result.get("conflicts", [])
                logger.warning(f"⚠️ [Finance] Conflicts detected: {conflicts}")
                # Budget conflicts may require re-estimation
                state["escalate"] = True
                state["escalation_reason"] = f"Budget conflicts detected: {conflicts}"
                
            else:
                logger.info("✅ [Finance] No conflicts detected - proceeding with budget approval")
                state["escalate"] = False
                state["escalation_reason"] = None
                
        except ImportError as e:
            logger.error(f"❌ [Finance] Could not import CoordinationAgent: {e}")
            # Fail-safe: proceed without coordination in degraded mode
            state["coordination_check"] = {
                "approved": True,
                "degraded_mode": True,
                "message": "Coordinator unavailable - proceeding without coordination check"
            }
            state["coordination_approved"] = True
            state["coordination_recommendations"] = []
            
        except Exception as e:
            logger.error(f"❌ [Finance] Coordination check failed: {e}", exc_info=True)
            # Fail-safe: proceed without coordination in degraded mode
            state["coordination_check"] = {
                "approved": True,
                "degraded_mode": True,
                "error": str(e),
                "message": "Coordinator error - proceeding without coordination check"
            }
            state["coordination_approved"] = True
            state["coordination_recommendations"] = []
            
    except Exception as e:
        logger.error(f"❌ [Finance] Coordination checkpoint failed: {e}", exc_info=True)
        # Fail-safe: proceed without coordination
        state["coordination_check"] = {
            "approved": True,
            "degraded_mode": True,
            "error": str(e)
        }
        state["coordination_approved"] = True
        state["coordination_recommendations"] = []
    
    return state
