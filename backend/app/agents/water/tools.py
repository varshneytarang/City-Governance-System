"""
Water Agent Tools
Database queries and helper functions for the Water Agent
"""
from typing import List, Dict, Any, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WaterInfrastructure, WaterResource, WaterIncident, Project
from datetime import datetime, date
import math


async def fetch_pipeline_data(
    db: AsyncSession, 
    location: str, 
    radius_km: float = 1.0
) -> List[Dict[str, Any]]:
    """
    Query pipeline database for location and surrounding area
    
    Args:
        db: Database session
        location: Location string
        radius_km: Search radius in kilometers
    
    Returns:
        List of pipeline data dictionaries
    """
    try:
        # Simple location-based query (can be enhanced with PostGIS)
        result = await db.execute(
            select(WaterInfrastructure).where(
                or_(
                    WaterInfrastructure.location.ilike(f"%{location}%"),
                    WaterInfrastructure.zone.ilike(f"%{location}%")
                )
            )
        )
        pipelines = result.scalars().all()
        
        return [
            {
                "pipeline_id": str(p.pipeline_id),
                "location": p.location,
                "zone": p.zone,
                "type": p.pipeline_type,
                "diameter_mm": p.diameter_mm,
                "material": p.material,
                "condition": p.condition,
                "risk_level": p.risk_level,
                "operational_status": p.operational_status,
                "last_maintenance": p.last_maintenance.isoformat() if p.last_maintenance else None,
                "capacity": p.capacity_liters_per_min
            }
            for p in pipelines
        ]
    except Exception as e:
        print(f"Error fetching pipeline data: {e}")
        return []


