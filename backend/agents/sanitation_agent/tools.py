"""
PHASE 7: Tool Execution

Tools that gather facts from the sanitation system.
Each tool returns structured data.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

from .database import DatabaseConnection, SanitationDepartmentQueries

logger = logging.getLogger(__name__)


class SanitationDepartmentTools:
    """Toolkit for Sanitation Department Agent"""
    
    def __init__(self, db: DatabaseConnection, queries: SanitationDepartmentQueries):
        self.db = db
        self.queries = queries
    
    # ========== TRUCK AVAILABILITY TOOLS ==========
    
    def check_truck_availability(self,
                                 location: str = None,
                                 truck_type: str = None,
                                 date: str = None,
                                 min_fuel_percent: int = None,
                                 **kwargs) -> Dict:
        """
        Check if trucks are available for route assignment.
        
        NOTE: Sanitation trucks table does not exist in schema.
        Returns placeholder data.
        """
        # There is no trucks table in schema; use workers as proxy for available staff
        logger.info("Using workers table as proxy for truck/crew availability")
        try:
            # worker 'role' can be passed via truck_type (e.g., driver, operator)
            workers = self.queries.get_available_workers(role=truck_type) if truck_type else self.queries.get_available_workers()

            # If location is provided and workers have a location field, filter
            if location:
                workers = [w for w in workers if location.lower() in (w.get("location") or "").lower()]

            available_count = len(workers)

            return {
                "available_count": available_count,
                "sufficient": available_count > 0,
                "workers": workers,
                "note": "Using workers table as proxy for crew availability"
            }
        except Exception as e:
            logger.error(f"Truck availability error: {e}")
            return {"error": str(e), "available_count": 0}
    
    # ========== ROUTE CAPACITY TOOLS ==========
    
    def check_route_capacity(self, route_id: str = None, zone: str = None) -> Dict:
        """
        Check route capacity and workload.
        
        NOTE: Routes table does not exist in schema.
        Uses work_schedules and projects as proxy.
        """
        logger.warning("⚠ Sanitation routes table does not exist - using work schedules")
        
        try:
            # Use work schedules as proxy for routes
            schedules = self.queries.get_work_schedule(location=zone, days_ahead=7)
            
            return {
                "total_routes": len(schedules),
                "overloaded_routes": 0,
                "avg_utilization_percent": 0,
                "routes": [
                    {
                        "id": str(s.get("schedule_id", "")),
                        "name": s.get("activity_type", "Unknown"),
                        "zone": s.get("location", zone or "Unknown"),
                        "type": s.get("activity_type", "collection"),
                        "frequency": "scheduled",
                        "status": s.get("status", "active")
                    }
                    for s in schedules[:10]
                ],
                "note": "Using work_schedules as routes proxy - sanitation_routes table does not exist"
            }
        except Exception as e:
            logger.error(f"Route capacity check error: {e}", exc_info=True)
            return {"error": str(e), "total_routes": 0}
    
    # ========== LANDFILL CAPACITY TOOLS ==========
    
    def check_landfill_capacity(self, min_capacity_percent: int = None, **kwargs) -> Dict:
        """
        Check landfill capacity and availability.
        
        NOTE: Landfills table does not exist in schema.
        Returns placeholder.
        """
        logger.warning("⚠ Landfills table does not exist in schema - returning placeholder")
        return {
            "total_landfills": 0,
            "operational": 0,
            "at_capacity": 0,
            "critical_alert": False,
            "avg_utilization_percent": 0,
            "landfills": [],
            "note": "Schema does not include landfills table"
        }
    
    # ========== COLLECTION DELAY ASSESSMENT ==========
    
    def assess_collection_delay(self, location: str = None, zone: str = None) -> Dict:
        """
        Assess potential delays in collection schedule.
        
        Uses available data from incidents and work schedules.
        """
        logger.warning("⚠ Using incidents and schedules - bins/complaints tables unavailable")
        
        try:
            # Check schedule
            schedules = self.queries.get_work_schedule(location=zone or location, days_ahead=3)
            delayed = [s for s in schedules if s.get("status") == "delayed"]
            
            # Check incidents as proxy for issues
            incidents = self.queries.get_recent_incidents(location=zone or location, days=7)
            
            delay_factors = []
            if len(delayed) > 0:
                delay_factors.append(f"{len(delayed)} delayed schedules")
            if len(incidents) > 3:
                delay_factors.append(f"{len(incidents)} recent incidents")
            
            # Determine risk level
            if len(delay_factors) >= 2 or len(incidents) > 5:
                risk = "high"
            elif len(delay_factors) >= 1 or len(incidents) > 2:
                risk = "medium"
            else:
                risk = "low"
            
            return {
                "delay_risk": risk,
                "factors": delay_factors,
                "delayed_schedules": len(delayed),
                "recent_incidents": len(incidents),
                "note": "Using incidents/schedules - bins/complaints tables unavailable"
            }
        except Exception as e:
            logger.error(f"Collection delay assessment error: {e}", exc_info=True)
            return {"error": str(e), "delay_risk": "unknown"}
    
    # ========== EQUIPMENT STATUS TOOLS ==========
    
    def check_equipment_status(self, truck_id: str = None, equipment_type: str = None, **kwargs) -> Dict:
        """
        Check truck and equipment condition.
        
        NOTE: Trucks table does not exist in schema.
        Returns placeholder.
        """
        logger.warning("⚠ Trucks table does not exist in schema - returning placeholder")
        # Attempt to infer equipment status from work schedules/equipment assignments
        try:
            schedules = self.queries.get_work_schedule(days_ahead=7)
            maintenance_needed = []
            issues = []
            trucks_seen = set()

            for s in schedules:
                eq = s.get("equipment_assigned")
                if not eq:
                    continue
                # equipment_assigned can be a list or a comma-separated string
                if isinstance(eq, str):
                    eq_list = [e.strip() for e in eq.split(",") if e.strip()]
                elif isinstance(eq, list):
                    eq_list = eq
                else:
                    eq_list = [str(eq)]

                for truck_ref in eq_list:
                    truck_num = str(truck_ref)
                    trucks_seen.add(truck_num)
                    # no detailed condition info available; flag if id present
                    # placeholder heuristic: if 'old' in id or numeric id above a threshold, mark for maintenance
                    if "old" in truck_num.lower():
                        maintenance_needed.append(truck_num)
                        issues.append({"truck": truck_num, "issues": ["age_suspected"]})

            if not trucks_seen:
                return {
                    "condition_summary": "unknown",
                    "maintenance_needed": False,
                    "issues": [],
                    "note": "No equipment assignment data available in work_schedules"
                }

            # determine coarse condition
            if len(maintenance_needed) > len(trucks_seen) * 0.5:
                condition = "poor"
            elif len(maintenance_needed) > 0:
                condition = "fair"
            else:
                condition = "good"

            return {
                "condition_summary": condition,
                "maintenance_needed": len(maintenance_needed) > 0,
                "trucks_needing_maintenance": list(maintenance_needed),
                "issues": issues,
                "tracked_trucks": list(trucks_seen)
            }
        except Exception as e:
            logger.error(f"Equipment status check error: {e}")
            return {"error": str(e), "condition_summary": "unknown"}
    
    # ========== COMPLAINT HISTORY TOOLS ==========
    
    def get_complaint_history(self, location: str = None, zone: str = None, days: int = 30) -> Dict:
        """
        Get complaint history for location/zone.
        
        Returns: {
            "total_complaints": int,
            "by_type": {...},
            "unresolved": int,
            "avg_resolution_hours": float
        }
        """
        try:
            # queries may expose recent complaints or use incidents as a proxy
            if hasattr(self.queries, "get_recent_complaints"):
                complaints = self.queries.get_recent_complaints(zone=zone, days=days)
            else:
                complaints = self.queries.get_recent_incidents(location=zone, days=days)
            
            # Filter by location if specified
            if location:
                complaints = [c for c in complaints if location.lower() in c.get("location", "").lower()]
            
            # Group by type
            by_type = {}
            for c in complaints:
                ctype = c.get("complaint_type", "other")
                by_type[ctype] = by_type.get(ctype, 0) + 1
            
            # Count unresolved
            unresolved = [c for c in complaints if c.get("status") not in ["resolved", "closed"]]
            
            return {
                "total_complaints": len(complaints),
                "by_type": by_type,
                "unresolved": len(unresolved),
                "high_priority": len([c for c in complaints if c.get("priority") in ["high", "urgent"]]),
                "recent_complaints": [
                    {
                        "type": c["complaint_type"],
                        "location": c["location"],
                        "priority": c["priority"],
                        "status": c["status"],
                        "reported": c["reported_date"].isoformat() if isinstance(c["reported_date"], datetime) else str(c["reported_date"])
                    }
                    for c in complaints[:5]
                ]
            }
        except Exception as e:
            logger.error(f"Complaint history error: {e}")
            return {"error": str(e), "total_complaints": 0}
    
    # ========== RECYCLING CENTER TOOLS ==========
    
    def check_recycling_center_availability(self) -> Dict:
        """
        Check recycling center capacity and availability.
        
        Returns: {
            "centers": [...],
            "at_capacity": int,
            "available": int
        }
        """
        # Recycling centers table/query not available in current sanitation queries
        logger.warning("⚠ Recycling centers query not available - returning placeholder")
        return {
            "total_centers": 0,
            "available": 0,
            "at_capacity": 0,
            "centers": [],
            "note": "No recycling center data available in queries"
        }
    
    # ========== WASTE VOLUME ESTIMATION ==========
    
    def estimate_waste_volume(self, location: str = None, route_id: str = None, date: str = None, **kwargs) -> Dict:
        """
        Estimate waste volume for zone on given date.
        
        Returns: {
            "estimated_tons": float,
            "peak_capacity_tons": float,
            "utilization_percent": float
        }
        """
        try:
            # No active_routes query available - use work schedules as a proxy
            schedules = self.queries.get_work_schedule(location=location, days_ahead=7)

            # crude estimation: assume average 0.5 tons per scheduled route
            total_avg = sum(0.5 for _ in schedules)
            # peak capacity estimate: assume 1.0 tons per route
            total_peak = sum(1.0 for _ in schedules) if schedules else 1.0

            utilization = (total_avg / total_peak * 100) if total_peak > 0 else 0

            return {
                "estimated_tons": round(total_avg, 2),
                "peak_capacity_tons": round(total_peak, 2),
                "utilization_percent": round(utilization, 2),
                "zone": zone,
                "routes_included": len(schedules)
            }
        except Exception as e:
            logger.error(f"Waste volume estimation error: {e}")
            return {"error": str(e), "estimated_tons": 0}
    
    # ========== BUDGET CHECK ==========
    
    def check_budget_availability(self, estimated_cost: Optional[float] = None, **kwargs) -> Dict:
        """
        Check if budget is available for operation.
        
        Returns: {
            "available": bool,
            "remaining": float,
            "sufficient": bool
        }
        """
        try:
            budget = self.queries.get_budget_status()
            
            if not budget:
                return {"available": False, "remaining": 0, "sufficient": False}

            # Normalize values safely
            remaining = float(budget.get("remaining") or 0)
            est_cost = float(estimated_cost or 0)
            sufficient = remaining >= est_cost
            
            return {
                "available": remaining > 0,
                "remaining": remaining,
                "sufficient": sufficient,
                "total_budget": float(budget.get("total_budget") or 0),
                "spent": float(budget.get("spent") or 0),
                "utilization_percent": float(budget.get("utilization_percent") or 0)
            }
        except Exception as e:
            logger.error(f"Budget check error: {e}")
            return {"available": False, "remaining": 0, "sufficient": False}


# Helper function to create tools instance
def create_tools(db: DatabaseConnection, queries: SanitationDepartmentQueries) -> SanitationDepartmentTools:
    """Create tools instance"""
    return SanitationDepartmentTools(db, queries)
