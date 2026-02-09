"""
PHASE 6.5: Coordination Checkpoint Node (PROACTIVE)

This node checks with the Coordination Agent DURING the workflow
to detect conflicts before executing the plan.

Implements proactive coordination instead of reactive conflict resolution.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def coordination_checkpoint_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check with coordination agent for conflicts before proceeding
    
    This enables proactive conflict detection and resolution during
    the agent's decision workflow, not after completion.
    
    Flow:
    1. Extract plan and resource requirements
    2. Call coordination agent's check_plan_conflicts()
    3. Update state based on coordinator feedback
    4. Proceed or retry based on recommendations
    """
    
    logger.info("\n" + "="*70)
    logger.info("PHASE 6.5: Coordination Checkpoint (Proactive Conflict Check)")
    logger.info("="*70)
    
    # Skip if already escalating
    if state.get("escalate"):
        logger.info("⏭️  Skipping coordination check (already escalating)")
        state["coordination_approved"] = False
        state["coordination_check"] = None
        state["coordination_recommendations"] = []
        return state
    
    # Skip if no plan yet
    if not state.get("plan"):
        logger.info("⏭️  Skipping coordination check (no plan yet)")
        state["coordination_approved"] = True
        state["coordination_check"] = None
        state["coordination_recommendations"] = []
        return state
    
    try:
        # Import here to avoid circular dependency
        from agents.coordination_agent import CoordinationAgent
        
        coordinator = CoordinationAgent()
        
        # Extract information for conflict check
        plan = state.get("plan", {})
        input_event = state.get("input_event", {})
        
        location = input_event.get("location", "Unknown")
        estimated_cost = input_event.get("estimated_cost", 0)
        priority = state.get("risk_level", "medium")
        
        # Determine resources needed from plan
        resources_needed = []
        if "workers_needed" in plan:
            resources_needed.append(f"workers_{location}")
        if estimated_cost > 0:
            resources_needed.append("budget_capital")
        if input_event.get("type") in ["schedule_shift_request", "maintenance_request"]:
            resources_needed.append(f"schedule_{location}")
        
        logger.info(f"🔍 Checking conflicts with coordination agent...")
        logger.info(f"   Location: {location}")
        logger.info(f"   Resources: {', '.join(resources_needed) if resources_needed else 'None'}")
        logger.info(f"   Cost: Rs.{estimated_cost:,}")
        
        # Call coordinator's proactive check
        coordination_result = coordinator.check_plan_conflicts(
            agent_id="water_dept",
            agent_type="water",
            plan=plan,
            location=location,
            resources_needed=resources_needed,
            estimated_cost=estimated_cost,
            priority=priority
        )
        
        coordinator.close()
        
        # Update state with coordination feedback
        state["coordination_check"] = coordination_result
        state["coordination_approved"] = coordination_result.get("should_proceed", True)
        state["coordination_recommendations"] = coordination_result.get("recommendations", [])
        
        # Log results
        has_conflicts = coordination_result.get("has_conflicts", False)
        should_proceed = coordination_result.get("should_proceed", True)
        requires_human = coordination_result.get("requires_human", False)
        
        if has_conflicts:
            logger.info(f"\n⚠️  CONFLICTS DETECTED:")
            for conflict_type in coordination_result.get("conflict_types", []):
                logger.info(f"   • {conflict_type}")
            
            logger.info(f"\n💡 COORDINATOR RECOMMENDATIONS:")
            for rec in coordination_result.get("recommendations", []):
                logger.info(f"   • {rec}")
        else:
            logger.info(f"✅ No conflicts detected - proceeding")
        
        # Handle conflicts
        if requires_human:
            logger.info(f"\n🚨 ESCALATING TO HUMAN due to coordination conflicts")
            state["escalate"] = True
            state["escalation_reason"] = (
                f"Coordination conflicts detected: "
                f"{', '.join(coordination_result.get('conflict_types', []))}"
            )
            state["feasible"] = False
            
        elif has_conflicts and not should_proceed:
            logger.info(f"\n🔄 RETRY NEEDED - trying alternative plan")
            state["retry_needed"] = True
            state["feasibility_reason"] = (
                f"Coordination conflicts: {', '.join(coordination_result.get('recommendations', []))}"
            )
            
            # Increment attempts
            state["attempts"] = state.get("attempts", 0) + 1
            
            # Check if exceeded max attempts
            if state["attempts"] >= state.get("max_attempts", 3):
                logger.info(f"❌ Max attempts reached, escalating")
                state["escalate"] = True
                state["escalation_reason"] = "Max retry attempts exceeded with coordination conflicts"
                state["retry_needed"] = False
        else:
            logger.info(f"✅ Coordination approved - proceeding with plan")
            state["retry_needed"] = False
        
        logger.info("="*70)
        
    except Exception as e:
        logger.warning(f"⚠️  Coordination check failed: {e}")
        logger.warning(f"   Proceeding without coordination (degraded mode)")
        
        # Fail-safe: proceed if coordinator unavailable
        state["coordination_approved"] = True
        state["coordination_check"] = {"error": str(e)}
        state["coordination_recommendations"] = ["Coordinator unavailable - proceeding with caution"]
    
    return state
