"""
Health Agent Coordination Checkpoint Node

This node implements Phase 6.5 in the workflow:
- Occurs between health_planner and health_policy
- Calls the coordination agent to check for conflicts
- Routes to escalate/retry/proceed based on coordinator's response
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def coordination_checkpoint_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check with coordination agent before proceeding with execution.
    
    This is the proactive coordination checkpoint that enables real-time
    conflict detection across all agents in the City Governance System.
    
    Workflow:
    1. Extract plan details from state
    2. Call coordination_agent.check_plan_conflicts()
    3. Update state with coordinator's response
    4. Set routing flags for downstream conditional edges
    
    Args:
        state: Current agent state with plan details
        
    Returns:
        Updated state with coordination_check, coordination_approved, and routing flags
    """
    logger.info("🔄 [Health] Coordination Checkpoint - checking with coordinator")
    
    try:
        # Extract plan details
        plan = state.get("plan", {})
        input_event = state.get("input_event", {})
        location = input_event.get("location", "unknown")
        
        # Extract resources from plan
        resources = []
        if plan.get("health_check_required"):
            resources.append("health_inspectors")
        if plan.get("vaccination_campaign"):
            resources.append("medical_staff")
        if plan.get("equipment_needed"):
            resources.extend(plan.get("equipment_needed", []))
        
        # Estimate cost
        estimated_cost = plan.get("estimated_cost", 0)
        if not estimated_cost and plan.get("budget_required"):
            estimated_cost = plan["budget_required"]
        
        logger.info(f"📡 [Health] Sending coordination request: location={location}, resources={resources}")
        
        # Import and call coordination agent
        try:
            from agents.coordination_agent.agent import CoordinationAgent
            coordinator = CoordinationAgent()
            
            # Check for conflicts - pass individual arguments
            check_result = coordinator.check_plan_conflicts(
                agent_id="health_agent",
                agent_type="health",
                plan=plan,
                location=location,
                resources_needed=resources,
                estimated_cost=estimated_cost,
                priority=input_event.get("priority", "normal")
            )
            
            logger.info(f"✅ [Health] Coordinator response: {check_result}")
            
            # Update state with coordinator's response
            state["coordination_check"] = check_result
            state["coordination_approved"] = check_result.get("approved", False)
            state["coordination_recommendations"] = check_result.get("recommendations", [])
            
            # Set routing flags
            if check_result.get("requires_human_intervention"):
                state["escalate"] = True
                logger.warning("⚠️ [Health] Coordinator requires human intervention - escalating")
                
            elif check_result.get("has_conflicts"):
                conflicts = check_result.get("conflicts", [])
                logger.warning(f"⚠️ [Health] Conflicts detected: {conflicts}")
                # Don't escalate immediately - let planner retry with recommendations
                state["escalate"] = False
                
            else:
                logger.info("✅ [Health] No conflicts detected - proceeding with plan")
                state["escalate"] = False
                
        except ImportError as e:
            logger.error(f"❌ [Health] Could not import CoordinationAgent: {e}")
            # Fail-safe: proceed without coordination in degraded mode
            state["coordination_check"] = {
                "approved": True,
                "degraded_mode": True,
                "message": "Coordinator unavailable - proceeding without coordination check"
            }
            state["coordination_approved"] = True
            state["coordination_recommendations"] = []
            
        except Exception as e:
            logger.error(f"❌ [Health] Coordination check failed: {e}", exc_info=True)
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
        logger.error(f"❌ [Health] Coordination checkpoint failed: {e}", exc_info=True)
        # Fail-safe: proceed without coordination
        state["coordination_check"] = {
            "approved": True,
            "degraded_mode": True,
            "error": str(e)
        }
        state["coordination_approved"] = True
        state["coordination_recommendations"] = []
    
    return state
