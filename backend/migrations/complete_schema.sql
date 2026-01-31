/* =========================================================
   COMPLETE DATABASE SCHEMA FOR CITY GOVERNANCE SYSTEM
   Database: departments
   Fresh installation - drops all existing tables
   ========================================================= */

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

/* ---------- DROP ALL EXISTING TABLES ---------- */

DROP TABLE IF EXISTS incidents CASCADE;
DROP TABLE IF EXISTS reservoirs CASCADE;
DROP TABLE IF EXISTS pipelines CASCADE;
DROP TABLE IF EXISTS workers CASCADE;
DROP TABLE IF EXISTS work_schedules CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS department_budgets CASCADE;
DROP TABLE IF EXISTS agent_decisions CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

/* ========================================================= */
/* AGENT DECISION AUDIT TABLE */
/* ========================================================= */

CREATE TABLE agent_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Agent metadata
    agent_type VARCHAR(50) NOT NULL,  -- 'water_department', 'fire_department', etc.
    request_type VARCHAR(100) NOT NULL,
    
    -- Request data (complete input event)
    request_data JSONB NOT NULL,
    context_snapshot JSONB,  -- Context gathered at decision time
    
    -- Plan and execution
    plan_attempted JSONB,  -- Which plan was tried
    tool_results JSONB,    -- Tool execution results
    
    -- Evaluation results
    feasible BOOLEAN,
    feasibility_reason TEXT,
    policy_compliant BOOLEAN,
    policy_violations JSONB,
    
    -- Confidence scoring
    confidence FLOAT,
    confidence_factors JSONB,
    
    -- Final decision
    decision VARCHAR(20) CHECK (decision IN ('approve', 'deny', 'escalate')),
    reasoning TEXT,
    escalation_reason TEXT,
    
    -- Response
    response TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Metadata
    agent_version VARCHAR(20),
    execution_time_ms INTEGER,
    retry_count INTEGER DEFAULT 0
);

-- Indexes for querying decisions
CREATE INDEX idx_agent_decisions_type ON agent_decisions(agent_type);
CREATE INDEX idx_agent_decisions_request_type ON agent_decisions(request_type);
CREATE INDEX idx_agent_decisions_decision ON agent_decisions(decision);
CREATE INDEX idx_agent_decisions_created ON agent_decisions(created_at DESC);
CREATE INDEX idx_agent_decisions_feasible ON agent_decisions(feasible);
CREATE INDEX idx_agent_decisions_confidence ON agent_decisions(confidence);


/* ========================================================= */
/* DEPARTMENT BUDGET TRACKING */
/* ========================================================= */

CREATE TABLE department_budgets (
    budget_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    department VARCHAR(50) NOT NULL,  -- 'water', 'fire', 'roads', etc.
    
    -- Budget period
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    
    -- Budget amounts (in local currency)
    total_budget NUMERIC(15, 2) NOT NULL,
    allocated NUMERIC(15, 2) DEFAULT 0,
    spent NUMERIC(15, 2) DEFAULT 0,
    remaining NUMERIC(15, 2) GENERATED ALWAYS AS (total_budget - spent) STORED,
    
    -- Utilization tracking
    utilization_percent NUMERIC(5, 2) GENERATED ALWAYS AS 
        (CASE WHEN total_budget > 0 THEN (spent / total_budget) * 100 ELSE 0 END) STORED,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('active', 'depleted', 'frozen', 'closed')),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(department, year, month)
);

-- Indexes for budget queries
CREATE INDEX idx_budget_department ON department_budgets(department);
CREATE INDEX idx_budget_period ON department_budgets(year, month);
CREATE INDEX idx_budget_status ON department_budgets(status);

/* ========================================================= */
/* FINANCE-SPECIFIC TABLES                                   */
/* ========================================================= */

-- Finance accounts (ledger-like accounts for departments)
CREATE TABLE finance_accounts (
    account_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department VARCHAR(50) NOT NULL,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50), -- e.g., 'operating', 'capital', 'reserve', 'grant'
    currency VARCHAR(10) DEFAULT 'INR',
    balance NUMERIC(18,2) DEFAULT 0,
    reserved_amount NUMERIC(18,2) DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_finance_accounts_department ON finance_accounts(department);

