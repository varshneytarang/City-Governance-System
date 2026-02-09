"""
Fire Department Tools

Operational tools for checking trucks, firefighters, equipment, hydrants, etc.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from .database import FireDepartmentQueries

logger = logging.getLogger(__name__)


class FireDepartmentTools:
    """Fire Department operational tools"""
    
    def __init__(self, queries: FireDepartmentQueries):
        self.queries = queries
    
    def check_truck_availability(self, station_id: int = None, 
                                 truck_type: str = None,
                                 min_fuel_percent: int = 30) -> Dict[str, Any]:
        """
        Check availability of fire trucks.
        
        NOTE: Fire department has no dedicated trucks table in schema.
        Returns placeholder data.
        """
        
        logger.info(f"Checking truck availability (station={station_id}, type={truck_type})")
        logger.warning("⚠ Fire trucks table does not exist in schema - returning placeholder")
        
        # No trucks table exists - return placeholder indicating availability is unknown
        return {
            "available_count": 0,
            "trucks": [],
            "sufficient": False,
            "details": "Fire trucks data not available in current schema",
            "note": "Schema does not include fire_trucks table"
        }
    
    def check_firefighter_availability(self, station_id: int = None,
                                      required_count: int = 3,
                                      min_rank: str = None) -> Dict[str, Any]:
        """
        Check availability of firefighters.
        
        Uses workers table with department='fire' filter.
        """
        
        logger.info(f"Checking firefighter availability (station={station_id}, required={required_count})")
        
        try:
            # Use get_available_workers - firefighters are stored as workers with department='fire'
            firefighters = self.queries.get_available_workers(role=min_rank)
            
            available_count = len(firefighters)
            sufficient = available_count >= required_count
            
            # Parse certifications - handle both string and list formats
            certifications = {}
            for ff in firefighters:
                cert_data = ff.get('certifications', '')
                
                # Handle different certification formats
                if isinstance(cert_data, list):
                    certs = cert_data
                elif isinstance(cert_data, str) and cert_data:
                    certs = [c.strip() for c in cert_data.split(',')]
                else:
                    certs = []
                
                for cert in certs:
                    if cert:
                        certifications[cert] = certifications.get(cert, 0) + 1
            
            return {
                "available_count": available_count,
                "required_count": required_count,
                "sufficient": sufficient,
                "firefighters": firefighters,
                "certifications_available": certifications,
                "details": f"{available_count}/{required_count} firefighters available"
            }
        
        except Exception as e:
            logger.error(f"Error checking firefighter availability: {e}", exc_info=True)
            return {
                "available_count": 0,
                "required_count": required_count,
                "sufficient": False,
                "error": str(e)
            }
    
    def check_equipment_status(self, station_id: int, 
                               equipment_type: str = None) -> Dict[str, Any]:
        """
        Check status of fire equipment at a station.
        
        NOTE: Equipment table does not exist in schema.
        Returns placeholder.
        """
        
        logger.info(f"Checking equipment status (station={station_id}, type={equipment_type})")
        logger.warning("⚠ Fire equipment table does not exist in schema - returning placeholder")
        
        # No equipment table exists
        return {
            "equipment_count": 0,
            "equipment": [],
            "overall_condition": "unknown",
            "note": "Schema does not include fire_equipment table",
            "details": "Equipment data not available in current schema"
        }
    
    def assess_response_time(self, location: str, zone: str) -> Dict[str, Any]:
        """
        Assess estimated response time to a location.
        
        Based on station coverage and average response times.
        """
        
        logger.info(f"Assessing response time to {location} ({zone})")
        
        try:
            # Find closest station covering the zone
            station = self.queries.get_fire_station_by_zone(zone)
            
            if not station:
                return {
                    "estimated_minutes": 999,
                    "status": "no_coverage",
                    "details": f"No operational station covers {zone}"
                }
            
            avg_response = station.get('response_time_avg_minutes', 15)
            
            # Check if station has available trucks
            trucks = self.queries.get_available_trucks(station_id=station['station_id'])
            
            if not trucks:
                return {
                    "estimated_minutes": avg_response + 5,  # Delay if no trucks
                    "status": "delayed",
                    "station": station['station_name'],
                    "details": f"No available trucks at {station['station_name']}, expect delays"
                }
            
            return {
                "estimated_minutes": avg_response,
                "status": "normal",
                "station": station['station_name'],
                "available_trucks": len(trucks),
                "details": f"~{avg_response} min from {station['station_name']}"
            }
        
        except Exception as e:
            logger.error(f"Error assessing response time: {e}")
            return {
                "estimated_minutes": 999,
                "status": "error",
                "error": str(e)
            }
    
    def check_hydrant_status(self, zone: str, 
                            min_pressure_psi: int = 50,
                            min_flow_gpm: int = 1000) -> Dict[str, Any]:
        """
        Check hydrant availability and status in a zone.
        
        NOTE: Hydrants table does not exist in schema.
        Returns placeholder.
        """
        
        logger.info(f"Checking hydrants in {zone}")
        logger.warning("⚠ Fire hydrants table does not exist in schema - returning placeholder")
        
        # No hydrants table exists
        return {
            "total_hydrants": 0,
            "adequate_hydrants": 0,
            "hydrants": [],
            "sufficient": False,
            "note": "Schema does not include fire_hydrants table",
            "details": "Hydrant data not available in current schema"
        }
    
    def get_incident_history(self, location: str = None, 
                            days: int = 90,
                            severity: str = None) -> Dict[str, Any]:
        """
        Get historical incident data for a location or overall.
        
        Returns incident patterns and trends.
        """
        
        logger.info(f"Retrieving incident history (location={location}, days={days})")
        
        try:
            if location:
                incidents = self.queries.get_incidents_by_location(location, days=days)
            else:
                incidents = self.queries.get_recent_incidents(days=days, severity=severity)
            
            # Analyze patterns
            severity_counts = {}
            incident_types = {}
            total_casualties = 0
            total_injuries = 0
            
            for inc in incidents:
                sev = inc.get('severity', 'unknown')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                inc_type = inc.get('incident_type', 'unknown')
                incident_types[inc_type] = incident_types.get(inc_type, 0) + 1
                
                total_casualties += inc.get('casualties', 0)
                total_injuries += inc.get('injuries', 0)
            
            return {
                "total_incidents": len(incidents),
                "incidents": incidents,
                "severity_breakdown": severity_counts,
                "incident_types": incident_types,
                "total_casualties": total_casualties,
                "total_injuries": total_injuries,
                "high_risk_location": severity_counts.get('major', 0) + severity_counts.get('catastrophic', 0) > 0,
                "details": f"{len(incidents)} incidents in last {days} days"
            }
        
        except Exception as e:
            logger.error(f"Error retrieving incident history: {e}")
            return {
                "total_incidents": 0,
                "error": str(e)
            }
    
    def estimate_resource_needs(self, incident_type: str,
                                severity: str = "moderate") -> Dict[str, Any]:
        """
        Estimate resource needs for an incident type.
        
        Based on incident type and severity.
        """
        
        logger.info(f"Estimating resources for {incident_type} ({severity})")
        
        # Resource estimation matrix
        resource_matrix = {
            "structure_fire": {
                "minor": {"trucks": 1, "firefighters": 4, "equipment": ["scba", "hose"]},
                "moderate": {"trucks": 2, "firefighters": 8, "equipment": ["scba", "hose", "ladder"]},
                "major": {"trucks": 3, "firefighters": 12, "equipment": ["scba", "hose", "ladder", "thermal_camera"]},
                "catastrophic": {"trucks": 5, "firefighters": 20, "equipment": ["scba", "hose", "ladder", "thermal_camera", "jaws_of_life"]}
            },
            "vehicle_fire": {
                "minor": {"trucks": 1, "firefighters": 3, "equipment": ["scba", "hose"]},
                "moderate": {"trucks": 1, "firefighters": 4, "equipment": ["scba", "hose"]},
                "major": {"trucks": 2, "firefighters": 6, "equipment": ["scba", "hose", "jaws_of_life"]},
                "catastrophic": {"trucks": 2, "firefighters": 8, "equipment": ["scba", "hose", "jaws_of_life"]}
            },
            "hazmat": {
                "minor": {"trucks": 1, "firefighters": 4, "equipment": ["scba", "hazmat_suits"]},
                "moderate": {"trucks": 2, "firefighters": 6, "equipment": ["scba", "hazmat_suits"]},
                "major": {"trucks": 3, "firefighters": 10, "equipment": ["scba", "hazmat_suits", "decon_equipment"]},
                "catastrophic": {"trucks": 4, "firefighters": 15, "equipment": ["scba", "hazmat_suits", "decon_equipment", "air_monitoring"]}
            },
            "rescue": {
                "minor": {"trucks": 1, "firefighters": 3, "equipment": ["rescue_tools"]},
                "moderate": {"trucks": 1, "firefighters": 5, "equipment": ["rescue_tools", "jaws_of_life"]},
                "major": {"trucks": 2, "firefighters": 8, "equipment": ["rescue_tools", "jaws_of_life", "rope_equipment"]},
                "catastrophic": {"trucks": 3, "firefighters": 12, "equipment": ["rescue_tools", "jaws_of_life", "rope_equipment", "heavy_rescue"]}
            },
            "medical": {
                "minor": {"trucks": 1, "firefighters": 2, "equipment": ["medical_kit"]},
                "moderate": {"trucks": 1, "firefighters": 3, "equipment": ["medical_kit", "aed"]},
                "major": {"trucks": 1, "firefighters": 4, "equipment": ["medical_kit", "aed", "backboard"]},
                "catastrophic": {"trucks": 2, "firefighters": 6, "equipment": ["medical_kit", "aed", "backboard", "advanced_life_support"]}
            }
        }
        
        # Get estimate
        estimates = resource_matrix.get(incident_type, {})
        estimate = estimates.get(severity, estimates.get("moderate", {}))
        
        if not estimate:
            # Default fallback
            estimate = {"trucks": 1, "firefighters": 4, "equipment": ["scba", "hose"]}
        
        return {
            "incident_type": incident_type,
            "severity": severity,
            "estimated_trucks": estimate.get("trucks", 1),
            "estimated_firefighters": estimate.get("firefighters", 4),
            "required_equipment": estimate.get("equipment", []),
            "details": f"{estimate.get('trucks', 1)} trucks, {estimate.get('firefighters', 4)} firefighters for {severity} {incident_type}"
        }
    
    def check_station_capacity(self, station_id: int) -> Dict[str, Any]:
        """
        Check station capacity and staffing levels.
        
        Returns current vs. maximum capacity.
        """
        
        logger.info(f"Checking station {station_id} capacity")
        
        try:
            stations = self.queries.get_fire_stations()
            station = next((s for s in stations if s['station_id'] == station_id), None)
            
            if not station:
                return {
                    "error": f"Station {station_id} not found",
                    "at_capacity": True
                }
            
            capacity = station.get('capacity', 20)
            current = station.get('current_staffing', 0)
            utilization = (current / capacity * 100) if capacity > 0 else 0
            
            return {
                "station_id": station_id,
                "station_name": station.get('station_name'),
                "capacity": capacity,
                "current_staffing": current,
                "available_space": capacity - current,
                "utilization_percent": round(utilization, 2),
                "at_capacity": utilization >= 90,
                "details": f"{current}/{capacity} capacity ({utilization:.0f}%)"
            }
        
        except Exception as e:
            logger.error(f"Error checking station capacity: {e}")
            return {
                "error": str(e),
                "at_capacity": True
            }
    
    def check_budget_availability(self, estimated_cost: float = None) -> Dict[str, Any]:
        """
        Check department budget availability.
        
        Returns budget status and whether cost is within budget.
        Uses department_budgets table.
        """
        
        logger.info(f"Checking budget (estimated cost: {estimated_cost})")
        
        try:
            budget = self.queries.get_budget_status()
            
            if not budget:
                return {
                    "available": 0,
                    "affordable": False,
                    "details": "Budget information not available",
                    "note": "No budget record found for current month"
                }
            
            # Use 'remaining' field from actual schema
            available = float(budget.get('remaining', 0))
            utilization = float(budget.get('utilization_percent', 0))
            total = float(budget.get('total_budget', 0))
            spent = float(budget.get('spent', 0))
            
            if estimated_cost:
                affordable = available >= estimated_cost
                remaining_after = available - estimated_cost if affordable else 0
            else:
                affordable = True
                remaining_after = available
            
            return {
                "total_budget": total,
                "spent": spent,
                "available": available,
                "utilization_percent": utilization,
                "estimated_cost": estimated_cost or 0,
                "affordable": affordable,
                "remaining_after_expense": remaining_after,
                "budget_constraint": utilization > 90,
                "details": f"${available:,.0f} available ({utilization:.1f}% utilized)"
            }
        
        except Exception as e:
            logger.error(f"Error checking budget: {e}", exc_info=True)
            return {
                "available": 0,
                "affordable": False,
                "error": str(e)
            }


def create_tools(db, queries: FireDepartmentQueries):
    """Create tools instance"""
    return FireDepartmentTools(queries)
