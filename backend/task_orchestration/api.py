"""
Task Orchestration API Endpoints

FastAPI routes for task management, workflows, contingency planning,
knowledge graphs, and notifications.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import UUID4

import logging
logger = logging.getLogger(__name__)

from .models import (
    WorkflowCreate, WorkflowResponse, WorkflowUpdate,
    TaskCreate, TaskResponse, TaskUpdate, TaskWithDependencies,
    DependencyCreate,
    ContingencyPlanCreate, ContingencyPlanResponse,
    NotificationResponse
)
from .task_manager import get_task_manager, TaskManager
from .workflow_engine import get_workflow_engine, WorkflowEngine
from .contingency_planner import get_contingency_planner, ContingencyPlanner
from .knowledge_graph import get_kg_generator, KnowledgeGraphGenerator
from .notification_service import get_notification_service, NotificationService

# Create router
router = APIRouter(prefix="/api/task-orchestration", tags=["Task Orchestration"])


# Dependency injection
def get_tm() -> TaskManager:
    return get_task_manager()


def get_engine() -> WorkflowEngine:
    return get_workflow_engine()


def get_planner() -> ContingencyPlanner:
    return get_contingency_planner()


def get_graph() -> KnowledgeGraphGenerator:
    return get_kg_generator()


def get_notif() -> NotificationService:
    return get_notification_service()


# ==================== WORKFLOW ENDPOINTS ====================

@router.post("/workflows", response_model=WorkflowResponse, status_code=201)
async def create_workflow(
    workflow: WorkflowCreate,
    tm: TaskManager = Depends(get_tm)
):
    """Create a new workflow"""
    try:
        result = tm.create_workflow(workflow)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create workflow")
        return result
    except Exception as e:
        logger.error(f"Error creating workflow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/generate-tasks")
async def generate_tasks_ai(
    workflow_data: Dict[str, Any],
    planner: ContingencyPlanner = Depends(get_planner)
):
    """
    Generate task breakdown using AI based on workflow details
    
    Returns suggested tasks with dependencies that can be reviewed and edited
    """
    try:
        if not planner.llm_client:
            raise HTTPException(status_code=503, detail="LLM service not available")
        
        # Extract workflow details
        workflow_name = workflow_data.get('workflow_name', '')
        workflow_desc = workflow_data.get('workflow_description', '')
        department = workflow_data.get('department', '')
        priority = workflow_data.get('priority', 'medium')
        
        # Build prompt for LLM
        prompt = f"""You are an expert city governance operations planner. Generate a detailed task breakdown for the following workflow.

Workflow: {workflow_name}
Description: {workflow_desc}
Department: {department}
Priority: {priority}

Generate 5-10 specific, actionable tasks that:
1. Break down the workflow into logical steps
2. Include realistic time estimates (in hours)
3. Assign appropriate departments (water, fire, engineering, health, finance, sanitation)
4. Set dependencies between tasks (which tasks must complete before others can start)
5. Include cost estimates where relevant

Return ONLY a valid JSON array of tasks in this exact format:
[
  {{
    "task_title": "Task name",
    "task_description": "Detailed description",
    "assigned_department": "department_name",
    "priority": "low|medium|high|critical",
    "estimated_duration_hours": 4.0,
    "estimated_cost": 1000.0,
    "depends_on": []
  }},
  {{
    "task_title": "Second task",
    "task_description": "Description",
    "assigned_department": "department_name",
    "priority": "medium",
    "estimated_duration_hours": 2.0,
    "estimated_cost": 500.0,
    "depends_on": [0]
  }}
]