-- Revenue history: actual revenue receipts by period and source
CREATE TABLE revenue_history (
    revenue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department VARCHAR(50),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    amount NUMERIC(18,2) NOT NULL,
    source VARCHAR(255), -- 'tax', 'user_charges', 'grant', 'other'
    details JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_revenue_period ON revenue_history(period_start, period_end);
CREATE INDEX idx_revenue_department ON revenue_history(department);

-- Revenue forecasts produced by the Finance Agent
CREATE TABLE revenue_forecasts (
    forecast_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department VARCHAR(50),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    forecast_amount NUMERIC(18,2) NOT NULL,
    method VARCHAR(100), -- 'llm', 'time_series', 'percent_of_budget'
    confidence NUMERIC(5,4), -- 0.0 - 1.0
    model_metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecast_period ON revenue_forecasts(period_start, period_end);

-- Grants table: external funding and conditions
CREATE TABLE grants (
    grant_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    grant_name VARCHAR(255) NOT NULL,
    provider VARCHAR(255),
    department VARCHAR(50),
    amount_awarded NUMERIC(18,2),
    amount_received NUMERIC(18,2) DEFAULT 0,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) CHECK (status IN ('proposed','awarded','active','closed','cancelled')),
    match_requirements JSONB,
    terms JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_grants_department ON grants(department);

-- Fund allocations: where budgeted amounts are allocated
CREATE TABLE fund_allocations (
    allocation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department VARCHAR(50) NOT NULL,
    budget_id UUID REFERENCES department_budgets(budget_id) ON DELETE SET NULL,
    account_id UUID REFERENCES finance_accounts(account_id) ON DELETE SET NULL,
    amount NUMERIC(18,2) NOT NULL,
    purpose TEXT,
    allocated_by VARCHAR(255),
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_allocations_budget ON fund_allocations(budget_id);

-- Financial transactions (credits/debits) recorded against accounts
CREATE TABLE financial_transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department VARCHAR(50),
    account_id UUID REFERENCES finance_accounts(account_id) ON DELETE SET NULL,
    amount NUMERIC(18,2) NOT NULL,
    transaction_type VARCHAR(20) CHECK (transaction_type IN ('credit','debit')),
    description TEXT,
    reference_id UUID, -- could reference projects or external docs
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_account ON financial_transactions(account_id);
CREATE INDEX idx_transactions_department ON financial_transactions(department);

-- Budget adjustments and approvals (audit trail of changes)
CREATE TABLE budget_adjustments (
    adjustment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    budget_id UUID REFERENCES department_budgets(budget_id) ON DELETE CASCADE,
    adjustment_amount NUMERIC(18,2) NOT NULL,
    reason TEXT,
    requested_by VARCHAR(255),
    approved_by VARCHAR(255),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_adjustments_budget ON budget_adjustments(budget_id);

-- Reserve funds per department
CREATE TABLE reserve_funds (
    reserve_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department VARCHAR(50) NOT NULL,
    reserve_name VARCHAR(255),
    amount NUMERIC(18,2) DEFAULT 0,
    min_required_percent NUMERIC(5,2) DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reserve_department ON reserve_funds(department);

-- Tax revenue breakdown (optional table for detailed tax streams)
CREATE TABLE tax_revenues (
    tax_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_start DATE,
    period_end DATE,
    source VARCHAR(255), -- 'property_tax', 'gst_share', etc.
    department VARCHAR(50),
    amount NUMERIC(18,2),
    details JSONB,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tax_revenues_period ON tax_revenues(period_start, period_end);

-- Finance policies table (policy text and metadata)
CREATE TABLE finance_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name VARCHAR(255) NOT NULL,
    description TEXT,
    effective_date DATE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_finance_policies_name ON finance_policies(policy_name);

/* ========================================================= */

/* ========================================================= */
/* HEALTH-SPECIFIC TABLES                                    */
/* ========================================================= */

-- Disease incidents (surveillance)
CREATE TABLE disease_incidents (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_type VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low','medium','high','critical')),
    reported_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reported_by VARCHAR(255),
    status VARCHAR(50) CHECK (status IN ('reported','investigating','contained','closed')),
    description TEXT,
    public_health_actions JSONB, -- actions taken or recommended
    related_decision_id UUID REFERENCES agent_decisions(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disease_incidents_location ON disease_incidents(location);
CREATE INDEX idx_disease_incidents_reported ON disease_incidents(reported_date DESC);

-- Vaccination campaigns
CREATE TABLE vaccination_campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    start_date DATE,
    end_date DATE,
    target_groups JSONB, -- e.g., [{"group":"children","ages":"0-5"}]
    coverage_percent NUMERIC(5,2),
    status VARCHAR(50) CHECK (status IN ('planned','active','completed','cancelled')),
    resources JSONB,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vaccination_campaigns_location ON vaccination_campaigns(location);

-- Sanitation inspections
CREATE TABLE sanitation_inspections (
    inspection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location TEXT,
    facility VARCHAR(255),
    inspection_date DATE NOT NULL,
    outcome VARCHAR(50) CHECK (outcome IN ('pass','conditional_pass','fail')),
    inspector VARCHAR(255),
    notes TEXT,
    findings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sanitation_inspections_location ON sanitation_inspections(location);
CREATE INDEX idx_sanitation_inspections_date ON sanitation_inspections(inspection_date DESC);

-- Vulnerable populations registry
CREATE TABLE vulnerable_populations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location TEXT,
    population_group VARCHAR(255), -- e.g., 'elderly','pregnant_women','slum_residents'
    population_count INTEGER,
    vulnerability_index NUMERIC(5,2),
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_vulnerable_populations_location ON vulnerable_populations(location);

-- Health facilities
CREATE TABLE health_facilities (
    facility_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location TEXT,
    capacity INTEGER,
    services JSONB, -- list of services offered
    status VARCHAR(50) CHECK (status IN ('open','closed','under_maintenance')),
    contact JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_facilities_location ON health_facilities(location);

-- Health resources (e.g., mobile clinics, ventilators)
CREATE TABLE health_resources (
    resource_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(255),
    quantity INTEGER DEFAULT 0,
    location TEXT,
    status VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_resources_type ON health_resources(resource_type);

-- Surveillance reports and summaries
CREATE TABLE health_surveillance_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(255), -- e.g., 'clinic_reports','self_reports','lab'
    report_date TIMESTAMP NOT NULL,
    summary JSONB,
    severity_assessment VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_surveillance_date ON health_surveillance_reports(report_date DESC);

-- Health policies table
CREATE TABLE health_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name VARCHAR(255) NOT NULL,
    description TEXT,
    effective_date DATE,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_health_policies_name ON health_policies(policy_name);




/* ========================================================= */
/* PROJECT TRACKING */
/* ========================================================= */

CREATE TABLE projects (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    department VARCHAR(50) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    project_type VARCHAR(100),
    
    location TEXT,
    
    -- Cost tracking
    estimated_cost NUMERIC(15, 2),
    actual_cost NUMERIC(15, 2) DEFAULT 0,
    
    -- Timeline
    start_date DATE,
    end_date DATE,
    completion_date DATE,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('planned', 'approved', 'in_progress', 'completed', 'cancelled')),
    
    -- Related to agent decision
    agent_decision_id UUID REFERENCES agent_decisions(id) ON DELETE SET NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for project queries
CREATE INDEX idx_projects_department ON projects(department);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_start_date ON projects(start_date);
CREATE INDEX idx_projects_location ON projects(location);


/* ========================================================= */
/* WORK SCHEDULES */
/* ========================================================= */

CREATE TABLE work_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    department VARCHAR(50) NOT NULL,
    activity_type VARCHAR(100) NOT NULL,
    
    location TEXT NOT NULL,
    
    -- Scheduling
    scheduled_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    
    -- Priority
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Resource allocation
    workers_assigned INTEGER,
    equipment_assigned JSONB,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    
    -- Related entities
    project_id UUID REFERENCES projects(project_id) ON DELETE SET NULL,
    agent_decision_id UUID REFERENCES agent_decisions(id) ON DELETE SET NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for schedule queries
CREATE INDEX idx_schedules_department ON work_schedules(department);
CREATE INDEX idx_schedules_date ON work_schedules(scheduled_date);
CREATE INDEX idx_schedules_location ON work_schedules(location);
CREATE INDEX idx_schedules_status ON work_schedules(status);
CREATE INDEX idx_schedules_priority ON work_schedules(priority);


/* ========================================================= */
/* WORKERS/MANPOWER TRACKING */
/* ========================================================= */

CREATE TABLE workers (
    worker_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    department VARCHAR(50) NOT NULL,
    worker_name VARCHAR(255) NOT NULL,
    
    -- Skills
    role VARCHAR(100),
    skills JSONB,
    certifications JSONB,
    
    -- Availability
    status VARCHAR(20) CHECK (status IN ('active', 'on_leave', 'sick', 'inactive')),
    
    -- Contact
    phone VARCHAR(20),
    email VARCHAR(255),
    
    -- Metadata
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for worker queries
CREATE INDEX idx_workers_department ON workers(department);
CREATE INDEX idx_workers_status ON workers(status);
CREATE INDEX idx_workers_role ON workers(role);


/* ========================================================= */
/* PIPELINES TABLE */
/* ========================================================= */

CREATE TABLE pipelines (
    pipeline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    location TEXT NOT NULL,
    zone VARCHAR(50),
    
    -- Pipeline specifications
    pipeline_type VARCHAR(20) CHECK (pipeline_type IN ('supply', 'drainage', 'sewage')),
    diameter_mm INTEGER,
    material VARCHAR(50),
    length_meters NUMERIC(10, 2),
    
    -- Condition monitoring
    pressure_psi NUMERIC(6, 2),  -- Current pressure
    flow_rate NUMERIC(10, 2),    -- Liters per minute
    
    condition VARCHAR(20) CHECK (condition IN ('excellent', 'good', 'fair', 'poor', 'critical')),
    
    -- Maintenance
    installation_date DATE,
    last_inspection_date DATE,
    next_inspection_due DATE,
    
    -- Status
    operational_status VARCHAR(20) CHECK (operational_status IN ('active', 'inactive', 'under_repair', 'retired')),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for pipeline queries
CREATE INDEX idx_pipelines_location ON pipelines(location);
CREATE INDEX idx_pipelines_zone ON pipelines(zone);
CREATE INDEX idx_pipelines_status ON pipelines(operational_status);
CREATE INDEX idx_pipelines_pressure ON pipelines(pressure_psi);


/* ========================================================= */
/* RESERVOIRS TABLE */
/* ========================================================= */

CREATE TABLE reservoirs (
    reservoir_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    
    -- Capacity
    capacity_liters BIGINT NOT NULL,
    current_level_liters BIGINT,
    
    -- Calculated fields
    level_percentage NUMERIC(5, 2) GENERATED ALWAYS AS 
        (CASE WHEN capacity_liters > 0 THEN (current_level_liters::NUMERIC / capacity_liters) * 100 ELSE 0 END) STORED,
    
    -- Status
    operational_status VARCHAR(20) CHECK (operational_status IN ('active', 'maintenance', 'emergency', 'inactive')),
    
    -- Monitoring
    last_reading_time TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for reservoir queries
CREATE INDEX idx_reservoirs_location ON reservoirs(location);
CREATE INDEX idx_reservoirs_status ON reservoirs(operational_status);


/* ========================================================= */
/* INCIDENTS TABLE */
/* ========================================================= */

CREATE TABLE incidents (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    department VARCHAR(50) NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    
    location TEXT NOT NULL,
    
    -- Severity
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    
    -- Reporting
    reported_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reported_by VARCHAR(255),
    
    description TEXT,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('reported', 'investigating', 'resolved', 'closed')),
    
    resolution_date TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for incident queries
CREATE INDEX idx_incidents_department ON incidents(department);
CREATE INDEX idx_incidents_location ON incidents(location);
CREATE INDEX idx_incidents_reported_date ON incidents(reported_date DESC);
CREATE INDEX idx_incidents_severity ON incidents(severity);

/* ========================================================= */
/* WATER-SPECIFIC SUPPORT TABLES                             */
/* These complement pipelines/reservoirs/incidents for water */
/* ========================================================= */

-- Departments master table (list of city departments)
CREATE TABLE departments (
    department_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    department_key VARCHAR(50) UNIQUE NOT NULL, -- 'water','fire','health'
    display_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    manager_name VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_departments_key ON departments(department_key);

-- Pipeline inspections history
CREATE TABLE pipeline_inspections (
    inspection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID REFERENCES pipelines(pipeline_id) ON DELETE CASCADE,
    inspector VARCHAR(255),
    inspection_date DATE NOT NULL,
    outcome VARCHAR(50), -- 'pass','minor_issues','major_issues','fail'
    notes TEXT,
    findings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipeline_inspections_pipeline ON pipeline_inspections(pipeline_id);
CREATE INDEX idx_pipeline_inspections_date ON pipeline_inspections(inspection_date DESC);

-- Periodic sensor/readings for water network (e.g., pressure/flow telemetry)
CREATE TABLE water_readings (
    reading_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_id UUID REFERENCES pipelines(pipeline_id) ON DELETE SET NULL,
    location TEXT,
    reading_time TIMESTAMP NOT NULL,
    pressure_psi NUMERIC(10,2),
    flow_rate NUMERIC(12,4),
    temperature NUMERIC(8,2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_water_readings_pipeline_time ON water_readings(pipeline_id, reading_time DESC);

-- Service outages and disruption reports for water
CREATE TABLE service_outages (
    outage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location TEXT,
    zone VARCHAR(50),
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    resolved_at TIMESTAMP,
    severity VARCHAR(20) CHECK (severity IN ('low','medium','high','critical')),
    cause TEXT,
    affected_customers INTEGER,
    status VARCHAR(20) CHECK (status IN ('reported','investigating','mitigating','resolved','closed')),
    related_pipeline_id UUID REFERENCES pipelines(pipeline_id) ON DELETE SET NULL,
    incident_id UUID REFERENCES incidents(incident_id) ON DELETE SET NULL,
    notes TEXT
);

CREATE INDEX idx_service_outages_location ON service_outages(location);
CREATE INDEX idx_service_outages_status ON service_outages(status);



/* ========================================================= */
/* UPDATE TIMESTAMP TRIGGERS */
/* ========================================================= */

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for all tables with updated_at
CREATE TRIGGER update_department_budgets_updated_at BEFORE UPDATE ON department_budgets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_work_schedules_updated_at BEFORE UPDATE ON work_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workers_updated_at BEFORE UPDATE ON workers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipelines_updated_at BEFORE UPDATE ON pipelines
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reservoirs_updated_at BEFORE UPDATE ON reservoirs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


/* ========================================================= */
/* SAMPLE DATA FOR TESTING */
/* ========================================================= */

-- Insert sample department budgets
INSERT INTO department_budgets (department, year, month, total_budget, spent, status)
VALUES 
    ('water', 2026, 1, 500000, 420000, 'active'),
    ('fire', 2026, 1, 750000, 320000, 'active'),
    ('roads', 2026, 1, 600000, 180000, 'active');

-- Insert sample workers (8 workers)
INSERT INTO workers (department, worker_name, role, status, skills)
VALUES 
    ('water', 'John Smith', 'Pipeline Technician', 'active', '["welding", "inspection"]'::jsonb),
    ('water', 'Jane Doe', 'Maintenance Engineer', 'active', '["hydraulics", "repair"]'::jsonb),
    ('water', 'Mike Johnson', 'Field Worker', 'active', '["excavation", "repair"]'::jsonb),
    ('water', 'Sarah Williams', 'Safety Inspector', 'active', '["safety", "compliance"]'::jsonb),
    ('water', 'Tom Brown', 'Pipeline Technician', 'active', '["welding", "installation"]'::jsonb),
    ('water', 'Lisa Davis', 'Field Worker', 'active', '["excavation", "maintenance"]'::jsonb),
    ('water', 'Robert Taylor', 'Maintenance Engineer', 'active', '["plumbing", "repair"]'::jsonb),
    ('water', 'Emma Wilson', 'Field Worker', 'on_leave', '["excavation", "repair"]'::jsonb);

-- Insert sample pipelines (6 pipelines)
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, pressure_psi, condition, operational_status, installation_date)
VALUES 
    ('Downtown', 'Zone-1', 'supply', 300, 'steel', 45.5, 'good', 'active', '2015-03-15'),
    ('Downtown', 'Zone-1', 'supply', 250, 'PVC', 42.0, 'good', 'active', '2018-06-20'),
    ('Downtown', 'Zone-1', 'drainage', 400, 'concrete', 38.5, 'fair', 'active', '2010-01-10'),
    ('East Zone', 'Zone-2', 'supply', 300, 'steel', 48.0, 'excellent', 'active', '2020-05-12'),
    ('West Zone', 'Zone-3', 'supply', 200, 'PVC', 35.0, 'poor', 'under_repair', '2008-09-30'),
    ('North District', 'Zone-4', 'supply', 350, 'steel', 50.0, 'excellent', 'active', '2021-11-05');

-- Insert sample reservoirs (3 reservoirs)
INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time)
VALUES 
    ('Main Reservoir', 'Downtown', 50000000, 42000000, 'active', CURRENT_TIMESTAMP),
    ('East Reservoir', 'East Zone', 30000000, 25000000, 'active', CURRENT_TIMESTAMP),
    ('North Reservoir', 'North District', 20000000, 18000000, 'active', CURRENT_TIMESTAMP);

-- Insert sample incidents (5 incidents for testing safety risk)
INSERT INTO incidents (department, incident_type, location, severity, reported_date, status)
VALUES 
    ('water', 'leakage', 'Downtown', 'medium', CURRENT_TIMESTAMP - INTERVAL '15 days', 'resolved'),
    ('water', 'blockage', 'East Zone', 'low', CURRENT_TIMESTAMP - INTERVAL '10 days', 'closed'),
    ('water', 'contamination', 'Industrial Zone A', 'high', CURRENT_TIMESTAMP - INTERVAL '5 days', 'investigating'),
    ('water', 'leakage', 'Industrial Zone A', 'high', CURRENT_TIMESTAMP - INTERVAL '3 days', 'reported'),
    ('water', 'pressure_drop', 'Industrial Zone A', 'high', CURRENT_TIMESTAMP - INTERVAL '1 day', 'reported');


/* ========================================================= */
/* SUCCESS MESSAGE */
/* ========================================================= */

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '====================================================';
    RAISE NOTICE '✅ DATABASE SCHEMA CREATED SUCCESSFULLY!';
    RAISE NOTICE '====================================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tables Created:';
    RAISE NOTICE '   ✓ agent_decisions (audit trail)';
    RAISE NOTICE '   ✓ department_budgets';
    RAISE NOTICE '   ✓ projects';
    RAISE NOTICE '   ✓ work_schedules';
    RAISE NOTICE '   ✓ workers (8 sample workers)';
    RAISE NOTICE '   ✓ pipelines (6 sample pipelines)';
    RAISE NOTICE '   ✓ reservoirs (3 sample reservoirs)';
    RAISE NOTICE '   ✓ incidents (5 sample incidents)';
    RAISE NOTICE '';
    RAISE NOTICE '   ✓ health tables (if health_schema.sql executed separately)';
    RAISE NOTICE '🔧 Features Configured:';
    RAISE NOTICE '   ✓ UUID extension enabled';
    RAISE NOTICE '   ✓ Update triggers configured';
    RAISE NOTICE '   ✓ Indexes created for performance';
    RAISE NOTICE '   ✓ Foreign key constraints';
    RAISE NOTICE '   ✓ Sample data inserted';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Ready to run tests!';
    RAISE NOTICE '====================================================';
END $$;
