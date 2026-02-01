"""
PHASE 3: Context Loader Node

Load reality before thinking. No reasoning yet.
"""

from typing import List, Dict, Any
import logging
from datetime import datetime

from ..state import DepartmentState
from ..database import WaterDepartmentQueries

logger = logging.getLogger(__name__)


def context_loader_node(state: DepartmentState,
                       queries: WaterDepartmentQueries = None) -> DepartmentState:
    """
    Load context from database.
    
    Purpose: Gather all relevant facts about the current situation.
    
    Fetches:
    - Active projects in the area
    - Current schedule
    - Available workers
    - Pipeline health
    - Reservoir levels
    - Recent incidents
    - Budget status
    
    Returns: state with context populated
    """
    
    logger.info("📊 [NODE: Context Loader] Loading reality...")
    
    try:
        # Ensure a queries object exists for backwards compatibility when tests call
        # this node without providing `queries`.
        if queries is None:
            queries = WaterDepartmentQueries()
        input_event = state.get("input_event", {})
        location = input_event.get("location")
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "location": location,
        }
        
        # Fetch active projects
        logger.info(f"  → Loading active projects for {location}")
        context["active_projects"] = queries.get_active_projects(location=location)
        
        # Fetch work schedule
        logger.info(f"  → Loading work schedule for {location}")
        context["scheduled_work"] = queries.get_work_schedule(location=location, days_ahead=7)
        
        # Fetch available workers
        logger.info(f"  → Checking worker availability")
        workers = queries.get_available_workers()
        context["total_workers_available"] = len(workers)
        context["workers_by_role"] = {}
        for worker in workers:
            role = worker.get("role", "unknown")
            if role not in context["workers_by_role"]:
                context["workers_by_role"][role] = 0
            context["workers_by_role"][role] += 1
        
        # Fetch pipeline health
        logger.info(f"  → Checking pipeline health")
        pipelines = queries.get_pipeline_status(location=location)
        context["pipelines_total"] = len(pipelines)
        context["pipelines_status"] = {
            p["condition"]: sum(1 for x in pipelines if x["condition"] == p["condition"])
            for p in pipelines
        }
        
        # Fetch reservoir levels
        logger.info(f"  → Checking reservoir levels")
        reservoirs = queries.get_reservoir_status()
        context["reservoirs"] = len(reservoirs)
        context["avg_reservoir_level"] = (
            sum(float(r.get("level_percentage", 0)) for r in reservoirs) / len(reservoirs)
            if reservoirs else 0
        )
        
        # Fetch recent incidents
        logger.info(f"  → Checking incident history")
        incidents = queries.get_recent_incidents(location=location, days=30)
        context["recent_incidents"] = len(incidents)
        context["incident_severity"] = {
            "critical": len([i for i in incidents if i["severity"] == "critical"]),
            "high": len([i for i in incidents if i["severity"] == "high"]),
            "medium": len([i for i in incidents if i["severity"] == "medium"]),
            "low": len([i for i in incidents if i["severity"] == "low"])
        }
        
        # Fetch budget status
        logger.info(f"  → Checking budget status")
        budget = queries.get_budget_status()
        if budget:
            context["budget"] = {
                "total": float(budget["total_budget"]),
                "spent": float(budget["spent"]),
                "remaining": float(budget["remaining"]),
                "utilization_percent": float(budget["utilization_percent"]) if budget["utilization_percent"] else 0,
                "status": budget["status"]
            }
        
        # Identify high-risk zones
        logger.info(f"  → Identifying high-risk zones")
        high_risk = queries.get_high_risk_zones()
        context["high_risk_zones"] = [z["location"] for z in high_risk]
        context["is_high_risk_zone"] = location in context["high_risk_zones"] if location else False
        
        state["context"] = context
        
        logger.info(f"✓ Context loaded: {len(context)} fields")
        
    except Exception as e:
        logger.error(f"✗ Context loader error: {e}")
        state["context"] = {
            "error": str(e),
            "location": state.get("input_event", {}).get("location")
        }
    
    return state
