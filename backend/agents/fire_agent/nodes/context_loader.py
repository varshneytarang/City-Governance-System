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
    - Fire stations in the zone/city
    - Available fire trucks
    - Available firefighters
    - Equipment status
    - Recent emergency calls
    - Fire hydrants in the zone
    - Recent incidents (for historical context)
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
    
    db = DatabaseConnection()
    queries = FireDepartmentQueries(db)
    context = {}
    
    try:
        # Load fire stations
        if zone:
            context["fire_stations"] = queries.get_fire_stations(zone=zone)
        else:
            context["fire_stations"] = queries.get_fire_stations()
        
        # Load available trucks
        if zone:
            context["available_trucks"] = queries.get_available_trucks(zone=zone)
        else:
            context["available_trucks"] = queries.get_available_trucks()
        
        # Load available firefighters
        if zone:
            context["available_firefighters"] = queries.get_available_firefighters(zone=zone)
        else:
            context["available_firefighters"] = queries.get_available_firefighters()
        
        # Load equipment by station (if specific zone)
        if zone and context.get("fire_stations"):
            station_ids = [s["id"] for s in context["fire_stations"]]
            if station_ids:
                context["equipment"] = queries.get_equipment_by_station(station_ids[0])
        
        # Load recent emergency calls
        if zone:
            context["recent_calls"] = queries.get_recent_emergency_calls(zone=zone, days=7)
        else:
            context["recent_calls"] = queries.get_recent_emergency_calls(days=7)
        
        # Load hydrants in zone
        if zone:
            context["fire_hydrants"] = queries.get_hydrants_by_zone(zone)
        
        # Load recent incidents (for pattern recognition)
        if location:
            context["location_incidents"] = queries.get_incidents_by_location(location, days=30)
        else:
            context["recent_incidents"] = queries.get_recent_incidents(days=30)
        
        # Load budget status
        context["budget"] = queries.get_budget_status()
        
        # Summary statistics
        context["summary"] = {
            "total_stations": len(context.get("fire_stations", [])),
            "available_trucks": len(context.get("available_trucks", [])),
            "available_firefighters": len(context.get("available_firefighters", [])),
            "recent_calls_count": len(context.get("recent_calls", [])),
            "hydrants_in_zone": len(context.get("fire_hydrants", [])),
            "recent_incidents_count": len(context.get("recent_incidents", [])) + len(context.get("location_incidents", []))
        }
        
        logger.info(f"Context loaded: {context['summary']}")
        
    except Exception as e:
        logger.error(f"Error loading context: {e}")
        context["error"] = str(e)
    finally:
        db.close()
    
    return {
        **state,
        "context": context,
        "phase": "context_loaded"
    }
