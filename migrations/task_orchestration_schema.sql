/* =========================================================
   TASK ORCHESTRATION SYSTEM - DATABASE SCHEMA
   Version: 1.0
   Created: February 28, 2026
   
   This schema adds task management, workflow orchestration,
   dependency tracking, contingency planning, and knowledge
   graph capabilities to the City Governance System.
   ========================================================= */

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

/* ========================================================= */
/* 1. WORKFLOWS - High-level workflow container */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS workflows (
    workflow_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Basic info
    workflow_name VARCHAR(255) NOT NULL,
    workflow_description TEXT,
    workflow_type VARCHAR(100), -- 'infrastructure', 'emergency', 'permit', 'maintenance'
    
    -- Origination
    initiated_by_department VARCHAR(50) NOT NULL,
    initiated_by_user_id UUID, -- Link to users table if exists
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'draft' CHECK (
        status IN ('draft', 'active', 'in_progress', 'completed', 'cancelled', 'blocked')
    ),
    
    -- Priority
    priority VARCHAR(20) DEFAULT 'medium' CHECK (
        priority IN ('low', 'medium', 'high', 'critical', 'emergency')
    ),
    
    -- Timeline
    planned_start_date TIMESTAMP,
    planned_end_date TIMESTAMP,
    actual_start_date TIMESTAMP,
    actual_end_date TIMESTAMP,
    estimated_duration_hours INTEGER,
    
    -- Budget
    estimated_total_cost NUMERIC(15, 2),
    actual_total_cost NUMERIC(15, 2) DEFAULT 0,
    
    -- Knowledge graph (stored as JSONB for flexibility)
    knowledge_graph_data JSONB,
    
    -- Metadata
    tags TEXT[], -- Array of tags for categorization
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Audit
    created_by VARCHAR(100),
    last_modified_by VARCHAR(100)
);

-- Indexes
CREATE INDEX idx_workflows_status ON workflows(status);
CREATE INDEX idx_workflows_priority ON workflows(priority);
CREATE INDEX idx_workflows_department ON workflows(initiated_by_department);
CREATE INDEX idx_workflows_created_at ON workflows(created_at DESC);
CREATE INDEX idx_workflows_tags ON workflows USING GIN(tags);


