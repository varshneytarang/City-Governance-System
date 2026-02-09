"""
Database connection and query utilities for Fire Department

USES ACTUAL SCHEMA TABLES:
- incidents (department='fire') - fire incidents stored here
- projects (department='fire')
- work_schedules (department='fire')  
- workers (department='fire')
- department_budgets (department='fire')

NOTE: There are NO fire-specific tables in schema. Fire department uses shared tables.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from typing import List, Dict, Any, Optional, Tuple
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
            logger.info(f"✓ Connected to {settings.DB_NAME} (Fire)")
        except psycopg2.Error as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute SELECT query and return results as list of dicts"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except psycopg2.Error as e:
            logger.error(f"Query error: {e}")
            logger.error(f"Query: {query}")
            raise


class FireDepartmentQueries:
    """Database queries for Fire Department using ACTUAL schema tables"""
    
    def __init__(self, db: DatabaseConnection = None):
        self.db = db or DatabaseConnection()
    
    # ========== FIRE INCIDENTS (stored in incidents table) ==========
    
    def get_fire_incidents(self, location: Optional[str] = None, days: int = 90, severity: Optional[str] = None) -> List[Dict]:
        """Get fire incidents from incidents table"""
        query = """
            SELECT incident_id, incident_type, location, severity, 
                   reported_date, reported_by, description, status, 
                   resolution_date, notes, created_at
            FROM incidents
            WHERE department = 'fire'
            AND reported_date > CURRENT_DATE - INTERVAL %s
        """
        params: Tuple = (f"{days} days",)
        
        if location:
            query += " AND location ILIKE %s"
            params = (f"{days} days", f"%{location}%")
        if severity:
            if location:
                query += " AND severity = %s"
                params = (f"{days} days", f"%{location}%", severity)
            else:
                query += " AND severity = %s"
                params = (f"{days} days", severity)
        
        query += " ORDER BY reported_date DESC"
        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} fire incidents")
        return results
    
    def get_active_fire_incidents(self, location: Optional[str] = None) -> List[Dict]:
        """Get currently active (unresolved) fire incidents"""
        query = """
            SELECT incident_id, incident_type, location, severity, 
                   reported_date, reported_by, description, status, notes
            FROM incidents
            WHERE department = 'fire'
            AND status IN ('reported', 'in_progress', 'investigating')
        """
        params = []
        
        if location:
            query += " AND location ILIKE %s"
            params.append(f"%{location}%")
        
        query += " ORDER BY severity DESC, reported_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_incidents_by_type(self, incident_type: Optional[str] = None, days: int = 90) -> List[Dict]:
        """Get fire incidents by type (e.g., 'fire', 'medical emergency', 'hazmat')"""
        query = """
            SELECT incident_id, incident_type, location, severity, 
                   reported_date, reported_by, description, status, 
                   resolution_date, notes
            FROM incidents
            WHERE department = 'fire'
            AND reported_date > CURRENT_DATE - INTERVAL %s
        """
        params: Tuple = (f"{days} days",)
        
        if incident_type:
            query += " AND incident_type = %s"
            params = (f"{days} days", incident_type)
        
        query += " ORDER BY reported_date DESC"
        return self.db.execute_query(query, params)
    
    # ========== SHARED TABLES (department='fire') ==========
    
    def get_active_projects(self, location: Optional[str] = None) -> List[Dict]:
        """Get active fire department projects"""
        query = """
            SELECT project_id, project_name, project_type, location, 
                   estimated_cost, actual_cost, start_date, end_date, 
                   status, notes
            FROM projects
            WHERE department = 'fire' 
            AND status IN ('approved', 'in_progress', 'planned')
        """
        params = []
        
        if location:
            query += " AND location ILIKE %s"
            params.append(f"%{location}%")
        
        query += " ORDER BY start_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_work_schedule(self, location: Optional[str] = None, days_ahead: int = 7) -> List[Dict]:
        """Get scheduled fire department work"""
        query = """
            SELECT schedule_id, activity_type, location, scheduled_date, 
                   start_time, end_time, priority, workers_assigned, 
                   equipment_assigned, status, notes
            FROM work_schedules
            WHERE department = 'fire'
            AND scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
        """
        params: Tuple = (days_ahead,)
        
        if location:
            query += " AND location ILIKE %s"
            params = (days_ahead, f"%{location}%")
        
        query += " ORDER BY scheduled_date, start_time"
        return self.db.execute_query(query, params)
    
    def get_available_workers(self, role: Optional[str] = None) -> List[Dict]:
        """Get available fire department workers"""
        query = """
            SELECT worker_id, worker_name, role, skills, certifications, 
                   status, phone, email, hire_date
            FROM workers
            WHERE department = 'fire' AND status = 'active'
        """
        params = []
        
        if role:
            query += " AND role = %s"
            params.append(role)
        
        query += " ORDER BY worker_name"
        return self.db.execute_query(query, tuple(params))
    
    def get_workers_by_certification(self, certification: str) -> List[Dict]:
        """Get workers with specific certification (e.g., 'EMT', 'Hazmat', 'Fire Level II')"""
        query = """
            SELECT worker_id, worker_name, role, skills, certifications, 
                   status, phone, email
            FROM workers
            WHERE department = 'fire' 
            AND status = 'active'
            AND certifications ILIKE %s
            ORDER BY worker_name
        """
        return self.db.execute_query(query, (f"%{certification}%",))
    
    def get_budget_status(self) -> Optional[Dict]:
        """Get current fire department budget"""
        query = """
            SELECT budget_id, department, year, month, total_budget, 
                   allocated, spent, remaining, utilization_percent, status
            FROM department_budgets
            WHERE department = 'fire'
            AND year = EXTRACT(YEAR FROM CURRENT_DATE)
            AND month = EXTRACT(MONTH FROM CURRENT_DATE)
            LIMIT 1
        """
        results = self.db.execute_query(query)
        return results[0] if results else None
    
    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Get recent decision history"""
        query = """
            SELECT id, request_type, decision, confidence, feasible,
                   created_at, execution_time_ms
            FROM agent_decisions
            WHERE agent_type = 'fire'
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,))


# Helper functions
def get_db() -> DatabaseConnection:
    """Get database connection instance"""
    return DatabaseConnection()


def get_queries(db: DatabaseConnection = None) -> FireDepartmentQueries:
    """Get queries instance"""
    return FireDepartmentQueries(db)
