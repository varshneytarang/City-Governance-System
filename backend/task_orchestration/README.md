# Task Orchestration System - README

## Overview

The Task Orchestration System is an external layer built on top of the existing City Governance multi-agent system. It provides advanced workflow management, dependency resolution, AI-powered contingency planning, knowledge graph visualization, and smart notifications.

## Architecture

### Hybrid "Strangler Fig" Pattern
- **Phase 1 (Current)**: External task layer operates alongside existing agents
- **Phase 2**: Gradual agent migration to task-aware architecture
- **Phase 3**: Full integration with backward compatibility

### Core Components

#### 1. Task Manager (`task_manager.py`)
**Purpose**: High-level business logic for workflows and tasks

**Key Features**:
- Workflow CRUD operations
- Task creation with auto-sequencing
- Status validation with state machine
- Dependency checking
- Progress tracking

**Main Methods**:
```python
create_workflow(workflow_data) -> WorkflowResponse
create_task(task_data) -> TaskResponse
update_task_status(task_id, new_status, notes) -> bool
get_ready_tasks_for_department(department) -> List[TaskResponse]
get_workflow_progress(workflow_id) -> Dict
```

#### 2. Workflow Engine (`workflow_engine.py`)
**Purpose**: Dependency resolution and execution orchestration

**Key Features**:
- Topological sorting (Kahn's algorithm)
- Circular dependency detection (DFS)
- Critical path calculation (dynamic programming)
- Task prioritization
- Bottleneck analysis

**Main Methods**:
```python
resolve_dependencies(workflow_id) -> Dict[ready_tasks, blocked_tasks, execution_order, critical_path]
start_workflow(workflow_id) -> Dict[status, ready_tasks, warnings]
analyze_task_dependencies(task_id) -> Dict[can_start, blocking_tasks, estimated_wait]
get_next_tasks_to_execute(workflow_id, limit) -> List[prioritized tasks]
suggest_workflow_optimizations(workflow_id) -> List[suggestions]
```

#### 3. LLM Contingency Planner (`contingency_planner.py`)
**Purpose**: AI-powered backup plan generation

**Key Features**:
- LLM-based plan generation (Groq/OpenAI)
- Rule-based fallback plans
- Trigger condition evaluation
- Plan ranking (risk, cost, success probability)
- Plan activation

**Main Methods**:
```python
generate_contingency_plans(task_id, failure_reason, num_plans) -> List[ContingencyPlanResponse]
activate_contingency_plan(plan_id, activated_by, reason) -> bool
evaluate_plan_triggers(task_id, current_situation) -> Optional[plan_id]
rank_plans(plans, criteria) -> List[ranked plans]
```

**LLM Prompt Structure**:
- Workflow context
- Failed task details
- Failure reason
- Constraints (budget, deadline, priority)
- Generates: name, approach, resources, cost, duration, risk, success probability, triggers

#### 4. Knowledge Graph Generator (`knowledge_graph.py`)
**Purpose**: Visual workflow representation

**Key Features**:
- Node/edge generation for visualization
- Auto-layout by department and sequence
- Status-based styling
- Graph analysis (depth, bottlenecks, hubs)
- Database persistence

**Main Methods**:
```python
generate_workflow_graph(workflow_id) -> Dict[nodes, edges, metadata]
get_workflow_graph(workflow_id) -> Optional[graph data]
analyze_graph_structure(workflow_id) -> Dict[structure, centrality, insights]
```

**Node Styling**:
- `pending`: gray (#94a3b8)
- `ready`: blue (#3b82f6)
- `in_progress`: amber (#f59e0b)
- `completed`: green (#10b981)
- `blocked`: red (#ef4444)
- `failed`: dark red (#dc2626)
- `cancelled`: gray (#6b7280)

**Border Width** = Priority level (1-5)

#### 5. Notification Service (`notification_service.py`)
**Purpose**: Smart notifications and reminders

**Key Features**:
- Multi-type notifications (task ready, dependency completed, deadline, approval, blocked, workflow completed)
- Priority-based (low, medium, high, urgent)
- Scheduled deadline reminders (1h, 6h, 24h, 48h)
- Read/unread tracking
- Department-targeted alerts

**Main Methods**:
```python
notify_task_ready(task_id) -> bool
notify_dependency_completed(task_id, completed_dependency_id) -> bool
notify_deadline_approaching(task_id, hours_remaining) -> bool
notify_approval_needed(workflow_id, task_id, approval_type, reason) -> bool
notify_task_blocked(task_id, blocker_reason, blocker_id) -> bool
check_and_send_deadline_reminders() -> int  # Scheduled job
```

## Database Schema

### Core Tables

#### `workflows`
- `workflow_id` (UUID, PK)
- `workflow_name` (VARCHAR)
- `workflow_type` (VARCHAR)
- `status` (workflow_status_enum)
- `created_by` (VARCHAR)
- `metadata` (JSONB)

#### `tasks`
- `task_id` (UUID, PK)
- `workflow_id` (UUID, FK)
- `task_title` (VARCHAR)
- `task_status` (task_status_enum)
- `assigned_department` (VARCHAR)
- `priority` (priority_enum)
- `estimated_duration_hours` (INT)
- `estimated_cost` (DECIMAL)
- `deadline` (TIMESTAMP)

#### `task_dependencies`
- `task_id` (UUID, FK)
- `depends_on_task_id` (UUID, FK)
- `dependency_type` (finish_to_start, start_to_start, etc.)
- `is_mandatory` (BOOLEAN)

#### `contingency_plans`
- `plan_id` (UUID, PK)
- `task_id` (UUID, FK)
- `plan_name` (VARCHAR)
- `trigger_conditions` (JSONB)
- `alternative_approach` (TEXT)
- `risk_level` (VARCHAR)
- `success_probability` (DECIMAL)
- `status` (ready, active, used, abandoned)

#### `task_notifications`
- `notification_id` (UUID, PK)
- `task_id` (UUID, FK)
- `notification_type` (notification_type_enum)
- `recipient_department` (VARCHAR)
- `message` (TEXT)
- `priority` (VARCHAR)
- `status` (sent, read)
- `sent_at`, `read_at` (TIMESTAMP)

## API Endpoints

### Workflows
```
POST   /api/task-orchestration/workflows
GET    /api/task-orchestration/workflows/{workflow_id}
GET    /api/task-orchestration/workflows
PUT    /api/task-orchestration/workflows/{workflow_id}
POST   /api/task-orchestration/workflows/{workflow_id}/start
GET    /api/task-orchestration/workflows/{workflow_id}/progress
GET    /api/task-orchestration/workflows/{workflow_id}/dependencies
GET    /api/task-orchestration/workflows/{workflow_id}/optimizations
GET    /api/task-orchestration/workflows/{workflow_id}/next-tasks
```

### Tasks
```
POST   /api/task-orchestration/tasks
GET    /api/task-orchestration/tasks/{task_id}
GET    /api/task-orchestration/tasks
PUT    /api/task-orchestration/tasks/{task_id}
POST   /api/task-orchestration/tasks/{task_id}/status
GET    /api/task-orchestration/tasks/{task_id}/dependencies
GET    /api/task-orchestration/departments/{department}/tasks
```

### Dependencies
```
POST   /api/task-orchestration/dependencies
```

### Contingency Plans
```
POST   /api/task-orchestration/tasks/{task_id}/contingency-plans
GET    /api/task-orchestration/tasks/{task_id}/contingency-plans
POST   /api/task-orchestration/contingency-plans/{plan_id}/activate
POST   /api/task-orchestration/contingency-plans/rank
```

### Knowledge Graphs
```
GET    /api/task-orchestration/workflows/{workflow_id}/graph
GET    /api/task-orchestration/workflows/{workflow_id}/graph/analysis
```

### Notifications
```
GET    /api/task-orchestration/departments/{department}/notifications
GET    /api/task-orchestration/departments/{department}/notifications/unread-count
POST   /api/task-orchestration/notifications/{notification_id}/read
POST   /api/task-orchestration/notifications/check-deadlines
```

## Usage Examples

### 1. Create a Workflow
```python
import requests

workflow_data = {
    "workflow_name": "Emergency Water Pipe Repair",
    "workflow_type": "emergency_response",
    "workflow_description": "Urgent repair of burst water pipe on Main St",
    "created_by": "coordination_agent",
    "metadata": {
        "priority": "critical",
        "location": "Main St & 5th Ave"
    }
}

response = requests.post(
    "http://localhost:8000/api/task-orchestration/workflows",
    json=workflow_data
)

workflow = response.json()
workflow_id = workflow['workflow_id']
```

### 2. Create Tasks with Dependencies
```python
# Task 1: Assess damage
task1_data = {
    "workflow_id": workflow_id,
    "task_title": "Assess Pipe Damage",
    "assigned_department": "water",
    "priority": "critical",
    "estimated_duration_hours": 2,
    "estimated_cost": 0
}

task1 = requests.post(
    "http://localhost:8000/api/task-orchestration/tasks",
    json=task1_data
).json()

# Task 2: Get approval (depends on Task 1)
task2_data = {
    "workflow_id": workflow_id,
    "task_title": "Get Budget Approval",
    "assigned_department": "finance",
    "priority": "high",
    "estimated_duration_hours": 1,
    "estimated_cost": 0
}

task2 = requests.post(
    "http://localhost:8000/api/task-orchestration/tasks",
    json=task2_data
).json()

# Create dependency
dependency_data = {
    "task_id": task2['task_id'],
    "depends_on_task_id": task1['task_id'],
    "dependency_type": "finish_to_start",
    "is_mandatory": True
}

requests.post(
    "http://localhost:8000/api/task-orchestration/dependencies",
    json=dependency_data
)

# Task 3: Execute repair (depends on Task 2)
task3_data = {
    "workflow_id": workflow_id,
    "task_title": "Execute Pipe Repair",
    "assigned_department": "water",
    "priority": "critical",
    "estimated_duration_hours": 8,
    "estimated_cost": 15000
}

task3 = requests.post(
    "http://localhost:8000/api/task-orchestration/tasks",
    json=task3_data
).json()

dependency_data = {
    "task_id": task3['task_id'],
    "depends_on_task_id": task2['task_id'],
    "dependency_type": "finish_to_start",
    "is_mandatory": True
}

requests.post(
    "http://localhost:8000/api/task-orchestration/dependencies",
    json=dependency_data
)
```

### 3. Start Workflow
```python
result = requests.post(
    f"http://localhost:8000/api/task-orchestration/workflows/{workflow_id}/start"
).json()

print(f"Ready tasks: {result['ready_tasks']}")
print(f"Execution order: {result['execution_order']}")
```

### 4. Generate Contingency Plans
```python
# If Task 3 fails
plans = requests.post(
    f"http://localhost:8000/api/task-orchestration/tasks/{task3['task_id']}/contingency-plans",
    params={
        "failure_reason": "Primary contractor unavailable",
        "num_plans": 3
    }
).json()

print(f"Generated {len(plans['plans'])} contingency plans")
for plan in plans['plans']:
    print(f"- {plan['plan_name']}: {plan['success_probability']}% success")
```

### 5. Get Knowledge Graph
```python
graph = requests.get(
    f"http://localhost:8000/api/task-orchestration/workflows/{workflow_id}/graph"
).json()

# Use in frontend visualization
# graph['nodes'] and graph['edges'] can be passed to React Flow or D3.js
```

### 6. Get Department Notifications
```python
# Water department checks their notifications
notifications = requests.get(
    "http://localhost:8000/api/task-orchestration/departments/water/notifications"
).json()

for notif in notifications:
    print(f"[{notif['priority']}] {notif['message']}")
```

## Configuration

### Environment Variables
```bash
# LLM Configuration
GROQ_API_KEY=your_groq_key_here
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.3
LLM_PROVIDER=groq  # or 'openai'

# Database
DATABASE_URL=postgresql://user:pass@host:5432/city_governance

# Task Settings
AUTO_GENERATE_CONTINGENCY=true
MAX_DEPENDENCY_DEPTH=10
```

### Configuration File (`config.py`)
```python
from task_orchestration import task_config

# LLM settings
task_config.LLM_PROVIDER = "groq"
task_config.GROQ_API_KEY = "..."
task_config.LLM_MODEL = "llama-3.3-70b-versatile"

# Notification settings
task_config.ENABLE_EMAIL_NOTIFICATIONS = True
task_config.ENABLE_PUSH_NOTIFICATIONS = False

# Workflow settings
task_config.AUTO_GENERATE_CONTINGENCY = True
task_config.MAX_DEPENDENCY_DEPTH = 10
```

## Integration with Existing Agents

### Current State (Phase 1)
Tasks are created externally, agents operate as before:

```python
# Backend receives request
@app.post("/api/v1/query")
async def submit_query(payload: InputEvent):
    # Route to coordination agent (existing behavior)
    result = coordinator.decide(payload)
    return result
```

### Future State (Phase 2) - Water Agent v2
After migration, Water Agent becomes task-aware:

```python
class WaterAgentV2(WaterAgent):
    def execute_task(self, task_id: str) -> Dict:
        """Execute a specific task"""
        task = get_task_manager().queries.get_task(task_id)
        
        # Update status
        get_task_manager().update_task_status(task_id, 'in_progress')
        
        # Execute work
        result = self.perform_work(task)
        
        # Complete
        get_task_manager().update_task_status(task_id, 'completed')
        
        return result
    
    def decide(self, event: InputEvent) -> Decision:
        """Backward compatible decision method"""
        # Legacy behavior preserved
        return super().decide(event)
```

## Testing

### Unit Tests
```bash
cd backend
pytest tests/test_task_orchestration.py -v
```

### Integration Tests
```bash
pytest tests/test_task_api_integration.py -v
```

### Manual Testing via API
```bash
# Create workflow
curl -X POST http://localhost:8000/api/task-orchestration/workflows \
  -H "Content-Type: application/json" \
  -d '{"workflow_name":"Test Workflow","created_by":"test"}'

# Get workflow progress
curl http://localhost:8000/api/task-orchestration/workflows/{id}/progress
```

## Deployment

### Database Migration
```bash
# Run schema migration
psql -U postgres -d city_governance -f migrations/task_orchestration_schema.sql

# Verify tables created
psql -U postgres -d city_governance -c "\dt"
```

### Start Backend
```bash
cd backend
python -m uvicorn app.server:app --reload --port 8000
```

### Schedule Reminder Job (Production)
```python
# Using APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from task_orchestration import get_notification_service

scheduler = BackgroundScheduler()

def check_reminders():
    notif_service = get_notification_service()
    notif_service.check_and_send_deadline_reminders()

# Run every hour
scheduler.add_job(check_reminders, 'interval', hours=1)
scheduler.start()
```

## Monitoring & Logging

### Log Levels
- `INFO`: Normal operations, notifications sent
- `WARNING`: LLM fallback, missing data
- `ERROR`: Database failures, invalid states

### Key Metrics
- Workflows created/completed per day
- Average task completion time
- Contingency plans generated/activated
- Notification delivery rate
- Dependency resolution time

## Future Enhancements

### Phase 2 (Months 3-8)
- [ ] Migrate Water Agent to task-aware
- [ ] Migrate Fire Agent to task-aware
- [ ] Migrate remaining agents
- [ ] Add task templates
- [ ] Implement workflow cloning

### Phase 3 (Consolidation)
- [ ] Remove dual interface, full task-based
- [ ] Advanced optimizations (ML-based scheduling)
- [ ] Inter-city workflow coordination
- [ ] Mobile app integration
- [ ] Voice notifications

## Support

For questions or issues:
- Email: support@citygovernance.local
- Slack: #task-orchestration
- Docs: https://docs.citygovernance.local/task-orchestration

## License

MIT License - City Governance System