/* ========================================================= */
/* 2. TASKS - Individual tasks within workflows */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Workflow association
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Task hierarchy (for sub-tasks)
    parent_task_id UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    sequence_order INTEGER, -- Order within workflow
    
    -- Basic info
    task_title VARCHAR(255) NOT NULL,
    task_description TEXT,
    task_type VARCHAR(100), -- 'approval', 'execution', 'inspection', 'review'
    
    -- Assignment
    assigned_department VARCHAR(50) NOT NULL,
    assigned_to_user_id UUID,
    assigned_by VARCHAR(100),
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN ('pending', 'ready', 'in_progress', 'completed', 'blocked', 'failed', 'cancelled', 'waiting_approval')
    ),
    
    -- Priority (can differ from workflow priority)
    priority VARCHAR(20) DEFAULT 'medium' CHECK (
        priority IN ('low', 'medium', 'high', 'critical', 'emergency')
    ),
    
    -- Timeline
    estimated_start_date TIMESTAMP,
    estimated_end_date TIMESTAMP,
    actual_start_date TIMESTAMP,
    actual_end_date TIMESTAMP,
    deadline TIMESTAMP,
    estimated_duration_hours INTEGER,
    
    -- Progress tracking
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage BETWEEN 0 AND 100),
    
    -- Budget
    estimated_cost NUMERIC(15, 2),
    actual_cost NUMERIC(15, 2) DEFAULT 0,
    budget_approved BOOLEAN DEFAULT false,
    
    -- Resources required
    required_resources JSONB, -- {"workers": 5, "equipment": ["excavator"], "materials": [...]}
    allocated_resources JSONB,
    
    -- Agent execution
    agent_decision_id UUID REFERENCES agent_decisions(id) ON DELETE SET NULL,
    agent_execution_result JSONB,
    
    -- Approval requirements
    requires_approval BOOLEAN DEFAULT false,
    approval_status VARCHAR(50) CHECK (
        approval_status IN ('pending', 'approved', 'rejected', 'not_required')
    ),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Metadata
    tags TEXT[],
    metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_tasks_workflow ON tasks(workflow_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_department ON tasks(assigned_department);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_parent ON tasks(parent_task_id);
CREATE INDEX idx_tasks_sequence ON tasks(workflow_id, sequence_order);


/* ========================================================= */
/* 3. TASK_DEPENDENCIES - Task dependency relationships */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS task_dependencies (
    dependency_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Relationship
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    
    -- Dependency type
    dependency_type VARCHAR(50) NOT NULL CHECK (
        dependency_type IN (
            'finish_to_start',  -- Most common: B starts after A finishes
            'start_to_start',   -- B can start when A starts
            'finish_to_finish', -- B must finish when A finishes
            'start_to_finish',  -- B must finish before A can start (rare)
            'blocks',           -- A blocks B entirely
            'requires'          -- B requires A's output/result
        )
    ),
    
    -- Optional lag time (in hours)
    lag_hours INTEGER DEFAULT 0, -- Delay between dependency satisfaction and task readiness
    
    -- Dependency strength
    is_hard_dependency BOOLEAN DEFAULT true, -- If false, can proceed with approval
    
    -- Conditional logic
    condition_expression TEXT, -- Optional: JSON logic expression for complex dependencies
    
    -- Status
    satisfied BOOLEAN DEFAULT false,
    satisfied_at TIMESTAMP,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent circular dependencies
    CONSTRAINT no_self_dependency CHECK (task_id != depends_on_task_id)
);

-- Indexes
CREATE INDEX idx_task_deps_task ON task_dependencies(task_id);
CREATE INDEX idx_task_deps_depends ON task_dependencies(depends_on_task_id);
CREATE INDEX idx_task_deps_satisfied ON task_dependencies(satisfied);


/* ========================================================= */
/* 4. CONTINGENCY_PLANS - Alternative plans for task failures */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS contingency_plans (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Associated task
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Plan details
    plan_name VARCHAR(255) NOT NULL,
    plan_description TEXT NOT NULL,
    plan_order INTEGER NOT NULL, -- Order to try plans (1 = primary, 2 = first backup, etc.)
    
    -- Trigger conditions
    trigger_conditions JSONB NOT NULL, -- When to activate this plan
    -- Example: {"if": "budget_rejected", "or": ["cost_too_high", "resources_unavailable"]}
    
    -- Plan specifics
    alternative_approach TEXT,
    alternative_department VARCHAR(50), -- If different dept needed
    alternative_resources JSONB,
    estimated_cost NUMERIC(15, 2),
    estimated_duration_hours INTEGER,
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high')),
    success_probability NUMERIC(3, 2) CHECK (success_probability BETWEEN 0 AND 1),
    
    -- Source
    generated_by VARCHAR(50) DEFAULT 'llm' CHECK (
        generated_by IN ('llm', 'human', 'rule_based', 'hybrid')
    ),
    llm_model VARCHAR(100), -- Which LLM generated this
    generation_confidence NUMERIC(3, 2),
    
    -- Status
    status VARCHAR(50) DEFAULT 'ready' CHECK (
        status IN ('ready', 'active', 'executed', 'failed', 'obsolete')
    ),
    activated_at TIMESTAMP,
    execution_result TEXT,
    
    -- Approval
    requires_approval BOOLEAN DEFAULT false,
    approved BOOLEAN DEFAULT false,
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_contingency_task ON contingency_plans(task_id);
CREATE INDEX idx_contingency_workflow ON contingency_plans(workflow_id);
CREATE INDEX idx_contingency_order ON contingency_plans(task_id, plan_order);
CREATE INDEX idx_contingency_status ON contingency_plans(status);


/* ========================================================= */
/* 5. TASK_NOTIFICATIONS - Notification queue and history */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS task_notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Target
    recipient_department VARCHAR(50) NOT NULL,
    recipient_user_id UUID,
    recipient_email VARCHAR(255),
    
    -- Associated entities
    workflow_id UUID REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    
    -- Notification details
    notification_type VARCHAR(50) NOT NULL CHECK (
        notification_type IN (
            'task_assigned',
            'task_ready',           -- Dependencies satisfied
            'task_due_soon',        -- Approaching deadline
            'task_overdue',
            'upstream_completed',   -- Dependency finished
            'waiting_for_you',      -- Your department's turn
            'approval_required',
            'task_blocked',
            'task_failed',
            'contingency_activated',
            'budget_threshold',
            'resource_conflict',
            'workflow_completed'
        )
    ),
    
    priority VARCHAR(20) DEFAULT 'medium' CHECK (
        priority IN ('low', 'medium', 'high', 'urgent')
    ),
    
    -- Content
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    action_url TEXT, -- Deep link to task/workflow
    action_required BOOLEAN DEFAULT false,
    
    -- Delivery
    delivery_method VARCHAR(50) DEFAULT 'in_app' CHECK (
        delivery_method IN ('in_app', 'email', 'sms', 'webhook', 'all')
    ),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN ('pending', 'sent', 'delivered', 'read', 'acted_upon', 'failed')
    ),
    
    scheduled_for TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    read_at TIMESTAMP,
    acted_upon_at TIMESTAMP,
    
    -- Retry logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notif_department ON task_notifications(recipient_department);
CREATE INDEX idx_notif_user ON task_notifications(recipient_user_id);
CREATE INDEX idx_notif_status ON task_notifications(status);
CREATE INDEX idx_notif_scheduled ON task_notifications(scheduled_for);
CREATE INDEX idx_notif_type ON task_notifications(notification_type);


/* ========================================================= */
/* 6. TASK_STATUS_HISTORY - Audit trail for task changes */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS task_status_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Task reference
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Status change
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    
    -- Reason for change
    change_reason TEXT,
    change_type VARCHAR(50) CHECK (
        change_type IN (
            'normal_progression',
            'manual_override',
            'dependency_satisfied',
            'contingency_activated',
            'blocked',
            'failed',
            'cancelled',
            'approved',
            'rejected'
        )
    ),
    
    -- Who made the change
    changed_by VARCHAR(100),
    changed_by_type VARCHAR(50) CHECK (
        changed_by_type IN ('user', 'agent', 'system', 'automation')
    ),
    
    -- Context
    context_data JSONB, -- Additional context about the change
    
    -- Timestamp
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_task_history_task ON task_status_history(task_id);
CREATE INDEX idx_task_history_time ON task_status_history(changed_at DESC);


/* ========================================================= */
/* 7. TASK_BLOCKERS - What's blocking a task */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS task_blockers (
    blocker_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Blocked task
    task_id UUID NOT NULL REFERENCES tasks(task_id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Blocker details
    blocker_type VARCHAR(50) NOT NULL CHECK (
        blocker_type IN (
            'dependency_not_met',
            'budget_unavailable',
            'resources_unavailable',
            'approval_pending',
            'technical_issue',
            'external_factor',
            'policy_violation',
            'other'
        )
    ),
    
    blocker_description TEXT NOT NULL,
    
    -- Reported by
    reported_by_department VARCHAR(50) NOT NULL,
    reported_by_user VARCHAR(100),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Resolution
    resolution_strategy TEXT,
    requires_approval BOOLEAN DEFAULT false,
    approval_status VARCHAR(50) CHECK (
        approval_status IN ('pending', 'approved', 'rejected', 'not_required')
    ),
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    approval_notes TEXT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (
        status IN ('active', 'resolving', 'resolved', 'escalated', 'accepted')
    ),
    
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    
    -- Escalation
    escalated BOOLEAN DEFAULT false,
    escalated_to VARCHAR(100),
    escalated_at TIMESTAMP,
    
    -- Impact
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    estimated_delay_hours INTEGER,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_blockers_task ON task_blockers(task_id);
CREATE INDEX idx_blockers_status ON task_blockers(status);
CREATE INDEX idx_blockers_approval ON task_blockers(approval_status);


/* ========================================================= */
/* 8. WORKFLOW_APPROVALS - Approval chain tracking */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS workflow_approvals (
    approval_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- What needs approval
    workflow_id UUID REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    
    -- At least one must be set
    CONSTRAINT workflow_or_task_required CHECK (
        workflow_id IS NOT NULL OR task_id IS NOT NULL
    ),
    
    -- Approval details
    approval_type VARCHAR(50) NOT NULL CHECK (
        approval_type IN (
            'workflow_initiation',
            'task_execution',
            'budget_allocation',
            'resource_allocation',
            'contingency_activation',
            'blocker_override',
            'deadline_extension',
            'workflow_cancellation'
        )
    ),
    
    -- Approval chain
    requires_approval_from VARCHAR(50)[], -- Array of roles/departments
    approval_sequence INTEGER, -- Order in chain (1 = first approver)
    
    -- Current approver
    current_approver_role VARCHAR(50),
    assigned_to_user VARCHAR(100),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending' CHECK (
        status IN ('pending', 'approved', 'rejected', 'escalated', 'cancelled')
    ),
    
    -- Decision
    decision VARCHAR(50),
    decision_notes TEXT,
    decided_by VARCHAR(100),
    decided_at TIMESTAMP,
    
    -- Metadata
    request_data JSONB, -- Full context for approval decision
    metadata JSONB,
    
    -- Timestamps
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_by TIMESTAMP,
    
    -- Escalation
    escalated_to VARCHAR(100),
    escalated_at TIMESTAMP,
    escalation_reason TEXT
);

-- Indexes
CREATE INDEX idx_approvals_workflow ON workflow_approvals(workflow_id);
CREATE INDEX idx_approvals_task ON workflow_approvals(task_id);
CREATE INDEX idx_approvals_status ON workflow_approvals(status);
CREATE INDEX idx_approvals_assignee ON workflow_approvals(assigned_to_user);


/* ========================================================= */
/* 9. KNOWLEDGE_GRAPH_NODES - Nodes for visualization */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS knowledge_graph_nodes (
    node_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Associated workflow
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Node type
    node_type VARCHAR(50) NOT NULL CHECK (
        node_type IN (
            'task',
            'decision_point',
            'approval_gate',
            'department',
            'resource',
            'milestone',
            'contingency_branch'
        )
    ),
    
    -- Reference to actual entity
    entity_id UUID, -- task_id, approval_id, etc.
    entity_type VARCHAR(50),
    
    -- Visual properties
    label VARCHAR(255) NOT NULL,
    description TEXT,
    node_color VARCHAR(20),
    node_shape VARCHAR(20),
    icon VARCHAR(50),
    
    -- Position (for layout persistence)
    position_x FLOAT,
    position_y FLOAT,
    
    -- Status (reflected in visualization)
    status VARCHAR(50),
    progress_percentage INTEGER,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_kg_nodes_workflow ON knowledge_graph_nodes(workflow_id);
CREATE INDEX idx_kg_nodes_entity ON knowledge_graph_nodes(entity_id, entity_type);


/* ========================================================= */
/* 10. KNOWLEDGE_GRAPH_EDGES - Connections between nodes */
/* ========================================================= */

CREATE TABLE IF NOT EXISTS knowledge_graph_edges (
    edge_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Associated workflow
    workflow_id UUID NOT NULL REFERENCES workflows(workflow_id) ON DELETE CASCADE,
    
    -- Connection
    source_node_id UUID NOT NULL REFERENCES knowledge_graph_nodes(node_id) ON DELETE CASCADE,
    target_node_id UUID NOT NULL REFERENCES knowledge_graph_nodes(node_id) ON DELETE CASCADE,
    
    -- Edge type
    edge_type VARCHAR(50) NOT NULL CHECK (
        edge_type IN (
            'depends_on',
            'triggers',
            'informs',
            'approves',
            'blocks',
            'contingency_for',
            'executes',
            'coordinates_with'
        )
    ),
    
    -- Visual properties
    label VARCHAR(255),
    edge_color VARCHAR(20),
    edge_style VARCHAR(20), -- 'solid', 'dashed', 'dotted'
    is_critical_path BOOLEAN DEFAULT false,
    
    -- Weight (for graph algorithms)
    weight FLOAT DEFAULT 1.0,
    
    -- Status
    active BOOLEAN DEFAULT true,
    
    -- Metadata
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_kg_edges_workflow ON knowledge_graph_edges(workflow_id);
CREATE INDEX idx_kg_edges_source ON knowledge_graph_edges(source_node_id);
CREATE INDEX idx_kg_edges_target ON knowledge_graph_edges(target_node_id);


/* ========================================================= */
/* TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES */
/* ========================================================= */

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contingency_plans_updated_at BEFORE UPDATE ON contingency_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_notifications_updated_at BEFORE UPDATE ON task_notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_blockers_updated_at BEFORE UPDATE ON task_blockers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


/* ========================================================= */
/* VIEWS FOR COMMON QUERIES */
/* ========================================================= */

-- Active tasks by department with dependency status
CREATE OR REPLACE VIEW v_department_active_tasks AS
SELECT 
    t.task_id,
    t.task_title,
    t.assigned_department,
    t.status,
    t.priority,
    t.deadline,
    t.progress_percentage,
    w.workflow_name,
    w.workflow_id,
    -- Count of dependencies
    COUNT(DISTINCT td.dependency_id) as total_dependencies,
    COUNT(DISTINCT CASE WHEN td.satisfied = true THEN td.dependency_id END) as satisfied_dependencies,
    -- Is task ready?
    CASE 
        WHEN COUNT(DISTINCT td.dependency_id) = COUNT(DISTINCT CASE WHEN td.satisfied = true THEN td.dependency_id END)
        THEN true ELSE false 
    END as dependencies_satisfied
FROM tasks t
JOIN workflows w ON t.workflow_id = w.workflow_id
LEFT JOIN task_dependencies td ON t.task_id = td.task_id
WHERE t.status IN ('pending', 'ready', 'in_progress')
GROUP BY t.task_id, t.task_title, t.assigned_department, t.status, t.priority, t.deadline, t.progress_percentage, w.workflow_name, w.workflow_id;

-- Workflow progress summary
CREATE OR REPLACE VIEW v_workflow_progress AS
SELECT 
    w.workflow_id,
    w.workflow_name,
    w.status,
    COUNT(t.task_id) as total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
    COUNT(CASE WHEN t.status = 'in_progress' THEN 1 END) as in_progress_tasks,
    COUNT(CASE WHEN t.status = 'blocked' THEN 1 END) as blocked_tasks,
    ROUND(
        (COUNT(CASE WHEN t.status = 'completed' THEN 1 END)::NUMERIC / NULLIF(COUNT(t.task_id), 0)) * 100, 
        2
    ) as completion_percentage
FROM workflows w
LEFT JOIN tasks t ON w.workflow_id = t.workflow_id
GROUP BY w.workflow_id, w.workflow_name, w.status;


/* ========================================================= */
/* SAMPLE DATA FOR TESTING */
/* ========================================================= */

-- Insert a sample workflow
INSERT INTO workflows (
    workflow_name, 
    workflow_description, 
    workflow_type, 
    initiated_by_department, 
    status, 
    priority
) VALUES (
    'Downtown Pipeline Replacement Project',
    'Complete replacement of aging water pipeline in downtown district',
    'infrastructure',
    'water',
    'draft',
    'high'
);


/* ========================================================= */
/* NOTES FOR FUTURE ENHANCEMENTS */
/* ========================================================= */

/*
FUTURE CONSIDERATIONS:
1. Task templates for recurring workflows
2. Resource calendar/scheduling
3. Cost tracking per resource type
4. Integration with external calendar systems
5. Webhooks for external system notifications
6. Advanced analytics tables (task completion times, bottlenecks)
7. Machine learning tables (predicted task durations, risk scores)
8. Document attachments (link to file storage)
9. Task comments/discussions
10. Time tracking per task
*/