The "depends_on" field contains array indices of tasks that must complete first.
Generate comprehensive, realistic tasks for city operations."""

        # Call LLM
        response = planner.llm_client.invoke(prompt)
        content = response.content.strip()
        
        # Extract JSON from response
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        # Parse tasks
        tasks = json.loads(content)
        
        # Validate and enhance tasks
        for i, task in enumerate(tasks):
            task['task_id'] = f"temp_{i}"  # Temporary ID for frontend
            task['task_status'] = 'pending'
            task['assigned_to'] = task.get('assigned_to', '')
            
            # Ensure all required fields exist
            if 'estimated_duration_hours' not in task:
                task['estimated_duration_hours'] = 4.0
            if 'estimated_cost' not in task:
                task['estimated_cost'] = 0.0
            if 'depends_on' not in task:
                task['depends_on'] = []
        
        return {
            "success": True,
            "tasks": tasks,
            "message": f"Generated {len(tasks)} tasks using AI"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response: {e}")
        raise HTTPException(status_code=500, detail="AI generated invalid task format")
    except Exception as e:
        logger.error(f"AI task generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str,
    tm: TaskManager = Depends(get_tm)
):
    """Get workflow by ID"""
    workflow = tm.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    status: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    tm: TaskManager = Depends(get_tm)
):
    """List workflows with optional filters"""
    workflows = tm.list_workflows(status=status, department=department, limit=limit)
    return workflows


@router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str,
    update_data: WorkflowUpdate,
    tm: TaskManager = Depends(get_tm)
):
    """Update workflow"""
    workflow = tm.update_workflow(workflow_id, update_data.dict(exclude_unset=True))
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


@router.post("/workflows/{workflow_id}/start")
async def start_workflow(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_engine)
):
    """Start workflow execution"""
    try:
        result = engine.start_workflow(workflow_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workflows/{workflow_id}/progress")
async def get_workflow_progress(
    workflow_id: str,
    tm: TaskManager = Depends(get_tm)
):
    """Get workflow progress statistics"""
    progress = tm.get_workflow_progress(workflow_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return progress


@router.get("/workflows/{workflow_id}/dependencies")
async def resolve_workflow_dependencies(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_engine)
):
    """Resolve workflow dependencies and get execution order"""
    try:
        result = engine.resolve_dependencies(workflow_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== TASK ENDPOINTS ====================

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(
    task: TaskCreate,
    tm: TaskManager = Depends(get_tm)
):
    """Create a new task"""
    try:
        result = tm.create_task(task)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create task")
        return result
    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}", response_model=TaskWithDependencies)
async def get_task(
    task_id: str,
    tm: TaskManager = Depends(get_tm)
):
    """Get task by ID with dependencies"""
    task = tm.get_task_with_dependencies(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    workflow_id: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    tm: TaskManager = Depends(get_tm)
):
    """List tasks with optional filters"""
    if workflow_id:
        tasks = tm.get_workflow_tasks(workflow_id)
    else:
        # Get tasks from database with filters
        from .database import get_db
        db = get_db()
        
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if department:
            query += " AND assigned_department = %s"
            params.append(department)
        
        if status:
            query += " AND task_status = %s"
            params.append(status)
        
        query += f" ORDER BY created_at DESC LIMIT {limit}"
        
        tasks = db.execute_query(query, tuple(params) if params else None)
    
    return tasks[:limit]


@router.get("/tasks/ongoing/{department}")
async def get_ongoing_tasks(
    department: str,
    limit: int = Query(50, ge=1, le=200),
    tm: TaskManager = Depends(get_tm)
):
    """
    Get ongoing (in_progress) tasks for a department
    Used by Task Orchestration Dashboard to show active tasks
    """
    try:
        with tm.queries.db.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    t.*,
                    w.workflow_name,
                    w.workflow_type
                FROM tasks t
                JOIN workflows w ON t.workflow_id = w.workflow_id
                WHERE t.assigned_department = %s
                  AND t.status = 'in_progress'
                ORDER BY t.updated_at DESC
                LIMIT %s
            """, (department, limit))
            
            tasks = cursor.fetchall()
        
        return {
            'department': department,
            'tasks': tasks,
            'count': len(tasks)
        }
    except Exception as e:
        logger.error(f"Error fetching ongoing tasks for {department}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    update_data: TaskUpdate,
    tm: TaskManager = Depends(get_tm),
    notif: NotificationService = Depends(get_notif)
):
    """Update task"""
    try:
        # Get old status
        old_task = tm.queries.get_task(task_id)
        old_status = old_task['task_status'] if old_task else None
        
        # Update task
        task = tm.update_task(task_id, update_data.dict(exclude_unset=True))
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Send notifications for status changes
        new_status = task['task_status']
        
        if old_status != new_status:
            if new_status == 'ready':
                notif.notify_task_ready(task_id)
            elif new_status == 'blocked':
                notif.notify_task_blocked(task_id, update_data.notes or "Task blocked")
        
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/status")
async def update_task_status(
    task_id: str,
    new_status: str,
    notes: Optional[str] = None,
    tm: TaskManager = Depends(get_tm),
    notif: NotificationService = Depends(get_notif)
):
    """Update task status"""
    try:
        success = tm.update_task_status(task_id, new_status, notes)
        
        if not success:
            raise HTTPException(status_code=400, detail="Invalid status transition")
        
        # Send notifications
        if new_status == 'ready':
            notif.notify_task_ready(task_id)
        elif new_status == 'blocked':
            notif.notify_task_blocked(task_id, notes or "Task blocked")
        elif new_status == 'completed':
            # Check if this unblocks other tasks
            task = tm.queries.get_task(task_id)
            if task:
                # Find tasks that depend on this one
                from .database import get_db
                db = get_db()
                
                query = """
                    SELECT DISTINCT task_id
                    FROM task_dependencies
                    WHERE depends_on_task_id = %s
                """
                dependent_tasks = db.execute_query(query, (task_id,))
                
                for dep_task in dependent_tasks:
                    dep_task_id = str(dep_task['task_id'])
                    notif.notify_dependency_completed(dep_task_id, task_id)
        
        return {"success": True, "task_id": task_id, "new_status": new_status}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/dependencies")
