"""
PHASE 8: Observe Node

Normalize tool outputs. No decision here, just organization.
"""

import logging

from ..state import DepartmentState

logger = logging.getLogger(__name__)


def observer_node(state: DepartmentState) -> DepartmentState:
    """
    PHASE 8: Observe Node
    
    Purpose: Normalize tool outputs.
    
    This step simply organizes results into a standard format
    for the feasibility evaluator.
    
    No reasoning or decision made here.
    """
    
    logger.info("👁️  [NODE: Observer]")
    
    try:
        tool_results = state.get("tool_results", {})
        
        # Normalize observations into a consistent structure
        observations = {
            "raw_results": tool_results,
            "extracted_facts": {}
        }
        
        # Extract key facts from tool results
        if "manpower" in tool_results:
            manpower = tool_results["manpower"]
            observations["extracted_facts"]["manpower_sufficient"] = manpower.get("sufficient", False)
            observations["extracted_facts"]["available_workers"] = manpower.get("available_count", 0)
            observations["extracted_facts"]["required_workers"] = manpower.get("required_count", 0)
        
        if "schedule" in tool_results:
            schedule = tool_results["schedule"]
            observations["extracted_facts"]["schedule_conflict"] = schedule.get("has_conflicts", False)
            observations["extracted_facts"]["scheduled_activities"] = schedule.get("activity_count", 0)
        
        if "pipeline_health" in tool_results:
            pipeline = tool_results["pipeline_health"]
            observations["extracted_facts"]["pipeline_condition"] = pipeline.get("overall_condition", "unknown")
            observations["extracted_facts"]["critical_pipeline_issues"] = pipeline.get("critical_issues", 0)
        
        if "reservoir_levels" in tool_results:
            reservoir = tool_results["reservoir_levels"]
            observations["extracted_facts"]["reservoir_status"] = reservoir.get("overall_status", "unknown")
            observations["extracted_facts"]["critical_reservoirs"] = reservoir.get("critical_count", 0)
        
        if "zone_risk" in tool_results:
            risk = tool_results["zone_risk"]
            observations["extracted_facts"]["zone_risk_level"] = risk.get("risk_level", "unknown")
            observations["extracted_facts"]["zone_risk_factors"] = risk.get("contributing_factors", [])
        
        if "budget" in tool_results:
            budget = tool_results["budget"]
            observations["extracted_facts"]["budget_available"] = budget.get("can_afford", False)
            observations["extracted_facts"]["remaining_budget"] = budget.get("remaining", 0)
        
        if "active_projects" in tool_results:
            projects = tool_results["active_projects"]
            observations["extracted_facts"]["active_projects_count"] = projects.get("active_count", 0)
        
        state["observations"] = observations
        logger.info(f"✓ Observations normalized: {len(observations['extracted_facts'])} facts")
        
    except Exception as e:
        logger.error(f"✗ Observer error: {e}")
        state["observations"] = {
            "raw_results": state.get("tool_results", {}),
            "error": str(e)
        }
    
    return state
