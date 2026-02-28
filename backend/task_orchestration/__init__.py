"""
Task Orchestration System

This module provides task management, workflow orchestration,
dependency resolution, contingency planning, and knowledge graph
generation for the City Governance System.

Architecture:
- Task Manager: CRUD operations for tasks and workflows
- Workflow Engine: Dependency resolution and state management
- Contingency Planner: LLM-powered backup plan generation
- Notification Service: Smart notifications and reminders
- Knowledge Graph: Visual workflow representation
"""

__version__ = "1.0.0"
__author__ = "City Governance Team"

# Core modules
from .config import task_config
from .models import (
    WorkflowCreate, WorkflowResponse, WorkflowUpdate,
    TaskCreate, TaskResponse, TaskUpdate, TaskWithDependencies,
    DependencyCreate, ContingencyPlanCreate, ContingencyPlanResponse,
    NotificationResponse, KnowledgeGraphData
)
from .database import get_db, get_queries
from .task_manager import get_task_manager, TaskManager
from .workflow_engine import get_workflow_engine, WorkflowEngine
from .contingency_planner import get_contingency_planner, ContingencyPlanner
from .knowledge_graph import get_kg_generator, KnowledgeGraphGenerator
from .notification_service import get_notification_service, NotificationService

# API Router
from .api import router as task_orchestration_router

__all__ = [
    # Config
    "task_config",
    
    # Models
    "WorkflowCreate", "WorkflowResponse", "WorkflowUpdate",
    "TaskCreate", "TaskResponse", "TaskUpdate", "TaskWithDependencies",
    "DependencyCreate", "ContingencyPlanCreate", "ContingencyPlanResponse",
    "NotificationResponse", "KnowledgeGraphData",
    
    # Classes
    "TaskManager", "WorkflowEngine", "ContingencyPlanner",
    "KnowledgeGraphGenerator", "NotificationService",
    
    # Singletons
    "get_db", "get_queries",
    "get_task_manager", "get_workflow_engine", "get_contingency_planner",
    "get_kg_generator", "get_notification_service",
    
    # API Router
    "task_orchestration_router"
]
