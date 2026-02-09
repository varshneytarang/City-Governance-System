"""
Tool Executor Node for Fire Department Agent.
Executes planned actions using fire department tools.
"""

from typing import Dict, Any, List
from agents.fire_agent.state import DepartmentState
from agents.fire_agent.tools import FireDepartmentTools
import logging

# Import database utilities
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from agents.water_agent.database import DatabaseConnection
from agents.fire_agent.database import FireDepartmentQueries

logger = logging.getLogger(__name__)


def execute_tools(state: DepartmentState) -> Dict[str, Any]:
    """
    Execute the planned tools and collect results.
    
    Runs each tool in the plan and aggregates results for evaluation.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with tool execution results
    """
    logger.info("Executing tools for fire department request")
    
    plan = state.get("plan", {})
    context = state.get("context", {})
    request = state.get("request", {})
    
    steps = plan.get("steps", [])
    
    # Create database connection and tools
    db = DatabaseConnection()
    queries = FireDepartmentQueries(db)
    tools = FireDepartmentTools(queries)
    
    tool_results = {}  # Use dictionary like water agent, not list
    all_passed = True
    
    for step in steps:
        try:
            logger.info(f"Executing tool: {step}")
            
            # Map tool names to methods and store with short keys for observer
            if step == "check_truck_availability":
                zone = request.get("zone")
                result = tools.check_truck_availability(zone)
                tool_results["check_truck_availability"] = result
                
            elif step == "check_firefighter_availability":
                zone = request.get("zone")
                result = tools.check_firefighter_availability(zone)
                tool_results["check_firefighter_availability"] = result
                
            elif step == "check_equipment_status":
                station_id = None
                if context.get("fire_stations"):
                    station_id = context["fire_stations"][0].get("id")
                result = tools.check_equipment_status(station_id)
                tool_results["check_equipment_status"] = result
                
            elif step == "assess_response_time":
                location = request.get("location", "")
                zone = request.get("zone", "Zone-1")
                result = tools.assess_response_time(location, zone)
                tool_results["assess_response_time"] = result
                
            elif step == "check_hydrant_status":
                zone = request.get("zone")
                result = tools.check_hydrant_status(zone)
                tool_results["check_hydrant_status"] = result
                
            elif step == "get_incident_history":
                location = request.get("location")
                zone = request.get("zone")
                result = tools.get_incident_history(location, zone)
                tool_results["get_incident_history"] = result
                
            elif step == "estimate_resource_needs":
                incident_type = request.get("incident_type", "structure_fire")
                severity = request.get("priority", "medium")
                result = tools.estimate_resource_needs(incident_type, severity)
                tool_results["estimate_resource_needs"] = result
                
            elif step == "check_station_capacity":
                zone = request.get("zone")
                result = tools.check_station_capacity(zone)
                tool_results["check_station_capacity"] = result
                
            elif step == "check_budget_availability":
                estimated_cost = plan.get("resource_requirements", {}).get("budget", 10000)
                result = tools.check_budget_availability(estimated_cost)
                tool_results["check_budget_availability"] = result
                
            else:
                logger.warning(f"Unknown tool: {step}")
                result = {
                    "tool": step,
                    "status": "unknown",
                    "message": f"Tool {step} not recognized"
                }
                tool_results[step] = result
            
            # Check if tool passed
            if result.get("status") not in ["available", "operational", "within_limits", "success"]:
                all_passed = False
                
        except Exception as e:
            logger.error(f"Error executing tool {step}: {e}")
            tool_results[step] = {
                "tool": step,
                "status": "error",
                "message": str(e)
            }
            all_passed = False
    
    # Aggregate results
    execution_summary = {
        "total_tools": len(steps),
        "successful": sum(1 for r in tool_results.values() if r.get("status") in ["available", "operational", "within_limits", "success"]),
        "failed": sum(1 for r in tool_results.values() if r.get("status") not in ["available", "operational", "within_limits", "success"]),
        "all_passed": all_passed
    }
    
    logger.info(f"Tool execution complete: {execution_summary}")
    
    # Close database connection
    db.close()
    
    return {
        **state,
        "tool_results": tool_results,  # Dictionary not list
        "execution_summary": execution_summary,
        "phase": "tools_executed"
    }
