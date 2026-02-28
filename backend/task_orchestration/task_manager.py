"""
Task Manager - High-level task and workflow management

Provides business logic layer on top of database queries.
Handles validation, state transitions, and coordination.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .database import get_queries, TaskQueries
from .models import (
    WorkflowCreate, WorkflowResponse, WorkflowWithTasks,
    TaskCreate, TaskUpdate, TaskResponse, TaskWithDependencies,
    DependencyCreate, TaskStatus, WorkflowStatus,
    TaskStatusChange, WorkflowProgress
)

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages workflows and tasks with business logic
    """
    
    def __init__(self):
        self.queries: TaskQueries = get_queries()
        logger.info("✓ Task Manager initialized")
    
    # ==================== WORKFLOW OPERATIONS ====================
    
    def create_workflow(
        self, 
        workflow_data: WorkflowCreate,
        created_by: str = "system"
    ) -> WorkflowResponse:
        """
        Create a new workflow
        
        Args:
            workflow_data: Workflow creation data
            created_by: User/system creating the workflow
        
        Returns:
            Created workflow data
        """
        logger.info(f"Creating workflow: {workflow_data.workflow_name}")
        
        # Prepare data for database
        db_data = workflow_data.dict()
        db_data['created_by'] = created_by
        db_data['status'] = 'draft'  # All workflows start as draft
        
        # Create in database
        workflow_id = self.queries.create_workflow(db_data)
        
        if not workflow_id:
            raise Exception("Failed to create workflow")
        
        # Fetch and return created workflow
        workflow = self.queries.get_workflow(workflow_id)
        logger.info(f"✓ Workflow created: {workflow_id}")
        
        return WorkflowResponse(**workflow)
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowResponse]:
        """Get workflow by ID"""
        workflow = self.queries.get_workflow(workflow_id)
        return WorkflowResponse(**workflow) if workflow else None
    
    def get_workflow_with_tasks(self, workflow_id: str) -> Optional[WorkflowWithTasks]:
        """Get workflow with all its tasks"""
        workflow = self.queries.get_workflow(workflow_id)
        if not workflow:
            return None
        
        tasks = self.queries.get_workflow_tasks(workflow_id)
        progress = self.queries.get_workflow_progress(workflow_id)
        
        return WorkflowWithTasks(
            **workflow,
            tasks=[TaskResponse(**t) for t in tasks],
            total_tasks=progress.get('total_tasks', 0) if progress else 0,
            completed_tasks=progress.get('completed_tasks', 0) if progress else 0,
            in_progress_tasks=progress.get('in_progress_tasks', 0) if progress else 0,
            blocked_tasks=progress.get('blocked_tasks', 0) if progress else 0,
            completion_percentage=progress.get('completion_percentage', 0.0) if progress else 0.0
        )
    
    def update_workflow(
        self, 
        workflow_id: str, 
        update_data: Dict[str, Any],
        updated_by: str = "system"
    ) -> bool:
        """Update workflow fields"""
        update_data['last_modified_by'] = updated_by
        return self.queries.update_workflow(workflow_id, update_data)
    
    def update_workflow_status(
        self, 
        workflow_id: str, 
        new_status: WorkflowStatus,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update workflow status with validation
        
        Valid transitions:
        - draft → active
        - active → in_progress
        - in_progress → completed/blocked/cancelled
        - blocked → in_progress
        """
        workflow = self.queries.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        old_status = workflow['status']
        
        # Validate status transition
        valid_transitions = {
            'draft': ['active', 'cancelled'],
            'active': ['in_progress', 'cancelled'],
            'in_progress': ['completed', 'blocked', 'cancelled'],
            'blocked': ['in_progress', 'cancelled'],
            'completed': [],  # Terminal state
            'cancelled': []   # Terminal state
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(
                f"Invalid status transition: {old_status} → {new_status}"
            )
        
        # Update status
        update_data = {'status': new_status}
        
        if new_status == 'in_progress' and not workflow.get('actual_start_date'):
            update_data['actual_start_date'] = datetime.utcnow()
        
        if new_status in ['completed', 'cancelled']:
            update_data['actual_end_date'] = datetime.utcnow()
        
        success = self.queries.update_workflow(workflow_id, update_data)
        
        if success:
            logger.info(
                f"Workflow {workflow_id} status: {old_status} → {new_status}" +
                (f" ({reason})" if reason else "")
            )
        
        return success
    
    def list_workflows(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkflowResponse]:
        """List workflows with filters"""
        workflows = self.queries.list_workflows(department, status, limit, offset)
        return [WorkflowResponse(**w) for w in workflows]
    
    # ==================== TASK OPERATIONS ====================
    
    def create_task(
        self, 
        task_data: TaskCreate,
        auto_sequence: bool = True
    ) -> TaskResponse:
        """
        Create a new task
        
        Args:
            task_data: Task creation data
            auto_sequence: Automatically set sequence_order if not provided
        
        Returns:
            Created task data
        """
        logger.info(f"Creating task: {task_data.task_title}")
        
        # Prepare data for database
        db_data = task_data.dict()
        
        # Auto-assign sequence order if not provided
        if auto_sequence and not db_data.get('sequence_order'):
            existing_tasks = self.queries.get_workflow_tasks(str(task_data.workflow_id))
            db_data['sequence_order'] = len(existing_tasks) + 1
        
        # Create in database
        task_id = self.queries.create_task(db_data)
        
        if not task_id:
            raise Exception("Failed to create task")
        
        # Log status change
        self.queries.log_status_change(
            task_id=task_id,
            workflow_id=str(task_data.workflow_id),
            old_status=None,
            new_status='pending',
            change_reason="Task created",
            change_type="normal_progression",
            changed_by="system",
            changed_by_type="system"
        )
        
        # Fetch and return created task
        task = self.queries.get_task(task_id)
        logger.info(f"✓ Task created: {task_id}")
        
        return TaskResponse(**task)
    
    def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """Get task by ID"""
        task = self.queries.get_task(task_id)
        return TaskResponse(**task) if task else None
    
    def get_task_with_dependencies(self, task_id: str) -> Optional[TaskWithDependencies]:
        """Get task with dependency information"""
        task = self.queries.get_task(task_id)
        if not task:
            return None
        
        dependencies = self.queries.get_task_dependencies(task_id)
        dependent_tasks = self.queries.get_dependent_tasks(task_id)
        
        # Check if all dependencies are satisfied
        dependencies_satisfied = all(d['satisfied'] for d in dependencies) if dependencies else True
        
        # Task is ready if dependencies satisfied and status is pending
        is_ready = dependencies_satisfied and task['status'] in ['pending', 'ready']
        
        return TaskWithDependencies(
            **task,
            dependencies=dependencies,
            dependent_tasks=dependent_tasks,
            dependencies_satisfied=dependencies_satisfied,
            is_ready=is_ready
        )
    
    def update_task(
        self,
        task_id: str,
        update_data: TaskUpdate,
        updated_by: str = "system"
    ) -> bool:
        """Update task fields"""
        updates = update_data.dict(exclude_unset=True)
        
        # Handle status changes separately (requires validation)
        if 'status' in updates:
            new_status = updates.pop('status')
            self.update_task_status(task_id, new_status, updated_by=updated_by)
        
        if not updates:
            return True
        
        return self.queries.update_task(task_id, updates)
    
    def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        reason: Optional[str] = None,
        updated_by: str = "system",
        updated_by_type: str = "system"
    ) -> bool:
        """
        Update task status with validation and history logging
        
        Valid transitions:
        - pending → ready → in_progress → completed
        - Any → blocked/failed/cancelled
        - blocked → ready/in_progress
        """
        task = self.queries.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        old_status = task['status']
        
        if old_status == new_status:
            return True  # No change needed
        
        # Validate status transition
        valid_transitions = {
            'pending': ['ready', 'blocked', 'cancelled'],
            'ready': ['in_progress', 'blocked', 'cancelled'],
            'in_progress': ['completed', 'blocked', 'failed', 'cancelled', 'waiting_approval'],
            'waiting_approval': ['in_progress', 'blocked', 'cancelled'],
            'blocked': ['ready', 'in_progress', 'failed', 'cancelled'],
            'completed': [],  # Terminal
            'failed': ['in_progress', 'cancelled'],  # Can retry
            'cancelled': []   # Terminal
        }
        
        if new_status not in valid_transitions.get(old_status, []):
            logger.warning(f"Invalid transition: {old_status} → {new_status}")
            # Allow some transitions with warning (flexible for agents)
        
        # Prepare update
        update_data = {'status': new_status}
        
        if new_status == 'in_progress' and not task.get('actual_start_date'):
            update_data['actual_start_date'] = datetime.utcnow()
        
        if new_status in ['completed', 'failed', 'cancelled']:
            update_data['actual_end_date'] = datetime.utcnow()
            if new_status == 'completed':
                update_data['progress_percentage'] = 100
                update_data['completed_at'] = datetime.utcnow()
        
        # Update task
        success = self.queries.update_task(task_id, update_data)
        
        if success:
            # Log status change
            self.queries.log_status_change(
                task_id=task_id,
                workflow_id=str(task['workflow_id']),
                old_status=old_status,
                new_status=new_status,
                change_reason=reason,
                change_type=self._determine_change_type(old_status, new_status),
                changed_by=updated_by,
                changed_by_type=updated_by_type
            )
            
            logger.info(
                f"Task {task_id} status: {old_status} → {new_status}" +
                (f" ({reason})" if reason else "")
            )
            
            # Check if dependent tasks can now proceed
            if new_status == 'completed':
                self._check_dependent_tasks(task_id)
        
        return success
    
    def _determine_change_type(self, old_status: str, new_status: str) -> str:
        """Determine the type of status change"""
        if new_status in ['blocked', 'failed']:
            return 'blocked'
        elif new_status == 'cancelled':
            return 'cancelled'
        elif old_status == 'blocked' and new_status in ['ready', 'in_progress']:
            return 'normal_progression'
        else:
            return 'normal_progression'
    
    def _check_dependent_tasks(self, completed_task_id: str):
        """Check if any dependent tasks are now ready"""
        dependent_tasks = self.queries.get_dependent_tasks(completed_task_id)
        
        for dep in dependent_tasks:
            # Update dependency as satisfied
            self.queries.update_dependency_satisfied(dep['dependency_id'], True)
            
            # Check if task is now ready
            task_deps = self.queries.get_task_dependencies(dep['task_id'])
            all_satisfied = all(d['satisfied'] for d in task_deps)
            
            if all_satisfied and dep['task_status'] == 'pending':
                # Update task to ready
                self.update_task_status(
                    str(dep['task_id']),
                    TaskStatus.READY,
                    reason=f"All dependencies satisfied (last: {completed_task_id})",
                    updated_by="system",
                    updated_by_type="automation"
                )
                
                # TODO: Send notification to assigned department
                logger.info(f"✓ Task {dep['task_id']} is now ready")
    
    def get_department_tasks(
        self,
        department: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[TaskResponse]:
        """Get tasks assigned to a department"""
        tasks = self.queries.get_department_tasks(department, status, limit)
        return [TaskResponse(**t) for t in tasks]
    
    def get_ready_tasks_for_department(self, department: str) -> List[TaskWithDependencies]:
        """Get tasks that are ready for a department to work on"""
        # Use the view that checks dependency satisfaction
        ready_tasks = self.queries.get_department_active_tasks_view(department)
        
        result = []
        for task_data in ready_tasks:
            if task_data['dependencies_satisfied'] and task_data['status'] in ['pending', 'ready']:
                task = self.get_task_with_dependencies(str(task_data['task_id']))
                if task:
                    result.append(task)
        
        return result
    
    # ==================== DEPENDENCY OPERATIONS ====================
    
    def create_dependency(self, dependency_data: DependencyCreate) -> str:
        """
        Create a task dependency with circular dependency check
        
        Args:
            dependency_data: Dependency creation data
        
        Returns:
            Dependency ID
        
        Raises:
            ValueError: If circular dependency would be created
        """
        # Check for circular dependency
        is_circular = self.queries.check_circular_dependency(
            str(dependency_data.task_id),
            str(dependency_data.depends_on_task_id)
        )
        
        if is_circular:
            raise ValueError(
                f"Cannot create dependency: would create circular dependency chain"
            )
        
        # Create dependency
        dependency_id = self.queries.create_dependency(dependency_data.dict())
        
        if not dependency_id:
            raise Exception("Failed to create dependency")
        
        logger.info(
            f"✓ Dependency created: {dependency_data.task_id} depends on "
            f"{dependency_data.depends_on_task_id} ({dependency_data.dependency_type})"
        )
        
        return dependency_id
    
    def check_task_ready(self, task_id: str) -> bool:
        """Check if a task is ready (all dependencies satisfied)"""
        dependencies = self.queries.get_task_dependencies(task_id)
        return all(d['satisfied'] for d in dependencies) if dependencies else True
    
    # ==================== PROGRESS TRACKING ====================
    
    def get_workflow_progress(self, workflow_id: str) -> Optional[WorkflowProgress]:
        """Get workflow progress summary"""
        progress = self.queries.get_workflow_progress(workflow_id)
        return WorkflowProgress(**progress) if progress else None
    
    def update_task_progress(
        self,
        task_id: str,
        progress_percentage: int,
        notes: Optional[str] = None
    ) -> bool:
        """Update task progress percentage"""
        if not (0 <= progress_percentage <= 100):
            raise ValueError("Progress must be between 0 and 100")
        
        return self.queries.update_task(task_id, {
            'progress_percentage': progress_percentage
        })
    
    # ==================== UTILITY METHODS ====================
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow and all its tasks (CASCADE)
        Only allowed if workflow is in draft or cancelled status
        """
        workflow = self.queries.get_workflow(workflow_id)
        if not workflow:
            return False
        
        if workflow['status'] not in ['draft', 'cancelled']:
            raise ValueError(
                f"Cannot delete workflow with status '{workflow['status']}'. "
                f"Cancel it first."
            )
        
        # Database CASCADE will handle task deletion
        # For now, just mark as deleted (soft delete)
        return self.queries.update_workflow(workflow_id, {
            'status': 'cancelled',
            'last_modified_by': 'system'
        })
    
    def get_task_history(self, task_id: str) -> List[Dict[str, Any]]:
        """Get complete status change history for a task"""
        return self.queries.get_task_history(task_id)


# Singleton instance
_task_manager = None


def get_task_manager() -> TaskManager:
    """Get task manager singleton"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
