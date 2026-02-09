"""
PHASE 7: Tool Execution Node

Convert plan into facts.
Each tool returns structured data.
"""

import logging
from typing import Dict, List

from ..state import DepartmentState
from ..tools import SanitationDepartmentTools

logger = logging.getLogger(__name__)


def tool_executor_node(state: DepartmentState, tools: SanitationDepartmentTools) -> DepartmentState:
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
        route_id = input_event.get("route_id")
        
        tool_results = {}
        
        if not steps:
            logger.warning("  ⚠ No steps in plan")
            state["tool_results"] = {}
            return state
        
        logger.info(f"  → Executing {len(steps)} tool steps")
        
        for step in steps:
            logger.info(f"    • {step}")
            
            try:
                if step == "check_truck_availability":
                    result = tools.check_truck_availability(
                        location=location,
                        min_fuel_percent=25
                    )
                    tool_results["truck_availability"] = result
                
                elif step == "check_route_capacity":
                    if route_id:
                        result = tools.check_route_capacity(route_id=route_id)
                        tool_results["route_capacity"] = result
                
                elif step == "check_landfill_capacity":
                    result = tools.check_landfill_capacity(
                        min_capacity_percent=input_event.get("min_capacity_percent", 10)
                    )
                    tool_results["landfill_capacity"] = result
                
                elif step == "assess_collection_delay":
                    if route_id:
                        result = tools.assess_collection_delay(route_id=route_id)
                        tool_results["collection_delay"] = result
                
                elif step == "check_equipment_status":
                    equipment_type = input_event.get("equipment_type")
                    result = tools.check_equipment_status(equipment_type=equipment_type)
                    tool_results["equipment_status"] = result
                
                elif step == "get_complaint_history":
                    result = tools.get_complaint_history(
                        location=location,
                        days=30
                    )
                    tool_results["complaint_history"] = result
                
                elif step == "check_recycling_center_availability":
                    result = tools.check_recycling_center_availability()
                    tool_results["recycling_centers"] = result
                
                elif step == "estimate_waste_volume":
                    result = tools.estimate_waste_volume(
                        location=location,
                        route_id=route_id
                    )
                    tool_results["waste_volume"] = result
                
                elif step == "check_budget_availability":
                    estimated_cost = input_event.get("estimated_cost")
                    result = tools.check_budget_availability(estimated_cost=estimated_cost)
                    tool_results["budget"] = result
                
                elif step == "alert_all_workers":
                    # Emergency notification
                    tool_results["alert"] = {
                        "type": "emergency_alert",
                        "status": "sent",
                        "recipients": "all_sanitation_department_workers"
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
