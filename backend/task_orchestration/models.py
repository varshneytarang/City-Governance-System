"""
Data Models for Task Orchestration System

Pydantic models for request/response validation and type safety.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


# ==================== ENUMS ====================

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"
    WAITING_APPROVAL = "waiting_approval"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class DependencyType(str, Enum):
    FINISH_TO_START = "finish_to_start"
    START_TO_START = "start_to_start"
    FINISH_TO_FINISH = "finish_to_finish"
    START_TO_FINISH = "start_to_finish"
    BLOCKS = "blocks"
    REQUIRES = "requires"


class NotificationType(str, Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_READY = "task_ready"
    TASK_DUE_SOON = "task_due_soon"
    TASK_OVERDUE = "task_overdue"
    UPSTREAM_COMPLETED = "upstream_completed"
    WAITING_FOR_YOU = "waiting_for_you"
    APPROVAL_REQUIRED = "approval_required"
    TASK_BLOCKED = "task_blocked"
    TASK_FAILED = "task_failed"
    CONTINGENCY_ACTIVATED = "contingency_activated"
    WORKFLOW_COMPLETED = "workflow_completed"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NOT_REQUIRED = "not_required"


# ==================== REQUEST MODELS ====================

class WorkflowCreate(BaseModel):
    """Request to create a new workflow"""
    workflow_name: str = Field(..., min_length=1, max_length=255)
    workflow_description: Optional[str] = None
    workflow_type: Optional[str] = Field(None, max_length=100)
    initiated_by_department: str = Field(..., max_length=50)
    priority: Priority = Priority.MEDIUM
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    estimated_total_cost: Optional[float] = None
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class WorkflowUpdate(BaseModel):
    """Request to update a workflow (all fields optional)"""
    workflow_name: Optional[str] = Field(None, min_length=1, max_length=255)
    workflow_description: Optional[str] = None
    workflow_type: Optional[str] = Field(None, max_length=100)
    status: Optional[WorkflowStatus] = None
    priority: Optional[Priority] = None
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    estimated_total_cost: Optional[float] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskCreate(BaseModel):
    """Request to create a new task"""
    workflow_id: UUID
    task_title: str = Field(..., min_length=1, max_length=255)
    task_description: Optional[str] = None
    task_type: Optional[str] = Field(None, max_length=100)
    assigned_department: str = Field(..., max_length=50)
    assigned_to_user_id: Optional[UUID] = None
    priority: Priority = Priority.MEDIUM
    estimated_start_date: Optional[datetime] = None
    estimated_end_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    estimated_duration_hours: Optional[int] = None
    estimated_cost: Optional[float] = None
    required_resources: Optional[Dict[str, Any]] = {}
    requires_approval: bool = False
    sequence_order: Optional[int] = None
    parent_task_id: Optional[UUID] = None
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class TaskUpdate(BaseModel):
    """Request to update a task"""
    task_title: Optional[str] = Field(None, min_length=1, max_length=255)
    task_description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    assigned_to_user_id: Optional[UUID] = None
    deadline: Optional[datetime] = None
    actual_cost: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('progress_percentage')
    def validate_progress(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Progress must be between 0 and 100')
        return v


class DependencyCreate(BaseModel):
    """Request to create a task dependency"""
    task_id: UUID
    depends_on_task_id: UUID
    dependency_type: DependencyType = DependencyType.FINISH_TO_START
    lag_hours: int = 0
    is_hard_dependency: bool = True
    notes: Optional[str] = None
    
    @validator('depends_on_task_id')
    def no_self_dependency(cls, v, values):
        if 'task_id' in values and v == values['task_id']:
            raise ValueError('A task cannot depend on itself')
        return v


class ContingencyPlanCreate(BaseModel):
    """Request to create a contingency plan"""
    task_id: UUID
    workflow_id: UUID
    plan_name: str = Field(..., min_length=1, max_length=255)
    plan_description: str = Field(..., min_length=1)
    plan_order: int = Field(..., ge=1)
    trigger_conditions: Dict[str, Any]
    alternative_approach: str
    alternative_department: Optional[str] = None
    alternative_resources: Optional[Dict[str, Any]] = {}
    estimated_cost: Optional[float] = None
    estimated_duration_hours: Optional[int] = None
    risk_level: str = "medium"
    success_probability: Optional[float] = Field(None, ge=0, le=1)
    generated_by: str = "llm"
    requires_approval: bool = False


class TaskBlockerCreate(BaseModel):
    """Request to report a task blocker"""
    task_id: UUID
    workflow_id: UUID
    blocker_type: str
    blocker_description: str = Field(..., min_length=1)
    reported_by_department: str = Field(..., max_length=50)
    reported_by_user: Optional[str] = None
    resolution_strategy: Optional[str] = None
    requires_approval: bool = False
    severity: str = "medium"
    estimated_delay_hours: Optional[int] = None


class ApprovalDecision(BaseModel):
    """Request to make an approval decision"""
    approval_id: UUID
    decision: str = Field(..., pattern="^(approved|rejected)$")
    decision_notes: Optional[str] = None
    decided_by: str = Field(..., max_length=100)


# ==================== RESPONSE MODELS ====================

class WorkflowResponse(BaseModel):
    """Workflow data response"""
    workflow_id: UUID
    workflow_name: str
    workflow_description: Optional[str]
    workflow_type: Optional[str]
    initiated_by_department: str
    status: WorkflowStatus
    priority: Priority
    planned_start_date: Optional[datetime]
    planned_end_date: Optional[datetime]
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    estimated_total_cost: Optional[float]
    actual_total_cost: Optional[float]
    knowledge_graph_data: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Task data response"""
    task_id: UUID
    workflow_id: UUID
    task_title: str
    task_description: Optional[str]
    task_type: Optional[str]
    assigned_department: str
    assigned_to_user_id: Optional[UUID]
    status: TaskStatus
    priority: Priority
    progress_percentage: int
    estimated_start_date: Optional[datetime]
    estimated_end_date: Optional[datetime]
    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]
    deadline: Optional[datetime]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    required_resources: Optional[Dict[str, Any]]
    requires_approval: bool
    approval_status: Optional[ApprovalStatus]
    sequence_order: Optional[int]
    parent_task_id: Optional[UUID]
    tags: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskWithDependencies(TaskResponse):
    """Task with dependency information"""
    dependencies: List[Dict[str, Any]] = []
    dependent_tasks: List[Dict[str, Any]] = []
    dependencies_satisfied: bool = False
    is_ready: bool = False


