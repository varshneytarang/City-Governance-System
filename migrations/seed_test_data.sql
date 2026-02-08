/* =========================================================
   SEED TEST DATA FOR CITY GOVERNANCE SYSTEM
   
   Purpose: Comprehensive test data with edge cases for all agents
   
   Coverage:
   - Multiple departments with varying budgets
   - Workers with different skills and availability
   - Infrastructure at various capacity levels
   - Active and historical projects
   - Emergency and routine incidents
   - Budget constraints and overruns
   - Temporal edge cases (past, current, future)
   
   Run after: complete_schema.sql
   ========================================================= */

-- Clear existing data (for re-running)
TRUNCATE TABLE incidents CASCADE;
TRUNCATE TABLE work_schedules CASCADE;
TRUNCATE TABLE workers CASCADE;
TRUNCATE TABLE pipelines CASCADE;
TRUNCATE TABLE reservoirs CASCADE;
TRUNCATE TABLE projects CASCADE;
TRUNCATE TABLE department_budgets CASCADE;
TRUNCATE TABLE agent_decisions CASCADE;

/* ========================================================= */
/* DEPARTMENT BUDGETS - Various Financial States */
/* ========================================================= */

-- Water Department: Normal budget with good utilization
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
('water', 2026, 1, 500000.00, 450000.00, 125000.00, 'active'),
('water', 2026, 2, 500000.00, 480000.00, 320000.00, 'active'),
('water', 2025, 12, 480000.00, 480000.00, 478500.00, 'closed');

-- Fire Department: High budget with low utilization (potential for cuts)
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
('fire', 2026, 1, 750000.00, 200000.00, 85000.00, 'active'),
('fire', 2026, 2, 750000.00, 220000.00, 95000.00, 'active');

-- Engineering: DEPLETED budget (edge case - no funds available)
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
('engineering', 2026, 1, 600000.00, 600000.00, 605000.00, 'depleted'),
('engineering', 2026, 2, 650000.00, 650000.00, 652000.00, 'depleted');

-- Health: Frozen budget (pending investigation)
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
('health', 2026, 1, 400000.00, 250000.00, 180000.00, 'frozen'),
('health', 2026, 2, 400000.00, 250000.00, 180000.00, 'frozen');

-- Finance: Well-managed budget
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
('finance', 2026, 1, 300000.00, 280000.00, 150000.00, 'active'),
('finance', 2026, 2, 300000.00, 290000.00, 175000.00, 'active');

-- Sanitation: Critical low budget (edge case - almost depleted)
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
('sanitation', 2026, 1, 350000.00, 350000.00, 345000.00, 'active'),
('sanitation', 2026, 2, 350000.00, 350000.00, 349500.00, 'active');

/* ========================================================= */
/* WATER INFRASTRUCTURE - RESERVOIRS */
/* ========================================================= */

-- Critical: Near empty reservoir (edge case - emergency)
INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time) VALUES
('North Reservoir', 'Zone-A', 5000000, 550000, 'emergency', '2026-02-01 10:00:00');

-- Normal: Healthy reservoir
INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time) VALUES
('Central Reservoir', 'Downtown', 10000000, 7500000, 'active', '2026-02-05 14:30:00');

-- Maintenance: Offline for repairs
INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time) VALUES
('South Reservoir', 'Zone-B', 8000000, 4000000, 'maintenance', '2026-01-28 09:15:00');

-- Emergency: Contaminated (edge case - quality issue)
INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time) VALUES
('East Reservoir', 'Zone-C', 6000000, 5500000, 'emergency', '2026-02-07 16:20:00');

-- Over capacity (edge case - flood risk)
INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time) VALUES
('West Reservoir', 'Zone-D', 7000000, 7200000, 'emergency', '2026-02-06 11:45:00');

/* ========================================================= */
/* WATER INFRASTRUCTURE - PIPELINES */
/* ========================================================= */

