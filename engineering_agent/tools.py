"""
Engineering Department Tools

Tools for gathering facts about infrastructure, contractors, equipment,
tenders, safety compliance, and weather/monsoon constraints.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .database import DatabaseConnection, EngineeringDepartmentQueries
from .config import settings

logger = logging.getLogger(__name__)


class EngineeringDepartmentTools:
    """Toolkit for Engineering Department Agent"""
    
    def __init__(self, db: DatabaseConnection, queries: EngineeringDepartmentQueries):
        self.db = db
        self.queries = queries
    
    # ========== PROJECT MANAGEMENT TOOLS ==========
    
    def check_active_projects(self, location: str = None) -> Dict:
        """
        Check currently active engineering projects.
        
        Returns: {
            "total_projects": int,
            "projects": [...],
            "capacity_available": bool
        }
        """
        try:
            projects = self.queries.get_active_projects(location=location)
            
            return {
                "total_projects": len(projects),
                "capacity_available": len(projects) < settings.MAX_CONCURRENT_PROJECTS,
                "max_allowed": settings.MAX_CONCURRENT_PROJECTS,
                "projects": [
                    {
                        "id": p["project_id"],
                        "name": p["project_name"],
                        "location": p["location"],
                        "status": p["status"],
                        "type": p.get("project_type", "unknown"),
                        "estimated_cost": float(p["estimated_cost"]) if p["estimated_cost"] else 0,
                        "actual_cost": float(p["actual_cost"]) if p["actual_cost"] else 0,
                        "start_date": str(p["start_date"]) if p["start_date"] else None
                    }
                    for p in projects[:20]
                ]
            }
        except Exception as e:
            logger.error(f"Active projects check error: {e}")
            return {"error": str(e), "total_projects": 0}
    
    # ========== CONTRACTOR MANAGEMENT TOOLS ==========
    
    def check_contractor_availability(self, min_rating: float = None) -> Dict:
        """
        Check available contractors with ratings.
        
        Returns: {
            "available_count": int,
            "contractors": [...],
            "qualified_contractors": int
        }
        """
        try:
            min_rating = min_rating or settings.MIN_CONTRACTOR_RATING
            contractors = self.queries.get_contractors(min_rating=min_rating)
            
            # For now, all active contractors are considered qualified
            # TODO: Add actual rating system
            qualified = contractors
            
            return {
                "available_count": len(contractors),
                "qualified_contractors": len(qualified),
                "min_rating_required": min_rating,
                "contractors": [
                    {
                        "id": c["contractor_id"],
                        "name": c["contractor_name"],
                        "role": c["role"],
                        "status": c["status"],
                        "rating": 4.0  # Placeholder
                    }
                    for c in contractors[:10]
                ]
            }
        except Exception as e:
            logger.error(f"Contractor check error: {e}")
            return {"error": str(e), "available_count": 0}
    
    # ========== EQUIPMENT MANAGEMENT TOOLS ==========
    
    def check_equipment_availability(self, equipment_type: str = None) -> Dict:
        """
        Check equipment availability.
        
        Returns: {
            "available": bool,
            "equipment": [...]
        }
        """
        try:
            equipment = self.queries.get_equipment_availability(equipment_type=equipment_type)
            
            # Simplified response
            return {
                "equipment_type": equipment_type or "all",
                "available": True,  # Placeholder
                "total_units": equipment[0]["total_equipment"] if equipment else 0,
                "available_units": equipment[0]["available_equipment"] if equipment else 0
            }
        except Exception as e:
            logger.error(f"Equipment check error: {e}")
            return {"error": str(e), "available": False}
    
    # ========== BUDGET MANAGEMENT TOOLS ==========
    
    def check_budget_availability(self, required_amount: float) -> Dict:
        """
        Check if budget is available for the required amount.
        
        Returns: {
            "available": bool,
            "remaining_budget": float,
            "required_amount": float,
            "sufficient": bool
        }
        """
        try:
            budget = self.queries.get_budget_status()
            remaining = budget.get("remaining", 0)
            
            return {
                "allocated": budget.get("allocated", 0),
                "spent": budget.get("spent", 0),
                "remaining": remaining,
                "required_amount": required_amount,
                "sufficient": remaining >= required_amount,
                "budget_year": budget.get("year", datetime.now().year)
            }
        except Exception as e:
            logger.error(f"Budget check error: {e}")
            return {"error": str(e), "sufficient": False}
    
    # ========== TENDER MANAGEMENT TOOLS ==========
    
    def check_tender_requirements(self, estimated_cost: float) -> Dict:
        """
        Check tender requirements based on cost.
        
        Returns: {
            "requires_tender": bool,
            "approval_level": str,
            "pending_tenders": int
        }
        """
        try:
            requires_tender = estimated_cost > settings.MAX_TENDER_AMOUNT_WITHOUT_APPROVAL
            
            # Determine approval level
            if estimated_cost < 100000:
                approval_level = "junior_engineer"
            elif estimated_cost < 500000:
                approval_level = "executive_engineer"
            elif estimated_cost < 2000000:
                approval_level = "superintendent_engineer"
            else:
                approval_level = "chief_engineer"
            
            pending = self.queries.get_pending_tenders(max_amount=estimated_cost * 2)
            
            return {
                "estimated_cost": estimated_cost,
                "requires_tender": requires_tender,
                "approval_level": approval_level,
                "pending_tenders_count": len(pending),
                "threshold": settings.MAX_TENDER_AMOUNT_WITHOUT_APPROVAL
            }
        except Exception as e:
            logger.error(f"Tender check error: {e}")
            return {"error": str(e), "requires_tender": True}
    
    # ========== WEATHER & SEASONAL TOOLS ==========
    
    def check_monsoon_restrictions(self, planned_start_month: int = None) -> Dict:
        """
        Check if monsoon restrictions apply.
        
        Returns: {
            "monsoon_season": bool,
            "restrictions_apply": bool,
            "safe_months": [...]
        }
        """
        try:
            current_month = planned_start_month or datetime.now().month
            
            is_monsoon = current_month in settings.MONSOON_BLACKOUT_MONTHS
            
            return {
                "current_month": current_month,
                "monsoon_season": is_monsoon,
                "restrictions_apply": is_monsoon,
                "monsoon_months": settings.MONSOON_BLACKOUT_MONTHS,
                "recommendation": "Delay project" if is_monsoon else "Proceed with caution"
            }
        except Exception as e:
            logger.error(f"Monsoon check error: {e}")
            return {"error": str(e), "restrictions_apply": False}
    
    # ========== SAFETY & COMPLIANCE TOOLS ==========
    
    def check_safety_compliance(self, location: str = None) -> Dict:
        """
        Check recent safety violations and compliance.
        
        Returns: {
            "compliant": bool,
            "recent_violations": int,
            "safety_score": float
        }
        """
        try:
            violations = self.queries.get_safety_violations(days_back=90)
            
            # Calculate safety score
            violation_count = len(violations)
            if violation_count == 0:
                safety_score = 5.0
            elif violation_count <= 2:
                safety_score = 4.5
            elif violation_count <= 5:
                safety_score = 4.0
            else:
                safety_score = 3.5
            
            return {
                "safety_score": safety_score,
                "min_required_score": settings.MIN_SAFETY_SCORE,
                "compliant": safety_score >= settings.MIN_SAFETY_SCORE,
                "recent_violations": violation_count,
                "violations": [
                    {
                        "type": v["violation_type"],
                        "location": v["location"],
                        "severity": v["severity"],
                        "date": str(v["reported_at"])
                    }
                    for v in violations[:5]
                ]
            }
        except Exception as e:
            logger.error(f"Safety compliance check error: {e}")
            return {"error": str(e), "compliant": True, "safety_score": 5.0}
    
    # ========== INCIDENT & RISK TOOLS ==========
    
    def check_recent_incidents(self, location: str = None, days_back: int = 30) -> Dict:
        """
        Check recent incidents in the area.
        
        Returns: {
            "total_incidents": int,
            "high_severity_count": int,
            "incidents": [...]
        }
        """
        try:
            incidents = self.queries.get_incidents(days_back=days_back)
            
            if location:
                incidents = [i for i in incidents if i["location"] == location]
            
            high_severity = [i for i in incidents if i["severity"] in ["high", "critical"]]
            
            return {
                "total_incidents": len(incidents),
                "high_severity_count": len(high_severity),
                "days_checked": days_back,
                "incidents": [
                    {
                        "id": i["incident_id"],
                        "type": i["incident_type"],
                        "location": i["location"],
                        "severity": i["severity"],
                        "date": str(i["reported_at"]),
                        "status": i["status"]
                    }
                    for i in incidents[:10]
                ]
            }
        except Exception as e:
            logger.error(f"Incident check error: {e}")
            return {"error": str(e), "total_incidents": 0}
    
    # ========== SCHEDULE TOOLS ==========
    
    def check_schedule_conflicts(self, location: str, 
                                 requested_date: str,
                                 duration_days: int = 1) -> Dict:
        """
        Check for schedule conflicts.
        
        Returns: {
            "has_conflicts": bool,
            "scheduled_activities": [...]
        }
        """
        try:
            schedule = self.queries.get_work_schedule(location, days_ahead=30)
            
            # Filter for requested date
            requested_activities = [
                s for s in schedule 
                if str(s["scheduled_date"]) == requested_date
            ]
            
            return {
                "requested_date": requested_date,
                "location": location,
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
    
    # ========== UTILITY TOOLS ==========
    
    def get_active_projects_count(self) -> Dict:
        """Simple count of active projects"""
        try:
            projects = self.queries.get_active_projects()
            return {
                "count": len(projects),
                "max_allowed": settings.MAX_CONCURRENT_PROJECTS,
                "capacity_available": len(projects) < settings.MAX_CONCURRENT_PROJECTS
            }
        except Exception as e:
            return {"error": str(e), "count": 0}
    
    def estimate_project_duration(self, project_type: str, scope: str) -> Dict:
        """Estimate project duration (simplified)"""
        # Simple heuristic-based estimation
        base_durations = {
            "road_construction": 90,
            "bridge_construction": 180,
            "building_construction": 120,
            "drainage": 60,
            "maintenance": 30,
            "inspection": 7
        }
        
        duration = base_durations.get(project_type, 60)
        
        return {
            "project_type": project_type,
            "estimated_days": duration,
            "confidence": 0.7
        }


def create_tools(db: DatabaseConnection, queries: EngineeringDepartmentQueries) -> EngineeringDepartmentTools:
    """Factory function to create tools instance"""
    return EngineeringDepartmentTools(db, queries)
