"""
Context Loader Node for Fire Department Agent.
Loads relevant context (stations, trucks, firefighters, equipment, calls, hydrants, incidents) from database.
"""

from typing import Dict, Any
from agents.fire_agent.state import DepartmentState
from agents.fire_agent.config import settings
import logging

# Import DatabaseConnection
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from agents.water_agent.database import DatabaseConnection
from agents.fire_agent.database import FireDepartmentQueries

logger = logging.getLogger(__name__)


def load_context(state: DepartmentState) -> Dict[str, Any]:
    """
    Load relevant fire department context based on the request.
    
    Retrieves:
    - Fire incidents (stored in incidents table with department='fire')
    - Active projects
    - Work schedule
    - Available workers
    - Budget status
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with context loaded
    """
    logger.info("Loading context for fire department request")
    
    request = state.get("request", {})
    zone = request.get("zone")
    location = request.get("location")
    incident_type = request.get("incident_type")
    
    # Ignore generic/placeholder zone/location values - treat them as "no filter"
    if zone and zone.lower() in ['general', 'all', 'any', 'city', 'citywide']:
        logger.info(f"⚠ Ignoring generic zone filter: '{zone}' - loading ALL data")
        zone = None
    if location and location.lower() in ['general', 'all', 'any', 'city', 'citywide']:
        logger.info(f"⚠ Ignoring generic location filter: '{location}' - loading ALL data")
        location = None
    
    db = DatabaseConnection()
    queries = FireDepartmentQueries(db)
    context = {}
    
    try:
        # Load fire incidents (main data source)
        logger.info(f"  → Loading fire incidents")
        incidents = queries.get_fire_incidents(location=location or zone, days=90)
        context["total_incidents"] = len(incidents)
        context["incidents_by_severity"] = {}
        for inc in incidents:
            severity = inc.get("severity", "unknown")
            context["incidents_by_severity"][severity] = context["incidents_by_severity"].get(severity, 0) + 1
        context["recent_incidents"] = incidents[:10]  # Store recent 10
        
        # Load active fire incidents (unresolved)
        logger.info(f"  → Loading active incidents")
        active_incidents = queries.get_active_fire_incidents(location=location or zone)
        context["active_incidents"] = len(active_incidents)
        context["active_incidents_list"] = active_incidents[:5]  # Store top 5
        
        # Load incidents by type if specified
        if incident_type:
            logger.info(f"  → Loading incidents of type: {incident_type}")
            typed_incidents = queries.get_incidents_by_type(incident_type=incident_type, days=90)
            context["incidents_of_type"] = len(typed_incidents)
            context["typed_incidents_list"] = typed_incidents[:5]
        
        # Load active projects
        logger.info(f"  → Loading active fire projects")
        projects = queries.get_active_projects(location=location or zone)
        context["total_projects"] = len(projects)
        context["projects_by_status"] = {}
        for proj in projects:
            status = proj.get("status", "unknown")
            context["projects_by_status"][status] = context["projects_by_status"].get(status, 0) + 1
        context["active_projects"] = projects[:5]  # Store recent 5
        
        # Load work schedule
        logger.info(f"  → Loading work schedule")
        schedules = queries.get_work_schedule(location=location or zone, days_ahead=7)
        context["scheduled_work_items"] = len(schedules)
        context["schedule_by_priority"] = {}
        for sched in schedules:
            priority = sched.get("priority", "normal")
            context["schedule_by_priority"][priority] = context["schedule_by_priority"].get(priority, 0) + 1
        context["upcoming_work"] = schedules[:5]  # Store next 5
        
        # Load available workers
        logger.info(f"  → Checking firefighter availability")
        workers = queries.get_available_workers()
        context["available_firefighters"] = len(workers)
        context["workers_by_role"] = {}
        for worker in workers:
            role = worker.get("role", "unknown")
            context["workers_by_role"][role] = context["workers_by_role"].get(role, 0) + 1
        context["available_workers_list"] = workers[:10]  # Store first 10
        
        # Load budget status
        logger.info(f"  → Checking budget status")
        budget = queries.get_budget_status()
        context["budget"] = budget
        
        # Summary statistics
        context["summary"] = {
            "total_incidents": context.get("total_incidents", 0),
            "active_incidents": context.get("active_incidents", 0),
            "available_firefighters": context.get("available_firefighters", 0),
            "total_projects": context.get("total_projects", 0),
            "scheduled_work_items": context.get("scheduled_work_items", 0),
            "budget_remaining": budget.get("remaining") if budget else None
        }
        
        logger.info(f"Context loaded: {context['summary']}")
        
    except Exception as e:
        logger.error(f"Error loading context: {e}", exc_info=True)
        context["error"] = str(e)
    finally:
        db.close()
    
    return {
        **state,
        "context": context,
        "phase": "context_loaded"
    }