-- Critical: Old pipeline with major leak
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, length_meters, pressure_psi, flow_rate, condition, operational_status, installation_date, last_inspection_date, next_inspection_due, notes) VALUES
('Downtown corridor from North Reservoir', 'Zone-A', 'supply', 800, 'cast_iron', 12500, 45.2, 15000, 'critical', 'under_repair', '1985-06-15', '2026-01-20', '2026-02-20', 'Major leak detected, emergency repairs scheduled');

-- Good: New pipeline
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, length_meters, pressure_psi, flow_rate, condition, operational_status, installation_date, last_inspection_date, next_inspection_due) VALUES
('Central Reservoir to Zone-A distribution', 'Zone-A', 'supply', 600, 'ductile_iron', 8300, 65.8, 22000, 'excellent', 'active', '2020-03-10', '2026-02-03', '2026-05-03');

-- Fair: Aging pipeline with minor issues
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, length_meters, pressure_psi, flow_rate, condition, operational_status, installation_date, last_inspection_date, next_inspection_due, notes) VALUES
('Downtown to Zone-B distribution', 'Zone-B', 'supply', 400, 'steel', 5700, 52.1, 18000, 'fair', 'active', '2005-11-22', '2026-01-15', '2026-04-15', 'Minor corrosion detected, monitoring required');

-- Poor: Pipeline needing replacement
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, length_meters, pressure_psi, flow_rate, condition, operational_status, installation_date, last_inspection_date, next_inspection_due, notes) VALUES
('Zone-C to Zone-D service line', 'Zone-D', 'supply', 300, 'galvanized_steel', 3200, 38.5, 8500, 'poor', 'active', '1992-08-05', '2025-12-10', '2026-03-10', 'Scheduled for replacement in Q2 2026');

-- Emergency: Burst pipeline (edge case - immediate action needed)
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, length_meters, pressure_psi, flow_rate, condition, operational_status, installation_date, last_inspection_date, notes) VALUES
('South Reservoir emergency line to Zone-E', 'Zone-E', 'supply', 500, 'pvc', 6800, 12.3, 2500, 'critical', 'inactive', '2015-04-18', '2026-02-08', 'BURST - Isolated, emergency repair crew dispatched');

/* ========================================================= */
/* WORKERS - Various Skills and Availability */
/* ========================================================= */

-- Available workers with different specializations
INSERT INTO workers (department, worker_name, role, skills, certifications, status, hire_date, phone, email) VALUES
('water', 'John Martinez', 'Senior Technician', '["pipeline_repair", "reservoir_maintenance", "quality_testing"]'::jsonb, '["Senior Water Tech Cert", "Safety Level 3"]'::jsonb, 'active', '2010-05-15', '555-0101', 'jmartinez@citygov.local'),
('water', 'Sarah Chen', 'Field Engineer', '["pipeline_inspection", "leak_detection", "pressure_testing"]'::jsonb, '["Engineering License", "NDT Certification"]'::jsonb, 'active', '2018-03-22', '555-0102', 'schen@citygov.local'),
('water', 'Michael Brown', 'Maintenance Lead', '["valve_operation", "pump_maintenance", "emergency_response"]'::jsonb, '["Master Plumber", "Emergency Response"]'::jsonb, 'active', '2012-08-10', '555-0103', 'mbrown@citygov.local'),
('water', 'Emily Davis', 'Water Quality Specialist', '["quality_testing", "contamination_analysis", "treatment_systems"]'::jsonb, '["Water Quality Expert", "Lab Certification"]'::jsonb, 'active', '2008-01-05', '555-0104', 'edavis@citygov.local'),
('water', 'Robert Wilson', 'Junior Technician', '["basic_repairs", "meter_reading", "customer_service"]'::jsonb, '["Basic Water Tech"]'::jsonb, 'active', '2024-06-01', '555-0105', 'rwilson@citygov.local');

