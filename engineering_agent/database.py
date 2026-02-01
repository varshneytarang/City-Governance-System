"""
Database connection and query utilities for Engineering Department
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import logging

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL connection and queries"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD
            )
            logger.info(f"✓ Connected to {settings.DB_NAME} (Engineering)")
        except psycopg2.Error as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Query error: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = None) -> Optional[str]:
        """Execute INSERT and return inserted ID"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                self.conn.commit()
                if cur.description is None:
                    return None
                result = cur.fetchone()
                return result[0] if result else None
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Insert error: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute UPDATE query and return number of affected rows"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                self.conn.commit()
                return cur.rowcount
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.error(f"Update error: {e}")
            raise


class EngineeringDepartmentQueries:
    """Database queries specific to Engineering Department"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    # ========== CONTEXT QUERIES ==========
    
    def get_active_projects(self, location: Optional[str] = None) -> List[Dict]:
        """Get all active engineering projects"""
        query = """
            SELECT project_id, project_name, location, status, project_type,
                   start_date, end_date, actual_cost, estimated_cost
            FROM projects
            WHERE department = 'engineering' AND status IN ('approved', 'in_progress')
        """
        params = []
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        query += " ORDER BY start_date DESC LIMIT 50"
        return self.db.execute_query(query, tuple(params))
    
    def get_contractors(self, min_rating: Optional[float] = None) -> List[Dict]:
        """Get available contractors"""
        # For now, return from workers table (will create contractors table later)
        query = """
            SELECT worker_id as contractor_id, worker_name as contractor_name,
                   role, status
            FROM workers
            WHERE department IN ('engineering', 'construction')
                  AND status = 'active'
                  AND role IN ('contractor', 'supervisor', 'engineer')
        """
        params = []
        query += " ORDER BY worker_name LIMIT 50"
        return self.db.execute_query(query, tuple(params))
    
    def get_equipment_availability(self, equipment_type: Optional[str] = None) -> List[Dict]:
        """Get available equipment"""
        # Simplified - use projects as proxy for equipment
        query = """
            SELECT COUNT(*) as total_equipment, 0 as available_equipment
            FROM projects
            WHERE department = 'engineering' AND status = 'in_progress'
        """
        return self.db.execute_query(query)
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get current budget status for engineering"""
        query = """
            SELECT department, budget_year, allocated_amount, 
                   spent_amount, remaining_amount, updated_at
            FROM department_budgets
            WHERE department = 'engineering' 
                  AND budget_year = EXTRACT(YEAR FROM CURRENT_DATE)
            ORDER BY updated_at DESC
            LIMIT 1
        """
        results = self.db.execute_query(query)
        
        if results:
            return {
                "allocated": float(results[0]['allocated_amount'] or 0),
                "spent": float(results[0]['spent_amount'] or 0),
                "remaining": float(results[0]['remaining_amount'] or 0),
                "year": int(results[0]['budget_year']),
                "updated_at": results[0]['updated_at']
            }
        
        return {
            "allocated": 0,
            "spent": 0,
            "remaining": 0,
            "year": datetime.now().year,
            "updated_at": None
        }
    
    def get_pending_tenders(self, max_amount: Optional[float] = None) -> List[Dict]:
        """Get pending tenders"""
        # Use projects with specific status as tenders
        query = """
            SELECT project_id as tender_id, project_name as tender_name,
                   estimated_cost, status, location, start_date
            FROM projects
            WHERE department = 'engineering'
                  AND status = 'planning'
        """
        params = []
        
        if max_amount:
            query += " AND estimated_cost <= %s"
            params.append(max_amount)
        
        query += " ORDER BY estimated_cost DESC LIMIT 20"
        return self.db.execute_query(query, tuple(params))
    
    def get_incidents(self, days_back: int = 30, severity: Optional[str] = None) -> List[Dict]:
        """Get recent incidents"""
        query = """
            SELECT incident_id, incident_type, location, severity,
                   description, reported_at, status, zone
            FROM incidents
            WHERE department = 'engineering'
                  AND reported_at >= CURRENT_DATE - INTERVAL '%s days'
        """
        params = [days_back]
        
        if severity:
            query += " AND severity = %s"
            params.append(severity)
        
        query += " ORDER BY reported_at DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_work_schedule(self, location: str, days_ahead: int = 7) -> List[Dict]:
        """Get scheduled work for location"""
        query = """
            SELECT schedule_id, activity_type, location, scheduled_date,
                   start_time, end_time, workers_assigned, priority, status
            FROM work_schedules
            WHERE department = 'engineering'
                  AND location = %s
                  AND scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
            ORDER BY scheduled_date ASC, start_time ASC
        """
        return self.db.execute_query(query, (location, days_ahead))
    
    def get_safety_violations(self, days_back: int = 90) -> List[Dict]:
        """Get recent safety violations"""
        query = """
            SELECT incident_id, incident_type as violation_type, 
                   location, severity, description, reported_at
            FROM incidents
            WHERE department = 'engineering'
                  AND incident_type LIKE '%safety%'
                  AND reported_at >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY reported_at DESC
        """
        return self.db.execute_query(query, (days_back,))
    
    # ========== DECISION LOGGING ==========
    
    def log_decision(self, decision_data: Dict[str, Any]) -> Optional[str]:
        """Log agent decision to database"""
        query = """
            INSERT INTO agent_decisions (
                department, request_type, request_data, context_snapshot,
                proposed_plan, tool_results, feasible, feasibility_reason,
                policy_compliant, policy_violations, confidence_score,
                decision, decision_reasoning, escalated, escalation_reason,
                execution_time_ms, agent_version
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING decision_id
        """
        
        params = (
            "engineering",
            decision_data.get("request_type", "unknown"),
            json.dumps(decision_data.get("request_data", {})),
            json.dumps(decision_data.get("context", {})),
            json.dumps(decision_data.get("plan", {})),
            json.dumps(decision_data.get("tool_results", {})),
            decision_data.get("feasible", False),
            decision_data.get("feasibility_reason", ""),
            decision_data.get("policy_ok", False),
            json.dumps(decision_data.get("policy_violations", [])),
            decision_data.get("confidence", 0.0),
            decision_data.get("decision", "escalate"),
            decision_data.get("reasoning", ""),
            decision_data.get("escalated", False),
            decision_data.get("escalation_reason"),
            decision_data.get("execution_time_ms", 0),
            decision_data.get("agent_version", "1.0")
        )
        
        return self.db.execute_insert(query, params)


# Global database instance
_db_instance = None


def get_db() -> DatabaseConnection:
    """Get database connection singleton"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance


def get_queries(db: DatabaseConnection) -> EngineeringDepartmentQueries:
    """Get queries instance"""
    return EngineeringDepartmentQueries(db)
