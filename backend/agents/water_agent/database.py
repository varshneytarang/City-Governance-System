"""
Database connection and query utilities
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
        import os
        try:
            # Use DATABASE_URL from Railway (mandatory)
            database_url = os.getenv("DATABASE_URL")
            if database_url:
                self.conn = psycopg2.connect(database_url, sslmode="require")
                logger.info(f"✓ Connected via DATABASE_URL")
            else:
                # Fallback to individual env vars (local development only)
                self.conn = psycopg2.connect(
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD
                )
                logger.info(f"✓ Connected to {settings.DB_NAME}")
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
                # Get last inserted ID
                cur.execute("SELECT lastval();")
                return cur.fetchone()[0]
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


class WaterDepartmentQueries:
    """Database queries specific to Water Department"""
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    # ========== CONTEXT QUERIES ==========
    
    def get_active_projects(self, location: Optional[str] = None) -> List[Dict]:
        """Get all active projects, optionally filtered by location"""
        query = """
            SELECT project_id, project_name, location, status, 
                   start_date, end_date, actual_cost, estimated_cost
            FROM projects
            WHERE department = 'water' AND status IN ('approved', 'in_progress')
        """
        params = []
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        query += " ORDER BY start_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_work_schedule(self, location: str, days_ahead: int = 7) -> List[Dict]:
        """Get scheduled work for the next N days"""
        query = """
            SELECT schedule_id, activity_type, location, scheduled_date,
                   start_time, end_time, workers_assigned, priority, status
            FROM work_schedules
            WHERE department = 'water' 
                  AND location = %s
                  AND scheduled_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '%s days'
            ORDER BY scheduled_date ASC, start_time ASC
        """
        return self.db.execute_query(query, (location, days_ahead))
    
    def get_available_workers(self, location: Optional[str] = None, role: Optional[str] = None) -> List[Dict]:
        """Get available workers"""
        query = """
            SELECT worker_id, worker_name, role, skills, status, 
                   certifications, phone, email
            FROM workers
            WHERE department = 'water' AND status = 'active'
        """
        params = []
        
        if role:
            query += " AND role = %s"
            params.append(role)
        
        query += " ORDER BY worker_name"
        return self.db.execute_query(query, tuple(params))
    
    def get_pipeline_status(self, location: Optional[str] = None, zone: Optional[str] = None) -> List[Dict]:
        """Get pipeline health and status"""
        query = """
            SELECT pipeline_id, location, zone, pipeline_type, 
                   condition, operational_status, pressure_psi, flow_rate,
                   material, diameter_mm, last_inspection_date, next_inspection_due
            FROM pipelines
            WHERE 1=1
        """
        params = []
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        if zone:
            query += " AND zone = %s"
            params.append(zone)
        
        query += " ORDER BY condition DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_reservoir_status(self) -> List[Dict]:
        """Get all reservoir status"""
        query = """
            SELECT reservoir_id, name, location, capacity_liters, 
                   current_level_liters, level_percentage, operational_status,
                   last_reading_time
            FROM reservoirs
            ORDER BY level_percentage ASC
        """
        return self.db.execute_query(query)
    
    def get_recent_incidents(self, location: Optional[str] = None, days: int = 30) -> List[Dict]:
        """Get recent incidents in the area"""
        query = """
            SELECT incident_id, incident_type, location, severity, 
                   reported_date, status, description
            FROM incidents
            WHERE department = 'water'
                  AND reported_date > CURRENT_TIMESTAMP - INTERVAL '%s days'
        """
        params = [days]
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        query += " ORDER BY reported_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_budget_status(self) -> Dict:
        """Get current budget status"""
        query = """
            SELECT department, year, month, total_budget, allocated, spent, 
                   remaining, status, utilization_percent
            FROM department_budgets
            WHERE department = 'water'
                  AND year = EXTRACT(YEAR FROM CURRENT_DATE)
                  AND month = EXTRACT(MONTH FROM CURRENT_DATE)
            LIMIT 1
        """
        results = self.db.execute_query(query)
        return results[0] if results else None
    
    # ========== RISK ANALYSIS QUERIES ==========
    
    def get_high_risk_zones(self) -> List[Dict]:
        """Identify zones with multiple recent incidents"""
        query = """
            SELECT location, COUNT(*) as incident_count, 
                   MAX(severity) as highest_severity
            FROM incidents
            WHERE department = 'water'
                  AND reported_date > CURRENT_TIMESTAMP - INTERVAL '30 days'
                  AND status IN ('reported', 'investigating')
            GROUP BY location
            HAVING COUNT(*) >= 2
            ORDER BY incident_count DESC
        """
        return self.db.execute_query(query)
    
    def get_pipeline_alerts(self) -> List[Dict]:
        """Get pipelines needing attention"""
        query = """
            SELECT pipeline_id, location, zone, condition, 
                   pressure_psi, operational_status, last_inspection_date
            FROM pipelines
            WHERE department IS NULL  -- all pipelines are general infrastructure
                  AND (condition IN ('poor', 'critical')
                       OR operational_status = 'under_repair'
                       OR next_inspection_due <= CURRENT_DATE)
            ORDER BY condition DESC
        """
        return self.db.execute_query(query)
    
    # ========== MEMORY/AUDIT QUERIES ==========
    
    def log_decision(self, decision_data: Dict) -> str:
        """Log a decision to agent_decisions table. Returns decision_id"""
        query = """
            INSERT INTO agent_decisions (
                agent_type, request_type, request_data, context_snapshot,
                plan_attempted, tool_results, feasible, feasibility_reason,
                policy_compliant, policy_violations, confidence, 
                confidence_factors, decision, reasoning, escalation_reason,
                response, agent_version, execution_time_ms, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
            ) RETURNING id
        """
        
        params = (
            "water_department",
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
            json.dumps(decision_data.get("confidence_factors", {})),
            decision_data.get("decision", "escalate"),  # approve/deny/escalate
            decision_data.get("reasoning", ""),
            decision_data.get("escalation_reason", None),
            json.dumps(decision_data.get("response", {})),
            "1.0",
            decision_data.get("execution_time_ms", 0)
        )
        
        with self.db.conn.cursor() as cur:
            cur.execute(query, params)
            self.db.conn.commit()
            result = cur.fetchone()
            return str(result[0]) if result else None
    
    def get_decision_history(self, limit: int = 10) -> List[Dict]:
        """Get recent decision history"""
        query = """
            SELECT id, agent_type, request_type, decision, confidence, 
                   feasible, policy_compliant, created_at, reasoning
            FROM agent_decisions
            WHERE agent_type = 'water_department'
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,))
    
    # ========== VALIDATION HELPERS ==========
    
    def check_location_exists(self, location: str) -> bool:
        """Verify location is valid"""
        query = """
            SELECT COUNT(*) FROM (
                SELECT DISTINCT location FROM pipelines
                UNION
                SELECT DISTINCT location FROM work_schedules WHERE department = 'water'
                UNION
                SELECT location FROM reservoirs
            ) as locations
            WHERE location = %s
        """
        result = self.db.execute_query(query, (location,))
        return result[0]['count'] > 0 if result else False
    
    # ========== ADDITIONAL WATER INFRASTRUCTURE QUERIES ==========
    
    def get_pipeline_inspections(self, pipeline_id: Optional[str] = None, days: int = 90) -> List[Dict]:
        """Get pipeline inspection history"""
        query = """
            SELECT pi.inspection_id, pi.pipeline_id, pi.inspector, pi.inspection_date,
                   pi.outcome, pi.notes, pi.findings,
                   p.location, p.zone, p.pipeline_type, p.condition
            FROM pipeline_inspections pi
            JOIN pipelines p ON pi.pipeline_id = p.pipeline_id
            WHERE pi.inspection_date > CURRENT_DATE - INTERVAL '%s days'
        """
        params = [days]
        
        if pipeline_id:
            query += " AND pi.pipeline_id = %s"
            params.append(pipeline_id)
        
        query += " ORDER BY pi.inspection_date DESC"
        return self.db.execute_query(query, tuple(params))
    
    def get_water_readings(self, location: Optional[str] = None, hours: int = 24) -> List[Dict]:
        """Get recent water network sensor readings"""
        query = """
            SELECT wr.reading_id, wr.pipeline_id, wr.location, wr.reading_time,
                   wr.pressure_psi, wr.flow_rate, wr.temperature, wr.metadata,
                   p.zone, p.pipeline_type
            FROM water_readings wr
            LEFT JOIN pipelines p ON wr.pipeline_id = p.pipeline_id
            WHERE wr.reading_time > CURRENT_TIMESTAMP - INTERVAL '%s hours'
        """
        params = [hours]
        
        if location:
            query += " AND wr.location = %s"
            params.append(location)
        
        query += " ORDER BY wr.reading_time DESC LIMIT 100"
        return self.db.execute_query(query, tuple(params))
    
    def get_service_outages(self, location: Optional[str] = None, status: Optional[str] = None) -> List[Dict]:
        """Get water service outages and disruptions"""
        query = """
            SELECT outage_id, location, zone, reported_at, started_at, resolved_at,
                   severity, cause, affected_customers, status, related_pipeline_id
            FROM service_outages
            WHERE 1=1
        """
        params = []
        
        if location:
            query += " AND location = %s"
            params.append(location)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        else:
            query += " AND status NOT IN ('closed', 'resolved')"
        
        query += " ORDER BY reported_at DESC"
        return self.db.execute_query(query, tuple(params))


def get_db() -> DatabaseConnection:
    """Factory function to create database connection"""
    return DatabaseConnection()


def get_queries(db: DatabaseConnection) -> WaterDepartmentQueries:
    """Factory function to create queries helper"""
    return WaterDepartmentQueries(db)
