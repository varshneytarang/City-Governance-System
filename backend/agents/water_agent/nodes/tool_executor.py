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


def _parse_tool_name(step: str) -> str:
    """
    Parse natural language step into tool name.
    Maps LLM-generated descriptions to actual tool function names.
    """
    step_lower = step.lower()
    
    # Direct match (exact tool name)
    tool_names = [
        "check_manpower_availability",
        "check_schedule_conflicts",
        "check_pipeline_health",
        "check_reservoir_levels",
        "assess_zone_risk",
        "check_budget_availability",
        "get_active_projects",
        "alert_all_workers",
        "activate_emergency_protocol",
        "document_request",
        "log_decision"
    ]
    
    if step in tool_names:
        return step
    
    # Intelligent mapping of natural language to tools
    if any(keyword in step_lower for keyword in ["manpower", "worker", "team", "personnel", "staff"]):
        return "check_manpower_availability"
    elif any(keyword in step_lower for keyword in ["schedule", "conflict", "timing", "calendar"]):
        return "check_schedule_conflicts"
    elif any(keyword in step_lower for keyword in ["pipeline", "pipe", "infrastructure", "condition"]):
        return "check_pipeline_health"
    elif any(keyword in step_lower for keyword in ["reservoir", "water level", "storage"]):
        return "check_reservoir_levels"
    elif any(keyword in step_lower for keyword in ["risk", "assess", "safety", "hazard"]):
        return "assess_zone_risk"
    elif any(keyword in step_lower for keyword in ["budget", "cost", "funding", "financial"]):
        return "check_budget_availability"
    elif any(keyword in step_lower for keyword in ["project", "ongoing", "active work"]):
        return "get_active_projects"
    elif any(keyword in step_lower for keyword in ["alert", "notify", "emergency notification"]):
        return "alert_all_workers"
    elif any(keyword in step_lower for keyword in ["emergency protocol", "activate emergency"]):
        return "activate_emergency_protocol"
    elif any(keyword in step_lower for keyword in ["document", "record"]):
        return "document_request"
    elif any(keyword in step_lower for keyword in ["log", "logging"]):
        return "log_decision"
    
    # No match found
    return None


def tool_executor_node(state: DepartmentState, tools: WaterDepartmentTools = None) -> DepartmentState:
    """
    PHASE 7: Tool Execution Node
    
    Purpose: Convert plan into facts.
    
    Executes the tools specified in the plan and collects their results.
    Each tool returns structured data.
    """
    
    logger.info("🔧 [NODE: Tool Executor]")
    
    try:
        # Backwards compatibility: instantiate tools if not provided by caller/tests
        if tools is None:
            tools = WaterDepartmentTools()
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
            
            # Parse step to tool name (handles both exact names and natural language)
            tool_name = _parse_tool_name(step)
            
            if not tool_name:
                logger.warning(f"    ⚠ Unknown tool: {step}")
                tool_results[step] = {"status": "not_implemented"}
                continue
            
            if tool_name != step:
                logger.info(f"      → Mapped to: {tool_name}")
            
            try:
                if tool_name == "check_manpower_availability":
                    result = tools.check_manpower_availability(
                        location=location,
                        required_count=input_event.get("required_workers", 5)
                    )
                    tool_results["manpower"] = result
                
                elif tool_name == "check_schedule_conflicts":
                    requested_date = input_event.get("requested_date")
                    if requested_date:
                        result = tools.check_schedule_conflicts(
                            location=location,
                            requested_date=requested_date
                        )
                        tool_results["schedule"] = result
                
                elif tool_name == "check_pipeline_health":
                    result = tools.check_pipeline_health(location=location)
                    tool_results["pipeline_health"] = result
                
                elif tool_name == "check_reservoir_levels":
                    result = tools.check_reservoir_levels()
                    tool_results["reservoir_levels"] = result
                
                elif tool_name == "assess_zone_risk":
                    if location:
                        result = tools.assess_zone_risk(location=location)
                        tool_results["zone_risk"] = result
                
                elif tool_name == "check_budget_availability":
                    estimated_cost = input_event.get("estimated_cost")
                    result = tools.check_budget_availability(estimated_cost=estimated_cost)
                    tool_results["budget"] = result
                
                elif tool_name == "get_active_projects":
                    result = tools.get_active_projects(location=location)
                    tool_results["active_projects"] = result
                
                elif tool_name == "alert_all_workers":
                    # Emergency notification
                    tool_results["alert"] = {
                        "type": "emergency_alert",
                        "status": "sent",
                        "recipients": "all_water_department_workers"
                    }
                
                elif tool_name == "activate_emergency_protocol":
                    tool_results["emergency_protocol"] = {
                        "status": "activated",
                        "timestamp": logger.info("timestamp")
                    }
                
                elif tool_name == "document_request":
                    tool_results["documentation"] = {
                        "status": "documented",
                        "request": input_event
                    }
                
                elif tool_name == "log_decision":
                    tool_results["logging"] = {
                        "status": "ready_for_logging"
                    }
            
            except Exception as e:
                logger.error(f"    ✗ Tool error {step}: {e}")
                tool_results[step] = {"error": str(e)}
        
        state["tool_results"] = tool_results
        logger.info(f"✓ Tool execution complete: {len(tool_results)} results")
        
    except Exception as e:
        logger.error(f"✗ Tool executor error: {e}")
        state["tool_results"] = {"error": str(e)}
    
    return state