async def get_task_dependencies(
    task_id: str,
    engine: WorkflowEngine = Depends(get_engine)
):
    """Get task dependency analysis"""
    try:
        analysis = engine.analyze_task_dependencies(task_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/departments/{department}/tasks")
async def get_department_ready_tasks(
    department: str,
    tm: TaskManager = Depends(get_tm)
):
    """Get tasks ready for execution by department"""
    tasks = tm.get_ready_tasks_for_department(department)
    return {"department": department, "ready_tasks": tasks}


# ==================== DEPENDENCY ENDPOINTS ====================

@router.post("/dependencies", status_code=201)
async def create_dependency(
    dependency: DependencyCreate,
    tm: TaskManager = Depends(get_tm)
):
    """Create task dependency"""
    try:
        success = tm.create_dependency(dependency)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create dependency (circular?)")
        
        return {"success": True, "message": "Dependency created"}
    
    except Exception as e:
        logger.error(f"Error creating dependency: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CONTINGENCY PLAN ENDPOINTS ====================

@router.post("/tasks/{task_id}/contingency-plans")
async def generate_contingency_plans(
    task_id: str,
    failure_reason: str,
    num_plans: int = Query(3, ge=1, le=5),
    planner: ContingencyPlanner = Depends(get_planner)
):
    """Generate contingency plans for a task"""
    try:
        plans = planner.generate_contingency_plans(
            task_id=task_id,
            failure_reason=failure_reason,
            num_plans=num_plans
        )
        return {"task_id": task_id, "plans": plans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/contingency-plans", response_model=List[ContingencyPlanResponse])
async def get_task_contingency_plans(
    task_id: str,
    planner: ContingencyPlanner = Depends(get_planner)
):
    """Get all contingency plans for a task"""
    plans = planner.get_task_plans(task_id)
    return plans


@router.post("/contingency-plans/{plan_id}/activate")
async def activate_contingency_plan(
    plan_id: str,
    activated_by: str,
    reason: Optional[str] = None,
    planner: ContingencyPlanner = Depends(get_planner),
    notif: NotificationService = Depends(get_notif)
):
    """Activate a contingency plan"""
    try:
        success = planner.activate_contingency_plan(plan_id, activated_by, reason)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to activate plan")
        
        # Notify about plan activation
        # TODO: Send notification to relevant department
        
        return {"success": True, "plan_id": plan_id, "activated_by": activated_by}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contingency-plans/rank")
async def rank_contingency_plans(
    plan_ids: List[str],
    criteria: Optional[Dict[str, float]] = None,
    planner: ContingencyPlanner = Depends(get_planner)
):
    """Rank contingency plans by desirability"""
    # Get all plans
    all_plans = []
    for plan_id in plan_ids:
        # TODO: Get plan by ID from database
        pass
    
    ranked = planner.rank_plans(all_plans, criteria)
    return {"ranked_plans": ranked}


# ==================== KNOWLEDGE GRAPH ENDPOINTS ====================

@router.get("/workflows/{workflow_id}/graph")
async def get_workflow_graph(
    workflow_id: str,
    regenerate: bool = Query(False),
    kg: KnowledgeGraphGenerator = Depends(get_graph)
):
    """Get workflow knowledge graph"""
    try:
        if regenerate:
            graph = kg.generate_workflow_graph(workflow_id)
        else:
            graph = kg.get_workflow_graph(workflow_id)
            
            # Generate if not exists
            if not graph:
                graph = kg.generate_workflow_graph(workflow_id)
        
        return graph
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/graph/analysis")
async def analyze_workflow_graph(
    workflow_id: str,
    kg: KnowledgeGraphGenerator = Depends(get_graph)
):
    """Analyze workflow graph structure"""
    try:
        analysis = kg.analyze_graph_structure(workflow_id)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NOTIFICATION ENDPOINTS ====================

@router.get("/departments/{department}/notifications", response_model=List[NotificationResponse])
async def get_department_notifications(
    department: str,
    include_read: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    notif: NotificationService = Depends(get_notif)
):
    """Get notifications for department"""
    notifications = notif.get_department_notifications(
        department=department,
        include_read=include_read,
        limit=limit
    )
    return notifications


@router.get("/departments/{department}/notifications/unread-count")
async def get_unread_notification_count(
    department: str,
    notif: NotificationService = Depends(get_notif)
):
    """Get count of unread notifications"""
    count = notif.get_unread_count(department)
    return {"department": department, "unread_count": count}


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    notif: NotificationService = Depends(get_notif)
):
    """Mark notification as read"""
    success = notif.mark_notification_read(notification_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True, "notification_id": notification_id}


@router.post("/notifications/check-deadlines")
async def check_deadline_reminders(
    notif: NotificationService = Depends(get_notif)
):
    """Manually trigger deadline reminder check (normally scheduled)"""
    count = notif.check_and_send_deadline_reminders()
    return {"reminders_sent": count}


# ==================== OPTIMIZATION ENDPOINTS ====================

@router.get("/workflows/{workflow_id}/optimizations")
async def get_workflow_optimizations(
    workflow_id: str,
    engine: WorkflowEngine = Depends(get_engine)
):
    """Get workflow optimization suggestions"""
    try:
        suggestions = engine.suggest_workflow_optimizations(workflow_id)
        return {"workflow_id": workflow_id, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}/next-tasks")
async def get_next_tasks_to_execute(
    workflow_id: str,
    limit: int = Query(10, ge=1, le=50),
    engine: WorkflowEngine = Depends(get_engine)
):
    """Get prioritized list of next tasks to execute"""
    try:
        tasks = engine.get_next_tasks_to_execute(workflow_id, limit)
        return {"workflow_id": workflow_id, "recommended_tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "task-orchestration",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== RECENT ACTIVITIES ====================

@router.get("/recent-activities/{department}")
async def get_recent_activities(
    department: str,
    limit: int = Query(10, ge=1, le=50),
    tm: TaskManager = Depends(get_tm)
):
    """
    Get recent workflow and task activities for a department
    Returns recent status changes, new workflows, task completions, etc.
    """
    try:
        activities = []
        
        # Get database cursor using context manager (returns RealDictCursor by default)
        with tm.queries.db.get_cursor() as cursor:
            # Query recent task updates for department
            cursor.execute("""
                SELECT 
                    t.task_id,
                    t.task_title,
                    t.status,
                    t.updated_at,
                    t.workflow_id,
                    w.workflow_name,
                    t.assigned_department,
                    t.priority
                FROM tasks t
                JOIN workflows w ON t.workflow_id = w.workflow_id
                WHERE t.assigned_department = %s
                ORDER BY t.updated_at DESC
                LIMIT %s
            """, (department, limit * 2))
            
            recent_tasks = cursor.fetchall()
        
        # Use separate cursor for second query - only get completed workflows
        with tm.queries.db.get_cursor() as cursor:
            # Query recent workflow updates (only completed ones)
            cursor.execute("""
                SELECT 
                    workflow_id,
                    workflow_name,
                    status,
                    priority,
                    updated_at,
                    initiated_by_department
                FROM workflows
                WHERE status = 'completed'
                  AND (
                    initiated_by_department = %s
                    OR workflow_id IN (
                        SELECT DISTINCT workflow_id 
                        FROM tasks 
                        WHERE assigned_department = %s
                    )
                  )
                ORDER BY updated_at DESC
                LIMIT %s
            """, (department, department, limit))
            
            recent_workflows = cursor.fetchall()
        
        # Process recent tasks into activities
        for task in recent_tasks:
            activity_type = 'info'
            icon = 'Activity'
            
            if task['status'] == 'completed':
                activity_type = 'success'
                icon = 'CheckCircle'
                message = f"Task completed: {task['task_title']}"
            elif task['status'] == 'in_progress':
                activity_type = 'progress'
                icon = 'Clock'
                message = f"Task started: {task['task_title']}"
            elif task['status'] == 'blocked':
                activity_type = 'warning'
                icon = 'AlertCircle'
                message = f"Task blocked: {task['task_title']}"
            else:
                icon = 'Activity'
                message = f"Task updated: {task['task_title']}"
            
            # Calculate time ago
            updated = task['updated_at']
            if isinstance(updated, str):
                updated = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            elif updated.tzinfo is None:
                # Make timezone aware if naive
                updated = updated.replace(tzinfo=timezone.utc)
                
            time_diff = datetime.now(timezone.utc) - updated
            
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif time_diff.seconds >= 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes} min ago"
            else:
                time_ago = "just now"
            
            activities.append({
                'id': str(task['task_id']),
                'message': message,
                'time': time_ago,
                'type': activity_type,
                'icon': icon,
                'workflow_name': task['workflow_name'],
                'workflow_id': str(task['workflow_id']),
                'priority': task.get('priority', 'medium'),
                'timestamp': updated.isoformat()
            })
        
        # Process workflows into activities
        for workflow in recent_workflows:
            activity_type = 'info'
            icon = 'Workflow'
            
            if workflow['status'] == 'completed':
                activity_type = 'success'
                icon = 'CheckCircle'
                message = f"Workflow completed: {workflow['workflow_name']}"
            elif workflow['status'] == 'active' or workflow['status'] == 'in_progress':
                activity_type = 'progress'
                icon = 'PlayCircle'
                message = f"Workflow active: {workflow['workflow_name']}"
            elif workflow['status'] == 'draft':
                activity_type = 'info'
                icon = 'FileText'
                message = f"Workflow created: {workflow['workflow_name']}"
            else:
                message = f"Workflow {workflow['status']}: {workflow['workflow_name']}"
            
            # Calculate time ago
            updated = workflow['updated_at']
            if isinstance(updated, str):
                updated = datetime.fromisoformat(updated.replace('Z', '+00:00'))
            elif updated.tzinfo is None:
                # Make timezone aware if naive
                updated = updated.replace(tzinfo=timezone.utc)
                
            time_diff = datetime.now(timezone.utc) - updated
            
            if time_diff.days > 0:
                time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif time_diff.seconds >= 60:
                minutes = time_diff.seconds // 60
                time_ago = f"{minutes} min ago"
            else:
                time_ago = "just now"
            
            activities.append({
                'id': str(workflow['workflow_id']),
                'message': message,
                'time': time_ago,
                'type': activity_type,
                'icon': icon,
                'workflow_name': workflow['workflow_name'],
                'workflow_id': str(workflow['workflow_id']),
                'priority': workflow.get('priority', 'medium'),
                'timestamp': updated.isoformat()
            })
        
        # Sort by timestamp and limit
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        activities = activities[:limit]
        
        return {
            'department': department,
            'activities': activities,
            'count': len(activities)
        }
        
    except Exception as e:
        logger.error(f"Error fetching recent activities for {department}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