-- Unavailable workers (on leave, assigned, etc.) - edge case
INSERT INTO workers (department, worker_name, role, skills, certifications, status, hire_date, phone, email) VALUES
('water', 'Lisa Anderson', 'Pipeline Specialist', '["pipeline_repair", "welding", "emergency_response"]'::jsonb, '["Welding Cert", "Pipeline Specialist"]'::jsonb, 'on_leave', '2011-09-20', '555-0106', 'landerson@citygov.local'),
('water', 'David Kim', 'Systems Operator', '["scada_operation", "pump_control", "monitoring"]'::jsonb, '["SCADA Operator", "Control Systems"]'::jsonb, 'sick', '2019-11-12', '555-0107', 'dkim@citygov.local');

-- Fire Department workers
INSERT INTO workers (department, worker_name, role, skills, certifications, status, hire_date, phone, email) VALUES
('fire', 'James Thompson', 'Fire Captain', '["firefighting", "rescue_operations", "hazmat"]'::jsonb, '["Fire Captain License", "Hazmat Response"]'::jsonb, 'active', '2009-04-15', '555-0201', 'jthompson@citygov.local'),
('fire', 'Maria Garcia', 'Paramedic', '["ems", "first_aid", "patient_transport"]'::jsonb, '["EMT-Paramedic", "Advanced Life Support"]'::jsonb, 'active', '2016-07-20', '555-0202', 'mgarcia@citygov.local');

-- Engineering workers
INSERT INTO workers (department, worker_name, role, skills, certifications, status, hire_date, phone, email) VALUES
('engineering', 'Christopher Lee', 'Civil Engineer', '["structural_design", "project_management", "cad_software"]'::jsonb, '["Professional Engineer", "PMP"]'::jsonb, 'active', '2007-02-28', '555-0301', 'clee@citygov.local'),
('engineering', 'Jennifer White', 'Construction Inspector', '["quality_control", "safety_compliance", "documentation"]'::jsonb, '["Inspector Certification", "OSHA 30"]'::jsonb, 'on_leave', '2013-10-05', '555-0302', 'jwhite@citygov.local');

/* ========================================================= */
/* WORK SCHEDULES - Various States */
/* ========================================================= */

-- Scheduled: Future work
INSERT INTO work_schedules (department, activity_type, location, scheduled_date, start_time, end_time, priority, workers_assigned, equipment_assigned, status, notes) VALUES
('water', 'pipeline_inspection', 'Downtown', '2026-02-10', '08:00:00', '16:00:00', 'high', 2, '["inspection_camera", "pressure_gauge"]'::jsonb, 'scheduled', 'Main Line A comprehensive inspection'),
('water', 'leak_detection_survey', 'Zone-B', '2026-02-11', '09:00:00', '17:00:00', 'medium', 1, '["acoustic_detector", "thermal_camera"]'::jsonb, 'scheduled', 'Routine leak detection patrol');

-- In Progress: Active work
INSERT INTO work_schedules (department, activity_type, location, scheduled_date, start_time, end_time, priority, workers_assigned, equipment_assigned, status, notes) VALUES
('water', 'emergency_valve_repair', 'Zone-A', '2026-02-08', '10:00:00', '18:00:00', 'critical', 3, '["valve_wrench", "welding_kit", "safety_barriers"]'::jsonb, 'in_progress', 'North Reservoir emergency valve repair - currently active'),
('water', 'water_quality_testing', 'Zone-C', '2026-02-08', '07:00:00', '15:00:00', 'critical', 1, '["test_kit", "sampling_equipment"]'::jsonb, 'in_progress', 'East Reservoir contamination investigation');

-- Completed: Historical work
INSERT INTO work_schedules (department, activity_type, location, scheduled_date, start_time, end_time, priority, workers_assigned, equipment_assigned, status, notes) VALUES
('water', 'routine_maintenance', 'Downtown', '2026-02-05', '08:00:00', '16:00:00', 'medium', 2, '["maintenance_tools", "cleaning_equipment"]'::jsonb, 'completed', 'Central Reservoir routine maintenance completed successfully'),
('water', 'meter_reading', 'Zone-D', '2026-02-03', '09:00:00', '17:00:00', 'low', 1, '["meter_reader", "tablet"]'::jsonb, 'completed', 'Quarterly meter readings Zone-D complete');

