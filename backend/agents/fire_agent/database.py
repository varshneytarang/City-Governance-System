"""
Fire Department Database Queries

All database queries for fire stations, trucks, firefighters, equipment, etc.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

# Reuse database connection from water_agent
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from agents.water_agent.database import DatabaseConnection

logger = logging.getLogger(__name__)


class FireDepartmentQueries:
    """Fire Department database query methods"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    def get_fire_stations(self, status: str = None) -> List[Dict]:
        """Get fire stations, optionally filtered by status"""
        
        query = "SELECT * FROM fire_stations"
        params = ()
        
        if status:
            query += " WHERE status = %s"
            params = (status,)
        
        query += " ORDER BY station_id"
        
        return self.db.execute_query(query, params)
    
    def get_fire_station_by_zone(self, zone: str) -> Optional[Dict]:
        """Get closest fire station covering a zone"""
        
        query = """
            SELECT * FROM fire_stations
            WHERE %s = ANY(coverage_zones)
            AND status = 'operational'
            ORDER BY response_time_avg_minutes ASC
            LIMIT 1
        """
        
        results = self.db.execute_query(query, (zone,))
        return results[0] if results else None
    
    def get_available_trucks(self, station_id: int = None, truck_type: str = None, 
                            min_fuel_percent: int = 30) -> List[Dict]:
        """Get available trucks, optionally filtered by station and type"""
        
        query = """
            SELECT * FROM fire_trucks
            WHERE status = 'available'
            AND fuel_percent >= %s
            AND equipment_check_status = 'passed'
        """
        params = [min_fuel_percent]
        
        if station_id:
            query += " AND station_id = %s"
            params.append(station_id)
        
        if truck_type:
            query += " AND truck_type = %s"
            params.append(truck_type)
        
        query += " ORDER BY fuel_percent DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_truck_by_id(self, truck_id: int) -> Optional[Dict]:
        """Get truck details by ID"""
        
        query = "SELECT * FROM fire_trucks WHERE truck_id = %s"
        results = self.db.execute_query(query, (truck_id,))
        return results[0] if results else None
    
    def get_available_firefighters(self, station_id: int = None, 
                                  min_rank: str = None) -> List[Dict]:
        """Get available firefighters"""
        
        query = """
            SELECT * FROM firefighters
            WHERE status IN ('on_duty', 'on_call')
        """
        params = []
        
        if station_id:
            query += " AND station_id = %s"
            params.append(station_id)
        
        if min_rank:
            # Filter by rank (basic hierarchy)
            rank_order = ['firefighter', 'driver', 'captain', 'battalion_chief']
            if min_rank in rank_order:
                min_idx = rank_order.index(min_rank)
                allowed_ranks = rank_order[min_idx:]
                query += f" AND rank IN ({','.join(['%s'] * len(allowed_ranks))})"
                params.extend(allowed_ranks)
        
        query += " ORDER BY rank DESC, years_of_service DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_equipment_by_station(self, station_id: int, 
                                 equipment_type: str = None) -> List[Dict]:
        """Get equipment at a station"""
        
        query = """
            SELECT * FROM fire_equipment
            WHERE station_id = %s
            AND status = 'available'
        """
        params = [station_id]
        
        if equipment_type:
            query += " AND equipment_type = %s"
            params.append(equipment_type)
        
        query += " ORDER BY condition DESC, equipment_type"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_recent_emergency_calls(self, hours: int = 24, 
                                  status: str = None) -> List[Dict]:
        """Get recent emergency calls"""
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        query = """
            SELECT * FROM emergency_calls
            WHERE call_timestamp >= %s
        """
        params = [cutoff]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY call_timestamp DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_emergency_call_by_id(self, call_id: int) -> Optional[Dict]:
        """Get emergency call details"""
        
        query = "SELECT * FROM emergency_calls WHERE call_id = %s"
        results = self.db.execute_query(query, (call_id,))
        return results[0] if results else None
    
    def get_hydrants_by_zone(self, zone: str, status: str = 'operational') -> List[Dict]:
        """Get hydrants in a zone"""
        
        query = """
            SELECT * FROM fire_hydrants
            WHERE zone = %s
        """
        params = [zone]
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY flow_rate_gpm DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_recent_incidents(self, days: int = 30, 
                            severity: str = None) -> List[Dict]:
        """Get recent fire incidents"""
        
        cutoff = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT * FROM fire_incidents
            WHERE incident_date >= %s
        """
        params = [cutoff]
        
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        
        query += " ORDER BY incident_date DESC"
        
        return self.db.execute_query(query, tuple(params))
    
    def get_incidents_by_location(self, location: str, days: int = 90) -> List[Dict]:
        """Get incidents at a specific location"""
        
        cutoff = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT * FROM fire_incidents
            WHERE location LIKE %s
            AND incident_date >= %s
            ORDER BY incident_date DESC
        """
        
        return self.db.execute_query(query, (f'%{location}%', cutoff))
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get department budget status (from shared budgets table)"""
        
        query = """
            SELECT * FROM budgets
            WHERE department = 'fire'
            AND year = EXTRACT(YEAR FROM CURRENT_DATE)
            LIMIT 1
        """
        
        results = self.db.execute_query(query)
        
        if results:
            budget = results[0]
            available = budget['allocated'] - budget['spent']
            utilization = (budget['spent'] / budget['allocated'] * 100) if budget['allocated'] > 0 else 0
            
            return {
                'allocated': float(budget['allocated']),
                'spent': float(budget['spent']),
                'available': float(available),
                'utilization_percent': round(utilization, 2)
            }
        else:
            return {
                'allocated': 0,
                'spent': 0,
                'available': 0,
                'utilization_percent': 0
            }
    
    def log_decision(self, decision_record: Dict[str, Any]) -> int:
        """Log agent decision to agent_decisions table"""
        
        query = """
            INSERT INTO agent_decisions (
                agent_type,
                request_type,
                request_data,
                context,
                plan,
                tool_results,
                feasible,
                feasibility_reason,
                policy_compliant,
                policy_violations,
                confidence,
                confidence_factors,
                decision,
                reasoning,
                escalation_reason,
                response,
                execution_time_ms,
                created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING decision_id
        """
        
        params = (
            'fire',
            decision_record.get('request_type'),
            json.dumps(decision_record.get('request_data', {})),
            json.dumps(decision_record.get('context', {})),
            json.dumps(decision_record.get('plan', {})),
            json.dumps(decision_record.get('tool_results', {})),
            decision_record.get('feasible', False),
            decision_record.get('feasibility_reason', ''),
            decision_record.get('policy_ok', False),
            json.dumps(decision_record.get('policy_violations', [])),
            decision_record.get('confidence', 0.0),
            json.dumps(decision_record.get('confidence_factors', {})),
            decision_record.get('decision', 'escalate'),
            decision_record.get('reasoning', ''),
            decision_record.get('escalation_reason'),
            json.dumps(decision_record.get('response', {})),
            decision_record.get('execution_time_ms', 0),
            datetime.now()
        )
        
        result = self.db.execute_query(query, params)
        return result[0]['decision_id'] if result else None


def get_db():
    """Get database connection"""
    return DatabaseConnection()


def get_queries(db: DatabaseConnection):
    """Get queries instance"""
    return FireDepartmentQueries(db)
