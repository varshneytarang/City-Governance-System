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
                                 zone: str = None,
                                 truck_type: str = None,
                                 date: str = None) -> Dict:
        """
        Check if trucks are available for route assignment.
        
        Returns: {
            "available_count": int,
            "total_trucks": int,
            "trucks": [{id, number, type, capacity, fuel_percent, condition}],
            "sufficient": bool
        }
        """
        try:
            trucks = self.queries.get_available_trucks(truck_type=truck_type)
            
            # Filter by fuel level (must be > 25%)
            operational_trucks = [
                t for t in trucks 
                if float(t.get("fuel_level_percent", 0)) > 25
            ]
            
            return {
                "available_count": len(operational_trucks),
                "total_trucks": len(trucks),
                "sufficient": len(operational_trucks) > 0,
                "trucks": [
                    {
                        "id": str(t["truck_id"]),
                        "number": t["truck_number"],
                        "type": t["truck_type"],
                        "capacity_tons": float(t["capacity_tons"]),
                        "fuel_percent": float(t.get("fuel_level_percent", 0)),
                        "condition": t["engine_condition"]
                    }
                    for t in operational_trucks[:5]  # Return top 5
                ]
            }
        except Exception as e:
            logger.error(f"Truck availability check error: {e}")
            return {"error": str(e), "available_count": 0, "sufficient": False}
    
    # ========== ROUTE CAPACITY TOOLS ==========
    
    def check_route_capacity(self, route_id: str = None, zone: str = None) -> Dict:
        """
        Check route capacity and workload.
        
        Returns: {
            "routes": [...],
            "total_routes": int,
            "overloaded_routes": int,
            "avg_utilization_percent": float
        }
        """
        try:
            routes = self.queries.get_active_routes(zone=zone)
            
            overloaded = [
                r for r in routes 
                if float(r.get("avg_waste_volume_tons", 0)) > float(r.get("peak_waste_volume_tons", 0)) * 0.9
            ]
            
            total_volume = sum(float(r.get("avg_waste_volume_tons", 0)) for r in routes)
            total_capacity = sum(float(r.get("peak_waste_volume_tons", 1)) for r in routes)
            avg_utilization = (total_volume / total_capacity * 100) if total_capacity > 0 else 0
            
            return {
                "total_routes": len(routes),
                "overloaded_routes": len(overloaded),
                "avg_utilization_percent": round(avg_utilization, 2),
                "routes": [
                    {
                        "id": str(r["route_id"]),
                        "name": r["route_name"],
                        "zone": r["zone"],
                        "type": r["route_type"],
                        "frequency": r["service_frequency"],
                        "avg_volume_tons": float(r["avg_waste_volume_tons"]),
                        "capacity_tons": float(r["peak_waste_volume_tons"])
                    }
                    for r in routes[:10]
                ]
            }
        except Exception as e:
            logger.error(f"Route capacity check error: {e}")
            return {"error": str(e), "total_routes": 0}
    
    # ========== LANDFILL CAPACITY TOOLS ==========
    
    def check_landfill_capacity(self) -> Dict:
        """
        Check landfill capacity and availability.
        
        Returns: {
            "landfills": [...],
            "total_landfills": int,
            "at_capacity": int,
            "avg_utilization_percent": float,
            "critical_alert": bool
        }
        """
        try:
            landfills = self.queries.get_landfill_status()
            
            at_capacity = [
                lf for lf in landfills 
                if float(lf.get("utilization_percent", 0)) >= 90
            ]
            
            critical = [
                lf for lf in landfills 
                if float(lf.get("utilization_percent", 0)) >= 95
            ]
            
            avg_util = sum(float(lf.get("utilization_percent", 0)) for lf in landfills) / len(landfills) if landfills else 0
            
            return {
                "total_landfills": len(landfills),
                "operational": len([lf for lf in landfills if lf["operational_status"] == "active"]),
                "at_capacity": len(at_capacity),
                "critical_alert": len(critical) > 0,
                "avg_utilization_percent": round(avg_util, 2),
                "landfills": [
                    {
                        "id": str(lf["landfill_id"]),
                        "name": lf["name"],
                        "location": lf["location"],
                        "utilization_percent": float(lf["utilization_percent"]),
                        "status": lf["operational_status"],
                        "daily_limit_tons": float(lf.get("daily_intake_limit_tons", 0)),
                        "distance_km": float(lf.get("distance_from_city_km", 0))
                    }
                    for lf in landfills
                ]
            }
        except Exception as e:
            logger.error(f"Landfill capacity check error: {e}")
            return {"error": str(e), "total_landfills": 0, "critical_alert": True}
    
    # ========== COLLECTION DELAY ASSESSMENT ==========
    
    def assess_collection_delay(self, location: str = None, zone: str = None) -> Dict:
        """
        Assess potential delays in collection schedule.
        
        Returns: {
            "delay_risk": "low|medium|high",
            "factors": [...],
            "affected_locations": int
        }
        """
        try:
            # Check bins status
            bins = self.queries.get_bin_status(zone=zone, location=location)
            full_bins = [b for b in bins if float(b.get("current_fill_percent", 0)) >= 90]
            
            # Check schedule
            schedules = self.queries.get_collection_schedule(zone=zone, days_ahead=3)
            delayed = [s for s in schedules if s.get("status") == "delayed"]
            
            # Check complaints
            complaints = self.queries.get_recent_complaints(zone=zone, days=7)
            missed_collections = [c for c in complaints if c["complaint_type"] == "missed_collection"]
            
            delay_factors = []
            if len(full_bins) > 5:
                delay_factors.append(f"{len(full_bins)} bins at/near capacity")
            if len(delayed) > 0:
                delay_factors.append(f"{len(delayed)} delayed schedules")
            if len(missed_collections) > 3:
                delay_factors.append(f"{len(missed_collections)} missed collection complaints")
            
            # Determine risk level
            if len(delay_factors) >= 3 or len(full_bins) > 10:
                risk = "high"
            elif len(delay_factors) >= 2 or len(full_bins) > 5:
                risk = "medium"
            else:
                risk = "low"
            
            return {
                "delay_risk": risk,
                "factors": delay_factors,
                "affected_bins": len(full_bins),
                "delayed_schedules": len(delayed),
                "recent_complaints": len(missed_collections)
            }
        except Exception as e:
            logger.error(f"Collection delay assessment error: {e}")
            return {"error": str(e), "delay_risk": "unknown"}
    
    # ========== EQUIPMENT STATUS TOOLS ==========
    
    def check_equipment_status(self, truck_id: str = None) -> Dict:
        """
        Check truck and equipment condition.
        
        Returns: {
            "condition_summary": "good|fair|poor",
            "maintenance_needed": bool,
            "issues": [...]
        }
        """
        try:
            trucks = self.queries.get_available_trucks()
            
            if truck_id:
                trucks = [t for t in trucks if str(t["truck_id"]) == truck_id]
            
            issues = []
            maintenance_needed = []
            
            for truck in trucks:
                truck_issues = []
                
                # Check fuel
                fuel = float(truck.get("fuel_level_percent", 0))
                if fuel < 25:
                    truck_issues.append(f"Low fuel: {fuel}%")
                
                # Check conditions
                if truck.get("engine_condition") in ["poor", "critical"]:
                    truck_issues.append(f"Engine condition: {truck['engine_condition']}")
                    maintenance_needed.append(truck["truck_number"])
                
                if truck.get("compactor_condition") in ["poor", "critical"]:
                    truck_issues.append(f"Compactor condition: {truck['compactor_condition']}")
                    maintenance_needed.append(truck["truck_number"])
                
                if truck_issues:
                    issues.append({
                        "truck": truck["truck_number"],
                        "issues": truck_issues
                    })
            
            # Overall condition
            if len(maintenance_needed) > len(trucks) * 0.5:
                condition = "poor"
            elif len(maintenance_needed) > 0:
                condition = "fair"
            else:
                condition = "good"
            
            return {
                "condition_summary": condition,
                "maintenance_needed": len(maintenance_needed) > 0,
                "trucks_needing_maintenance": list(set(maintenance_needed)),
                "issues": issues
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
            complaints = self.queries.get_recent_complaints(zone=zone, days=days)
            
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
        try:
            centers = self.queries.get_recycling_centers()
            
            at_capacity = [c for c in centers if c.get("operational_status") == "at_capacity"]
            available = [c for c in centers if c.get("operational_status") == "active"]
            
            return {
                "total_centers": len(centers),
                "available": len(available),
                "at_capacity": len(at_capacity),
                "centers": [
                    {
                        "id": str(c["center_id"]),
                        "name": c["name"],
                        "location": c["location"],
                        "capacity_per_day": float(c.get("processing_capacity_tons_per_day", 0)),
                        "current_load": float(c.get("current_load_tons", 0)),
                        "status": c["operational_status"],
                        "efficiency": float(c.get("processing_efficiency_percent", 0))
                    }
                    for c in centers
                ]
            }
        except Exception as e:
            logger.error(f"Recycling center check error: {e}")
            return {"error": str(e), "total_centers": 0}
    
    # ========== WASTE VOLUME ESTIMATION ==========
    
    def estimate_waste_volume(self, zone: str, date: str = None) -> Dict:
        """
        Estimate waste volume for zone on given date.
        
        Returns: {
            "estimated_tons": float,
            "peak_capacity_tons": float,
            "utilization_percent": float
        }
        """
        try:
            routes = self.queries.get_active_routes(zone=zone)
            
            total_avg = sum(float(r.get("avg_waste_volume_tons", 0)) for r in routes)
            total_peak = sum(float(r.get("peak_waste_volume_tons", 1)) for r in routes)
            
            utilization = (total_avg / total_peak * 100) if total_peak > 0 else 0
            
            return {
                "estimated_tons": round(total_avg, 2),
                "peak_capacity_tons": round(total_peak, 2),
                "utilization_percent": round(utilization, 2),
                "zone": zone,
                "routes_included": len(routes)
            }
        except Exception as e:
            logger.error(f"Waste volume estimation error: {e}")
            return {"error": str(e), "estimated_tons": 0}
    
    # ========== BUDGET CHECK ==========
    
    def check_budget_availability(self, estimated_cost: float = 0) -> Dict:
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
            
            remaining = float(budget.get("remaining", 0))
            sufficient = remaining >= estimated_cost
            
            return {
                "available": remaining > 0,
                "remaining": remaining,
                "sufficient": sufficient,
                "total_budget": float(budget.get("total_budget", 0)),
                "spent": float(budget.get("spent", 0)),
                "utilization_percent": float(budget.get("utilization_percent", 0))
            }
        except Exception as e:
            logger.error(f"Budget check error: {e}")
            return {"available": False, "remaining": 0, "sufficient": False}


# Helper function to create tools instance
def create_tools(db: DatabaseConnection, queries: SanitationDepartmentQueries) -> SanitationDepartmentTools:
    """Create tools instance"""
    return SanitationDepartmentTools(db, queries)