-- Cancelled: Postponed work (edge case)
INSERT INTO work_schedules (department, activity_type, location, scheduled_date, start_time, end_time, priority, workers_assigned, status, notes) VALUES
('water', 'pipeline_replacement', 'Zone-E', '2026-02-09', '08:00:00', '16:00:00', 'low', 4, 'cancelled', 'Postponed due to budget constraints - rescheduling pending funding');

-- Delayed: Overdue work (edge case - missed deadline)
INSERT INTO work_schedules (department, activity_type, location, scheduled_date, start_time, end_time, priority, workers_assigned, equipment_assigned, status, notes) VALUES
('water', 'critical_repair', 'Zone-C', '2026-02-06', '08:00:00', '16:00:00', 'high', 2, '["excavator", "repair_materials"]'::jsonb, 'scheduled', 'DELAYED: Weather postponed - rescheduling for next available date');

/* ========================================================= */
/* INCIDENTS - Various Severities and States */
/* ========================================================= */

-- Critical: Active emergency requiring immediate response
INSERT INTO incidents (department, incident_type, location, severity, description, reported_date, reported_by, status, notes) VALUES
('water', 'major_leak', 'Zone-A, Main Street', 'critical', 'Major water main break flooding street, affecting 500+ households', '2026-02-08 06:30:00', 'Emergency Dispatch', 'investigating', 'Emergency crews deployed, traffic diverted, residents notified'),
('water', 'contamination', 'Zone-C, East Reservoir', 'critical', 'Suspected bacterial contamination detected in water quality test', '2026-02-07 14:20:00', 'Water Quality Lab', 'investigating', 'Samples sent to state lab, residents advised to boil water');

-- High: Serious issues needing quick attention
INSERT INTO incidents (department, incident_type, location, severity, description, reported_date, reported_by, status, notes) VALUES
('water', 'pressure_drop', 'Zone-B, Commercial District', 'high', 'Significant pressure drop affecting businesses, potential pipeline damage', '2026-02-08 08:45:00', 'Business Owner', 'investigating', 'Field team en route to investigate cause'),
('water', 'service_interruption', 'Zone-D, Residential Area', 'high', 'No water service to 200 homes, cause unknown', '2026-02-08 09:15:00', 'Resident Call', 'reported', 'Investigating valve stations and pumps in area');

-- Medium: Routine issues
INSERT INTO incidents (department, incident_type, location, severity, description, reported_date, reported_by, status, notes) VALUES
('water', 'minor_leak', 'Zone-E, Park Avenue', 'medium', 'Small leak from fire hydrant, non-emergency but needs repair', '2026-02-07 11:00:00', 'Park Maintenance', 'reported', 'Scheduled for repair next week'),
('water', 'quality_concern', 'Downtown, City Hall', 'medium', 'Discolored water reported, likely sediment from old pipes', '2026-02-06 15:30:00', 'Building Manager', 'investigating', 'Flushing mains in area, testing water samples');

-- Low: Minor issues
INSERT INTO incidents (department, incident_type, location, severity, description, reported_date, reported_by, status) VALUES
('water', 'meter_malfunction', 'Zone-A, Residential', 'low', 'Water meter not recording usage correctly', '2026-02-05 10:00:00', 'Homeowner', 'reported');

-- Resolved: Completed incidents (historical data)
INSERT INTO incidents (department, incident_type, location, severity, description, reported_date, reported_by, status, resolution_date, notes) VALUES
('water', 'minor_leak', 'Zone-B, Oak Street', 'medium', 'Leak from pipe joint', '2026-02-04 13:00:00', 'Street Patrol', 'resolved', '2026-02-04 16:30:00', 'Replaced faulty joint, tested for leaks, service restored'),
('water', 'service_interruption', 'Zone-C, School District', 'high', 'Scheduled maintenance caused longer outage than planned', '2026-02-02 07:00:00', 'Maintenance Supervisor', 'closed', '2026-02-02 14:00:00', 'Maintenance completed, all valves reopened, pressure normalized');