class WorkflowWithTasks(WorkflowResponse):
    """Workflow with all its tasks"""
    tasks: List[TaskResponse] = []
    total_tasks: int = 0
    completed_tasks: int = 0
    in_progress_tasks: int = 0
    blocked_tasks: int = 0
    completion_percentage: float = 0.0


class ContingencyPlanResponse(BaseModel):
    """Contingency plan response"""
    plan_id: UUID
    task_id: UUID
    workflow_id: UUID
    plan_name: str
    plan_description: str
    plan_order: int
    trigger_conditions: Dict[str, Any]
    alternative_approach: str
    alternative_department: Optional[str]
    estimated_cost: Optional[float]
    estimated_duration_hours: Optional[int]
    risk_level: str
    success_probability: Optional[float]
    generated_by: str
    status: str
    requires_approval: bool
    approved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationCreate(BaseModel):
    """Create a new notification"""
    task_id: Optional[UUID] = None
    workflow_id: Optional[UUID] = None
    notification_type: NotificationType
    recipient_department: str
    recipient_user_id: Optional[UUID] = None
    recipient_email: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    title: Optional[str] = None
    message: str
    action_url: Optional[str] = None
    action_required: bool = False
    delivery_method: str = "in_app"
    scheduled_for: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('title', always=True)
    def generate_title(cls, v, values):
        """Auto-generate title from notification_type if not provided"""
        if v:
            return v
        
        notif_type = values.get('notification_type')
        if not notif_type:
            return "Task Notification"
        
        # Generate readable title from notification type
        title_map = {
            NotificationType.TASK_ASSIGNED: "Task Assigned",
            NotificationType.TASK_READY: "Task Ready to Start",
            NotificationType.TASK_DUE_SOON: "Task Deadline Approaching",
            NotificationType.TASK_OVERDUE: "Task Overdue",
            NotificationType.UPSTREAM_COMPLETED: "Dependency Completed",
            NotificationType.WAITING_FOR_YOU: "Waiting for Your Action",
            NotificationType.APPROVAL_REQUIRED: "Approval Required",
            NotificationType.TASK_BLOCKED: "Task Blocked",
            NotificationType.TASK_FAILED: "Task Failed",
            NotificationType.CONTINGENCY_ACTIVATED: "Contingency Plan Activated",
            NotificationType.WORKFLOW_COMPLETED: "Workflow Completed"
        }
        
        return title_map.get(notif_type, "Task Notification")


class NotificationResponse(BaseModel):
    """Notification response"""
    notification_id: UUID
    recipient_department: str
    recipient_user_id: Optional[UUID]
    notification_type: NotificationType
    priority: Priority
    title: str
    message: str
    action_url: Optional[str]
    action_required: bool
    status: str
    scheduled_for: datetime
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class KnowledgeGraphData(BaseModel):
    """Knowledge graph structure"""
    workflow_id: UUID
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    layout: Optional[str] = "hierarchical"
    metadata: Optional[Dict[str, Any]] = {}


# ==================== UTILITY MODELS ====================

class TaskStatusChange(BaseModel):
    """Task status change information"""
    task_id: UUID
    old_status: Optional[TaskStatus]
    new_status: TaskStatus
    change_reason: Optional[str]
    change_type: str
    changed_by: str
    changed_by_type: str  # 'user', 'agent', 'system', 'automation'


class DependencyStatus(BaseModel):
    """Dependency satisfaction status"""
    dependency_id: UUID
    task_id: UUID
    depends_on_task_id: UUID
    dependency_type: DependencyType
    satisfied: bool
    blocking_reason: Optional[str] = None


class WorkflowProgress(BaseModel):
    """Workflow progress summary"""
    workflow_id: UUID
    workflow_name: str
    status: WorkflowStatus
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    failed_tasks: int
    completion_percentage: float
    on_track: bool
    estimated_completion_date: Optional[datetime]
    is_delayed: bool


# ==================== ERROR MODELS ====================

class TaskOrchestrationError(BaseModel):
    """Error response"""
    error: str
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
