"""
Task Orchestration API Endpoints

FastAPI routes for task management, workflows, contingency planning,
knowledge graphs, and notifications.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/create-with-ai", response_model=Dict[str, Any], status_code=201)
async def create_workflow_with_ai(
    data: Dict[str, Any],
    tm: TaskManager = Depends(get_tm),
    kg: KnowledgeGraphGenerator = Depends(get_graph),
):
    """
    Create a complete workflow with AI-generated tasks, dependencies, and knowledge graph
    
    Request body should contain:
    - workflow: WorkflowCreate data
    - tasks: Array of AI-generated tasks from /workflows/generate-tasks
    """
    try:
        workflow_data = data.get('workflow')
        ai_tasks = data.get('tasks', [])
        
        if not workflow_data:
            raise HTTPException(status_code=400, detail="Missing workflow data")
        
        # Create the workflow
        workflow = WorkflowCreate(**workflow_data)
        created_workflow = tm.create_workflow(workflow)
        workflow_id = created_workflow.workflow_id
        
        logger.info(f"Creating workflow {workflow_id} with {len(ai_tasks)} AI-generated tasks")
        
        # Track created task IDs for dependency mapping
        task_id_mapping = {}  # temp_id -> actual task_id
        created_tasks = []
        
        # Create all tasks first (without dependencies)
        for i, task_data in enumerate(ai_tasks):
            temp_id = task_data.get('task_id', f'temp_{i}')
            
            # Prepare task creation data
            task_create = TaskCreate(
                workflow_id=workflow_id,
                task_title=task_data.get('task_title', f'Task {i+1}'),
                task_description=task_data.get('task_description', ''),
                task_type=task_data.get('task_type', 'operational'),
                assigned_department=task_data.get('assigned_department', workflow_data.get('initiated_by_department')),
                priority=task_data.get('priority', 'medium'),
                estimated_duration_hours=float(task_data.get('estimated_duration_hours', 4.0)),
                estimated_cost=float(task_data.get('estimated_cost', 0.0)),
                status='pending',
                sequence_order=i,
                tags=task_data.get('tags', []),
                metadata={'ai_generated': True, 'original_index': i}
            )
            
            created_task = tm.create_task(task_create)
            task_id_mapping[temp_id] = created_task.task_id
            task_id_mapping[i] = created_task.task_id  # Also map by index
            created_tasks.append(created_task)
        
        # Now create dependencies
        dependencies_created = []
        for i, task_data in enumerate(ai_tasks):
            depends_on = task_data.get('depends_on', [])
            current_task_id = task_id_mapping[i]
            
            for dep_index in depends_on:
                if dep_index in task_id_mapping:
                    dep_create = DependencyCreate(
                        task_id=current_task_id,
                        depends_on_task_id=task_id_mapping[dep_index],
                        dependency_type='finish_to_start',
                        is_hard_dependency=True
                    )
                    dependency = tm.create_dependency(dep_create)
                    dependencies_created.append(dependency)
        
        # Generate knowledge graph
        try:
            graph_data = kg.generate_workflow_graph(workflow_id)
        except Exception as e:
            logger.warning(f"Knowledge graph generation failed: {e}")
            graph_data = None
        
        logger.info(f"✓ Workflow {workflow_id} created with {len(created_tasks)} tasks and {len(dependencies_created)} dependencies")
        
        return {
            "workflow": created_workflow,
            "tasks": created_tasks,
            "dependencies_count": len(dependencies_created),
            "knowledge_graph": graph_data,
            "message": f"Successfully created workflow with {len(created_tasks)} AI-generated tasks"
        }
        
    except Exception as e:
        logger.error(f"Failed to create workflow with AI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/generate-tasks")
async def generate_tasks_ai(
    workflow_data: Dict[str, Any],
    planner: ContingencyPlanner = Depends(get_planner),
    tm: TaskManager = Depends(get_tm)
):
    """
    Generate task breakdown using AI based on workflow details and database context
    
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
        
        # Gather database context for more realistic planning
        database_context = await _gather_database_context(department, tm)
        
        # Build enhanced prompt for LLM with database context
        prompt = f"""You are an expert city governance operations planner. Generate a detailed task breakdown for the following workflow using real city data.

Workflow: {workflow_name}
Description: {workflow_desc}
Department: {department}
Priority: {priority}

CURRENT CITY DATA CONTEXT:
{database_context}

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


@router.get("/workflows/{workflow_id}/detailed")
async def get_workflow_detailed(
    workflow_id: str,
    tm: TaskManager = Depends(get_tm),
    engine: WorkflowEngine = Depends(get_engine)
):
    """
    Get detailed workflow information including:
    - All tasks with dependencies
    - Progress metrics
    - Stalled tasks with reasons
    - Blocking departments
    """
    try:
        # Get workflow with tasks
        workflow = tm.get_workflow_with_tasks(workflow_id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Get all tasks
        tasks = tm.queries.get_workflow_tasks(workflow_id)
        
        # Analyze each task for blocking/stall reasons
        task_analysis = []
        stalled_tasks = []
        blocking_departments = {}
        
        for task in tasks:
            task_id = task['task_id']
            task_status = task['status']
            assigned_dept = task.get('assigned_department', 'Unknown')
            
            # Get dependencies
            dependencies = tm.queries.get_task_dependencies(task_id)
            blocking_deps = []
            is_blocked = False
            stall_reason = None
            
            # Check if task is blocked by dependencies
            if task_status in ['pending', 'ready']:
                for dep in dependencies:
                    dep_task = tm.queries.get_task(dep['depends_on_task_id'])
                    if dep_task and dep_task['status'] not in ['completed', 'cancelled']:
                        blocking_deps.append({
                            'task_id': dep_task['task_id'],
                            'task_title': dep_task['task_title'],
                            'status': dep_task['status'],
                            'department': dep_task.get('assigned_department', 'Unknown')
                        })
                        is_blocked = True
                        
                        # Track blocking departments
                        blocking_dept = dep_task.get('assigned_department', 'Unknown')
                        if blocking_dept not in blocking_departments:
                            blocking_departments[blocking_dept] = 0
                        blocking_departments[blocking_dept] += 1
            
            # Determine stall reason
            if is_blocked:
                stall_reason = f"Waiting on {len(blocking_deps)} dependent task(s)"
            elif task_status == 'in_progress':
                # Check if task has been in progress too long
                if task.get('actual_start_date'):
                    from datetime import datetime, timedelta
                    start_date = task['actual_start_date']
                    if isinstance(start_date, str):
                        start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    expected_duration = task.get('estimated_duration_hours', 24)
                    if datetime.now() > start_date + timedelta(hours=expected_duration * 1.5):
                        stall_reason = "Exceeding estimated duration"
                        stalled_tasks.append({
                            'task': task,
                            'reason': stall_reason,
                            'department': assigned_dept
                        })
            elif task_status == 'blocked':
                stall_reason = "Manually blocked"
                stalled_tasks.append({
                    'task': task,
                    'reason': stall_reason,
                    'department': assigned_dept
                })
            
            task_analysis.append({
                **task,
                'is_blocked': is_blocked,
                'blocking_dependencies': blocking_deps,
                'stall_reason': stall_reason
            })
        
        # Calculate progress statistics
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks if t['status'] == 'completed'])
        in_progress_tasks = len([t for t in tasks if t['status'] == 'in_progress'])
        pending_tasks = len([t for t in tasks if t['status'] in ['pending', 'ready']])
        blocked_tasks = len([t for t in task_analysis if t.get('is_blocked', False) or t['status'] == 'blocked'])
        
        # Group tasks by status
        tasks_by_status = {
            'completed': [t for t in task_analysis if t['status'] == 'completed'],
            'in_progress': [t for t in task_analysis if t['status'] == 'in_progress'],
            'ready': [t for t in task_analysis if t['status'] == 'ready'],
            'pending': [t for t in task_analysis if t['status'] == 'pending'],
            'blocked': [t for t in task_analysis if t.get('is_blocked', False) or t['status'] == 'blocked'],
            'cancelled': [t for t in task_analysis if t['status'] == 'cancelled']
        }
        
        # Department involvement
        dept_involvement = {}
        for task in tasks:
            dept = task.get('assigned_department', 'Unknown')
            if dept not in dept_involvement:
                dept_involvement[dept] = {
                    'total_tasks': 0,
                    'completed': 0,
                    'in_progress': 0,
                    'pending': 0,
                    'blocked': 0
                }
            dept_involvement[dept]['total_tasks'] += 1
            status = task['status']
            if status in dept_involvement[dept]:
                dept_involvement[dept][status] += 1
        
        return {
            'workflow': workflow.dict(),
            'progress': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'pending_tasks': pending_tasks,
                'blocked_tasks': blocked_tasks,
                'completion_percentage': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                'tasks_remaining': total_tasks - completed_tasks
            },
            'tasks': task_analysis,
            'tasks_by_status': tasks_by_status,
            'stalled_tasks': stalled_tasks,
            'blocking_departments': [
                {'department': dept, 'blocking_count': count}
                for dept, count in sorted(blocking_departments.items(), key=lambda x: x[1], reverse=True)
            ],
            'department_involvement': dept_involvement
        }
        
    except Exception as e:
        logger.error(f"Error getting detailed workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@router.get("/workflows/department/{department}")
async def get_department_workflows_with_tasks(
    department: str,
    status: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    tm: TaskManager = Depends(get_tm)
):
    """
    Get workflows and tasks for a specific department
    
    Returns workflows where:
    - The workflow is initiated by the department, OR
    - The department has tasks assigned to them
    
    Includes task details showing what each department needs to do
    """
    try:
        # Get workflows initiated by or involving this department
        workflows = tm.list_workflows(department=department, status=status, limit=limit)
        
        result = []
        for workflow in workflows:
            # Get all tasks for this workflow
            workflow_with_tasks = tm.get_workflow_with_tasks(workflow.workflow_id)
            
            if workflow_with_tasks:
                # Filter tasks to show only those assigned to this department
                department_tasks = [
                    task for task in workflow_with_tasks.tasks 
                    if task.assigned_department == department
                ]
                
                result.append({
                    "workflow": workflow,
                    "department_tasks": department_tasks,
                    "total_tasks": workflow_with_tasks.total_tasks,
                    "department_task_count": len(department_tasks),
                    "completion_percentage": workflow_with_tasks.completion_percentage
                })
        
        return {
            "department": department,
            "workflows": result,
            "total_workflows": len(result),
            "total_department_tasks": sum(w["department_task_count"] for w in result)
        }
        
    except Exception as e:
        logger.error(f"Failed to get department workflows: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        result = tm.create_task(task.dict())
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create task")
        return result
    except Exception as e:
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
        success = tm.create_dependency(dependency.dict())
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create dependency (circular?)")
        
        return {"success": True, "message": "Dependency created"}
    
    except Exception as e:
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


@router.get("/workflows/by-department/{department}")
async def get_workflows_by_department(
    department: str,
    status: Optional[str] = Query(None),
    tm: TaskManager = Depends(get_tm)
):
    """
    Get workflows that involve a specific department
    Returns workflows where the department is initiator or has assigned tasks
    """
    try:
        workflows = tm.queries.get_workflows_by_department(department, status)
        
        # Enhance with task counts and involvement details
        enhanced_workflows = []
        for workflow in workflows:
            workflow_id = workflow['workflow_id']
            
            # Get tasks for this department
            dept_tasks = tm.queries.get_tasks_by_department(workflow_id, department)
            all_tasks = tm.queries.get_workflow_tasks(workflow_id)
            
            # Calculate involvement
            is_initiator = workflow.get('initiated_by_department') == department
            has_tasks = len(dept_tasks) > 0
            involvement_percentage = (len(dept_tasks) / len(all_tasks) * 100) if all_tasks else 0
            
            enhanced_workflow = {
                **workflow,
                'department_involvement': {
                    'is_initiator': is_initiator,
                    'has_tasks': has_tasks,
                    'assigned_tasks_count': len(dept_tasks),
                    'total_tasks_count': len(all_tasks),
                    'involvement_percentage': round(involvement_percentage, 1)
                },
                'department_tasks': dept_tasks
            }
            enhanced_workflows.append(enhanced_workflow)
        
        return {
            "department": department,
            "count": len(enhanced_workflows),
            "workflows": enhanced_workflows
        }
    except Exception as e:
        logger.error(f"Error fetching workflows for department {department}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HELPER FUNCTIONS ====================

async def _gather_database_context(department: str, tm: TaskManager) -> str:
    """
    Gather relevant database context for AI workflow generation
    Queries actual city data to make planning more realistic
    """
    context_parts = []
    
    try:
        # Get database connection from task manager
        conn = tm.queries.get_connection()
        cursor = conn.cursor()
        
        # Department-specific context gathering
        if department == 'water':
            cursor.execute("""
                SELECT COUNT(*) as total, 
                       COUNT(CASE WHEN status = 'operational' THEN 1 END) as operational,
                       AVG(capacity_liters) as avg_capacity
                FROM reservoirs
            """)
            reservoir_data = cursor.fetchone()
            if reservoir_data:
                context_parts.append(f"• Water Infrastructure: {reservoir_data[0]} reservoirs, {reservoir_data[1]} operational, avg capacity {reservoir_data[2]:.0f}L")
            
            cursor.execute("""
                SELECT COUNT(*) as total, 
                       COUNT(CASE WHEN condition = 'good' THEN 1 END) as good_condition
                FROM pipelines
            """)
            pipeline_data = cursor.fetchone()
            if pipeline_data:
                context_parts.append(f"• Pipelines: {pipeline_data[0]} total, {pipeline_data[1]} in good condition")
        
        elif department == 'fire':
            cursor.execute("""
                SELECT COUNT(*) as total_incidents,
                       COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
                       AVG(severity) as avg_severity
                FROM incidents
                WHERE incident_type = 'fire'
                AND created_at > NOW() - INTERVAL '30 days'
            """)
            incident_data = cursor.fetchone()
            if incident_data:
                context_parts.append(f"• Recent Fire Incidents (30 days): {incident_data[0]} total, {incident_data[1]} resolved, avg severity {incident_data[2]:.1f}/5")
        
        elif department == 'engineering':
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as active,
                       SUM(total_cost) as total_cost
                FROM projects
                WHERE department = 'engineering'
            """)
            project_data = cursor.fetchone()
            if project_data:
                context_parts.append(f"• Engineering Projects: {project_data[0]} total, {project_data[1]} active, ${project_data[2]:,.0f} total cost")
        
        elif department == 'health':
            cursor.execute("""
                SELECT COUNT(*) as total_cases,
                       disease_type,
                       COUNT(*) as case_count
                FROM disease_incidents
                WHERE reported_date > NOW() - INTERVAL '30 days'
                GROUP BY disease_type
                ORDER BY case_count DESC
                LIMIT 3
            """)
            health_data = cursor.fetchall()
            if health_data:
                diseases = ", ".join([f"{row[1]}: {row[2]} cases" for row in health_data])
                context_parts.append(f"• Recent Health Issues (30 days): {diseases}")
        
        elif department == 'finance':
            cursor.execute("""
                SELECT department,
                       SUM(total_budget) as budget,
                       SUM(spent) as spent,
                       AVG(utilization_percent) as utilization
                FROM department_budgets
                WHERE year = EXTRACT(YEAR FROM NOW())
                GROUP BY department
                ORDER BY budget DESC
                LIMIT 5
            """)
            budget_data = cursor.fetchall()
            if budget_data:
                budgets = ", ".join([f"{row[0]}: ${row[1]:,.0f} ({row[3]:.1f}% used)" for row in budget_data])
                context_parts.append(f"• Department Budgets: {budgets}")
        
        elif department == 'sanitation':
            cursor.execute("""
                SELECT COUNT(*) as total_workers,
                       AVG(efficiency_rating) as avg_efficiency
                FROM workers
                WHERE department = 'sanitation' AND status = 'active'
            """)
            worker_data = cursor.fetchone()
            if worker_data:
                context_parts.append(f"• Sanitation Workers: {worker_data[0]} active, avg efficiency {worker_data[1]:.2f}/5")
        
        # General city data
        cursor.execute("""
            SELECT COUNT(*) as active_workflows,
                   COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical
            FROM workflows
            WHERE status IN ('active', 'in_progress')
        """)
        workflow_data = cursor.fetchone()
        if workflow_data:
            context_parts.append(f"• Active Workflows: {workflow_data[0]} total, {workflow_data[1]} critical priority")
        
        cursor.close()
        
    except Exception as e:
        logger.warning(f"Could not gather database context: {e}")
        context_parts.append("• Using general city governance knowledge")
    
    return "\n".join(context_parts) if context_parts else "No specific city data available"


# ==================== HEALTH CHECK ====================

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "task-orchestration",
        "timestamp": datetime.utcnow().isoformat()
    }