-- Old unresolved incident (edge case - stale ticket)
INSERT INTO incidents (department, incident_type, location, severity, description, reported_date, reported_by, status, notes) VALUES
('water', 'quality_concern', 'Zone-D, Industrial Park', 'low', 'Slight odor in water, investigation pending', '2026-01-15 09:00:00', 'Factory Manager', 'reported', 'Low priority - awaiting lab availability');

/* ========================================================= */
/* PROJECTS - Various States and Budgets */
/* ========================================================= */

-- Active project: On budget and on time
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, end_date, status, notes) VALUES
('water', 'Zone-B Pipeline Upgrade Phase 2', 'infrastructure_upgrade', 'Zone-B', 450000.00, 275000.00, '2025-11-01', '2026-06-30', 'in_progress', 'Project proceeding on schedule, 60% complete');

-- Active project: Over budget (edge case)
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, end_date, status, notes) VALUES
('engineering', 'Downtown Bridge Repairs', 'maintenance', 'Downtown', 350000.00, 425000.00, '2025-10-15', '2026-03-31', 'in_progress', 'Over budget due to unexpected structural issues, completion delayed');

-- Active project: Behind schedule
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, end_date, status, notes) VALUES
('water', 'North Reservoir Expansion', 'expansion', 'Zone-A', 850000.00, 520000.00, '2025-09-01', '2026-02-28', 'in_progress', 'Delayed by weather and equipment availability, requesting extension to April 2026');

-- Planned: Approved but not started
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, status, notes) VALUES
('sanitation', 'New Recycling Facility', 'new_construction', 'Zone-F', 1200000.00, 0.00, '2026-04-01', 'approved', 'Funding secured, awaiting contractor selection');

-- Planned: Awaiting budget approval (edge case)
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, status, notes) VALUES
('health', 'Mobile Health Clinic Program', 'new_program', 'City-wide', 680000.00, 0.00, '2026-07-01', 'planned', 'Pending budget approval due to frozen health department funds');

-- Completed: Successful project
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, end_date, completion_date, status, notes) VALUES
('water', 'Central Reservoir Maintenance', 'maintenance', 'Downtown', 125000.00, 118000.00, '2025-12-01', '2026-01-31', '2026-01-28', 'completed', 'Completed under budget and ahead of schedule');

-- Cancelled: Project abandoned (edge case)
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, status, notes) VALUES
('engineering', 'Highway Extension Project', 'new_construction', 'Zone-G', 2500000.00, 350000.00, '2025-06-01', 'cancelled', 'Cancelled due to environmental concerns and community opposition after initial site work');

-- Completed: Over budget and late, but finished
INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, start_date, end_date, completion_date, status, notes) VALUES
('fire', 'New Fire Station Construction', 'new_construction', 'Zone-H', 1800000.00, 2150000.00, '2024-03-01', '2025-09-30', '2025-12-15', 'completed', 'Delivered late and over budget, but fully operational and serves growing community');

/* ========================================================= */
/* AGENT DECISIONS - Historical Decision Audit Trail */
/* ========================================================= */

-- Water agent: Approved capacity query
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, confidence, decision, reasoning, response,
    agent_version, execution_time_ms
) VALUES (
    'water_department',
    'capacity_query',
    '{"type": "capacity_query", "location": "Downtown", "query": "What is current water capacity?"}'::jsonb,
    '{"reservoirs": [{"name": "Central Reservoir", "capacity": 10000000, "level": 7500000}]}'::jsonb,
    '{"actions": ["check_reservoir_levels", "check_pipeline_status"]}'::jsonb,
    '{"reservoir_status": "operational", "available_capacity": 2500000}'::jsonb,
    true,
    'Sufficient capacity available in Central Reservoir',
    true,
    0.92,
    'approve',
    'System has adequate capacity to meet current demand. Central Reservoir at 75% capacity with healthy margins.',
    'The Downtown area is served by Central Reservoir which currently has 7.5 million liters (75% of capacity). This provides excellent capacity margins for normal operations and unexpected demand spikes.',
    '1.0',
    2340
);

