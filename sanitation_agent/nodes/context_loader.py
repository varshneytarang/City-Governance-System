"""
PHASE 3: Context Loader Node

Load reality before thinking. No reasoning yet.
"""

from typing import List, Dict, Any
import logging
from datetime import datetime

from ..state import DepartmentState
from ..database import SanitationDepartmentQueries

logger = logging.getLogger(__name__)


def context_loader_node(state: DepartmentState, 
                       queries: SanitationDepartmentQueries) -> DepartmentState:
    """
    Load context from database.
    
    Purpose: Gather all relevant facts about the current sanitation situation.
    
    Fetches:
    - Active routes in the area
    - Available trucks and their status
    - Collection schedules
    - Bin status and fill levels
    - Landfill capacity
    - Recycling center availability
    - Recent complaints
    - Budget status
    
    Returns: state with context populated
    """
    
    logger.info("📊 [NODE: Context Loader] Loading reality...")
    
    try:
        input_event = state.get("input_event", {})
        zone = input_event.get("zone") or input_event.get("location")
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "zone": zone,
        }
        
        # Fetch active routes
        logger.info(f"  → Loading active routes for zone: {zone}")
        routes = queries.get_active_routes(zone=zone)
        context["active_routes"] = len(routes)
        context["routes_by_type"] = {}
        for route in routes:
            rtype = route.get("route_type", "unknown")
            context["routes_by_type"][rtype] = context["routes_by_type"].get(rtype, 0) + 1
        
        # Fetch available trucks
        logger.info(f"  → Checking truck availability")
        trucks = queries.get_available_trucks()
        context["total_trucks_available"] = len(trucks)
        context["trucks_by_type"] = {}
        for truck in trucks:
            ttype = truck.get("truck_type", "unknown")
            context["trucks_by_type"][ttype] = context["trucks_by_type"].get(ttype, 0) + 1
        
        # Fetch collection schedule
        logger.info(f"  → Loading collection schedule")
        schedules = queries.get_collection_schedule(zone=zone, days_ahead=7)
        context["scheduled_collections"] = len(schedules)
        context["schedule_status"] = {
            s["status"]: sum(1 for x in schedules if x["status"] == s["status"])
            for s in schedules
        }
        
        # Fetch bin status
        logger.info(f"  → Checking bin status")
        bins = queries.get_bin_status(zone=zone)
        context["total_bins"] = len(bins)
        context["bins_critical_fill"] = len([b for b in bins if float(b.get("current_fill_percent", 0)) >= 90])
        context["bins_full"] = len([b for b in bins if b.get("operational_status") == "full"])
        
        # Fetch landfill status
        logger.info(f"  → Checking landfill capacity")
        landfills = queries.get_landfill_status()
        context["landfills_total"] = len(landfills)
        context["landfills_operational"] = len([lf for lf in landfills if lf["operational_status"] == "active"])
        context["avg_landfill_utilization"] = (
            sum(float(lf.get("utilization_percent", 0)) for lf in landfills) / len(landfills)
            if landfills else 0
        )
        
        # Fetch recycling centers
        logger.info(f"  → Checking recycling centers")
        recycling_centers = queries.get_recycling_centers()
        context["recycling_centers_total"] = len(recycling_centers)
        context["recycling_centers_available"] = len([rc for rc in recycling_centers if rc["operational_status"] == "active"])
        
        # Fetch recent complaints
        logger.info(f"  → Checking complaint history")
        complaints = queries.get_recent_complaints(zone=zone, days=30)
        context["recent_complaints"] = len(complaints)
        context["complaints_by_type"] = {}
        for c in complaints:
            ctype = c.get("complaint_type", "other")
            context["complaints_by_type"][ctype] = context["complaints_by_type"].get(ctype, 0) + 1
        context["unresolved_complaints"] = len([c for c in complaints if c["status"] not in ["resolved", "closed"]])
        
        # Fetch budget status
        logger.info(f"  → Checking budget status")
        budget = queries.get_budget_status()
        if budget:
            context["budget"] = {
                "total": float(budget["total_budget"]),
                "spent": float(budget["spent"]),
                "remaining": float(budget["remaining"]),
                "utilization_percent": float(budget["utilization_percent"])
            }
        else:
            context["budget"] = None
        
        # Fetch available workers
        logger.info(f"  → Checking worker availability")
        workers = queries.get_available_workers()
        context["total_workers_available"] = len(workers)
        context["workers_by_role"] = {}
        for worker in workers:
            role = worker.get("role", "unknown")
            context["workers_by_role"][role] = context["workers_by_role"].get(role, 0) + 1
        
        logger.info(f"✓ Context loaded: {len(routes)} routes, {len(trucks)} trucks, "
                   f"{len(bins)} bins, {len(complaints)} recent complaints")
        
        state["context"] = context
        
    except Exception as e:
        logger.error(f"✗ Context loader error: {e}")
        state["context"] = {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    return state