async def check_conflicts_with_projects(
    db: AsyncSession,
    location: str,
    project_types: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Check if location has active construction projects
    
    Args:
        db: Database session
        location: Location to check
        project_types: Filter by project types (e.g., ["road", "building"])
    
    Returns:
        List of conflicting projects
    """
    try:
        query = select(Project).where(
            and_(
                Project.location.ilike(f"%{location}%"),
                Project.status.in_(["planned", "active"])
            )
        )
        
        result = await db.execute(query)
        projects = result.scalars().all()
        
        return [
            {
                "project_id": str(p.project_id),
                "project_type": p.project_type,
                "location": p.location,
                "status": p.status,
                "priority": p.priority,
                "start_date": p.start_date.isoformat() if p.start_date else None,
                "end_date": p.end_date.isoformat() if p.end_date else None,
                "nuisance_score": float(p.nuisance_score) if p.nuisance_score else 0.0
            }
            for p in projects
        ]
    except Exception as e:
        print(f"Error checking project conflicts: {e}")
        return []


async def get_reservoir_status(db: AsyncSession) -> Dict[str, Any]:
    """
    Get current status of all water reservoirs
    
    Returns:
        Dictionary with reservoir status information
    """
    try:
        result = await db.execute(
            select(WaterResource).where(
                WaterResource.resource_type == "reservoir"
            )
        )
        reservoirs = result.scalars().all()
        
        total_capacity = sum(r.capacity_liters or 0 for r in reservoirs)
        total_current = sum(r.current_level_liters or 0 for r in reservoirs)
        avg_level = (total_current / total_capacity * 100) if total_capacity > 0 else 0
        
        return {
            "total_reservoirs": len(reservoirs),
            "total_capacity_liters": total_capacity,
            "current_level_liters": total_current,
            "average_level_percentage": round(avg_level, 2),
            "status": "critical" if avg_level < 30 else "low" if avg_level < 50 else "normal",
            "reservoirs": [
                {
                    "name": r.name,
                    "capacity": r.capacity_liters,
                    "current": r.current_level_liters,
                    "percentage": float(r.level_percentage) if r.level_percentage else 0.0,
                    "status": r.operational_status
                }
                for r in reservoirs
            ]
        }
    except Exception as e:
        print(f"Error getting reservoir status: {e}")
        return {
            "total_reservoirs": 0,
            "status": "unknown",
            "error": str(e)
        }


async def estimate_water_demand(
    area_type: str,
    population: int = 0,
    area_sq_km: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate estimated water demand for new development
    
    Args:
        area_type: Type of area ("residential", "commercial", "industrial")
        population: Estimated population
        area_sq_km: Area in square kilometers
    
    Returns:
        Water demand estimates
    """
    # Standard water consumption rates (liters per person per day)
    consumption_rates = {
        "residential": 135,  # per person
        "commercial": 250,   # per person equivalent
        "industrial": 500    # per person equivalent
    }
    
    rate = consumption_rates.get(area_type, 135)
    daily_demand = population * rate
    peak_demand = daily_demand * 1.5  # Peak factor
    
    return {
        "area_type": area_type,
        "population": population,
        "daily_demand_liters": daily_demand,
        "peak_demand_liters": peak_demand,
        "required_pipeline_capacity_lpm": int(peak_demand / 24 / 60),  # Convert to liters per minute
        "estimated_cost_inr": population * 15000,  # Rough estimate
        "recommendation": f"Pipeline diameter: {_calculate_pipe_diameter(peak_demand)}mm"
    }


def _calculate_pipe_diameter(flow_rate_liters_per_day: float) -> int:
    """Calculate recommended pipe diameter based on flow rate"""
    lpm = flow_rate_liters_per_day / 24 / 60
    
    if lpm < 100:
        return 50
    elif lpm < 500:
        return 100
    elif lpm < 2000:
        return 150
    elif lpm < 5000:
        return 200
    elif lpm < 10000:
        return 300
    else:
        return 400


async def check_incident_history(
    db: AsyncSession,
    location: str,
    months_back: int = 12
) -> Dict[str, Any]:
    """
    Check historical incidents at location
    
    Args:
        db: Database session
        location: Location to check
        months_back: How many months of history to check
    
    Returns:
        Incident history summary
    """
    try:
        result = await db.execute(
            select(WaterIncident).where(
                WaterIncident.location.ilike(f"%{location}%")
            )
        )
        incidents = result.scalars().all()
        
        incident_counts = {}
        for incident in incidents:
            incident_type = incident.incident_type
            incident_counts[incident_type] = incident_counts.get(incident_type, 0) + 1
        
        return {
            "total_incidents": len(incidents),
            "incident_types": incident_counts,
            "high_severity_count": sum(1 for i in incidents if i.severity in ["high", "critical"]),
            "average_resolution_time": _calculate_avg_resolution_time(incidents),
            "recommendation": "High-risk area" if len(incidents) > 5 else "Normal risk"
        }
    except Exception as e:
        print(f"Error checking incident history: {e}")
        return {"total_incidents": 0, "error": str(e)}


def _calculate_avg_resolution_time(incidents: List) -> Optional[int]:
    """Calculate average resolution time in minutes"""
    resolution_times = [i.resolution_time_minutes for i in incidents if i.resolution_time_minutes]
    return int(sum(resolution_times) / len(resolution_times)) if resolution_times else None


def assess_risk_level(
    pipeline_condition: str,
    conflicts_count: int,
    incident_history: int,
    reservoir_status: str
) -> str:
    """
    Assess overall risk level for the operation
    
    Returns:
        Risk level: "low", "medium", "high", "critical"
    """
    risk_score = 0
    
    # Pipeline condition scoring
    condition_scores = {"excellent": 0, "good": 1, "fair": 2, "poor": 3, "critical": 5}
    risk_score += condition_scores.get(pipeline_condition, 2)
    
    # Conflicts scoring
    risk_score += min(conflicts_count * 2, 5)
    
    # Incident history
    risk_score += min(incident_history, 5)
    
    # Reservoir status
    if reservoir_status == "critical":
        risk_score += 3
    elif reservoir_status == "low":
        risk_score += 1
    
    # Determine risk level
    if risk_score >= 10:
        return "critical"
    elif risk_score >= 7:
        return "high"
    elif risk_score >= 4:
        return "medium"
    else:
        return "low"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c