-- Water agent: Escalated emergency (low confidence)
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, policy_violations, confidence, decision, reasoning, escalation_reason, response,
    agent_version, execution_time_ms
) VALUES (
    'water_department',
    'emergency_response',
    '{"type": "emergency_response", "location": "Zone-A", "severity": "critical", "incident_type": "major_leak"}'::jsonb,
    '{"workers_available": 2, "required_workers": 5, "budget_remaining": 50000}'::jsonb,
    '{"actions": ["deploy_emergency_team", "isolate_damaged_section", "notify_residents"]}'::jsonb,
    '{"available_workers": ["w1", "w3"], "required_budget": 125000}'::jsonb,
    false,
    'Insufficient workers (need 5, have 2) and budget shortfall of $75,000',
    true,
    '[]'::jsonb,
    0.45,
    'escalate',
    'Critical emergency requires resources beyond current availability. Risk of extended service disruption.',
    'Insufficient staffing and budget to execute emergency response plan within acceptable timeframe',
    'This critical water main break requires immediate attention but exceeds available resources. Human decision needed on budget reallocation and worker overtime authorization.',
    '1.0',
    1850
);

-- Fire agent: Approved emergency deployment
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, confidence, decision, reasoning, response,
    agent_version, execution_time_ms
) VALUES (
    'fire_department',
    'emergency_response',
    '{"type": "emergency_response", "location": "Zone-E", "severity": "high", "incident_type": "structure_fire"}'::jsonb,
    '{"units_available": 4, "personnel_on_duty": 12}'::jsonb,
    '{"actions": ["deploy_engine_company", "deploy_ladder_company", "request_ems"]}'::jsonb,
    '{"units_dispatched": ["Engine-1", "Ladder-2"], "eta_minutes": 4}'::jsonb,
    true,
    'Sufficient units and personnel available for immediate deployment',
    true,
    0.96,
    'approve',
    'Standard emergency response protocol activated. All required resources available and dispatched.',
    'Emergency units Engine-1 and Ladder-2 dispatched to structure fire in Zone-E with ETA of 4 minutes. EMS standing by.',
    '1.0',
    1200
);

-- Engineering agent: Denied due to depleted budget
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, policy_violations, confidence, decision, reasoning, response,
    agent_version, execution_time_ms
) VALUES (
    'engineering_department',
    'project_planning',
    '{"type": "project_planning", "location": "Zone-B", "project_type": "road_repair", "estimated_cost": 85000}'::jsonb,
    '{"budget_remaining": -5000, "budget_status": "depleted"}'::jsonb,
    '{"actions": ["assess_damage", "estimate_costs", "schedule_repairs"]}'::jsonb,
    '{"required_budget": 85000, "available_budget": -5000}'::jsonb,
    false,
    'Department budget depleted - currently $5,000 over allocated budget',
    false,
    '[{"policy": "budget_compliance", "severity": "high", "details": "Cannot approve expenditure when budget is negative"}]'::jsonb,
    0.88,
    'deny',
    'Project cannot proceed due to budget depletion. Requires budget reallocation or approval for supplemental funding.',
    'While the road repair is feasible from a technical standpoint, the Engineering Department currently has a budget overrun of $5,000. Policy requires positive budget balance before new projects can be approved. This project would require $85,000, making it financially infeasible at this time.',
    '1.0',
    1650
);

