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
        
        # Ignore generic/placeholder zone values - treat them as "no zone filter"
        if zone and zone.lower() in ['general', 'all', 'any', 'city', 'citywide']:
            logger.info(f"⚠ Ignoring generic zone filter: '{zone}' - loading ALL data")
            zone = None
        elif zone:
            logger.info(f"📍 Loading data for specific zone: '{zone}'")
        else:
            logger.info(f"📊 No zone filter - loading ALL data")
        
        context = {
            "timestamp": datetime.now().isoformat(),
            "zone": zone,
        }
        
        # Fetch sanitation inspections (main sanitation-specific data)
        logger.info(f"  → Loading recent sanitation inspections")
        inspections = queries.get_sanitation_inspections(location=zone, days=90)
        context["total_inspections"] = len(inspections)
        context["inspections_by_outcome"] = {}
        for insp in inspections:
            outcome = insp.get("outcome", "unknown")
            context["inspections_by_outcome"][outcome] = context["inspections_by_outcome"].get(outcome, 0) + 1
        context["recent_inspections"] = inspections[:5]  # Store recent 5
        
        # Fetch active projects
        logger.info(f"  → Loading active sanitation projects")
        projects = queries.get_active_projects(location=zone)
        context["total_projects"] = len(projects)
        context["projects_by_status"] = {}
        for proj in projects:
            status = proj.get("status", "unknown")
            context["projects_by_status"][status] = context["projects_by_status"].get(status, 0) + 1
        context["active_projects"] = projects[:5]  # Store recent 5
        
        # Fetch work schedule
        logger.info(f"  → Loading work schedule")
        schedules = queries.get_work_schedule(location=zone, days_ahead=7)
        context["scheduled_work_items"] = len(schedules)
        context["schedule_by_priority"] = {}
        for sched in schedules:
            priority = sched.get("priority", "normal")
            context["schedule_by_priority"][priority] = context["schedule_by_priority"].get(priority, 0) + 1
        context["upcoming_work"] = schedules[:5]  # Store next 5
        
        # Fetch available workers
        logger.info(f"  → Checking worker availability")
        workers = queries.get_available_workers()
        context["total_workers_available"] = len(workers)
        context["workers_by_role"] = {}
        for worker in workers:
            role = worker.get("role", "unknown")
            context["workers_by_role"][role] = context["workers_by_role"].get(role, 0) + 1
        context["available_workers"] = workers[:10]  # Store first 10
        
        # Fetch recent incidents
        logger.info(f"  → Loading recent sanitation incidents")
        incidents = queries.get_recent_incidents(location=zone, days=30)
        context["total_incidents"] = len(incidents)
        context["incidents_by_severity"] = {}
        for inc in incidents:
            severity = inc.get("severity", "unknown")
            context["incidents_by_severity"][severity] = context["incidents_by_severity"].get(severity, 0) + 1
        context["recent_incidents"] = incidents[:5]  # Store recent 5
        
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
