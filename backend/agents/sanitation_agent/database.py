"""
Database connection and query utilities for Sanitation Department

USES ACTUAL SCHEMA TABLES:
- sanitation_inspections (sanitation-specific)
- projects (department='sanitation')
- work_schedules (department='sanitation')  
- workers (department='sanitation')
- incidents (department='sanitation')
- department_budgets (department='sanitation')
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
        import os
        try:
            # Use DATABASE_URL from Railway (mandatory)
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                self.conn = psycopg2.connect(database_url, sslmode="require")
                logger.info(f"✓ Connected to database (Sanitation) via DATABASE_URL")
            else:
                # Fallback to individual env vars (local development only)
                self.conn = psycopg2.connect(
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD
                )
                logger.info(f"✓ Connected to {settings.DB_NAME} (Sanitation)")
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


class SanitationDepartmentQueries:
    """Database queries for Sanitation Department using ACTUAL schema tables"""
    
    def __init__(self, db: DatabaseConnection = None):
        self.db = db or DatabaseConnection()
    
    # ========== SANITATION-SPECIFIC TABLE ==========
    
    def get_sanitation_inspections(self, location: Optional[str] = None, days: int = 90) -> List[Dict]:
        """Get sanitation inspections from sanitation_inspections table"""
        query = """
            SELECT inspection_id, location, facility, inspection_date, outcome, 
                   inspector, notes, findings, created_at
            FROM sanitation_inspections
            WHERE inspection_date > CURRENT_DATE - INTERVAL %s
        """
        params: Tuple = (f"{days} days",)
        
        if location:
            query += " AND location ILIKE %s"
            params = (f"{days} days", f"%{location}%")
        
        query += " ORDER BY inspection_date DESC"
        results = self.db.execute_query(query, params)
        logger.info(f"✓ Retrieved {len(results)} sanitation inspections")
        return results
    
    def get_recent_inspections_by_outcome(self, outcome: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get recent inspections filtered by outcome (pass/conditional_pass/fail)"""
        query = """
            SELECT inspection_id, location, facility, inspection_date, outcome, 
                   inspector, notes, findings
            FROM sanitation_inspections
            WHERE inspection_date > CURRENT_DATE - INTERVAL %s
        """
        params: Tuple = (f"{days} days",)
        
        if outcome:
            query += " AND outcome = %s"
            params = (f"{days} days", outcome)
        
        query += " ORDER BY inspection_date DESC"
        return self.db.execute_query(query, params)
    
    # ========== SHARED TABLES (department='sanitation') ==========
    
    def get_active_projects(self, location: Optional[str] = None) -> List[Dict]:
        """Get active sanitation projects"""
        query = """
            SELECT project_id, project_name, project_type, location, 
                   estimated_cost, actual_cost, start_date, end_date, 
                   status, notes
            FROM projects
            WHERE department = 'sanitation' 
            AND status IN ('approved', 'in_progress', 'planned')
        """
        params = []
        
        if location:
            query += " AND location ILIKE %s"
            params.append(f"%{location}%")
        
        query += " ORDER BY start_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_work_schedule(self, location: Optional[str] = None, days_ahead: int = 7) -> List[Dict]:
        """Get scheduled sanitation work"""
        query = """
            SELECT schedule_id, activity_type, location, scheduled_date, 
                   start_time, end_time, priority, workers_assigned, 
                   equipment_assigned, status, notes
            FROM work_schedules
            WHERE department = 'sanitation'
            AND scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
        """
        params: Tuple = (days_ahead,)
        
        if location:
            query += " AND location ILIKE %s"
            params = (days_ahead, f"%{location}%")
        
        query += " ORDER BY scheduled_date, start_time"
        return self.db.execute_query(query, params)
    
    def get_available_workers(self, role: Optional[str] = None) -> List[Dict]:
        """Get available sanitation workers"""
        query = """
            SELECT worker_id, worker_name, role, skills, certifications, 
                   status, phone, email, hire_date
            FROM workers
            WHERE department = 'sanitation' AND status = 'active'
        """
        params = []
        
        if role:
            query += " AND role = %s"
            params.append(role)
        
        query += " ORDER BY worker_name"
        return self.db.execute_query(query, tuple(params))
    
    def get_recent_incidents(self, location: Optional[str] = None, days: int = 30, severity: Optional[str] = None) -> List[Dict]:
        """Get recent sanitation incidents"""
        query = """
            SELECT incident_id, incident_type, location, severity, 
                   reported_date, reported_by, description, status, 
                   resolution_date, notes
            FROM incidents
            WHERE department = 'sanitation'
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
        return self.db.execute_query(query, params)
    
    def get_budget_status(self) -> Optional[Dict]:
        """Get current sanitation budget"""
        query = """
            SELECT budget_id, department, year, month, total_budget, 
                   allocated, spent, remaining, utilization_percent, status
            FROM department_budgets
            WHERE department = 'sanitation'
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
            WHERE agent_type = 'sanitation'
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,))


# Helper functions
def get_db() -> DatabaseConnection:
    """Get database connection instance"""
    return DatabaseConnection()


def get_queries(db: DatabaseConnection = None) -> SanitationDepartmentQueries:
    """Get queries instance"""
    return SanitationDepartmentQueries(db)
