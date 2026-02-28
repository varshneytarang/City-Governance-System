"""
Database Connection and Query Layer for Task Orchestration

Provides connection pooling and prepared queries for all
task orchestration database operations.
"""

import logging
import psycopg2
from psycopg2 import pool, extras
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from datetime import datetime
import json

from .config import task_config

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Manages PostgreSQL connection pool for task orchestration
    """
    
    def __init__(self):
        self.connection_pool: Optional[pool.SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=20,
                host=task_config.DB_HOST,
                port=task_config.DB_PORT,
                database=task_config.DB_NAME,
                user=task_config.DB_USER,
                password=task_config.DB_PASSWORD
            )
            logger.info("✓ Task orchestration database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor):
        """
        Context manager for getting a cursor with automatic connection handling
        
        Usage:
            with db.get_cursor() as cursor:
                cursor.execute(...)
                result = cursor.fetchall()
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(
        self, 
        query: str, 
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = True
    ) -> Optional[Any]:
        """
        Execute a query and return results
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return single row
            fetch_all: Return all rows (default)
        
        Returns:
            Query results or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return None
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute same query with multiple parameter sets
        
        Returns:
            Number of rows affected
        """
        with self.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("✓ Task orchestration database pool closed")


class TaskQueries:
    """
    Prepared queries for task orchestration operations
    """
    
    def __init__(self, db: DatabaseConnection):
        self.db = db
    
    # ==================== WORKFLOW QUERIES ====================
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Optional[str]:
        """Create a new workflow and return its ID"""
        query = """
            INSERT INTO workflows (
                workflow_name, workflow_description, workflow_type,
                initiated_by_department, status, priority,
                planned_start_date, planned_end_date,
                estimated_total_cost, tags, metadata, created_by
            ) VALUES (
                %(workflow_name)s, %(workflow_description)s, %(workflow_type)s,
                %(initiated_by_department)s, %(status)s, %(priority)s,
                %(planned_start_date)s, %(planned_end_date)s,
                %(estimated_total_cost)s, %(tags)s, %(metadata)s, %(created_by)s
            ) RETURNING workflow_id
        """
        
        # Convert Python lists/dicts to PostgreSQL arrays/JSON
        workflow_data['tags'] = workflow_data.get('tags', [])
        workflow_data['metadata'] = json.dumps(workflow_data.get('metadata', {}))
        workflow_data['status'] = workflow_data.get('status', 'draft')
        
        result = self.db.execute_query(query, workflow_data, fetch_one=True)
        return str(result['workflow_id']) if result else None
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        query = "SELECT * FROM workflows WHERE workflow_id = %s"
        return self.db.execute_query(query, (workflow_id,), fetch_one=True)
    
    def update_workflow(self, workflow_id: str, update_data: Dict[str, Any]) -> bool:
        """Update workflow fields"""
        if not update_data:
            return False
        
        # Build dynamic UPDATE query
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['metadata', 'knowledge_graph_data']:
                value = json.dumps(value) if value else None
            set_clauses.append(f"{key} = %s")
            params.append(value)
        
        params.append(workflow_id)
        
        query = f"""
            UPDATE workflows 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE workflow_id = %s
        """
        
        self.db.execute_query(query, tuple(params), fetch_all=False)
        return True
    
    def list_workflows(
        self, 
        department: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List workflows with optional filters"""
        conditions = []
        params = []
        
        if department:
            conditions.append("initiated_by_department = %s")
            params.append(department)
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        query = f"""
            SELECT * FROM workflows
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        return self.db.execute_query(query, tuple(params))
    
    # ==================== TASK QUERIES ====================
    
    def create_task(self, task_data: Dict[str, Any]) -> Optional[str]:
        """Create a new task and return its ID"""
        query = """
            INSERT INTO tasks (
                workflow_id, task_title, task_description, task_type,
                assigned_department, assigned_to_user_id, status, priority,
                estimated_start_date, estimated_end_date, deadline,
                estimated_duration_hours, estimated_cost,
                required_resources, requires_approval, sequence_order,
                parent_task_id, tags, metadata
            ) VALUES (
                %(workflow_id)s, %(task_title)s, %(task_description)s, %(task_type)s,
                %(assigned_department)s, %(assigned_to_user_id)s, %(status)s, %(priority)s,
                %(estimated_start_date)s, %(estimated_end_date)s, %(deadline)s,
                %(estimated_duration_hours)s, %(estimated_cost)s,
                %(required_resources)s, %(requires_approval)s, %(sequence_order)s,
                %(parent_task_id)s, %(tags)s, %(metadata)s
            ) RETURNING task_id
        """
        
        # Convert to PostgreSQL types
        task_data['tags'] = task_data.get('tags', [])
        task_data['required_resources'] = json.dumps(task_data.get('required_resources', {}))
        task_data['metadata'] = json.dumps(task_data.get('metadata', {}))
        task_data['status'] = task_data.get('status', 'pending')
        
        result = self.db.execute_query(query, task_data, fetch_one=True)
        return str(result['task_id']) if result else None
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        query = "SELECT * FROM tasks WHERE task_id = %s"
        return self.db.execute_query(query, (task_id,), fetch_one=True)
    
    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update task fields"""
        if not update_data:
            return False
        
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['required_resources', 'allocated_resources', 'metadata', 'agent_execution_result']:
                value = json.dumps(value) if value else None
            set_clauses.append(f"{key} = %s")
            params.append(value)
        
        params.append(task_id)
        
        query = f"""
            UPDATE tasks 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE task_id = %s
        """
        
        self.db.execute_query(query, tuple(params), fetch_all=False)
        return True
    
    def get_workflow_tasks(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a workflow"""
        query = """
            SELECT * FROM tasks 
            WHERE workflow_id = %s 
            ORDER BY sequence_order, created_at
        """
        return self.db.execute_query(query, (workflow_id,))
    
    def get_department_tasks(
        self, 
        department: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get tasks assigned to a department"""
        conditions = ["assigned_department = %s"]
        params = [department]
        
        if status:
            conditions.append("status = %s")
            params.append(status)
        
        query = f"""
            SELECT t.*, w.workflow_name
            FROM tasks t
            JOIN workflows w ON t.workflow_id = w.workflow_id
            WHERE {' AND '.join(conditions)}
            ORDER BY priority DESC, deadline ASC
            LIMIT %s
        """
        
        params.append(limit)
        return self.db.execute_query(query, tuple(params))
    
    # ==================== DEPENDENCY QUERIES ====================
    
    def create_dependency(self, dependency_data: Dict[str, Any]) -> Optional[str]:
        """Create a task dependency"""
        query = """
            INSERT INTO task_dependencies (
                task_id, depends_on_task_id, dependency_type,
                lag_hours, is_hard_dependency, notes
            ) VALUES (
                %(task_id)s, %(depends_on_task_id)s, %(dependency_type)s,
                %(lag_hours)s, %(is_hard_dependency)s, %(notes)s
            ) RETURNING dependency_id
        """
        
        result = self.db.execute_query(query, dependency_data, fetch_one=True)
        return str(result['dependency_id']) if result else None
    
    def get_task_dependencies(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all dependencies for a task (what this task depends on)"""
        query = """
            SELECT td.*, t.task_title as depends_on_title, t.status as depends_on_status
            FROM task_dependencies td
            JOIN tasks t ON td.depends_on_task_id = t.task_id
            WHERE td.task_id = %s
        """
        return self.db.execute_query(query, (task_id,))
    
    def get_dependent_tasks(self, task_id: str) -> List[Dict[str, Any]]:
        """Get tasks that depend on this task"""
        query = """
            SELECT td.*, t.task_title, t.status as task_status
            FROM task_dependencies td
            JOIN tasks t ON td.task_id = t.task_id
            WHERE td.depends_on_task_id = %s
        """
        return self.db.execute_query(query, (task_id,))
    
    def update_dependency_satisfied(self, dependency_id: str, satisfied: bool) -> bool:
        """Mark a dependency as satisfied or not"""
        query = """
            UPDATE task_dependencies 
            SET satisfied = %s, satisfied_at = CASE WHEN %s THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE dependency_id = %s
        """
        self.db.execute_query(query, (satisfied, satisfied, dependency_id), fetch_all=False)
        return True
    
    def check_circular_dependency(self, task_id: str, depends_on_task_id: str) -> bool:
        """
        Check if adding this dependency would create a circular dependency
        Returns True if circular dependency would be created
        """
        query = """
            WITH RECURSIVE dep_chain AS (
                -- Start with the proposed dependency
                SELECT depends_on_task_id as task_id
                FROM task_dependencies
                WHERE task_id = %s
                
                UNION
                
                -- Follow the chain
                SELECT td.depends_on_task_id
                FROM task_dependencies td
                INNER JOIN dep_chain dc ON td.task_id = dc.task_id
            )
            SELECT EXISTS(SELECT 1 FROM dep_chain WHERE task_id = %s) as is_circular
        """
        
        result = self.db.execute_query(query, (depends_on_task_id, task_id), fetch_one=True)
        return result['is_circular'] if result else False
    
    # ==================== CONTINGENCY PLAN QUERIES ====================
    
    def create_contingency_plan(self, plan_data: Dict[str, Any]) -> Optional[str]:
        """Create a contingency plan"""
        query = """
            INSERT INTO contingency_plans (
                task_id, workflow_id, plan_name, plan_description, plan_order,
                trigger_conditions, alternative_approach, alternative_department,
                alternative_resources, estimated_cost, estimated_duration_hours,
                risk_level, success_probability, generated_by, llm_model,
                generation_confidence, requires_approval, metadata
            ) VALUES (
                %(task_id)s, %(workflow_id)s, %(plan_name)s, %(plan_description)s, %(plan_order)s,
                %(trigger_conditions)s, %(alternative_approach)s, %(alternative_department)s,
                %(alternative_resources)s, %(estimated_cost)s, %(estimated_duration_hours)s,
                %(risk_level)s, %(success_probability)s, %(generated_by)s, %(llm_model)s,
                %(generation_confidence)s, %(requires_approval)s, %(metadata)s
            ) RETURNING plan_id
        """
        
        # Convert to JSON
        plan_data['trigger_conditions'] = json.dumps(plan_data.get('trigger_conditions', {}))
        plan_data['alternative_resources'] = json.dumps(plan_data.get('alternative_resources', {}))
        plan_data['metadata'] = json.dumps(plan_data.get('metadata', {}))
        
        result = self.db.execute_query(query, plan_data, fetch_one=True)
        return str(result['plan_id']) if result else None
    
    def get_task_contingency_plans(self, task_id: str) -> List[Dict[str, Any]]:
        """Get all contingency plans for a task"""
        query = """
            SELECT * FROM contingency_plans 
            WHERE task_id = %s 
            ORDER BY plan_order
        """
        return self.db.execute_query(query, (task_id,))
    
    # ==================== NOTIFICATION QUERIES ====================
    
    def create_notification(self, notification_data: Dict[str, Any]) -> Optional[str]:
        """Create a notification"""
        query = """
            INSERT INTO task_notifications (
                recipient_department, recipient_user_id, recipient_email,
                workflow_id, task_id, notification_type, priority,
                title, message, action_url, action_required,
                delivery_method, scheduled_for, metadata
            ) VALUES (
                %(recipient_department)s, %(recipient_user_id)s, %(recipient_email)s,
                %(workflow_id)s, %(task_id)s, %(notification_type)s, %(priority)s,
                %(title)s, %(message)s, %(action_url)s, %(action_required)s,
                %(delivery_method)s, %(scheduled_for)s, %(metadata)s
            ) RETURNING notification_id
        """
        
        notification_data['metadata'] = json.dumps(notification_data.get('metadata', {}))
        notification_data['scheduled_for'] = notification_data.get('scheduled_for', datetime.utcnow())
        
        result = self.db.execute_query(query, notification_data, fetch_one=True)
        return str(result['notification_id']) if result else None
    
    def get_pending_notifications(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get pending notifications ready to send"""
        query = """
            SELECT * FROM task_notifications
            WHERE status = 'pending' 
            AND scheduled_for <= CURRENT_TIMESTAMP
            AND retry_count < max_retries
            ORDER BY priority DESC, scheduled_for ASC
            LIMIT %s
        """
        return self.db.execute_query(query, (limit,))
    
    def update_notification_status(
        self, 
        notification_id: str, 
        status: str,
        error: Optional[str] = None
    ) -> bool:
        """Update notification status"""
        query = """
            UPDATE task_notifications 
            SET status = %s,
                sent_at = CASE WHEN %s = 'sent' THEN CURRENT_TIMESTAMP ELSE sent_at END,
                delivered_at = CASE WHEN %s = 'delivered' THEN CURRENT_TIMESTAMP ELSE delivered_at END,
                read_at = CASE WHEN %s = 'read' THEN CURRENT_TIMESTAMP ELSE read_at END,
                last_error = %s,
                retry_count = CASE WHEN %s = 'failed' THEN retry_count + 1 ELSE retry_count END,
                updated_at = CURRENT_TIMESTAMP
            WHERE notification_id = %s
        """
        self.db.execute_query(
            query, 
            (status, status, status, status, error, status, notification_id),
            fetch_all=False
        )
        return True
    
    # ==================== STATUS HISTORY QUERIES ====================
    
    def log_status_change(
        self,
        task_id: str,
        workflow_id: str,
        old_status: Optional[str],
        new_status: str,
        change_reason: Optional[str],
        change_type: str,
        changed_by: str,
        changed_by_type: str,
        context_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log a task status change"""
        query = """
            INSERT INTO task_status_history (
                task_id, workflow_id, old_status, new_status,
                change_reason, change_type, changed_by, changed_by_type, context_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        context_json = json.dumps(context_data) if context_data else None
        
        self.db.execute_query(
            query,
            (task_id, workflow_id, old_status, new_status, change_reason,
             change_type, changed_by, changed_by_type, context_json),
            fetch_all=False
        )
        return True
    
    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Get status change history for a task"""
        query = """
            SELECT * FROM task_status_history
            WHERE task_id = %s
            ORDER BY changed_at DESC
        """
        return self.db.execute_query(query, (task_id,))
    
    # ==================== UTILITY QUERIES ====================
    
    def get_workflow_progress(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow progress summary"""
        query = """
            SELECT * FROM v_workflow_progress
            WHERE workflow_id = %s
        """
        return self.db.execute_query(query, (workflow_id,), fetch_one=True)
    
    def get_department_active_tasks_view(self, department: str) -> List[Dict[str, Any]]:
        """Get active tasks for department with dependency status"""
        query = """
            SELECT * FROM v_department_active_tasks
            WHERE assigned_department = %s
            ORDER BY priority DESC, deadline ASC
        """
        return self.db.execute_query(query, (department,))


# Singleton instances
_db_connection = None
_task_queries = None


def get_db() -> DatabaseConnection:
    """Get database connection singleton"""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def get_queries() -> TaskQueries:
    """Get task queries singleton"""
    global _task_queries
    if _task_queries is None:
        _task_queries = TaskQueries(get_db())
    return _task_queries