-- Health agent: Approved with high confidence
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, confidence, decision, reasoning, response,
    agent_version, execution_time_ms
) VALUES (
    'health_department',
    'inspection_request',
    '{"type": "inspection_request", "location": "Restaurant - Main Street", "inspection_type": "routine", "priority": "medium"}'::jsonb,
    '{"inspectors_available": 3, "scheduled_inspections": 5}'::jsonb,
    '{"actions": ["assign_inspector", "schedule_inspection", "notify_establishment"]}'::jsonb,
    '{"inspector_assigned": "Inspector Smith", "inspection_date": "2026-02-12"}'::jsonb,
    true,
    'Inspector available, routine inspection scheduled within standard timeframe',
    true,
    0.94,
    'approve',
    'Routine health inspection scheduled according to policy. No urgent issues requiring immediate attention.',
    'Routine health inspection for restaurant on Main Street has been scheduled for February 12, 2026. Inspector Smith assigned. Establishment will be notified 48 hours in advance per policy.',
    '1.0',
    980
);

-- Finance agent: Budget reallocation (complex decision)
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, confidence, decision, reasoning, response,
    agent_version, execution_time_ms
) VALUES (
    'finance_department',
    'budget_allocation',
    '{"type": "budget_allocation", "from_department": "fire", "to_department": "engineering", "amount": 100000, "reason": "critical infrastructure repair"}'::jsonb,
    '{"fire_budget_utilization": 0.15, "engineering_budget_status": "depleted"}'::jsonb,
    '{"actions": ["verify_source_budget", "verify_policy_compliance", "calculate_impact"]}'::jsonb,
    '{"fire_available": 625000, "reallocation_allowed": true, "impact_assessment": "low risk"}'::jsonb,
    true,
    'Fire department has significant unused budget (85% available), reallocation within policy limits',
    true,
    0.87,
    'approve',
    'Budget reallocation approved. Fire department under-utilizing budget while engineering has critical needs. Meets policy requirements for inter-departmental transfers.',
    'Approved transfer of $100,000 from Fire Department to Engineering Department. Fire currently has $625,000 available (85% of monthly budget unused) while Engineering is in budget deficit. This reallocation addresses critical infrastructure needs while maintaining adequate fire department reserves.',
    '1.0',
    3200
);

-- Sanitation agent: Escalated due to policy violation
INSERT INTO agent_decisions (
    agent_type, request_type, request_data, context_snapshot,
    plan_attempted, tool_results, feasible, feasibility_reason,
    policy_compliant, policy_violations, confidence, decision, reasoning, escalation_reason, response,
    agent_version, execution_time_ms
) VALUES (
    'sanitation_department',
    'collection_schedule',
    '{"type": "collection_schedule", "location": "Zone-F", "requested_time": "Sunday 6am", "reason": "reduce traffic congestion"}'::jsonb,
    '{"current_schedule": "weekdays only", "noise_ordinances": "no operations before 7am or on Sundays"}'::jsonb,
    '{"actions": ["evaluate_request", "check_ordinances", "assess_feasibility"]}'::jsonb,
    '{"schedule_technically_feasible": true, "ordinance_violation": true}'::jsonb,
    true,
    'Technically feasible with available equipment and personnel',
    false,
    '[{"policy": "noise_ordinance", "severity": "high", "details": "Sunday operations not permitted"}, {"policy": "early_hours_restriction", "severity": "medium", "details": "Operations before 7am require special permit"}]'::jsonb,
    0.91,
    'escalate',
    'Request violates multiple city ordinances. Would require City Council approval to override noise and Sunday operation restrictions.',
    'Multiple policy violations require council approval - cannot approve at department level',
    'The requested collection schedule change is technically feasible and would reduce traffic congestion. However, it violates city ordinances prohibiting Sunday operations and work before 7am. Such changes require City Council approval and special permits.',
    '1.0',
    2100
);

/* ========================================================= */
/* COORDINATION SCENARIOS - Multi-Agent Conflicts */
/* ========================================================= */

-- Note: These are example decisions showing how coordination agent handles conflicts
-- In practice, these would be created dynamically by the coordination agent

