"""
Coordination Agent Database Queries
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any, List
import logging

from .config import CoordinationConfig

logger = logging.getLogger(__name__)


class CoordinationDatabase:
    """Database singleton for coordination agent"""
    
    _instance: Optional['CoordinationDatabase'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.conn = None
        self.connect()
        self._initialized = True
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=CoordinationConfig.DB_HOST,
                port=CoordinationConfig.DB_PORT,
                dbname=CoordinationConfig.DB_NAME,
                user=CoordinationConfig.DB_USER,
                password=CoordinationConfig.DB_PASSWORD
            )
            self.conn.autocommit = True
            logger.info("✓ Database connection established")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise


class CoordinationQueries:
    """Database queries for coordination agent"""
    
    def __init__(self):
        self.db = CoordinationDatabase()
    
    def log_coordination_decision(
        self,
        coordination_id: str,
        conflict_type: str,
        agents_involved: List[str],
        resolution_method: str,
        resolution_rationale: str,
        llm_confidence: Optional[float],
        human_approver: Optional[str],
        outcome: str
    ) -> bool:
        """Log coordination decision to audit trail"""
        query = """
            INSERT INTO coordination_decisions (
                coordination_id, conflict_type, agents_involved,
                resolution_method, resolution_rationale, llm_confidence,
                human_approver, outcome, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, NOW()
            )
        """
        try:
            self.db.execute_query(query, (
                coordination_id,
                conflict_type,
                agents_involved,
                resolution_method,
                resolution_rationale,
                llm_confidence,
                human_approver,
                outcome
            ))
            logger.info(f"✓ Logged coordination decision: {coordination_id}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to log coordination decision: {e}")
            return False
    
    def get_pending_human_approvals(self) -> List[Dict[str, Any]]:
        """Get all pending human approvals"""
        query = """
            SELECT * FROM coordination_decisions
            WHERE outcome = 'pending_human_approval'
            ORDER BY created_at DESC
        """
        return self.db.execute_query(query)
    
    def update_human_approval(
        self,
        coordination_id: str,
        approver: str,
        outcome: str,
        notes: Optional[str] = None
    ) -> bool:
        """Update human approval status"""
        query = """
            UPDATE coordination_decisions
            SET human_approver = %s,
                outcome = %s,
                approval_notes = %s,
                resolved_at = NOW()
            WHERE coordination_id = %s
        """
        try:
            self.db.execute_query(query, (approver, outcome, notes, coordination_id))
            logger.info(f"✓ Updated human approval for: {coordination_id}")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to update human approval: {e}")
            return False
    
    def get_coordination_history(
        self,
        limit: int = 50,
        agent_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get coordination decision history"""
        if agent_type:
            query = """
                SELECT * FROM coordination_decisions
                WHERE %s = ANY(agents_involved)
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.db.execute_query(query, (agent_type, limit))
        else:
            query = """
                SELECT * FROM coordination_decisions
                ORDER BY created_at DESC
                LIMIT %s
            """
            return self.db.execute_query(query, (limit,))
    
    def get_conflict_statistics(self) -> Dict[str, Any]:
        """Get statistics on conflict resolution"""
        query = """
            SELECT
                conflict_type,
                resolution_method,
                COUNT(*) as count,
                AVG(llm_confidence) as avg_confidence
            FROM coordination_decisions
            GROUP BY conflict_type, resolution_method
        """
        results = self.db.execute_query(query)
        
        stats = {}
        for row in results:
            key = f"{row['conflict_type']}_{row['resolution_method']}"
            stats[key] = {
                "count": row['count'],
                "avg_confidence": float(row['avg_confidence']) if row['avg_confidence'] else 0.0
            }
        
        return stats
    
    def check_resource_availability(
        self,
        resource_type: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """Check current resource availability across all departments"""
        
        if resource_type == "budget":
            query = """
                SELECT
                    department_name,
                    total_budget,
                    allocated_budget,
                    (total_budget - allocated_budget) as available_budget
                FROM department_budgets
                WHERE (total_budget - allocated_budget) > 0
            """
            if location:
                query += " AND location = %s"
                results = self.db.execute_query(query, (location,))
            else:
                results = self.db.execute_query(query)
            
            return {
                "resource_type": "budget",
                "availability": results
            }
        
        elif resource_type == "workers":
            query = """
                SELECT
                    zone,
                    COUNT(*) as total_workers,
                    SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) as available_workers
                FROM workers
                GROUP BY zone
            """
            if location:
                query += " HAVING zone = %s"
                results = self.db.execute_query(query, (location,))
            else:
                results = self.db.execute_query(query)
            
            return {
                "resource_type": "workers",
                "availability": results
            }
        
        else:
            return {"resource_type": resource_type, "availability": []}
    
    def get_active_projects_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Get all active projects in a specific location"""
        query = """
            SELECT
                project_name,
                department,
                status,
                start_date,
                end_date,
                estimated_cost
            FROM projects
            WHERE location = %s
            AND status IN ('in_progress', 'planned')
            ORDER BY start_date
        """
        return self.db.execute_query(query, (location,))
    
    def create_coordination_tables_if_not_exists(self):
        """Create coordination-specific tables if they don't exist"""
        create_table_query = """
            CREATE TABLE IF NOT EXISTS coordination_decisions (
                id SERIAL PRIMARY KEY,
                coordination_id VARCHAR(100) UNIQUE NOT NULL,
                agent_type VARCHAR(50),
                agent_id VARCHAR(100),
                location VARCHAR(255),
                resources_needed TEXT[],
                estimated_cost DECIMAL(15, 2),
                plan_details JSONB,
                conflict_type VARCHAR(50),
                agents_involved TEXT[],
                resolution_method VARCHAR(20),
                resolution_rationale TEXT,
                llm_confidence DECIMAL(3, 2),
                human_approver VARCHAR(100),
                outcome VARCHAR(50),
                approval_notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                resolved_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            );
            
            CREATE INDEX IF NOT EXISTS idx_coordination_outcome
            ON coordination_decisions(outcome);
            
            CREATE INDEX IF NOT EXISTS idx_coordination_created
            ON coordination_decisions(created_at DESC);
            
            CREATE INDEX IF NOT EXISTS idx_coordination_location
            ON coordination_decisions(location);
            
            CREATE INDEX IF NOT EXISTS idx_coordination_status
            ON coordination_decisions(status);
        """
        try:
            self.db.execute_query(create_table_query)
            logger.info("✓ Coordination tables verified/created")
        except Exception as e:
            logger.warning(f"⚠ Table creation warning: {e}")


def get_coordination_db() -> CoordinationDatabase:
    """Get database singleton instance"""
    return CoordinationDatabase()
