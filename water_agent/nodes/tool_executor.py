"""
PHASE 7: Tool Execution Node

Convert plan into facts.
Each tool returns structured data.
"""

import logging
from typing import Dict, List

from ..state import DepartmentState
from ..tools import WaterDepartmentTools

logger = logging.getLogger(__name__)


def tool_executor_node(state: DepartmentState, tools: WaterDepartmentTools) -> DepartmentState:
    """
    PHASE 7: Tool Execution Node
    
    Purpose: Convert plan into facts.
    
    Executes the tools specified in the plan and collects their results.
    Each tool returns structured data.
    """
    
    logger.info("🔧 [NODE: Tool Executor]")
    
    try:
        plan = state.get("plan", {})
        steps = plan.get("steps", [])
        input_event = state.get("input_event", {})
        location = input_event.get("location")
        
        tool_results = {}
        
        if not steps:
            logger.warning("  ⚠ No steps in plan")
            state["tool_results"] = {}
            return state
        
        logger.info(f"  → Executing {len(steps)} tool steps")
        
        for step in steps:
            logger.info(f"    • {step}")
            
            try:
                if step == "check_manpower_availability":
                    result = tools.check_manpower_availability(
                        location=location,
                        required_count=input_event.get("required_workers", 5)
                    )
                    tool_results["manpower"] = result
                
                elif step == "check_schedule_conflicts":
                    requested_date = input_event.get("requested_date")
                    if requested_date:
                        result = tools.check_schedule_conflicts(
                            location=location,
                            requested_date=requested_date
                        )
                        tool_results["schedule"] = result
                
                elif step == "check_pipeline_health":
                    result = tools.check_pipeline_health(location=location)
                    tool_results["pipeline_health"] = result
                
                elif step == "check_reservoir_levels":
                    result = tools.check_reservoir_levels()
                    tool_results["reservoir_levels"] = result
                
                elif step == "assess_zone_risk":
                    if location:
                        result = tools.assess_zone_risk(location=location)
                        tool_results["zone_risk"] = result
                
                elif step == "check_budget_availability":
                    estimated_cost = input_event.get("estimated_cost")
                    result = tools.check_budget_availability(estimated_cost=estimated_cost)
                    tool_results["budget"] = result
                
                elif step == "get_active_projects":
                    result = tools.get_active_projects(location=location)
                    tool_results["active_projects"] = result
                
                elif step == "alert_all_workers":
                    # Emergency notification
                    tool_results["alert"] = {
                        "type": "emergency_alert",
                        "status": "sent",
                        "recipients": "all_water_department_workers"
                    }
                
                elif step == "activate_emergency_protocol":
                    tool_results["emergency_protocol"] = {
                        "status": "activated",
                        "timestamp": logger.info("timestamp")
                    }
                
                elif step == "document_request":
                    tool_results["documentation"] = {
                        "status": "documented",
                        "request": input_event
                    }
                
                elif step == "log_decision":
                    tool_results["logging"] = {
                        "status": "ready_for_logging"
                    }
                
                else:
                    logger.warning(f"    ⚠ Unknown tool: {step}")
                    tool_results[step] = {"status": "not_implemented"}
            
            except Exception as e:
                logger.error(f"    ✗ Tool error {step}: {e}")
                tool_results[step] = {"error": str(e)}
        
        state["tool_results"] = tool_results
        logger.info(f"✓ Tool execution complete: {len(tool_results)} results")
        
    except Exception as e:
        logger.error(f"✗ Tool executor error: {e}")
        state["tool_results"] = {"error": str(e)}
    
    return state