-- Scenario 1: Water + Engineering conflict (same location, different projects)
INSERT INTO agent_decisions (
    agent_type, request_type, request_data,
    decision, reasoning, response, created_at
) VALUES (
    'coordination_agent',
    'conflict_resolution',
    '{"conflict_type": "location_overlap", "agents": ["water", "engineering"], "location": "Zone-B, Main Street", "water_project": "pipeline_replacement", "engineering_project": "road_resurfacing"}'::jsonb,
    'approve',
    'Coordinated timeline: Water completes pipeline work first (Feb 10-15), then Engineering resurfaces road (Feb 18-22). Sequential execution prevents rework.',
    'Resolved scheduling conflict between Water and Engineering departments for Main Street Zone-B. Water Department will complete pipeline replacement February 10-15. Engineering Department will begin road resurfacing February 18-22 after pipeline work is complete and inspected.',
    '2026-02-05 10:30:00'
);

-- Scenario 2: Fire + Water cooperation (emergency requiring both)
INSERT INTO agent_decisions (
    agent_type, request_type, request_data,
    decision, reasoning, response, created_at
) VALUES (
    'coordination_agent',
    'multi_agent_coordination',
    '{"scenario": "emergency_cooperation", "agents": ["fire", "water"], "incident_type": "hydrant_fire", "location": "Zone-C, Industrial Park"}'::jsonb,
    'approve',
    'Coordinated emergency response: Fire uses hydrant for firefighting, Water increases pressure in Zone-C and monitors system. Joint operation executed successfully.',
    'Coordinated emergency response executed. Fire Department utilized hydrant at full capacity while Water Department boosted pressure in Zone-C feed lines and monitored for system stress. Emergency resolved without service disruption to other areas.',
    '2026-02-07 14:45:00'
);

/* ========================================================= */
/* DATA SUMMARY */
/* ========================================================= */

-- Display summary of inserted test data
DO $$
BEGIN
    RAISE NOTICE '================================================';
    RAISE NOTICE 'TEST DATA INSERTION COMPLETE';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Budget Records:      %', (SELECT COUNT(*) FROM department_budgets);
    RAISE NOTICE 'Reservoirs:          %', (SELECT COUNT(*) FROM reservoirs);
    RAISE NOTICE 'Pipelines:           %', (SELECT COUNT(*) FROM pipelines);
    RAISE NOTICE 'Workers:             %', (SELECT COUNT(*) FROM workers);
    RAISE NOTICE 'Work Schedules:      %', (SELECT COUNT(*) FROM work_schedules);
    RAISE NOTICE 'Incidents:           %', (SELECT COUNT(*) FROM incidents);
    RAISE NOTICE 'Projects:            %', (SELECT COUNT(*) FROM projects);
    RAISE NOTICE 'Agent Decisions:     %', (SELECT COUNT(*) FROM agent_decisions);
    RAISE NOTICE '================================================';
    RAISE NOTICE 'EDGE CASES INCLUDED:';
    RAISE NOTICE '  - Depleted budgets (Engineering)';
    RAISE NOTICE '  - Frozen budgets (Health)';
    RAISE NOTICE '  - Nearly empty reservoir (North Reservoir 11%%)';
    RAISE NOTICE '  - Contaminated water (East Reservoir)';
    RAISE NOTICE '  - Over capacity reservoir (West Reservoir 103%%)';
    RAISE NOTICE '  - Burst pipeline (Zone-E inactive)';
    RAISE NOTICE '  - Critical incidents (major leak, contamination)';
    RAISE NOTICE '  - Over-budget projects (+21%%)';
    RAISE NOTICE '  - Behind schedule projects';
    RAISE NOTICE '  - Cancelled projects';
    RAISE NOTICE '  - Unavailable workers (on_leave, sick status)';
    RAISE NOTICE '  - Delayed/cancelled work schedules';
    RAISE NOTICE '  - Policy violations in decisions';
    RAISE NOTICE '  - Multi-agent conflicts';
    RAISE NOTICE '================================================';
END $$;
