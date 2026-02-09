"""
PHASE 7: Tool Execution

Tools that gather facts from the system.
Each tool returns structured data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .database import DatabaseConnection, WaterDepartmentQueries

logger = logging.getLogger(__name__)


class WaterDepartmentTools:
    """Toolkit for Water Department Agent"""
    
    def __init__(self, db: DatabaseConnection, queries: WaterDepartmentQueries):
        self.db = db
        self.queries = queries
    
    # ========== MANPOWER TOOLS ==========
    
    def check_manpower_availability(self, 
                                   location: str, 
                                   role: str = None,
                                   required_count: int = 1) -> Dict:
        """
        Check if enough workers are available for the task.
        
        Returns: {
            "available_count": int,
            "required_count": int,
            "sufficient": bool,
            "workers": [{id, name, role, skills}]
        }
        """
        try:
            workers = self.queries.get_available_workers(location=location, role=role)
            
            return {
                "available_count": len(workers),
                "required_count": required_count,
                "sufficient": len(workers) >= required_count,
                "worker_details": [
                    {
                        "id": w["worker_id"],
                        "name": w["worker_name"],
                        "role": w["role"],
                        "skills": w["skills"] if isinstance(w["skills"], list) else []
                    }
                    for w in workers[:5]  # Return top 5
                ]
            }
        except Exception as e:
            logger.error(f"Manpower check error: {e}")
            return {"error": str(e), "available_count": 0, "sufficient": False}
    
    # ========== INFRASTRUCTURE TOOLS ==========
    
    def check_pipeline_health(self, location: str = None, zone: str = None) -> Dict:
        """
        Check pipeline conditions and operational status.
        
        Returns: {
            "pipelines": [...],
            "critical_issues": [...],
            "overall_condition": "good|fair|poor"
        }
        """
        try:
            pipelines = self.queries.get_pipeline_status(location=location, zone=zone)
            
            critical = [p for p in pipelines if p["condition"] in ["poor", "critical"]]
            under_repair = [p for p in pipelines if p["operational_status"] == "under_repair"]
            
            # Determine overall status
            if critical or under_repair:
                overall = "poor"
            elif any(p["condition"] == "fair" for p in pipelines):
                overall = "fair"
            else:
                overall = "good"
            
            return {
                "total_pipelines": len(pipelines),
                "overall_condition": overall,
                "critical_issues": len(critical),
                "under_repair": len(under_repair),
                "pipelines": [
                    {
                        "id": p["pipeline_id"],
                        "location": p["location"],
                        "zone": p["zone"],
                        "type": p["pipeline_type"],
                        "condition": p["condition"],
                        "status": p["operational_status"],
                        "pressure_psi": float(p["pressure_psi"]) if p["pressure_psi"] else None
                    }
                    for p in pipelines
                ]
            }
        except Exception as e:
            logger.error(f"Pipeline health check error: {e}")
            return {"error": str(e)}
    
    def check_reservoir_levels(self) -> Dict:
        """
        Check water reservoir levels.
        
        Returns: {
            "reservoirs": [...],
            "critical_low": [...],
            "overall_status": "safe|warning|critical"
        }
        """
        try:
            reservoirs = self.queries.get_reservoir_status()
            
            critical = [r for r in reservoirs if r["level_percentage"] < 20]
            warning = [r for r in reservoirs if 20 <= r["level_percentage"] < 40]
            
            if critical:
                overall = "critical"
            elif warning:
                overall = "warning"
            else:
                overall = "safe"
            
            return {
                "total_reservoirs": len(reservoirs),
                "overall_status": overall,
                "critical_count": len(critical),
                "reservoirs": [
                    {
                        "id": r["reservoir_id"],
                        "name": r["name"],
                        "location": r["location"],
                        "level_percent": float(r["level_percentage"]) if r["level_percentage"] else None,
                        "capacity_liters": r["capacity_liters"],
                        "current_liters": r["current_level_liters"],
                        "status": r["operational_status"]
                    }
                    for r in reservoirs
                ]
            }
        except Exception as e:
            logger.error(f"Reservoir check error: {e}")
            return {"error": str(e)}
    
    # ========== SCHEDULE TOOLS ==========
    
    def check_schedule_conflicts(self, location: str, 
                                 requested_date: str,
                                 duration_hours: int = 8) -> Dict:
        """
        Check for schedule conflicts on a given date.
        
        Returns: {
            "conflicts": bool,
            "scheduled_activities": [...],
            "available_slots": [...]
        }
        """
        try:
            schedule = self.queries.get_work_schedule(location, days_ahead=7)
            
            # Filter for the requested date
            requested_activities = [
                s for s in schedule 
                if str(s["scheduled_date"]) == requested_date
            ]
            
            return {
                "requested_date": requested_date,
                "has_conflicts": len(requested_activities) > 0,
                "activity_count": len(requested_activities),
                "scheduled_activities": [
                    {
                        "activity": s["activity_type"],
                        "time": f"{s['start_time']} - {s['end_time']}",
                        "workers": s["workers_assigned"],
                        "priority": s["priority"]
                    }
                    for s in requested_activities
                ]
            }
        except Exception as e:
            logger.error(f"Schedule conflict check error: {e}")
            return {"error": str(e), "has_conflicts": None}
    
    # ========== RISK ASSESSMENT TOOLS ==========
    
    def assess_zone_risk(self, location: str) -> Dict:
        """
        Assess safety and operational risk in a location.
        
        Returns: {
            "risk_level": "low|medium|high|critical",
            "contributing_factors": [...],
            "incident_history": [...]
        }
        """
        try:
            # Get recent incidents
            incidents = self.queries.get_recent_incidents(location=location, days=30)
            
            # Get high-risk zones
            high_risk_zones = self.queries.get_high_risk_zones()
            is_high_risk_zone = any(z["location"] == location for z in high_risk_zones)
            
            # Get pipeline issues
            pipelines = self.queries.get_pipeline_status(location=location)
            pipeline_issues = sum(1 for p in pipelines if p["condition"] in ["poor", "critical"])
            
            # Calculate risk level
            factors = []
            risk_score = 0
            
            if is_high_risk_zone:
                factors.append("Multiple incidents in past 30 days")
                risk_score += 2
            
            if pipeline_issues > 0:
                factors.append(f"{pipeline_issues} pipeline(s) in poor condition")
                risk_score += pipeline_issues
            
            critical_incidents = [i for i in incidents if i["severity"] == "critical"]
            if critical_incidents:
                factors.append(f"{len(critical_incidents)} critical incident(s)")
                risk_score += 3
            
            # Determine risk level
            if risk_score >= 5:
                risk_level = "critical"
            elif risk_score >= 3:
                risk_level = "high"
            elif risk_score >= 1:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            return {
                "location": location,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "contributing_factors": factors,
                "recent_incidents": len(incidents),
                "incidents": [
                    {
                        "type": i["incident_type"],
                        "severity": i["severity"],
                        "date": str(i["reported_date"]),
                        "status": i["status"]
                    }
                    for i in incidents[:5]
                ]
            }
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {"error": str(e), "risk_level": "unknown"}
    
    # ========== BUDGET TOOLS ==========
    
    def check_budget_availability(self, estimated_cost: float = None) -> Dict:
        """
        Check if budget is available for the operation.
        
        Returns: {
            "current_budget": float,
            "spent": float,
            "remaining": float,
            "utilization_percent": float,
            "can_afford": bool
        }
        """
        try:
            budget = self.queries.get_budget_status()
            
            if not budget:
                return {
                    "error": "No budget data for current period",
                    "can_afford": False
                }
            
            remaining = float(budget["remaining"]) if budget["remaining"] else 0
            can_afford = True
            
            if estimated_cost and remaining < estimated_cost:
                can_afford = False
            
            return {
                "total_budget": float(budget["total_budget"]),
                "spent": float(budget["spent"]),
                "remaining": remaining,
                "utilization_percent": float(budget["utilization_percent"]) if budget["utilization_percent"] else 0,
                "status": budget["status"],
                "estimated_cost": estimated_cost,
                "can_afford": can_afford
            }
        except Exception as e:
            logger.error(f"Budget check error: {e}")
            return {"error": str(e), "can_afford": False}
    
    # ========== PROJECT TOOLS ==========
    
    def get_active_projects(self, location: str = None) -> Dict:
        """
        Get list of active projects that might conflict.
        
        Returns: {
            "active_count": int,
            "projects": [...]
        }
        """
        try:
            projects = self.queries.get_active_projects(location=location)
            
            return {
                "location": location,
                "active_count": len(projects),
                "projects": [
                    {
                        "id": p["project_id"],
                        "name": p["project_name"],
                        "location": p["location"],
                        "status": p["status"],
                        "start_date": str(p["start_date"]),
                        "end_date": str(p["end_date"])
                    }
                    for p in projects
                ]
            }
        except Exception as e:
            logger.error(f"Active projects check error: {e}")
            return {"error": str(e), "active_count": 0}


def create_tools(db: DatabaseConnection, queries: WaterDepartmentQueries) -> WaterDepartmentTools:
    """Factory to create tools"""
    return WaterDepartmentTools(db, queries)
