"""
Fire Agent Tools

Database query functions and utility tools for the Fire Agent.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import math

from app.models import FireStation, EmergencyIncident, AgentMessage


async def fetch_nearby_stations(
    db: AsyncSession,
    location: Dict[str, Any],
    max_distance_km: float = 10.0
) -> List[Dict[str, Any]]:
    """
    Fetch fire stations within a certain radius
    Uses simple distance calculation (Haversine formula)
    """
    query = select(FireStation).where(FireStation.operational_status == "operational")
    result = await db.execute(query)
    stations = result.scalars().all()
    
    nearby = []
    for station in stations:
        distance = calculate_distance(
            location["latitude"],
            location["longitude"],
            station.location["latitude"],
            station.location["longitude"]
        )
        
        if distance <= max_distance_km:
            nearby.append({
                "id": station.id,
                "name": station.name,
                "location": station.location,
                "distance_km": round(distance, 2),
                "personnel_count": station.personnel_count,
                "vehicle_count": station.vehicle_count,
                "equipment": station.equipment,
                "response_time_avg": station.response_time_avg,
                "operational_status": station.operational_status
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    return nearby


async def get_available_resources(
    db: AsyncSession,
    station_ids: List[int]
) -> Dict[int, Dict[str, Any]]:
    """
    Get available resources for specified stations
    """
    query = select(FireStation).where(FireStation.id.in_(station_ids))
    result = await db.execute(query)
    stations = result.scalars().all()
    
    resources = {}
    for station in stations:
        resources[station.id] = {
            "personnel_count": station.personnel_count,
            "vehicle_count": station.vehicle_count,
            "equipment": station.equipment,
            "response_time_avg": station.response_time_avg,
            "operational_status": station.operational_status
        }
    
    return resources


async def check_active_incidents(
    db: AsyncSession,
    location: Dict[str, Any],
    radius_km: float = 5.0
) -> List[Dict[str, Any]]:
    """
    Check for active emergency incidents in the area
    """
    # Get incidents from last 24 hours that are not resolved
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    query = select(EmergencyIncident).where(
        and_(
            EmergencyIncident.reported_at >= time_threshold,
            EmergencyIncident.status.in_(["reported", "dispatched", "responding", "on_scene"])
        )
    )
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    nearby_incidents = []
    for incident in incidents:
        distance = calculate_distance(
            location["latitude"],
            location["longitude"],
            incident.location["latitude"],
            incident.location["longitude"]
        )
        
        if distance <= radius_km:
            nearby_incidents.append({
                "id": incident.id,
                "incident_type": incident.incident_type,
                "severity": incident.severity,
                "status": incident.status,
                "location": incident.location,
                "distance_km": round(distance, 2),
                "reported_at": incident.reported_at.isoformat(),
                "responding_stations": incident.responding_stations,
                "casualties": incident.casualties
            })
    
    return nearby_incidents


async def get_historical_incident_patterns(
    db: AsyncSession,
    location: Dict[str, Any],
    incident_type: Optional[str] = None,
    days: int = 90
) -> Dict[str, Any]:
    """
    Analyze historical incident patterns in the area
    """
    time_threshold = datetime.utcnow() - timedelta(days=days)
    
    query = select(EmergencyIncident).where(
        EmergencyIncident.reported_at >= time_threshold
    )
    
    if incident_type:
        query = query.where(EmergencyIncident.incident_type == incident_type)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    # Filter by proximity
    nearby_incidents = []
    for incident in incidents:
        distance = calculate_distance(
            location["latitude"],
            location["longitude"],
            incident.location["latitude"],
            incident.location["longitude"]
        )
        if distance <= 5.0:  # 5km radius
            nearby_incidents.append(incident)
    
    # Calculate patterns
    total_incidents = len(nearby_incidents)
    incident_types = {}
    severity_distribution = {"minor": 0, "moderate": 0, "major": 0, "critical": 0}
    avg_response_time = 0
    
    for incident in nearby_incidents:
        # Count by type
        incident_types[incident.incident_type] = incident_types.get(incident.incident_type, 0) + 1
        
        # Count by severity
        if incident.severity in severity_distribution:
            severity_distribution[incident.severity] += 1
        
        # Calculate average response time
        if incident.response_time:
            avg_response_time += incident.response_time
    
    if total_incidents > 0:
        avg_response_time = avg_response_time / total_incidents
    
    return {
        "total_incidents": total_incidents,
        "incident_types": incident_types,
        "severity_distribution": severity_distribution,
        "avg_response_time_minutes": round(avg_response_time, 1),
        "time_period_days": days
    }


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula
    Returns distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


def calculate_eta(distance_km: float, avg_speed_kmh: float = 50.0) -> int:
    """
    Calculate estimated time of arrival in minutes
    Default average speed is 50 km/h for emergency vehicles
    """
    if distance_km <= 0:
        return 0
    
    hours = distance_km / avg_speed_kmh
    minutes = hours * 60
    return math.ceil(minutes)


def assess_severity_score(
    incident_type: str,
    casualties: int,
    building_type: Optional[str],
    fire_intensity: Optional[str]
) -> int:
    """
    Calculate severity score (0-100) based on incident parameters
    """
    score = 0
    
    # Base score by incident type
    type_scores = {
        "fire": 40,
        "rescue": 30,
        "medical": 20,
        "hazmat": 50,
        "other": 10
    }
    score += type_scores.get(incident_type, 10)
    
    # Casualties impact
    score += min(casualties * 10, 30)
    
    # Building type impact
    if building_type == "high-rise":
        score += 20
    elif building_type == "industrial":
        score += 15
    elif building_type == "commercial":
        score += 10
    
    # Fire intensity impact
    if fire_intensity == "conflagration":
        score += 30
    elif fire_intensity == "major":
        score += 20
    elif fire_intensity == "moderate":
        score += 10
    
    return min(score, 100)


def calculate_required_resources(
    severity_score: int,
    incident_type: str,
    building_type: Optional[str]
) -> Dict[str, Any]:
    """
    Calculate required resources based on severity
    """
    personnel = 4  # Minimum crew
    vehicles = 1   # Minimum vehicle
    
    # Scale based on severity
    if severity_score >= 70:
        personnel = 20
        vehicles = 4
        equipment = ["ladder_truck", "rescue_truck", "water_tender", "hazmat_unit"]
    elif severity_score >= 50:
        personnel = 12
        vehicles = 3
        equipment = ["ladder_truck", "rescue_truck", "water_tender"]
    elif severity_score >= 30:
        personnel = 8
        vehicles = 2
        equipment = ["ladder_truck", "rescue_truck"]
    else:
        personnel = 4
        vehicles = 1
        equipment = ["standard_fire_truck"]
    
    # Adjust for high-rise buildings
    if building_type == "high-rise":
        equipment.append("aerial_ladder")
        personnel += 4
    
    # Adjust for hazmat
    if incident_type == "hazmat":
        equipment.append("hazmat_unit")
        equipment.append("decontamination_unit")
        personnel += 4
    
    return {
        "personnel": personnel,
        "vehicles": vehicles,
        "equipment": equipment
    }


async def create_dispatch_plan(
    db: AsyncSession,
    nearby_stations: List[Dict[str, Any]],
    required_resources: Dict[str, Any],
    location: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create an optimal dispatch plan
    """
    plan = {
        "stations": [],
        "total_personnel": 0,
        "total_vehicles": 0,
        "estimated_eta": 0,
        "backup_stations": [],
        "mutual_aid_needed": False
    }
    
    personnel_needed = required_resources["personnel"]
    vehicles_needed = required_resources["vehicles"]
    
    # Select stations to dispatch
    for station in nearby_stations:
        if plan["total_personnel"] >= personnel_needed and plan["total_vehicles"] >= vehicles_needed:
            # Add to backup
            plan["backup_stations"].append(station["id"])
        else:
            # Add to primary dispatch
            plan["stations"].append({
                "station_id": station["id"],
                "station_name": station["name"],
                "distance_km": station["distance_km"],
                "eta_minutes": calculate_eta(station["distance_km"]),
                "personnel": min(station["personnel_count"], personnel_needed - plan["total_personnel"]),
                "vehicles": min(station["vehicle_count"], vehicles_needed - plan["total_vehicles"])
            })
            
            plan["total_personnel"] += station["personnel_count"]
            plan["total_vehicles"] += station["vehicle_count"]
    
    # Calculate overall ETA (use closest station's ETA)
    if plan["stations"]:
        plan["estimated_eta"] = min(s["eta_minutes"] for s in plan["stations"])
    
    # Check if mutual aid is needed
    if plan["total_personnel"] < personnel_needed or plan["total_vehicles"] < vehicles_needed:
        plan["mutual_aid_needed"] = True
    
    return plan
