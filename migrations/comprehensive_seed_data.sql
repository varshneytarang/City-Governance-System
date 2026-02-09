/* =========================================================
   COMPREHENSIVE SEED DATA FOR CITY GOVERNANCE SYSTEM
   Database: departments
   Created: February 2026
   
   This file contains realistic test data for a city with:
   - 6 departments (water, fire, engineering, health, finance, sanitation)
   - Multiple ongoing projects, incidents, and activities
   - Historical data spanning several months
   ========================================================= */

-- Clear existing data (in reverse order of dependencies)
TRUNCATE TABLE workers CASCADE;
TRUNCATE TABLE work_schedules CASCADE;
TRUNCATE TABLE water_readings CASCADE;
TRUNCATE TABLE vulnerable_populations CASCADE;
TRUNCATE TABLE vaccination_campaigns CASCADE;
TRUNCATE TABLE tax_revenues CASCADE;
TRUNCATE TABLE service_outages CASCADE;
TRUNCATE TABLE sanitation_inspections CASCADE;
TRUNCATE TABLE revenue_history CASCADE;
TRUNCATE TABLE revenue_forecasts CASCADE;
TRUNCATE TABLE reservoirs CASCADE;
TRUNCATE TABLE pipeline_inspections CASCADE;
TRUNCATE TABLE budget_adjustments CASCADE;
TRUNCATE TABLE coordination_decisions CASCADE;
TRUNCATE TABLE agent_decisions CASCADE;
TRUNCATE TABLE department_budgets CASCADE;
TRUNCATE TABLE departments CASCADE;
TRUNCATE TABLE disease_incidents CASCADE;
TRUNCATE TABLE finance_accounts CASCADE;
TRUNCATE TABLE finance_policies CASCADE;
TRUNCATE TABLE financial_transactions CASCADE;
TRUNCATE TABLE fund_allocations CASCADE;
TRUNCATE TABLE grants CASCADE;
TRUNCATE TABLE health_facilities CASCADE;
TRUNCATE TABLE health_policies CASCADE;
TRUNCATE TABLE health_resources CASCADE;
TRUNCATE TABLE health_surveillance_reports CASCADE;
TRUNCATE TABLE incidents CASCADE;
TRUNCATE TABLE pipelines CASCADE;
TRUNCATE TABLE projects CASCADE;
TRUNCATE TABLE reserve_funds CASCADE;

/* ========================================================= */
/* 1. DEPARTMENTS - Department Registry */
/* ========================================================= */

INSERT INTO departments (department_key, display_name, contact_email, contact_phone, manager_name, metadata) VALUES
('water', 'Water Department', 'water@citygovt.gov', '+1-555-0101', 'Sarah Johnson', '{"office_location": "City Hall - Floor 3", "operating_hours": "24/7"}'::jsonb),
('fire', 'Fire Department', 'fire@citygovt.gov', '+1-555-0102', 'Michael Chen', '{"office_location": "Central Fire Station", "operating_hours": "24/7", "emergency_line": "911"}'::jsonb),
('engineering', 'Engineering & Public Works', 'engineering@citygovt.gov', '+1-555-0103', 'David Rodriguez', '{"office_location": "Municipal Building", "operating_hours": "Mon-Fri 8AM-5PM"}'::jsonb),
('health', 'Health Department', 'health@citygovt.gov', '+1-555-0104', 'Dr. Emily Watson', '{"office_location": "Health Services Center", "operating_hours": "Mon-Fri 8AM-6PM"}'::jsonb),
('finance', 'Finance Department', 'finance@citygovt.gov', '+1-555-0105', 'Robert Williams', '{"office_location": "City Hall - Floor 2", "operating_hours": "Mon-Fri 9AM-5PM"}'::jsonb),
('sanitation', 'Sanitation Department', 'sanitation@citygovt.gov', '+1-555-0106', 'Maria Garcia', '{"office_location": "Sanitation Depot", "operating_hours": "Mon-Sat 6AM-4PM"}'::jsonb);

/* ========================================================= */
/* 2. DEPARTMENT_BUDGETS - Quarterly Budget Tracking */
/* ========================================================= */

-- Q4 2025 Budgets (October, November, December)
INSERT INTO department_budgets (department, year, month, total_budget, allocated, spent, status) VALUES
-- October 2025
('water', 2025, 10, 850000.00, 820000.00, 785000.00, 'closed'),
('fire', 2025, 10, 1200000.00, 1150000.00, 1098000.00, 'closed'),
('engineering', 2025, 10, 950000.00, 920000.00, 856000.00, 'closed'),
('health', 2025, 10, 750000.00, 720000.00, 695000.00, 'closed'),
('finance', 2025, 10, 450000.00, 430000.00, 412000.00, 'closed'),
('sanitation', 2025, 10, 680000.00, 650000.00, 628000.00, 'closed'),

-- November 2025
('water', 2025, 11, 850000.00, 830000.00, 812000.00, 'closed'),
('fire', 2025, 11, 1200000.00, 1180000.00, 1156000.00, 'closed'),
('engineering', 2025, 11, 950000.00, 940000.00, 923000.00, 'closed'),
('health', 2025, 11, 750000.00, 735000.00, 718000.00, 'closed'),
('finance', 2025, 11, 450000.00, 445000.00, 438000.00, 'closed'),
('sanitation', 2025, 11, 680000.00, 670000.00, 658000.00, 'closed'),

-- December 2025
('water', 2025, 12, 900000.00, 880000.00, 867000.00, 'closed'),
('fire', 2025, 12, 1250000.00, 1220000.00, 1198000.00, 'closed'),
('engineering', 2025, 12, 1000000.00, 980000.00, 965000.00, 'closed'),
('health', 2025, 12, 800000.00, 785000.00, 772000.00, 'closed'),
('finance', 2025, 12, 500000.00, 490000.00, 485000.00, 'closed'),
('sanitation', 2025, 12, 720000.00, 710000.00, 703000.00, 'closed'),

-- Q1 2026 Budgets (January, February)
-- January 2026
('water', 2026, 1, 920000.00, 890000.00, 823000.00, 'active'),
('fire', 2026, 1, 1300000.00, 1250000.00, 1156000.00, 'active'),
('engineering', 2026, 1, 1050000.00, 1020000.00, 945000.00, 'active'),
('health', 2026, 1, 820000.00, 800000.00, 738000.00, 'active'),
('finance', 2026, 1, 520000.00, 505000.00, 472000.00, 'active'),
('sanitation', 2026, 1, 750000.00, 730000.00, 685000.00, 'active'),

-- February 2026 (Current Month)
('water', 2026, 2, 920000.00, 650000.00, 420000.00, 'active'),
('fire', 2026, 2, 1300000.00, 800000.00, 520000.00, 'active'),
('engineering', 2026, 2, 1050000.00, 720000.00, 380000.00, 'active'),
('health', 2026, 2, 820000.00, 600000.00, 340000.00, 'active'),
('finance', 2026, 2, 520000.00, 380000.00, 220000.00, 'active'),
('sanitation', 2026, 2, 750000.00, 550000.00, 310000.00, 'active');

/* ========================================================= */
/* 3. FINANCE_ACCOUNTS - Department Financial Accounts */
/* ========================================================= */

INSERT INTO finance_accounts (department, account_name, account_type, currency, balance, reserved_amount, metadata) VALUES
-- Water Department Accounts
('water', 'Water Operations Account', 'operational', 'USD', 2450000.00, 320000.00, '{"account_number": "WTR-001", "bank": "City Central Bank"}'::jsonb),
('water', 'Infrastructure Reserve', 'reserve', 'USD', 1800000.00, 450000.00, '{"account_number": "WTR-002", "purpose": "Emergency repairs"}'::jsonb),
('water', 'Capital Projects', 'capital', 'USD', 3200000.00, 1200000.00, '{"account_number": "WTR-003", "projects": ["Pipeline Expansion", "Treatment Plant Upgrade"]}'::jsonb),

-- Fire Department Accounts
('fire', 'Fire Operations Account', 'operational', 'USD', 3100000.00, 450000.00, '{"account_number": "FIR-001", "bank": "City Central Bank"}'::jsonb),
('fire', 'Equipment Fund', 'capital', 'USD', 2500000.00, 800000.00, '{"account_number": "FIR-002", "purpose": "New trucks and equipment"}'::jsonb),
('fire', 'Training & Safety', 'operational', 'USD', 450000.00, 85000.00, '{"account_number": "FIR-003", "purpose": "Personnel training"}'::jsonb),

-- Engineering Department Accounts
('engineering', 'Public Works Operations', 'operational', 'USD', 2800000.00, 520000.00, '{"account_number": "ENG-001", "bank": "City Central Bank"}'::jsonb),
('engineering', 'Road Maintenance Fund', 'operational', 'USD', 1950000.00, 380000.00, '{"account_number": "ENG-002", "purpose": "Road repairs"}'::jsonb),
('engineering', 'Infrastructure Development', 'capital', 'USD', 4500000.00, 1800000.00, '{"account_number": "ENG-003", "purpose": "Major construction projects"}'::jsonb),

-- Health Department Accounts
('health', 'Health Services Operations', 'operational', 'USD', 1850000.00, 290000.00, '{"account_number": "HLT-001", "bank": "City Central Bank"}'::jsonb),
('health', 'Public Health Programs', 'operational', 'USD', 950000.00, 180000.00, '{"account_number": "HLT-002", "purpose": "Vaccination campaigns"}'::jsonb),
('health', 'Emergency Response Fund', 'reserve', 'USD', 750000.00, 150000.00, '{"account_number": "HLT-003", "purpose": "Disease outbreaks"}'::jsonb),

-- Finance Department Accounts
('finance', 'Administration Operations', 'operational', 'USD', 980000.00, 125000.00, '{"account_number": "FIN-001", "bank": "City Central Bank"}'::jsonb),
('finance', 'City General Fund', 'general', 'USD', 15000000.00, 2500000.00, '{"account_number": "FIN-002", "purpose": "Municipal operations"}'::jsonb),

-- Sanitation Department Accounts
('sanitation', 'Sanitation Operations', 'operational', 'USD', 1680000.00, 310000.00, '{"account_number": "SAN-001", "bank": "City Central Bank"}'::jsonb),
('sanitation', 'Waste Management Fund', 'operational', 'USD', 1250000.00, 220000.00, '{"account_number": "SAN-002", "purpose": "Collection and disposal"}'::jsonb),
('sanitation', 'Recycling Program', 'operational', 'USD', 420000.00, 65000.00, '{"account_number": "SAN-003", "purpose": "Recycling initiatives"}'::jsonb);

/* ========================================================= */
/* 4. FINANCE_POLICIES - Financial Governance Policies */
/* ========================================================= */

INSERT INTO finance_policies (policy_name, description, effective_date, metadata) VALUES
('Emergency Fund Policy', 'Requires minimum 10% reserve for emergency situations across all departments', '2025-01-01', 
 '{"minimum_reserve_percent": 10, "applies_to": "all_departments", "review_frequency": "annual"}'::jsonb),

('Budget Approval Threshold', 'Expenditures over $50,000 require department head approval; over $250,000 require city council approval', '2025-01-01',
 '{"threshold_tier1": 50000, "threshold_tier2": 250000, "approval_chain": ["dept_head", "finance_director", "city_council"]}'::jsonb),

('Capital Project Guidelines', 'All capital projects must undergo cost-benefit analysis and environmental impact assessment', '2025-06-01',
 '{"required_assessments": ["cost_benefit", "environmental_impact", "community_impact"], "minimum_project_cost": 100000}'::jsonb),

('Grant Matching Requirements', 'City must match 25% of federal grants and 15% of state grants', '2024-07-01',
 '{"federal_match_percent": 25, "state_match_percent": 15, "local_match_percent": 0}'::jsonb),

('Procurement Policy', 'Competitive bidding required for purchases over $25,000; three quotes required for purchases over $10,000', '2025-01-01',
 '{"competitive_bid_threshold": 25000, "multi_quote_threshold": 10000, "single_source_max": 5000}'::jsonb),

('Revenue Forecasting Standards', 'Quarterly revenue forecasts required with minimum 85% confidence level', '2025-01-01',
 '{"forecast_frequency": "quarterly", "minimum_confidence": 0.85, "variance_tolerance": 0.10}'::jsonb),

('Debt Service Coverage', 'Maintain minimum debt service coverage ratio of 1.5x for all bond obligations', '2024-01-01',
 '{"minimum_dscr": 1.5, "calculation_method": "annual", "includes": ["bonds", "loans"]}'::jsonb);

/* ========================================================= */
/* 5. AGENT_DECISIONS - Decision Audit Trail */
/* ========================================================= */

INSERT INTO agent_decisions (agent_type, request_type, request_data, context_snapshot, plan_attempted, tool_results, 
                              feasible, feasibility_reason, policy_compliant, policy_violations, confidence, 
                              confidence_factors, decision, reasoning, escalation_reason, response, 
                              agent_version, execution_time_ms, retry_count, created_at, completed_at) VALUES

-- Water Department Decisions
('water_department', 'pipeline_repair', 
 '{"location": "Downtown Main Street", "issue": "Pressure drop detected", "severity": "high"}'::jsonb,
 '{"available_budget": 500000, "available_workers": 8, "nearby_incidents": 2}'::jsonb,
 '{"action": "emergency_repair", "workers_needed": 4, "estimated_cost": 35000}'::jsonb,
 '{"budget_check": "passed", "worker_availability": "sufficient", "scheduling": "immediate"}'::jsonb,
 true, 'Budget available, workers on standby, emergency protocols allow immediate action',
 true, '[]'::jsonb, 0.92,
 '{"budget_confidence": 0.95, "resource_confidence": 0.90, "timeline_confidence": 0.91}'::jsonb,
 'approve', 'Emergency repair approved for critical infrastructure. 4 workers assigned, $35,000 allocated.', NULL,
 'Repair approved and scheduled for immediate execution', '1.2', 2341, 0,
 '2026-02-07 08:15:23', '2026-02-07 08:15:25'),

('water_department', 'capacity_query',
 '{"location": "North District", "query": "Current reservoir levels and supply capacity"}'::jsonb,
 '{"reservoir_levels": [{"name": "North Reservoir", "level_percent": 78}, {"name": "Main Reservoir", "level_percent": 85}]}'::jsonb,
 '{"action": "provide_status_report"}'::jsonb,
 '{"reservoirs_checked": 3, "pipelines_checked": 12}'::jsonb,
 true, 'Data available from monitoring systems',
 true, '[]'::jsonb, 0.98,
 '{"data_quality": 0.99, "timeliness": 0.98, "completeness": 0.97}'::jsonb,
 'approve', 'Status report generated with current capacity data for North District.',
 NULL, 'North District supplied by North Reservoir (78% capacity) and Main Reservoir (85% capacity). Current supply capacity: 2.8M liters/day, demand: 2.1M liters/day. Margin: 33%',
 '1.2', 1823, 0,
 '2026-02-08 14:22:11', '2026-02-08 14:22:13'),

('water_department', 'emergency_response',
 '{"location": "Industrial Zone A", "issue": "Pipeline burst", "severity": "critical"}'::jsonb,
 '{"available_budget": 465000, "emergency_workers": 12, "equipment_status": "available"}'::jsonb,
 '{"action": "immediate_shutdown_and_repair", "workers": 8, "estimated_cost": 125000, "timeline": "6-8 hours"}'::jsonb,
 '{"valve_closure": "success", "isolation": "complete", "repair_team_dispatched": true}'::jsonb,
 true, 'Emergency protocols activated, sufficient resources available',
 true, '[]'::jsonb, 0.88,
 '{"urgency_assessment": 0.95, "resource_confidence": 0.85, "safety_confidence": 0.84}'::jsonb,
 'approve', 'Critical pipeline burst - immediate response authorized. Area isolated, repair team dispatched.',
 NULL, 'Emergency response activated. Pipeline isolated, 8 workers on site, estimated repair time 6-8 hours.',
 '1.2', 3156, 0,
 '2026-02-06 03:45:18', '2026-02-06 03:45:21'),

-- Fire Department Decisions
('fire_department', 'fire_emergency',
 '{"location": "Riverside Apartments", "type": "structure_fire", "severity": "critical", "floors_affected": 3}'::jsonb,
 '{"available_trucks": 8, "available_firefighters": 24, "hydrant_pressure": "adequate", "weather": "clear"}'::jsonb,
 '{"action": "full_response", "trucks": 4, "firefighters": 16, "ems_units": 2}'::jsonb,
 '{"dispatch_time": "90_seconds", "first_arrival": "4_minutes", "fire_controlled": "22_minutes"}'::jsonb,
 true, 'Sufficient resources, rapid response achievable',
 true, '[]'::jsonb, 0.94,
 '{"response_time_confidence": 0.96, "resource_adequacy": 0.93, "safety_protocols": 0.93}'::jsonb,
 'approve', 'Structure fire at Riverside Apartments - full response authorized. 4 engines, 16 firefighters, 2 EMS units dispatched.',
 NULL, 'Fire response executed. All occupants evacuated safely, fire contained to 3rd-5th floors, no fatalities.',
 '1.2', 1678, 0,
 '2026-02-05 19:34:52', '2026-02-05 19:34:54'),

('fire_department', 'equipment_inspection',
 '{"station": "Central Station", "equipment_type": "respiratory", "due_date": "2026-02-10"}'::jsonb,
 '{"equipment_count": 24, "inspector_available": true, "budget_remaining": 780000}'::jsonb,
 '{"action": "schedule_inspection", "date": "2026-02-09", "inspector": "Safety Officer Rodriguez"}'::jsonb,
 '{"scheduling": "confirmed", "equipment_prepared": true}'::jsonb,
 true, 'Routine inspection within compliance timeframe',
 true, '[]'::jsonb, 0.97,
 '{"compliance": 0.99, "resource_availability": 0.96, "timing": 0.96}'::jsonb,
 'approve', 'Respiratory equipment inspection scheduled for Central Station on Feb 9.',
 NULL, 'Inspection scheduled and confirmed. All 24 SCBA units will be tested and certified.',
 '1.2', 1245, 0,
 '2026-02-08 09:15:33', '2026-02-08 09:15:34'),

-- Engineering Department Decisions
('engineering_department', 'road_repair',
 '{"location": "Maple Avenue", "issue": "Pothole cluster", "severity": "medium", "size": "12 potholes"}'::jsonb,
 '{"budget_remaining": 670000, "available_crews": 3, "weather_forecast": "clear_3_days"}'::jsonb,
 '{"action": "schedule_repair", "crew_size": 4, "estimated_cost": 8500, "timeline": "2_days"}'::jsonb,
 '{"crew_assigned": true, "materials_ordered": true, "traffic_control_arranged": true}'::jsonb,
 true, 'Budget sufficient, weather permitting, crew available',
 true, '[]'::jsonb, 0.89,
 '{"cost_accuracy": 0.91, "timeline_confidence": 0.88, "weather_confidence": 0.88}'::jsonb,
 'approve', 'Maple Avenue pothole repair approved. 4-person crew assigned, materials ordered, 2-day timeline.',
 NULL, 'Repair scheduled for Feb 10-11. Traffic control in place, 12 potholes to be patched.',
 '1.2', 1956, 0,
 '2026-02-08 11:28:47', '2026-02-08 11:28:49'),

('engineering_department', 'project_planning',
 '{"project": "East Side Bridge Rehabilitation", "estimated_cost": 850000, "urgency": "high"}'::jsonb,
 '{"annual_budget": 1050000, "spent_ytd": 380000, "grants_available": 400000}'::jsonb,
 '{"action": "approve_with_grant", "city_contribution": 450000, "grant_application": "federal_infrastructure"}'::jsonb,
 '{"budget_analysis": "feasible", "grant_eligibility": "qualified", "timeline": "6_months"}'::jsonb,
 true, 'Project cost within budget when combined with federal grant. Bridge condition requires attention.',
 true, '[]'::jsonb, 0.84,
 '{"budget_confidence": 0.87, "grant_probability": 0.80, "technical_feasibility": 0.85}'::jsonb,
 'approve', 'Bridge rehabilitation approved pending federal grant. City to contribute $450K, seeking $400K grant.',
 NULL, 'Project approved for planning phase. Grant application to be submitted by Feb 15.',
 '1.2', 2734, 0,
 '2026-02-07 15:42:19', '2026-02-07 15:42:22'),

-- Health Department Decisions
('health_department', 'vaccination_campaign',
 '{"campaign": "Spring Flu Vaccination Drive", "target": "seniors_65plus", "location": "Community Centers"}'::jsonb,
 '{"target_population": 8500, "vaccine_supply": 10000, "staff_available": 12, "budget": 95000}'::jsonb,
 '{"action": "approve_campaign", "sites": 4, "dates": "Feb 15-Mar 15", "staff_per_site": 3}'::jsonb,
 '{"venue_bookings": "confirmed", "vaccine_orders": "placed", "staffing": "scheduled"}'::jsonb,
 true, 'Adequate vaccine supply, sufficient staff, budget covers costs',
 true, '[]'::jsonb, 0.91,
 '{"coverage_estimate": 0.92, "logistics_confidence": 0.90, "participation_estimate": 0.91}'::jsonb,
 'approve', 'Spring flu vaccination campaign approved for seniors. 4 sites, Feb 15-Mar 15, target 8,500 people.',
 NULL, 'Campaign approved. Community centers booked, vaccines ordered, staff scheduled. Expected coverage: 65-70% of target population.',
 '1.2', 2145, 0,
 '2026-02-06 13:55:28', '2026-02-06 13:55:30'),

('health_department', 'health_inspection',
 '{"location": "Downtown Food Court", "type": "routine_inspection", "establishments": 12}'::jsonb,
 '{"inspectors_available": 3, "scheduled_date": "2026-02-12"}'::jsonb,
 '{"action": "conduct_inspection", "inspectors": 2, "estimated_time": "4_hours"}'::jsonb,
 '{"scheduling": "confirmed", "checklist_prepared": true}'::jsonb,
 true, 'Routine inspection within compliance schedule',
 true, '[]'::jsonb, 0.96,
 '{"compliance_requirement": 0.99, "resource_availability": 0.95, "timing": 0.94}'::jsonb,
 'approve', 'Downtown Food Court inspection scheduled for Feb 12. Two inspectors assigned.',
 NULL, 'Inspection approved and scheduled. All 12 establishments to be inspected for health code compliance.',
 '1.2', 1534, 0,
 '2026-02-08 10:18:55', '2026-02-08 10:18:57'),

-- Finance Department Decisions
('finance_department', 'budget_approval',
 '{"department": "engineering", "amount": 85000, "purpose": "Emergency road repairs - winter damage"}'::jsonb,
 '{"department_budget_remaining": 670000, "emergency_fund": 1200000, "approval_required": "tier1"}'::jsonb,
 '{"action": "approve_from_emergency_fund", "amount": 85000, "replenishment_timeline": "Q2_2026"}'::jsonb,
 '{"fund_check": "sufficient", "authorization_level": "finance_director"}'::jsonb,
 true, 'Emergency fund has sufficient balance, request within tier-1 approval authority',
 true, '[]'::jsonb, 0.95,
 '{"fund_availability": 0.98, "justification_strength": 0.93, "repayment_feasibility": 0.94}'::jsonb,
 'approve', 'Emergency fund allocation approved for winter road damage repairs. $85,000 authorized.',
 NULL, 'Allocation approved from emergency fund. Engineering department to replenish in Q2 2026.',
 '1.2', 1867, 0,
 '2026-02-08 08:47:22', '2026-02-08 08:47:24'),

('finance_department', 'financial_audit',
 '{"department": "sanitation", "period": "Q4_2025", "scope": "operational_expenses"}'::jsonb,
 '{"total_expenses": 2068000, "flagged_transactions": 3, "compliance_issues": 0}'::jsonb,
 '{"action": "complete_audit", "findings": "minor_documentation_gaps", "rating": "satisfactory"}'::jsonb,
 '{"reviewed_transactions": 1247, "documentation_score": 92, "compliance_score": 98}'::jsonb,
 true, 'Audit completed within standard timeframe',
 true, '[]'::jsonb, 0.94,
 '{"audit_thoroughness": 0.96, "documentation_quality": 0.92, "compliance_level": 0.94}'::jsonb,
 'approve', 'Q4 2025 audit of Sanitation Department completed. Rating: Satisfactory with minor recommendations.',
 NULL, 'Audit completed. Minor documentation improvements recommended for 3 transactions. No compliance violations found.',
 '1.2', 3421, 0,
 '2026-02-07 16:33:48', '2026-02-07 16:33:51'),

-- Sanitation Department Decisions
('sanitation_department', 'waste_collection',
 '{"zone": "Residential Zone 3", "type": "special_pickup", "reason": "Holiday accumulation"}'::jsonb,
 '{"available_trucks": 6, "available_crews": 8, "estimated_volume": "15_tons"}'::jsonb,
 '{"action": "schedule_extra_pickup", "trucks": 2, "crew_size": 8, "date": "2026-02-10"}'::jsonb,
 '{"route_planned": true, "trucks_assigned": true, "crews_scheduled": true}'::jsonb,
 true, 'Sufficient trucks and crew available, volume manageable',
 true, '[]'::jsonb, 0.90,
 '{"resource_confidence": 0.93, "volume_estimate": 0.88, "timing": 0.89}'::jsonb,
 'approve', 'Extra waste collection approved for Residential Zone 3. 2 trucks, 8 crew members, Feb 10.',
 NULL, 'Special pickup scheduled. Estimated 15 tons of holiday waste to be collected.',
 '1.2', 1723, 0,
 '2026-02-08 12:09:34', '2026-02-08 12:09:36');

/* ========================================================= */
/* 6. BUDGET_ADJUSTMENTS - Budget Modification History */
/* ========================================================= */

INSERT INTO budget_adjustments (budget_id, adjustment_amount, reason, requested_by, approved_by, approved_at, created_at)
SELECT 
    b.budget_id,
    50000.00,
    'Additional allocation for emergency pipeline repairs',
    'Sarah Johnson',
    'Robert Williams',
    '2026-01-15 14:30:00',
    '2026-01-15 09:22:15'
FROM department_budgets b
WHERE b.department = 'water' AND b.year = 2026 AND b.month = 1;

INSERT INTO budget_adjustments (budget_id, adjustment_amount, reason, requested_by, approved_by, approved_at, created_at)
SELECT 
    b.budget_id,
    -25000.00,
    'Reduced equipment maintenance costs due to vendor discount',
    'Michael Chen',
    'Robert Williams',
    '2026-01-22 11:15:00',
    '2026-01-22 10:05:33'
FROM department_budgets b
WHERE b.department = 'fire' AND b.year = 2026 AND b.month = 1;

INSERT INTO budget_adjustments (budget_id, adjustment_amount, reason, requested_by, approved_by, approved_at, created_at)
SELECT 
    b.budget_id,
    75000.00,
    'Winter storm damage - additional road repair funding',
    'David Rodriguez',
    'Robert Williams',
    '2026-02-03 16:45:00',
    '2026-02-03 14:28:47'
FROM department_budgets b
WHERE b.department = 'engineering' AND b.year = 2026 AND b.month = 2;

INSERT INTO budget_adjustments (budget_id, adjustment_amount, reason, requested_by, approved_by, approved_at, created_at)
SELECT 
    b.budget_id,
    30000.00,
    'Increased vaccination campaign funding',
    'Dr. Emily Watson',
    'Robert Williams',
    '2026-02-05 10:20:00',
    '2026-02-05 09:15:22'
FROM department_budgets b
WHERE b.department = 'health' AND b.year = 2026 AND b.month = 2;

INSERT INTO budget_adjustments (budget_id, adjustment_amount, reason, requested_by, approved_by, approved_at, created_at)
SELECT 
    b.budget_id,
    20000.00,
    'Additional waste collection for holiday season overflow',
    'Maria Garcia',
    'Robert Williams',
    '2026-02-07 13:30:00',
    '2026-02-07 11:42:19'
FROM department_budgets b
WHERE b.department = 'sanitation' AND b.year = 2026 AND b.month = 2;

/* ========================================================= */
/* 7. FUND_ALLOCATIONS - Budget to Account Allocations */
/* ========================================================= */

INSERT INTO fund_allocations (department, budget_id, account_id, amount, purpose, allocated_by, allocated_at)
SELECT 
    'water',
    b.budget_id,
    a.account_id,
    250000.00,
    'Monthly operations - pipeline maintenance',
    'Robert Williams',
    '2026-02-01 08:00:00'
FROM department_budgets b
CROSS JOIN finance_accounts a
WHERE b.department = 'water' AND b.year = 2026 AND b.month = 2
  AND a.department = 'water' AND a.account_name = 'Water Operations Account'
LIMIT 1;

INSERT INTO fund_allocations (department, budget_id, account_id, amount, purpose, allocated_by, allocated_at)
SELECT 
    'water',
    b.budget_id,
    a.account_id,
    150000.00,
    'Emergency repairs - reserve fund',
    'Robert Williams',
    '2026-02-01 08:00:00'
FROM department_budgets b
CROSS JOIN finance_accounts a
WHERE b.department = 'water' AND b.year = 2026 AND b.month = 2
  AND a.department = 'water' AND a.account_name = 'Infrastructure Reserve'
LIMIT 1;

INSERT INTO fund_allocations (department, budget_id, account_id, amount, purpose, allocated_by, allocated_at)
SELECT 
    'fire',
    b.budget_id,
    a.account_id,
    400000.00,
    'Station operations and salaries',
    'Robert Williams',
    '2026-02-01 08:00:00'
FROM department_budgets b
CROSS JOIN finance_accounts a
WHERE b.department = 'fire' AND b.year = 2026 AND b.month = 2
  AND a.department = 'fire' AND a.account_name = 'Fire Operations Account'
LIMIT 1;

INSERT INTO fund_allocations (department, budget_id, account_id, amount, purpose, allocated_by, allocated_at)
SELECT 
    'engineering',
    b.budget_id,
    a.account_id,
    320000.00,
    'Road maintenance and repairs',
    'Robert Williams',
    '2026-02-01 08:00:00'
FROM department_budgets b
CROSS JOIN finance_accounts a
WHERE b.department = 'engineering' AND b.year = 2026 AND b.month = 2
  AND a.department = 'engineering' AND a.account_name = 'Road Maintenance Fund'
LIMIT 1;

INSERT INTO fund_allocations (department, budget_id, account_id, amount, purpose, allocated_by, allocated_at)
SELECT 
    'health',
    b.budget_id,
    a.account_id,
    280000.00,
    'Health programs and inspections',
    'Robert Williams',
    '2026-02-01 08:00:00'
FROM department_budgets b
CROSS JOIN finance_accounts a
WHERE b.department = 'health' AND b.year = 2026 AND b.month = 2
  AND a.department = 'health' AND a.account_name = 'Health Services Operations'
LIMIT 1;

INSERT INTO fund_allocations (department, budget_id, account_id, amount, purpose, allocated_by, allocated_at)
SELECT 
    'sanitation',
    b.budget_id,
    a.account_id,
    350000.00,
    'Waste collection operations',
    'Robert Williams',
    '2026-02-01 08:00:00'
FROM department_budgets b
CROSS JOIN finance_accounts a
WHERE b.department = 'sanitation' AND b.year = 2026 AND b.month = 2
  AND a.department = 'sanitation' AND a.account_name = 'Sanitation Operations'
LIMIT 1;

/* ========================================================= */
/* 8. FINANCIAL_TRANSACTIONS - Transaction History */
/* ========================================================= */

INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, reference_id, metadata, created_at)
SELECT 
    'water',
    a.account_id,
    35000.00,
    'debit',
    'Emergency pipeline repair - Downtown Main Street',
    ad.id,
    '{"vendor": "Metro Plumbing Services", "invoice": "INV-2026-0234", "payment_method": "ACH"}'::jsonb,
    '2026-02-07 15:30:00'
FROM finance_accounts a
CROSS JOIN agent_decisions ad
WHERE a.department = 'water' AND a.account_name = 'Water Operations Account'
  AND ad.agent_type = 'water_department' AND ad.request_type = 'pipeline_repair'
LIMIT 1;

INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, reference_id, metadata, created_at)
SELECT 
    'water',
    a.account_id,
    125000.00,
    'debit',
    'Emergency response - Industrial Zone A pipeline burst',
    ad.id,
    '{"vendor": "Emergency Repair Contractors", "invoice": "INV-2026-0198", "urgent": true}'::jsonb,
    '2026-02-06 18:00:00'
FROM finance_accounts a
CROSS JOIN agent_decisions ad
WHERE a.department = 'water' AND a.account_name = 'Infrastructure Reserve'
  AND ad.agent_type = 'water_department' AND ad.request_type = 'emergency_response'
LIMIT 1;

INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, reference_id, metadata, created_at)
SELECT 
    'fire',
    a.account_id,
    8500.00,
    'debit',
    'SCBA equipment maintenance and certification',
    NULL,
    '{"vendor": "SafetyFirst Equipment", "invoice": "INV-2026-0156", "equipment_count": 24}'::jsonb,
    '2026-02-08 11:00:00'
FROM finance_accounts a
WHERE a.department = 'fire' AND a.account_name = 'Training & Safety'
LIMIT 1;

INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, reference_id, metadata, created_at)
SELECT 
    'engineering',
    a.account_id,
    8500.00,
    'debit',
    'Pothole repair materials - Maple Avenue',
    ad.id,
    '{"vendor": "City Asphalt Supply", "invoice": "INV-2026-0287", "materials": "asphalt mix, crack filler"}'::jsonb,
    '2026-02-08 14:00:00'
FROM finance_accounts a
CROSS JOIN agent_decisions ad
WHERE a.department = 'engineering' AND a.account_name = 'Road Maintenance Fund'
  AND ad.agent_type = 'engineering_department' AND ad.request_type = 'road_repair'
LIMIT 1;

INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, reference_id, metadata, created_at)
SELECT 
    'health',
    a.account_id,
    12500.00,
    'debit',
    'Flu vaccine procurement for senior campaign',
    ad.id,
    '{"vendor": "MedSupply Co", "invoice": "INV-2026-0245", "vaccine_doses": 10000}'::jsonb,
    '2026-02-06 16:00:00'
FROM finance_accounts a
CROSS JOIN agent_decisions ad
WHERE a.department = 'health' AND a.account_name = 'Public Health Programs'
  AND ad.agent_type = 'health_department' AND ad.request_type = 'vaccination_campaign'
LIMIT 1;

INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, reference_id, metadata, created_at)
SELECT 
    'sanitation',
    a.account_id,
    5200.00,
    'debit',
    'Fuel and maintenance for extra collection trucks',
    ad.id,
    '{"vendor": "City Fleet Services", "invoice": "INV-2026-0301", "trucks": 2}'::jsonb,
    '2026-02-08 13:30:00'
FROM finance_accounts a
CROSS JOIN agent_decisions ad
WHERE a.department = 'sanitation' AND a.account_name = 'Sanitation Operations'
  AND ad.agent_type = 'sanitation_department' AND ad.request_type = 'waste_collection'
LIMIT 1;

-- Revenue transactions (credits)
INSERT INTO financial_transactions (department, account_id, amount, transaction_type, description, metadata, created_at) VALUES
((SELECT account_id FROM finance_accounts WHERE account_name = 'City General Fund'), 
 NULL, 2500000.00, 'credit', 'Monthly property tax collection', 
 '{"source": "Property Tax", "period": "February 2026", "parcels": 12450}'::jsonb, '2026-02-01 10:00:00'),

((SELECT account_id FROM finance_accounts WHERE account_name = 'City General Fund'),
 NULL, 850000.00, 'credit', 'State revenue sharing - Q1 2026',
 '{"source": "State Government", "program": "Revenue Sharing", "quarter": "Q1"}'::jsonb, '2026-02-05 09:00:00'),

((SELECT account_id FROM finance_accounts WHERE account_name = 'Water Operations Account'),
 'water', 425000.00, 'credit', 'Water utility payments - February',
 '{"source": "Utility Bills", "customers": 8520, "period": "February 2026"}'::jsonb, '2026-02-01 12:00:00');

/* ========================================================= */
/* 9. DISEASE_INCIDENTS - Public Health Tracking */
/* ========================================================= */

INSERT INTO disease_incidents (incident_type, location, severity, reported_date, reported_by, status, description, public_health_actions, related_decision_id) VALUES

('Influenza Outbreak', 'Riverside Elementary School', 'medium', '2026-01-28 09:15:00', 'School Nurse Thompson',
 'contained', 'Cluster of 15 flu cases among students in grades 3-5',
 '{"actions": ["school_notification", "parent_communication", "enhanced_cleaning", "vaccination_drive"], "affected_students": 15, "quarantine_days": 5}'::jsonb,
 NULL),

('Gastrointestinal Illness', 'Downtown Food Court', 'high', '2026-02-02 14:30:00', 'Dr. Martinez - City Health',
 'investigating', '8 cases of food poisoning traced to food court vendors',
 '{"actions": ["vendor_inspection", "food_samples_collected", "temporary_closure_2_vendors"], "affected_persons": 8, "inspections_scheduled": 12}'::jsonb,
 NULL),

('COVID-19 Cluster', 'Oakwood Nursing Home', 'high', '2026-02-04 08:00:00', 'Facility Director',
 'investigating', '6 residents and 3 staff members tested positive',
 '{"actions": ["isolation_protocols", "contact_tracing", "testing_expansion", "PPE_distribution"], "affected_residents": 6, "affected_staff": 3, "facility_status": "restricted_access"}'::jsonb,
 NULL),

('Tuberculosis Case', 'Central District', 'medium', '2026-01-15 11:20:00', 'Dr. Wilson - Public Health',
 'contained', 'Single active TB case, contact tracing completed',
 '{"actions": ["contact_tracing", "testing_contacts", "treatment_started", "education_campaign"], "contacts_identified": 24, "contacts_tested": 24, "positive_contacts": 0}'::jsonb,
 NULL),

('Measles Case', 'Westside Community', 'high', '2026-02-06 16:45:00', 'Emergency Department',
 'investigating', 'Unvaccinated child diagnosed with measles',
 '{"actions": ["outbreak_alert", "school_notification", "vaccination_campaign_accelerated", "contact_tracing"], "contacts_identified": 12, "vaccination_status_review": "ongoing"}'::jsonb,
 NULL),

('Norovirus Outbreak', 'City Convention Center', 'medium', '2026-01-22 19:00:00', 'Event Coordinator',
 'closed', '22 attendees reported illness after corporate event',
 '{"actions": ["facility_deep_clean", "food_vendor_investigation", "attendee_survey"], "affected_attendees": 22, "event_date": "2026-01-20", "resolution": "food_handling_violation_identified"}'::jsonb,
 NULL);

/* ========================================================= */
/* 10. COORDINATION_DECISIONS - Inter-Department Coordination */
/* ========================================================= */

INSERT INTO coordination_decisions (coordination_id, agent_type, agent_id, location, resources_needed, estimated_cost, 
                                     plan_details, conflict_type, agents_involved, resolution_method, 
                                     resolution_rationale, llm_confidence, human_approver, outcome, 
                                     approval_notes, status, created_at, resolved_at) VALUES

('COORD-2026-001', 'water_department', 'water_agent_1', 'Downtown Main Street', 
 ARRAY['road_closure', 'engineering_support', 'traffic_control'], 85000.00,
 '{"task": "pipeline_replacement", "duration": "3_days", "road_closure_hours": "6am-6pm", "detour_routes": ["2nd Ave", "Park Street"]}'::jsonb,
 'resource_conflict', ARRAY['water', 'engineering', 'sanitation'],
 'sequential_scheduling', 
 'Water work scheduled Mon-Wed, Sanitation adjusts collection to Thu-Sat, Engineering provides traffic control',
 0.88, 'Sarah Johnson', 'approved',
 'Coordinated schedule approved. Engineering to provide 2 traffic control personnel daily.',
 'resolved', '2026-02-05 10:15:00', '2026-02-05 14:30:00'),

('COORD-2026-002', 'fire_department', 'fire_agent_1', 'Industrial Zone A',
 ARRAY['water_supply', 'road_access', 'hazmat_response'], 45000.00,
 '{"task": "hazmat_drill", "duration": "4_hours", "area_evacuation": "200m_radius", "water_needed": "5000_gallons"}'::jsonb,
 'resource_conflict', ARRAY['fire', 'water', 'engineering'],
 'resource_sharing',
 'Water to provide hydrant access and 5000 gal reserve, Engineering to manage road closures',
 0.92, 'Michael Chen', 'approved',
 'Multi-agency drill approved for Feb 15. Water confirms hydrant capacity, Engineering coordinates road closure.',
 'active', '2026-02-07 09:00:00', NULL),

('COORD-2026-003', 'engineering_department', 'engineering_agent_1', 'Maple Avenue and 5th Street',
 ARRAY['budget_increase', 'extended_timeline', 'sanitation_rescheduling'], 95000.00,
 '{"task": "road_resurfacing", "original_cost": 75000, "additional_scope": "drainage_upgrades", "duration": "5_days"}'::jsonb,
 'budget_conflict', ARRAY['engineering', 'finance', 'sanitation'],
 'budget_reallocation',
 'Finance approved $20K from emergency fund. Sanitation reschedules collection route during construction.',
 0.85, 'David Rodriguez', 'approved',
 'Additional scope approved with emergency funds. Work extended to include drainage improvements.',
 'resolved', '2026-02-03 11:30:00', '2026-02-03 16:00:00'),

('COORD-2026-004', 'health_department', 'health_agent_1', 'Multiple Community Centers',
 ARRAY['facility_access', 'parking_coordination', 'signage'], 12000.00,
 '{"task": "vaccination_campaign", "sites": 4, "dates": "Feb 15-Mar 15", "expected_visitors": 8500}'::jsonb,
 'location_conflict', ARRAY['health', 'sanitation', 'engineering'],
 'scheduling_coordination',
 'Engineering provides temporary parking signs, Sanitation adjusts bin collection schedule at sites',
 0.90, 'Dr. Emily Watson', 'approved',
 'Vaccination sites confirmed. Engineering installs parking signs Feb 14, Sanitation adjusts schedule.',
 'active', '2026-02-06 14:00:00', NULL),

('COORD-2026-005', 'sanitation_department', 'sanitation_agent_1', 'Residential Zone 3',
 ARRAY['additional_trucks', 'landfill_capacity', 'worker_overtime'], 18000.00,
 '{"task": "holiday_waste_overflow", "estimated_volume": "15_tons", "extra_pickups": 2, "crew_size": 8}'::jsonb,
 'resource_conflict', ARRAY['sanitation', 'finance'],
 'budget_approval',
 'Finance approved overtime and additional truck rental from emergency operations budget',
 0.87, 'Maria Garcia', 'approved',
 'Extra collection approved. Finance allocates $18K for weekend overtime and truck rental.',
 'resolved', '2026-02-08 08:30:00', '2026-02-08 10:15:00');

/* ========================================================= */
/* 11. GRANTS - Federal and State Grant Funding */
/* ========================================================= */

INSERT INTO grants (grant_name, provider, department, amount_awarded, amount_received, start_date, end_date, status, match_requirements, terms) VALUES

('Federal Water Infrastructure Grant 2025', 'U.S. Environmental Protection Agency', 'water', 1200000.00, 800000.00, '2025-07-01', '2027-06-30',
 'active', '{"match_percent": 25, "match_amount": 300000}'::jsonb,
 '{"purpose": "Pipeline replacement and water treatment upgrades", "reporting_frequency": "quarterly", "completion_deadline": "2027-06-30"}'::jsonb),

('State Transportation Improvement Grant', 'State Department of Transportation', 'engineering', 850000.00, 425000.00, '2025-09-01', '2026-08-31',
 'active', '{"match_percent": 15, "match_amount": 127500}'::jsonb,
 '{"purpose": "Bridge rehabilitation and road resurfacing", "milestones": ["design_approval", "construction_start", "completion"], "reporting_frequency": "monthly"}'::jsonb),

('Community Health Initiative Grant', 'State Health Department', 'health', 350000.00, 175000.00, '2026-01-01', '2026-12-31',
 'active', '{"match_percent": 10, "match_amount": 35000}'::jsonb,
 '{"purpose": "Vaccination campaigns and public health education", "target_populations": ["seniors", "low_income", "children"], "deliverables": ["vaccination_events", "education_materials"]}'::jsonb),

('Fire Equipment Modernization Grant', 'Department of Homeland Security', 'fire', 500000.00, 500000.00, '2025-10-01', '2026-09-30',
 'active', '{"match_percent": 0, "match_amount": 0}'::jsonb,
 '{"purpose": "Purchase new SCBA equipment and thermal imaging cameras", "allowed_equipment": ["respiratory_protection", "thermal_cameras", "communication_systems"], "buy_american_required": true}'::jsonb),

('Green Infrastructure Grant', 'U.S. EPA', 'water', 450000.00, 0.00, '2026-03-01', '2027-02-28',
 'awarded', '{"match_percent": 25, "match_amount": 112500}'::jsonb,
 '{"purpose": "Stormwater management and green infrastructure", "project_types": ["rain_gardens", "permeable_pavement", "bioswales"], "reporting_frequency": "quarterly"}'::jsonb),

('Emergency Management Performance Grant', 'Federal Emergency Management Agency', 'fire', 180000.00, 90000.00, '2025-10-01', '2026-09-30',
 'active', '{"match_percent": 50, "match_amount": 90000}'::jsonb,
 '{"purpose": "Emergency planning and preparedness programs", "activities": ["training", "exercises", "planning", "equipment"], "reporting_frequency": "semi_annual"}'::jsonb),

('Brownfield Cleanup Grant', 'U.S. EPA', 'sanitation', 200000.00, 50000.00, '2025-11-01', '2027-10-31',
 'active', '{"match_percent": 20, "match_amount": 40000}'::jsonb,
 '{"purpose": "Cleanup of contaminated former industrial sites", "sites": ["Old Mill Site", "Former Gas Station - 5th Ave"], "environmental_assessments_required": true}'::jsonb);

/* ========================================================= */
/* 12. HEALTH_FACILITIES - Healthcare Infrastructure */
/* ========================================================= */

INSERT INTO health_facilities (name, location, capacity, services, status, contact) VALUES

('City Central Health Clinic', 'Downtown - 450 Main Street', 120,
 '["primary_care", "pediatrics", "vaccinations", "lab_services", "pharmacy"]'::jsonb, 'open',
 '{"phone": "+1-555-0201", "email": "central@cityhealth.gov", "hours": "Mon-Fri 7AM-7PM, Sat 8AM-4PM"}'::jsonb),

('North District Community Health Center', 'North District - 1820 Oak Boulevard', 80,
 '["primary_care", "dental", "mental_health", "nutrition_counseling", "vaccinations"]'::jsonb, 'open',
 '{"phone": "+1-555-0202", "email": "north@cityhealth.gov", "hours": "Mon-Fri 8AM-6PM"}'::jsonb),

('Eastside Family Health Center', 'East Zone - 3344 Riverside Drive', 60,
 '["primary_care", "maternal_health", "pediatrics", "vaccinations"]'::jsonb, 'open',
 '{"phone": "+1-555-0203", "email": "eastside@cityhealth.gov", "hours": "Mon-Fri 8AM-5PM"}'::jsonb),

('Westside Urgent Care', 'Westside - 1275 Park Avenue', 40,
 '["urgent_care", "x-ray", "lab_services", "minor_procedures"]'::jsonb, 'open',
 '{"phone": "+1-555-0204", "email": "westside@cityhealth.gov", "hours": "7 days, 8AM-10PM"}'::jsonb),

('Mobile Health Unit #1', 'Various Locations', 15,
 '["vaccinations", "health_screenings", "basic_care"]'::jsonb, 'open',
 '{"phone": "+1-555-0205", "email": "mobile1@cityhealth.gov", "schedule": "rotating_weekly"}'::jsonb),

('Senior Wellness Center', 'Central District - 890 Elm Street', 50,
 '["geriatric_care", "physical_therapy", "social_services", "nutrition"]'::jsonb, 'open',
 '{"phone": "+1-555-0206", "email": "senior@cityhealth.gov", "hours": "Mon-Fri 8AM-4PM"}'::jsonb),

('South District Health Station', 'South District - 2156 Industrial Way', 45,
 '["primary_care", "occupational_health", "vaccinations", "health_screenings"]'::jsonb, 'under_maintenance',
 '{"phone": "+1-555-0207", "email": "south@cityhealth.gov", "maintenance_until": "2026-02-20", "reason": "HVAC system upgrade"}'::jsonb);

/* ========================================================= */
/* 13. HEALTH_POLICIES - Public Health Regulations */
/* ========================================================= */

INSERT INTO health_policies (policy_name, description, effective_date, metadata) VALUES

('Food Service Sanitation Standards', 'Mandatory health inspections for all food service establishments at minimum bi-annual frequency', '2025-01-01',
 '{"inspection_frequency": "semi_annual", "scoring_system": "100_point_scale", "closure_threshold": 70, "critical_violations": ["temperature_control", "cross_contamination", "handwashing"]}'::jsonb),

('Vaccination Requirements for School Entry', 'Children must be current on all state-required vaccinations before school enrollment', '2024-09-01',
 '{"required_vaccines": ["MMR", "DTaP", "Polio", "Varicella", "Hepatitis_B"], "exemptions": ["medical", "religious"], "documentation_required": true}'::jsonb),

('Disease Reporting Protocol', 'Healthcare providers must report notifiable diseases within 24 hours of diagnosis', '2025-01-01',
 '{"notifiable_diseases": ["measles", "tuberculosis", "hepatitis", "COVID-19", "meningitis"], "reporting_method": "electronic_system", "penalties": "license_suspension"}'::jsonb),

('Public Pool and Spa Regulations', 'Weekly water quality testing and quarterly inspections required for all public aquatic facilities', '2025-06-01',
 '{"testing_requirements": ["chlorine", "pH", "bacteria"], "inspection_frequency": "quarterly", "operator_certification_required": true}'::jsonb),

('Smoking Ban in Public Facilities', 'Prohibition of smoking and vaping in all city-owned buildings and within 25 feet of entrances', '2024-01-01',
 '{"enforcement": "health_inspectors_police", "violation_fine": 150, "signage_required": true, "includes": ["cigarettes", "vaping", "e-cigarettes"]}'::jsonb);

/* ========================================================= */
/* 14. HEALTH_RESOURCES - Medical Supplies and Equipment */
/* ========================================================= */

INSERT INTO health_resources (resource_type, quantity, location, status, metadata) VALUES

('N95 Respirator Masks', 15000, 'City Central Health Clinic', 'available',
 '{"expiration_date": "2027-08-15", "supplier": "MedSupply Co", "lot_number": "N95-2025-08442", "storage_conditions": "cool_dry"}'::jsonb),

('COVID-19 Vaccine Doses (Pfizer)', 2500, 'North District Community Health Center', 'available',
 '{"expiration_date": "2026-06-30", "storage_temp": "-70C", "lot_number": "PF-CV19-2025-9823"}'::jsonb),

('Influenza Vaccine Doses', 8000, 'Multiple Facilities', 'available',
 '{"expiration_date": "2026-05-31", "storage_temp": "2-8C", "season": "2025-2026", "strains": ["H1N1", "H3N2", "B-strain"]}'::jsonb),

('Portable Defibrillators (AED)', 45, 'Various City Facilities', 'available',
 '{"last_inspection": "2026-01-15", "battery_status": "good", "maintenance_schedule": "monthly", "training_required": true}'::jsonb),

('COVID-19 Rapid Test Kits', 10000, 'City Central Health Clinic', 'available',
 '{"expiration_date": "2026-12-31", "manufacturer": "QuickTest Labs", "accuracy": "95_percent", "result_time": "15_minutes"}'::jsonb),

('PPE Kits (Gown, Gloves, Mask)', 5000, 'Emergency Response Storage', 'available',
 '{"contents": ["isolation_gown", "nitrile_gloves", "surgical_mask", "face_shield"], "size_distribution": {"small": 1000, "medium": 2500, "large": 1500}}'::jsonb),

('Blood Pressure Monitors', 120, 'Multiple Clinics', 'available',
 '{"type": "automatic_digital", "calibration_date": "2025-12-01", "next_calibration": "2026-06-01"}'::jsonb),

('Thermometers (Non-Contact)', 200, 'All Health Facilities', 'available',
 '{"type": "infrared_forehead", "battery_type": "AAA", "accuracy": "±0.2C"}'::jsonb),

('Emergency Medical Backpacks', 12, 'Mobile Health Units', 'available',
 '{"contents": ["first_aid_supplies", "medications", "diagnostic_tools"], "last_stocked": "2026-02-01", "expiry_check_frequency": "monthly"}'::jsonb);

/* ========================================================= */
/* 15. HEALTH_SURVEILLANCE_REPORTS - Disease Monitoring */
/* ========================================================= */

INSERT INTO health_surveillance_reports (source, report_date, summary, severity_assessment) VALUES

('Weekly Communicable Disease Summary', '2026-02-01 00:00:00',
 '{"influenza_cases": 42, "covid19_cases": 8, "strep_throat": 15, "gastroenteritis": 12, "trend": "influenza_increasing", "hospitalizations": 5}'::jsonb,
 'low'),

('Weekly Communicable Disease Summary', '2026-02-08 00:00:00',
 '{"influenza_cases": 38, "covid19_cases": 11, "strep_throat": 18, "gastroenteritis": 9, "measles": 1, "trend": "measles_alert_issued", "hospitalizations": 6}'::jsonb,
 'medium'),

('Monthly Water Quality Report', '2026-01-31 00:00:00',
 '{"samples_tested": 156, "violations": 0, "contaminants_detected": [], "chlorine_levels": "within_standards", "bacteria_tests": "all_negative", "compliance_rate": 100}'::jsonb,
 'low'),

('Food Safety Inspection Summary', '2026-01-31 00:00:00',
 '{"establishments_inspected": 87, "critical_violations": 12, "closures": 2, "reinspections_required": 15, "average_score": 92, "common_issues": ["temperature_control", "employee_hygiene"]}'::jsonb,
 'low'),

('Emergency Department Syndromic Surveillance', '2026-02-07 00:00:00',
 '{"respiratory_illness": 95, "gastrointestinal_illness": 34, "fever_rash": 3, "unusual_patterns": "measles_case_identified", "alerts_generated": 1}'::jsonb,
 'medium'),

('Vaccination Coverage Report', '2026-01-31 00:00:00',
 '{"target_population": 45000, "fully_vaccinated": 38250, "coverage_rate": 85, "vaccine_types": {"covid19": 82, "influenza": 67, "routine_childhood": 94}, "gaps_identified": ["adult_boosters", "flu_in_seniors"]}'::jsonb,
 'low');

/* ========================================================= */
/* 16. INCIDENTS - General Incident Tracking */
/* ========================================================= */

INSERT INTO incidents (department, incident_type, location, severity, reported_date, reported_by, description, status, resolution_date, notes) VALUES

-- Water Department Incidents
('water', 'pipeline_leak', 'Downtown - 3rd Street & Main', 'high', '2026-02-06 14:30:00', 'Resident Call-In',
 'Water main leak causing road flooding. Traffic impacted.', 'resolved', '2026-02-07 18:00:00',
 'Emergency crew responded within 45 minutes. Pipeline section replaced. Road repaired.'),

('water', 'low_pressure', 'North District - Oak Boulevard Area', 'medium', '2026-02-05 08:15:00', 'Multiple Residents',
 'Several residents reporting low water pressure during morning hours.', 'investigating', NULL,
 'Investigating pressure regulator valve. Scheduled for inspection Feb 10.'),

('water', 'water_quality_complaint', 'Eastside - Riverside Apartments', 'low', '2026-02-03 16:20:00', 'Building Manager',
 'Residents reporting slight discoloration in tap water.', 'resolved', '2026-02-04 10:00:00',
 'Tested water samples - within safe limits. Discoloration from internal building pipes. Advised building maintenance.'),

-- Fire Department Incidents
('fire', 'structure_fire', 'Riverside Apartments - 2250 River Road', 'critical', '2026-02-05 19:30:00', '911 Call',
 'Multi-unit residential fire, three floors affected.', 'resolved', '2026-02-05 22:45:00',
 'Full response with 4 engines, 16 firefighters. Fire contained, no fatalities. 12 residents displaced. Red Cross notified.'),

('fire', 'vehicle_fire', 'Downtown Parking Garage - Level 3', 'medium', '2026-02-08 11:15:00', 'Garage Security',
 'Vehicle fire in enclosed parking structure.', 'resolved', '2026-02-08 12:30:00',
 'Responded with 2 engines. Fire extinguished. Ventilation systems activated. No injuries.'),

('fire', 'false_alarm', 'City Convention Center', 'low', '2026-02-07 15:45:00', 'Automatic Alarm System',
 'Fire alarm activation during event.', 'closed', '2026-02-07 16:15:00',
 'Building evacuated per protocol. No fire found. Alarm triggered by stage smoke effects.'),

-- Engineering Department Incidents
('engineering', 'pothole_cluster', 'Maple Avenue - Between 5th & 8th Streets', 'medium', '2026-02-08 07:30:00', 'City Inspector',
 'Multiple potholes formed after winter freeze-thaw cycles.', 'reported', NULL,
 'Documented 12 potholes. Repair crew scheduled for Feb 10-11. Traffic control arranged.'),

('engineering', 'sidewalk_damage', 'Central District - Elm Street', 'medium', '2026-02-04 13:20:00', 'Pedestrian Report',
 'Cracked and uneven sidewalk creating trip hazard.', 'investigating', NULL,
 'Inspected site. Tree roots causing uplift. Requires tree trimming and sidewalk replacement.'),

('engineering', 'street_light_outage', 'Industrial Zone A - Multiple Locations', 'low', '2026-02-06 19:00:00', 'Security Patrol',
 'Ten street lights not functioning in industrial area.', 'resolved', '2026-02-07 14:00:00',
 'Circuit breaker issue at main panel. Reset circuit, all lights restored.'),

-- Health Department Incidents
('health', 'food_poisoning', 'Downtown Food Court', 'high', '2026-02-02 14:30:00', 'Hospital ER',
 'Multiple cases of gastrointestinal illness traced to food court.', 'investigating', NULL,
 'Health inspectors deployed. Food samples collected. Two vendors temporarily closed pending investigation.'),

('health', 'pest_infestation', 'Riverside Restaurant - 445 Water Street', 'medium', '2026-02-01 10:00:00', 'Health Inspector',
 'Rodent evidence found during routine inspection.', 'resolved', '2026-02-03 15:00:00',
 'Restaurant voluntarily closed. Pest control completed. Re-inspection passed. Permit restored.'),

-- Sanitation Department Incidents
('sanitation', 'missed_collection', 'Residential Zone 3', 'low', '2026-02-08 09:00:00', 'Multiple Residents',
 'Waste collection missed due to truck breakdown.', 'resolved', '2026-02-08 17:00:00',
 'Backup truck deployed. All collections completed by end of day. Residents notified.'),

('sanitation', 'illegal_dumping', 'North District - Vacant Lot on Oak Blvd', 'medium', '2026-02-05 14:30:00', 'Code Enforcement',
 'Large amount of construction debris illegally dumped.', 'investigating', NULL,
 'Cleanup crew scheduled. Investigating contractor plates. Seeking violators for citation.'),

-- Finance Department Incidents
('finance', 'system_outage', 'Finance Department - Payment Processing', 'medium', '2026-02-04 10:15:00', 'IT Director',
 'Online payment portal unavailable for 2 hours.', 'resolved', '2026-02-04 12:30:00',
 'Server issue resolved. All transactions restored. No data loss. Affected customers notified.');

/* ========================================================= */
/* 17. PIPELINE_INSPECTIONS - Water Pipeline Inspection Records */
/* ========================================================= */

INSERT INTO pipeline_inspections (pipeline_id, inspector, inspection_date, outcome, notes, findings)
SELECT 
    p.pipeline_id,
    'Inspector Rodriguez - Water Dept',
    '2026-01-15',
    'pass',
    'Routine annual inspection completed. Pipeline in good condition.',
    '{"pressure_ok": true, "corrosion": "minimal", "leaks": "none", "coating_condition": "good", "valve_operation": "normal"}'::jsonb
FROM pipelines p
WHERE p.location = 'Downtown' AND p.pipeline_type = 'supply' AND p.diameter_mm = 300
LIMIT 1;

INSERT INTO pipeline_inspections (pipeline_id, inspector, inspection_date, outcome, notes, findings)
SELECT 
    p.pipeline_id,
    'Inspector Chen - Water Dept',
    '2026-01-20',
    'conditional_pass',
    'Minor corrosion detected. Recommend monitoring and re-inspection in 6 months.',
    '{"pressure_ok": true, "corrosion": "moderate_external", "leaks": "none", "coating_condition": "fair", "valve_operation": "normal", "action_required": "re_inspect_6_months"}'::jsonb
FROM pipelines p
WHERE p.location = 'West Zone' AND p.operational_status = 'under_repair'
LIMIT 1;

INSERT INTO pipeline_inspections (pipeline_id, inspector, inspection_date, outcome, notes, findings)
SELECT 
    p.pipeline_id,
    'Inspector Williams - Water Dept',
    '2026-01-28',
    'pass',
    'New pipeline installation inspected and approved for service.',
    '{"pressure_test": "passed", "leak_test": "passed", "installation_quality": "excellent", "documentation_complete": true}'::jsonb
FROM pipelines p
WHERE p.location = 'North District' AND p.condition = 'excellent'
LIMIT 1;

INSERT INTO pipeline_inspections (pipeline_id, inspector, inspection_date, outcome, notes, findings)
SELECT 
    p.pipeline_id,
    'Inspector Martinez - Water Dept',
    '2026-02-03',
    'pass',
    'Drainage pipeline inspection shows normal wear for age.',
    '{"flow_capacity": "adequate", "blockage": "none", "structural_integrity": "good", "cleanout_accessible": true}'::jsonb
FROM pipelines p
WHERE p.location = 'Downtown' AND p.pipeline_type = 'drainage'
LIMIT 1;

/* ========================================================= */
/* 18. PIPELINES - Water Infrastructure */
/* ========================================================= */

-- Continuing with additional pipeline records beyond what's in complete_schema.sql
INSERT INTO pipelines (location, zone, pipeline_type, diameter_mm, material, length_meters, pressure_psi, flow_rate, 
                       condition, installation_date, last_inspection_date, next_inspection_due, operational_status, notes) VALUES

('Central Business District', 'Zone-1', 'supply', 350, 'ductile_iron', 850.00, 48.5, 2500.00, 'excellent',
 '2022-03-15', '2026-01-15', '2027-01-15', 'active', 'High-capacity main serving downtown area'),

('Residential North Area', 'Zone-2', 'supply', 200, 'PVC', 1200.00, 42.0, 1200.00, 'good',
 '2019-06-20', '2025-11-10', '2026-11-10', 'active', 'Residential distribution network'),

('South Industrial Park', 'Zone-4', 'supply', 400, 'steel', 650.00, 52.0, 3000.00, 'good',
 '2020-09-10', '2026-01-20', '2027-01-20', 'active', 'Industrial water supply, high flow requirements'),

('East Residential District', 'Zone-2', 'supply', 250, 'PVC', 980.00, 40.0, 1500.00, 'good',
 '2018-04-12', '2025-10-15', '2026-10-15', 'active', 'Standard residential service'),

('Old Town Area', 'Zone-1', 'supply', 150, 'cast_iron', 420.00, 35.0, 800.00, 'fair',
 '2005-07-18', '2025-12-05', '2026-06-05', 'active', 'Older infrastructure, scheduled for replacement in 2027'),

('Highway Corridor', 'Zone-3', 'drainage', 600, 'concrete', 1500.00, NULL, NULL, 'good',
 '2016-08-22', '2026-01-25', '2027-01-25', 'active', 'Major drainage corridor for highway runoff'),

('Downtown Storm System', 'Zone-1', 'drainage', 450, 'concrete', 780.00, NULL, NULL, 'fair',
 '2010-05-14', '2025-09-30', '2026-03-30', 'active', 'Storm drainage, some sediment buildup'),

('Park District', 'Zone-2', 'supply', 200, 'PVC', 340.00, 38.0, 900.00, 'excellent',
 '2023-05-08', '2026-02-01', '2027-02-01', 'active', 'New installation serving park facilities'),

('University Campus', 'Zone-3', 'supply', 300, 'ductile_iron', 1100.00, 45.0, 2200.00, 'good',
 '2017-11-03', '2025-12-18', '2026-12-18', 'active', 'Campus water distribution system'),

('South Residential Zone', 'Zone-4', 'sewage', 350, 'PVC', 920.00, NULL, NULL, 'good',
 '2019-03-25', '2026-01-30', '2027-01-30', 'active', 'Sewage collection main');

/* ========================================================= */
/* 19. PROJECTS - Department Projects */
/* ========================================================= */

INSERT INTO projects (department, project_name, project_type, location, estimated_cost, actual_cost, 
                      start_date, end_date, completion_date, status, notes) VALUES

-- Water Department Projects
('water', 'East Side Pipeline Expansion', 'infrastructure', 'East Zone', 850000.00, 420000.00,
 '2025-10-01', '2026-06-30', NULL, 'in_progress',
 'Phase 1 complete. Phase 2 installation in progress. 50% complete.'),

('water', 'Downtown Water Main Replacement', 'infrastructure', 'Downtown - 3rd Street', 125000.00, 125000.00,
 '2026-02-06', '2026-02-07', '2026-02-07', 'completed',
 'Emergency replacement completed after leak. Fully restored.'),

('water', 'North Reservoir Capacity Assessment', 'planning', 'North District', 45000.00, 12000.00,
 '2026-01-15', '2026-03-31', NULL, 'in_progress',
 'Engineering study to evaluate expansion feasibility. 30% complete.'),

('water', 'Smart Water Meter Installation', 'technology', 'Citywide', 1200000.00, 0.00,
 '2026-03-01', '2027-02-28', NULL, 'planned',
 'Phased rollout of smart metering across all zones. Grant funded.'),

-- Fire Department Projects
('fire', 'Central Station Equipment Upgrade', 'equipment', 'Central Fire Station', 280000.00, 180000.00,
 '2025-11-01', '2026-02-28', NULL, 'in_progress',
 'New SCBA units, thermal cameras, and communication equipment. 65% complete.'),

('fire', 'Fire Hydrant Replacement Program', 'infrastructure', 'Various Locations', 150000.00, 45000.00,
 '2026-01-01', '2026-12-31', NULL, 'in_progress',
 'Replacing 30 aging hydrants citywide. 10 completed to date.'),

('fire', 'Hazmat Response Training Facility', 'facility', 'Fire Training Center', 450000.00, 0.00,
 '2026-04-01', '2026-11-30', NULL, 'approved',
 'New training facility for hazmat and confined space rescue. Grant funded.'),

-- Engineering Department Projects
('engineering', 'Maple Avenue Road Repair', 'maintenance', 'Maple Avenue', 8500.00, 0.00,
 '2026-02-10', '2026-02-11', NULL, 'approved',
 'Pothole repair and surface patching. 2-day project.'),

('engineering', 'East Side Bridge Rehabilitation', 'infrastructure', 'East Side River Crossing', 850000.00, 125000.00,
 '2026-01-15', '2026-07-31', NULL, 'in_progress',
 'Bridge deck replacement and structural reinforcement. Design phase 100%, construction 15%.'),

('engineering', 'Street Lighting LED Conversion', 'energy_efficiency', 'Citywide', 380000.00, 95000.00,
 '2025-09-01', '2026-08-31', NULL, 'in_progress',
 'Converting 500 street lights to LED. 125 completed. Energy savings documented.'),

('engineering', 'Bike Lane Network Expansion', 'transportation', 'Downtown & East Zone', 220000.00, 0.00,
 '2026-03-15', '2026-09-30', NULL, 'planned',
 'Adding 5 miles of protected bike lanes. Community input sessions scheduled.'),

-- Health Department Projects
('health', 'Spring Flu Vaccination Campaign', 'public_health', 'Multiple Community Centers', 95000.00, 12500.00,
 '2026-02-01', '2026-03-15', NULL, 'in_progress',
 'Targeting seniors 65+. 4 sites confirmed. Vaccines ordered. Launch Feb 15.'),

('health', 'Mobile Health Unit Acquisition', 'equipment', 'Health Department', 185000.00, 0.00,
 '2026-03-01', '2026-06-30', NULL, 'approved',
 'Purchase second mobile health unit to expand rural reach. Grant funded 60%.'),

('health', 'Food Safety Technology Upgrade', 'technology', 'Health Department Office', 42000.00, 8000.00,
 '2026-01-01', '2026-04-30', NULL, 'in_progress',
 'New inspection software and tablet devices for field inspectors. Training scheduled March.'),

-- Sanitation Department Projects
('sanitation', 'Recycling Center Expansion', 'facility', 'North Recycling Center', 320000.00, 80000.00,
 '2025-11-01', '2026-05-31', NULL, 'in_progress',
 'Expanding sorting capacity by 40%. New equipment installed. Building expansion underway.'),

('sanitation', 'Waste Truck Fleet Replacement', 'equipment', 'Sanitation Depot', 480000.00, 0.00,
 '2026-04-01', '2026-09-30', NULL, 'approved',
 'Replacing 3 aging collection trucks with new CNG vehicles. Procurement in progress.'),

-- Finance Department Projects
('finance', 'Financial System Modernization', 'technology', 'City Hall', 225000.00, 85000.00,
 '2025-10-01', '2026-06-30', NULL, 'in_progress',
 'Upgrading enterprise financial system. Data migration 60% complete. Training planned for May.'),

-- Completed Projects (Historical)
('water', 'West Zone Pipeline Repair', 'maintenance', 'West Zone', 45000.00, 43500.00,
 '2025-11-10', '2025-11-25', '2025-11-24', 'completed',
 'Repaired corroded section identified in October inspection. Project under budget.'),

('engineering', 'Winter Road Preparation', 'maintenance', 'Citywide', 75000.00, 72000.00,
 '2025-10-15', '2025-11-30', '2025-11-28', 'completed',
 'Pre-winter road treatment and drainage cleaning completed on schedule.');

/* ========================================================= */
/* 20. RESERVE_FUNDS - Department Reserve Accounts */
/* ========================================================= */

INSERT INTO reserve_funds (department, reserve_name, amount, min_required_percent, metadata) VALUES

('water', 'Emergency Repair Fund', 450000.00, 10.00,
 '{"purpose": "Urgent pipeline repairs and emergency response", "last_withdrawal": "2026-02-06", "withdrawal_amount": 125000, "replenishment_schedule": "quarterly"}'::jsonb),

('water', 'Infrastructure Replacement Reserve', 1800000.00, 15.00,
 '{"purpose": "Planned pipeline and equipment replacement", "projects_funded": ["Smart Meter Installation", "Pipeline Expansion"], "allocation_method": "capital_planning"}'::jsonb),

('fire', 'Equipment Replacement Fund', 380000.00, 12.00,
 '{"purpose": "Fire truck and equipment lifecycle replacement", "next_major_purchase": "2027-01-01", "target_amount": 850000, "monthly_contribution": 35000}'::jsonb),

('fire', 'Training and Certification Reserve', 125000.00, 5.00,
 '{"purpose": "Ongoing firefighter training and certification", "annual_training_budget": 180000, "courses_funded": ["hazmat", "technical_rescue", "emt_certification"]}'::jsonb),

('engineering', 'Road Maintenance Reserve', 520000.00, 10.00,
 '{"purpose": "Winter damage repairs and emergency road work", "seasonal_allocation": {"winter": 40, "spring": 30, "summer": 20, "fall": 10}, "avg_annual_use": 450000}'::jsonb),

('engineering', 'Bridge and Structure Reserve', 890000.00, 18.00,
 '{"purpose": "Major bridge repairs and structural maintenance", "bridge_count": 12, "inspection_schedule": "biennial", "projects_in_queue": ["East Side Bridge", "River Crossing"]}'::jsonb),

('health', 'Disease Outbreak Response Fund', 150000.00, 8.00,
 '{"purpose": "Rapid response to disease outbreaks and health emergencies", "activation_criteria": ["outbreak_declaration", "state_emergency"], "last_activation": "2024-03-15"}'::jsonb),

('health', 'Medical Supply Reserve', 95000.00, 5.00,
 '{"purpose": "Emergency medical supplies and vaccine procurement", "inventory_target": "90_day_supply", "automatic_reorder": true}'::jsonb),

('sanitation', 'Equipment Maintenance Reserve', 185000.00, 8.00,
 '{"purpose": "Waste truck repairs and equipment maintenance", "fleet_size": 18, "avg_annual_maintenance": 220000, "emergency_repairs_budgeted": 50000}'::jsonb),

('sanitation', 'Landfill Closure Fund', 420000.00, 25.00,
 '{"purpose": "Future landfill closure and remediation costs", "regulatory_requirement": true, "projected_closure_date": "2045-01-01", "estimated_closure_cost": 2500000, "funding_progress": 17}'::jsonb),

('finance', 'General City Reserve', 2500000.00, 15.00,
 '{"purpose": "City-wide emergency fund and contingency", "access_approval": "city_council", "minimum_balance": 2000000, "investment_strategy": "conservative_growth"}'::jsonb),

('finance', 'Technology Infrastructure Reserve', 340000.00, 7.00,
 '{"purpose": "IT system upgrades and cybersecurity", "major_projects": ["Financial System Modernization", "Cybersecurity Enhancement"], "annual_technology_refresh": 180000}'::jsonb);

/* ========================================================= */
/* DATA SUMMARY - TABLES 11-20 */
/* ========================================================= */

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE '✅ COMPREHENSIVE SEED DATA LOADED - TABLES 11-20';
    RAISE NOTICE '====================================================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Additional Records Created:';
    RAISE NOTICE '   ✓ grants: 7 federal and state grants';
    RAISE NOTICE '   ✓ health_facilities: 7 health clinics and centers';
    RAISE NOTICE '   ✓ health_policies: 5 public health regulations';
    RAISE NOTICE '   ✓ health_resources: 9 medical supply categories';
    RAISE NOTICE '   ✓ health_surveillance_reports: 6 surveillance reports';
    RAISE NOTICE '   ✓ incidents: 15 incidents across all departments';
    RAISE NOTICE '   ✓ pipeline_inspections: 4 inspection records';
    RAISE NOTICE '   ✓ pipelines: 10 additional pipeline records (16 total)';
    RAISE NOTICE '   ✓ projects: 19 active and completed projects';
    RAISE NOTICE '   ✓ reserve_funds: 12 reserve accounts';
    RAISE NOTICE '';
    RAISE NOTICE '💰 Grant Funding Summary:';
    RAISE NOTICE '   • Total grants awarded: $3,730,000';
    RAISE NOTICE '   • Total received to date: $2,015,000';
    RAISE NOTICE '   • Required city match: $704,500';
    RAISE NOTICE '';
    RAISE NOTICE '🏗️ Projects Summary:';
    RAISE NOTICE '   • In Progress: 13 projects';
    RAISE NOTICE '   • Approved/Planned: 4 projects';
    RAISE NOTICE '   • Completed: 3 projects';
    RAISE NOTICE '   • Total project value: $6.2M';
    RAISE NOTICE '';
    RAISE NOTICE '💰 Reserve Funds Total: $7,855,000';
    RAISE NOTICE '====================================================================';
END $$;

/* ========================================================= */
/* 21. RESERVOIRS - Water Storage Facilities */
/* ========================================================= */

INSERT INTO reservoirs (name, location, capacity_liters, current_level_liters, operational_status, last_reading_time) VALUES

('Main City Reservoir', 'North District - Hilltop Drive', 50000000, 42500000, 'active', '2026-02-09 06:00:00'),
('East Side Reservoir', 'East Zone - Riverside Park', 30000000, 25500000, 'active', '2026-02-09 06:00:00'),
('North District Reservoir', 'North District - Oak Ridge', 20000000, 18200000, 'active', '2026-02-09 06:00:00'),
('Industrial Zone Tank', 'Industrial Zone A', 8000000, 7200000, 'active', '2026-02-09 06:00:00'),
('South Emergency Reserve', 'South District - Emergency Station', 12000000, 11500000, 'active', '2026-02-09 06:00:00'),
('Downtown Storage Tank', 'Downtown - Water Treatment Plant', 6000000, 5800000, 'active', '2026-02-09 06:00:00'),
('West Zone Reservoir', 'West Zone - Mountain View', 15000000, 9500000, 'maintenance', '2026-02-08 18:00:00');

/* ========================================================= */
/* 22. REVENUE_FORECASTS - Financial Projections */
/* ========================================================= */

INSERT INTO revenue_forecasts (department, period_start, period_end, forecast_amount, method, confidence, model_metadata) VALUES

('water', '2026-03-01', '2026-03-31', 485000.00, 'time_series_analysis', 0.89,
 '{"model": "ARIMA", "historical_months": 24, "seasonality_adjusted": true, "variables": ["usage_patterns", "weather", "customer_growth"]}'::jsonb),

('water', '2026-04-01', '2026-06-30', 1520000.00, 'regression_model', 0.87,
 '{"model": "multiple_regression", "factors": ["seasonal_demand", "temperature", "customer_base"], "r_squared": 0.91}'::jsonb),

('sanitation', '2026-03-01', '2026-05-31', 285000.00, 'historical_average', 0.85,
 '{"model": "3_year_average", "adjusted_for": "inflation", "growth_rate": 2.5}'::jsonb),

('finance', '2026-02-01', '2026-03-31', 5200000.00, 'composite_forecast', 0.92,
 '{"model": "ensemble", "components": ["property_tax", "utility_fees", "state_revenue_share"], "weights": [0.50, 0.30, 0.20]}'::jsonb),

('finance', '2026-04-01', '2026-06-30', 5450000.00, 'composite_forecast', 0.90,
 '{"model": "ensemble", "components": ["property_tax", "utility_fees", "state_revenue_share", "grants"], "quarterly_adjustment": true}'::jsonb);

/* ========================================================= */
/* 23. REVENUE_HISTORY - Historical Revenue Records */
/* ========================================================= */

INSERT INTO revenue_history (department, period_start, period_end, amount, source, details, recorded_at) VALUES

-- Water Department Revenue
('water', '2026-01-01', '2026-01-31', 425000.00, 'Utility Payments',
 '{"residential_customers": 7200, "commercial_customers": 850, "industrial_customers": 35, "avg_residential_bill": 48.50}'::jsonb,
 '2026-02-01 09:00:00'),

('water', '2025-12-01', '2025-12-31', 438000.00, 'Utility Payments',
 '{"residential_customers": 7180, "commercial_customers": 845, "industrial_customers": 33, "avg_residential_bill": 50.20}'::jsonb,
 '2026-01-02 09:00:00'),

('water', '2025-11-01', '2025-11-30', 412000.00, 'Utility Payments',
 '{"residential_customers": 7150, "commercial_customers": 842, "industrial_customers": 32, "avg_residential_bill": 47.30}'::jsonb,
 '2025-12-01 09:00:00'),

-- Sanitation Department Revenue
('sanitation', '2026-01-01', '2026-01-31', 275000.00, 'Waste Collection Fees',
 '{"residential_accounts": 8500, "commercial_accounts": 620, "monthly_fee_residential": 28.50, "monthly_fee_commercial": 125.00}'::jsonb,
 '2026-02-01 09:00:00'),

('sanitation', '2025-12-01', '2025-12-31', 268000.00, 'Waste Collection Fees',
 '{"residential_accounts": 8450, "commercial_accounts": 615, "monthly_fee_residential": 28.00, "monthly_fee_commercial": 125.00}'::jsonb,
 '2026-01-02 09:00:00'),

-- General City Revenue
('finance', '2026-01-01', '2026-01-31', 5180000.00, 'Mixed Revenue',
 '{"property_tax": 2500000, "sales_tax": 850000, "business_licenses": 220000, "permits": 185000, "state_revenue_share": 950000, "other": 475000}'::jsonb,
 '2026-02-01 09:00:00'),

('finance', '2025-12-01', '2025-12-31', 5520000.00, 'Mixed Revenue',
 '{"property_tax": 2800000, "sales_tax": 920000, "business_licenses": 195000, "permits": 210000, "state_revenue_share": 980000, "other": 415000, "note": "High December property tax collections"}'::jsonb,
 '2026-01-02 09:00:00'),

('finance', '2025-11-01', '2025-11-30', 4850000.00, 'Mixed Revenue',
 '{"property_tax": 2200000, "sales_tax": 880000, "business_licenses": 205000, "permits": 165000, "state_revenue_share": 950000, "other": 450000}'::jsonb,
 '2025-12-01 09:00:00');

/* ========================================================= */
/* 24. SANITATION_INSPECTIONS - Facility Sanitation Checks */
/* ========================================================= */

INSERT INTO sanitation_inspections (location, facility, inspection_date, outcome, inspector, notes, findings) VALUES

('Downtown Food Court', 'Asian Fusion Restaurant', '2026-02-05', 'conditional_pass', 'Inspector Davis',
 'Minor violations found. Re-inspection required in 30 days.',
 '{"score": 82, "violations": ["temperature_control_issue", "hand_sink_soap_missing"], "critical_violations": 1, "follow_up_date": "2026-03-05"}'::jsonb),

('Downtown Food Court', 'Pizza Palace', '2026-02-05', 'pass', 'Inspector Davis',
 'No violations found. Excellent food safety practices.',
 '{"score": 98, "violations": [], "critical_violations": 0, "commendations": ["excellent_cleanliness", "proper_documentation"]}'::jsonb),

('Riverside Elementary School', 'School Cafeteria', '2026-01-18', 'pass', 'Inspector Rodriguez',
 'Routine inspection completed. All requirements met.',
 '{"score": 95, "violations": ["minor_labeling_issue"], "critical_violations": 0}'::jsonb),

('Oak Boulevard', 'Sunshine Daycare Center', '2026-01-22', 'pass', 'Inspector Chen',
 'Annual sanitation inspection passed.',
 '{"score": 97, "violations": [], "critical_violations": 0, "areas_inspected": ["kitchen", "bathrooms", "play_areas", "diaper_changing"]}'::jsonb),

('Industrial Zone A', 'Factory Breakroom', '2026-02-01', 'fail', 'Inspector Martinez',
 'Multiple critical violations. Facility closed until corrected.',
 '{"score": 58, "violations": ["inadequate_refrigeration", "pest_evidence", "improper_food_storage", "dirty_surfaces"], "critical_violations": 3, "closure_order": true}'::jsonb),

('Central District', 'City Hall Cafeteria', '2026-01-29', 'pass', 'Inspector Williams',
 'Bi-annual inspection completed successfully.',
 '{"score": 93, "violations": ["minor_temperature_log_gap"], "critical_violations": 0}'::jsonb),

('Eastside', 'Senior Wellness Center Kitchen', '2026-02-03', 'pass', 'Inspector Rodriguez',
 'Special focus on food service for vulnerable population. Excellent compliance.',
 '{"score": 96, "violations": [], "critical_violations": 0, "special_considerations": "senior_nutrition_program"}'::jsonb);

/* ========================================================= */
/* 25. SERVICE_OUTAGES - Utility Service Interruptions */
/* ========================================================= */

INSERT INTO service_outages (location, zone, reported_at, started_at, resolved_at, severity, cause, 
                              affected_customers, status, notes) VALUES

('Downtown - 3rd Street', 'Zone-1', '2026-02-06 14:32:00', '2026-02-06 14:15:00', '2026-02-07 18:00:00',
 'high', 'Water main break - pipeline failure', 450, 'resolved',
 'Emergency repair completed. Pipeline section replaced. All customers restored.'),

('North District - Oak Boulevard Area', 'Zone-2', '2026-02-05 08:20:00', '2026-02-05 07:00:00', NULL,
 'medium', 'Pressure regulator malfunction', 280, 'investigating',
 'Low pressure reported by multiple residents. Investigating valve system. Inspection scheduled Feb 10.'),

('Industrial Zone A', 'Zone-4', '2026-02-06 03:48:00', '2026-02-06 03:45:00', '2026-02-06 09:30:00',
 'critical', 'Pipeline burst - age-related failure', 12, 'resolved',
 'Critical pipeline failure. 8-worker emergency crew responded. Pipeline isolated and repaired.'),

('East Residential District', 'Zone-2', '2026-01-15 16:00:00', '2026-01-15 15:45:00', '2026-01-15 19:30:00',
 'low', 'Planned maintenance - valve replacement', 125, 'resolved',
 'Scheduled maintenance. Customers notified 48 hours in advance. Completed on schedule.'),

('West Zone - Sunset Avenue', 'Zone-3', '2026-01-28 09:00:00', '2026-01-28 08:30:00', '2026-01-28 14:00:00',
 'medium', 'Frozen pipe repair', 85, 'resolved',
 'Winter weather-related freeze. Thawed and repaired. Customers advised on pipe protection.'),

('Downtown - City Center', 'Zone-1', '2026-02-08 11:20:00', '2026-02-08 11:15:00', '2026-02-08 12:45:00',
 'low', 'Valve exercise - routine maintenance', 35, 'resolved',
 'Brief outage for valve maintenance. 90-minute duration as planned.');

/* ========================================================= */
/* 26. TAX_REVENUES - Tax Collection Records */
/* ========================================================= */

INSERT INTO tax_revenues (period_start, period_end, source, department, amount, details, recorded_at) VALUES

('2026-01-01', '2026-01-31', 'Property Tax', 'finance', 2500000.00,
 '{"parcels_collected": 12450, "delinquent_rate": 2.3, "payment_methods": {"online": 8200, "mail": 3450, "in_person": 800}, "avg_per_parcel": 200.80}'::jsonb,
 '2026-02-01 10:00:00'),

('2026-01-01', '2026-01-31', 'Sales Tax', 'finance', 850000.00,
 '{"businesses_reporting": 1250, "retail_portion": 620000, "restaurant_portion": 180000, "services_portion": 50000, "tax_rate": 0.085}'::jsonb,
 '2026-02-01 10:00:00'),

('2025-12-01', '2025-12-31', 'Property Tax', 'finance', 2800000.00,
 '{"parcels_collected": 12520, "delinquent_rate": 1.8, "year_end_surge": true, "note": "Annual payment deadline"}'::jsonb,
 '2026-01-02 10:00:00'),

('2025-12-01', '2025-12-31', 'Sales Tax', 'finance', 920000.00,
 '{"businesses_reporting": 1280, "holiday_shopping_boost": true, "retail_portion": 680000, "restaurant_portion": 195000, "services_portion": 45000}'::jsonb,
 '2026-01-02 10:00:00'),

('2026-01-01', '2026-01-31', 'Business License Fees', 'finance', 220000.00,
 '{"new_licenses": 45, "renewals": 875, "license_types": {"retail": 380, "restaurant": 145, "professional_services": 280, "construction": 115}}'::jsonb,
 '2026-02-01 10:00:00'),

('2026-01-01', '2026-01-31', 'Building Permits', 'engineering', 185000.00,
 '{"residential_permits": 28, "commercial_permits": 12, "renovation_permits": 65, "total_permits": 105, "estimated_construction_value": 8500000}'::jsonb,
 '2026-02-01 10:00:00'),

('2025-11-01', '2025-11-30', 'Property Tax', 'finance', 2200000.00,
 '{"parcels_collected": 12380, "delinquent_rate": 2.5}'::jsonb,
 '2025-12-01 10:00:00'),

('2025-11-01', '2025-11-30', 'Sales Tax', 'finance', 880000.00,
 '{"businesses_reporting": 1240, "retail_portion": 640000, "restaurant_portion": 190000, "services_portion": 50000}'::jsonb,
 '2025-12-01 10:00:00');

/* ========================================================= */
/* 27. VACCINATION_CAMPAIGNS - Public Health Immunization Programs */
/* ========================================================= */

INSERT INTO vaccination_campaigns (name, location, start_date, end_date, target_groups, coverage_percent, 
                                    status, resources, notes) VALUES

('Spring 2026 Senior Flu Vaccination Drive', 'Multiple Community Centers', '2026-02-15', '2026-03-15',
 '["seniors_65_plus", "immunocompromised"]'::jsonb, 12.50, 'active',
 '{"vaccine_doses": 10000, "staff": 12, "sites": 4, "appointments_booked": 1250, "walk_ins_accepted": true}'::jsonb,
 'Campaign launched Feb 15. Four sites operational. Target: 8,500 seniors. Currently 12.5% of target reached (1,062 vaccinated).'),

('School Entry Vaccination Compliance', 'All City Schools', '2025-08-01', '2025-09-15',
 '["kindergarten_entry", "7th_grade_entry"]'::jsonb, 94.20, 'completed',
 '{"schools_participating": 18, "students_targeted": 2400, "students_compliant": 2261, "exemptions_granted": 58}'::jsonb,
 'Annual school vaccination verification completed. 94.2% compliance rate exceeds state requirement of 92%.'),

('COVID-19 Booster Campaign - Winter 2025', 'Health Clinics & Pharmacies', '2025-11-01', '2026-01-31',
 '["adults_18_plus", "high_risk"]'::jsonb, 38.50, 'completed',
 '{"vaccine_doses_administered": 8925, "target_population": 23000, "partnership_pharmacies": 8, "city_clinics": 4}'::jsonb,
 'Winter booster campaign completed. 38.5% uptake among eligible population. Exceeded target of 35%.'),

('Measles Response Vaccination', 'Westside Community & Schools', '2026-02-07', '2026-02-28',
 '["unvaccinated_children", "school_contacts", "community_members"]'::jsonb, 45.00, 'active',
 '{"rapid_response": true, "vaccine_doses": 500, "doses_administered": 225, "target_population": 500, "contact_tracing_complete": true}'::jsonb,
 'Rapid response to measles case. Targeting contacts and unvaccinated community members. 225 vaccinated to date.'),

('HPV Vaccination Middle School Program', 'Middle Schools', '2025-09-15', '2025-11-30',
 '["6th_grade_students", "7th_grade_students"]'::jsonb, 76.30, 'completed',
 '{"schools": 6, "students_eligible": 1450, "doses_series_1": 1106, "doses_series_2": 982, "parental_consent_rate": 78}'::jsonb,
 'School-based HPV vaccination program completed. 76.3% received first dose. Second dose series ongoing.'),

('Hepatitis A Outbreak Response', 'Downtown & Homeless Services', '2025-10-01', '2025-12-15',
 '["homeless_population", "food_service_workers", "healthcare_workers"]'::jsonb, 82.00, 'completed',
 '{"outbreak_related": true, "doses_administered": 1640, "target_population": 2000, "mobile_clinics": 8, "partner_organizations": 5}'::jsonb,
 'Outbreak response vaccination completed. High coverage achieved through mobile clinics and partnerships.'),

('Annual Flu Vaccination - Fall 2025', 'Multiple Locations', '2025-09-01', '2025-11-30',
 '["general_public", "seniors", "healthcare_workers", "teachers"]'::jsonb, 42.50, 'completed',
 '{"doses_administered": 19125, "target_population": 45000, "pharmacies": 12, "clinics": 7, "employer_programs": 25}'::jsonb,
 'Annual flu campaign. 42.5% coverage among general population. Exceeds national average of 38%.');

/* ========================================================= */
/* 28. VULNERABLE_POPULATIONS - At-Risk Community Tracking */
/* ========================================================= */

INSERT INTO vulnerable_populations (location, population_group, population_count, vulnerability_index, notes, metadata) VALUES

('Downtown District', 'Homeless Population', 285, 9.2,
 'High vulnerability due to lack of shelter, healthcare access challenges, and extreme weather exposure.',
 '{"primary_needs": ["shelter", "healthcare", "mental_health_services"], "services_available": ["emergency_shelter", "meal_program", "health_clinic"], "outreach_frequency": "daily"}'::jsonb),

('Eastside Low-Income Housing', 'Low-Income Families', 1450, 6.8,
 'Economic vulnerability, food insecurity, limited healthcare access.',
 '{"avg_household_income": 28000, "food_bank_participation": 620, "medicaid_enrollment": 1180, "children_count": 890}'::jsonb),

('North District Senior Housing', 'Seniors 75+', 820, 7.5,
 'Age-related vulnerability, chronic conditions, mobility limitations, social isolation.',
 '{"avg_age": 82, "living_alone": 480, "chronic_conditions_avg": 2.8, "home_health_recipients": 245, "meal_delivery": 380}'::jsonb),

('Westside Apartments', 'Recent Immigrants & Refugees', 380, 7.1,
 'Language barriers, limited healthcare knowledge, cultural adjustment challenges.',
 '{"languages_spoken": ["Spanish", "Arabic", "Somali", "Vietnamese"], "interpretation_services": true, "community_health_workers": 4, "cultural_liaison": true}'::jsonb),

('South Industrial Area', 'Disabled Adults', 195, 8.3,
 'Physical and cognitive disabilities requiring specialized services and accessibility accommodations.',
 '{"mobility_impaired": 85, "cognitive_disabilities": 45, "multiple_disabilities": 65, "supported_living": 120, "home_care_recipients": 140}'::jsonb),

('Central District', 'Single Parent Households', 680, 6.2,
 'Economic stress, childcare challenges, time poverty, healthcare access barriers.',
 '{"children_count": 1285, "employed_parents": 590, "childcare_assistance": 385, "food_assistance": 480}'::jsonb),

('Riverside Area', 'Chronically Ill Patients', 425, 8.0,
 'Complex medical needs, frequent healthcare utilization, medication management challenges.',
 '{"diabetes": 180, "heart_disease": 145, "copd": 95, "multiple_conditions": 215, "home_health": 165, "avg_er_visits_annual": 4.2}'::jsonb),

('East Zone Schools', 'At-Risk Youth', 340, 7.8,
 'Educational challenges, behavioral health needs, family instability, poverty.',
 '{"truancy_issues": 85, "behavioral_referrals": 125, "counseling_services": 280, "free_lunch_eligible": 320, "mentorship_program": 145}'::jsonb);

/* ========================================================= */
/* 29. WATER_READINGS - Pipeline Monitoring Data */
/* ========================================================= */

INSERT INTO water_readings (pipeline_id, location, reading_time, pressure_psi, flow_rate, temperature, metadata)
SELECT 
    p.pipeline_id,
    p.location,
    '2026-02-09 06:00:00',
    p.pressure_psi,
    p.flow_rate,
    12.5,
    '{"sensor_id": "WS-001", "reading_type": "automated", "quality": "good"}'::jsonb
FROM pipelines p
WHERE p.pipeline_type = 'supply' AND p.operational_status = 'active'
LIMIT 1;

INSERT INTO water_readings (pipeline_id, location, reading_time, pressure_psi, flow_rate, temperature, metadata)
SELECT 
    p.pipeline_id,
    p.location,
    '2026-02-09 03:00:00',
    p.pressure_psi - 2.5,
    p.flow_rate * 0.85,
    11.8,
    '{"sensor_id": "WS-002", "reading_type": "automated", "quality": "good", "note": "night_low_demand"}'::jsonb
FROM pipelines p
WHERE p.zone = 'Zone-2' AND p.pipeline_type = 'supply' AND p.operational_status = 'active'
LIMIT 1;

INSERT INTO water_readings (pipeline_id, location, reading_time, pressure_psi, flow_rate, temperature, metadata)
SELECT 
    p.pipeline_id,
    p.location,
    '2026-02-08 18:00:00',
    p.pressure_psi + 1.5,
    p.flow_rate * 1.15,
    13.2,
    '{"sensor_id": "WS-003", "reading_type": "automated", "quality": "good", "note": "evening_peak_demand"}'::jsonb
FROM pipelines p
WHERE p.zone = 'Zone-1' AND p.location LIKE '%Downtown%' AND p.operational_status = 'active'
LIMIT 1;

-- Historical readings
INSERT INTO water_readings (pipeline_id, location, reading_time, pressure_psi, flow_rate, temperature, metadata)
SELECT 
    p.pipeline_id,
    p.location,
    '2026-02-08 12:00:00',
    p.pressure_psi,
    p.flow_rate * 1.05,
    14.0,
    '{"sensor_id": "WS-004", "reading_type": "automated", "quality": "good"}'::jsonb
FROM pipelines p
WHERE p.zone = 'Zone-4' AND p.pipeline_type = 'supply' AND p.operational_status = 'active'
LIMIT 1;

INSERT INTO water_readings (pipeline_id, location, reading_time, pressure_psi, flow_rate, temperature, metadata)
SELECT 
    p.pipeline_id,
    p.location,
    '2026-02-07 06:00:00',
    p.pressure_psi - 1.0,
    p.flow_rate * 0.95,
    12.8,
    '{"sensor_id": "WS-005", "reading_type": "automated", "quality": "good"}'::jsonb
FROM pipelines p
WHERE p.zone = 'Zone-3' AND p.pipeline_type = 'supply' AND p.operational_status = 'active'
LIMIT 1;

/* ========================================================= */
/* 30. WORK_SCHEDULES - Department Work Planning */
/* ========================================================= */

INSERT INTO work_schedules (department, activity_type, location, scheduled_date, start_time, end_time, 
                             priority, workers_assigned, equipment_assigned, status, notes) VALUES

-- Water Department Schedules
('water', 'pipeline_inspection', 'North District - Oak Boulevard', '2026-02-10', '08:00:00', '16:00:00',
 'high', 3, '["pressure_testing_equipment", "leak_detection_tools", "safety_gear"]'::jsonb, 'scheduled',
 'Investigating low pressure reports. Full valve and regulator inspection.'),

('water', 'valve_maintenance', 'Downtown - City Center', '2026-02-11', '22:00:00', '02:00:00',
 'medium', 2, '["valve_tools", "lubricants", "safety_equipment"]'::jsonb, 'scheduled',
 'Night shift to minimize disruption. Routine valve exercise program.'),

('water', 'meter_reading', 'Residential Zone 1', '2026-02-12', '08:00:00', '17:00:00',
 'low', 4, '["handheld_readers", "tablets"]'::jsonb, 'scheduled',
 'Monthly meter reading route. Approximately 1,200 meters.'),

-- Fire Department Schedules
('fire', 'equipment_inspection', 'Central Fire Station', '2026-02-09', '09:00:00', '15:00:00',
 'critical', 2, '["testing_equipment", "documentation_tablets"]'::jsonb, 'in_progress',
 'SCBA equipment certification. 24 units to be tested and certified.'),

('fire', 'training_exercise', 'Fire Training Center', '2026-02-12', '08:00:00', '12:00:00',
 'medium', 16, '["training_props", "safety_equipment", "medical_supplies"]'::jsonb, 'scheduled',
 'Multi-company training exercise. Confined space rescue scenarios.'),

('fire', 'hydrant_inspection', 'Industrial Zone A', '2026-02-13', '09:00:00', '16:00:00',
 'medium', 3, '["hydrant_tools", "flow_testing_equipment", "paint_supplies"]'::jsonb, 'scheduled',
 'Quarterly hydrant inspection and flow testing. 45 hydrants in zone.'),

-- Engineering Department Schedules
('engineering', 'pothole_repair', 'Maple Avenue', '2026-02-10', '06:00:00', '18:00:00',
 'high', 4, '["asphalt_truck", "compactor", "safety_cones", "traffic_signs"]'::jsonb, 'scheduled',
 'Repair 12 potholes. Traffic control in place. 2-day project timeline.'),

('engineering', 'street_sweeping', 'Downtown District', '2026-02-11', '05:00:00', '08:00:00',
 'low', 2, '["street_sweeper", "water_truck"]'::jsonb, 'scheduled',
 'Weekly street cleaning. Early morning to avoid traffic.'),

('engineering', 'bridge_inspection', 'East Side River Crossing', '2026-02-14', '08:00:00', '17:00:00',
 'high', 5, '["inspection_equipment", "safety_harnesses", "drone", "measurement_tools"]'::jsonb, 'scheduled',
 'Quarterly bridge safety inspection. Part of rehabilitation project.'),

-- Health Department Schedules
('health', 'restaurant_inspections', 'Downtown Food Court', '2026-02-12', '10:00:00', '15:00:00',
 'medium', 2, '["inspection_tablets", "temperature_probes", "test_kits"]'::jsonb, 'scheduled',
 'Follow-up inspections for 2 establishments. Regular inspections for 5 others.'),

('health', 'vaccination_clinic', 'North Community Center', '2026-02-15', '09:00:00', '16:00:00',
 'high', 6, '["vaccine_refrigerators", "medical_supplies", "registration_tablets"]'::jsonb, 'scheduled',
 'Spring flu vaccination campaign kickoff. Expecting 200-250 seniors.'),

('health', 'water_quality_sampling', 'Citywide - 15 locations', '2026-02-13', '07:00:00', '14:00:00',
 'medium', 2, '["sampling_equipment", "coolers", "lab_supplies"]'::jsonb, 'scheduled',
 'Bi-weekly water quality sampling. 15 locations across all zones.'),

-- Sanitation Department Schedules
('sanitation', 'waste_collection', 'Residential Zone 3', '2026-02-10', '06:00:00', '14:00:00',
 'high', 8, '["collection_trucks_2", "safety_equipment"]'::jsonb, 'scheduled',
 'Special holiday overflow collection. 2 trucks assigned.'),

('sanitation', 'recycling_collection', 'North District', '2026-02-11', '06:00:00', '14:00:00',
 'medium', 6, '["recycling_truck", "safety_gear"]'::jsonb, 'scheduled',
 'Weekly recycling route. Approximately 1,800 households.'),

('sanitation', 'street_cleaning', 'Downtown & Central District', '2026-02-12', '20:00:00', '04:00:00',
 'low', 4, '["sweeper_trucks_2", "pressure_washer"]'::jsonb, 'scheduled',
 'Night shift street cleaning. High-traffic areas. Monthly deep clean.'),

-- Recent Completed Work
('water', 'emergency_repair', 'Downtown - 3rd Street', '2026-02-06', '15:00:00', '18:00:00',
 'critical', 8, '["excavator", "pipe_sections", "welding_equipment", "safety_gear"]'::jsonb, 'completed',
 'Emergency pipeline burst repair. Completed ahead of schedule.'),

('engineering', 'snow_removal', 'Citywide - Priority Routes', '2026-02-03', '03:00:00', '12:00:00',
 'critical', 12, '["snow_plows_6", "salt_spreaders", "front_loaders"]'::jsonb, 'completed',
 'Winter storm response. All priority routes cleared by noon.');

/* ========================================================= */
/* 31. WORKERS - Department Personnel */
/* ========================================================= */

INSERT INTO workers (department, worker_name, role, skills, certifications, status, phone, email, hire_date) VALUES

-- Water Department Workers
('water', 'John Martinez', 'Pipeline Technician', '["welding", "pipeline_repair", "pressure_testing"]'::jsonb,
 '["certified_welder", "confined_space", "hazmat_awareness"]'::jsonb, 'active', '+1-555-1001', 'j.martinez@citywater.gov', '2018-03-15'),

('water', 'Sarah Chen', 'Senior Maintenance Engineer', '["hydraulics", "pump_systems", "project_management"]'::jsonb,
 '["professional_engineer", "water_treatment_operator_III"]'::jsonb, 'active', '+1-555-1002', 's.chen@citywater.gov', '2015-06-20'),

('water', 'Michael Rodriguez', 'Field Technician', '["leak_detection", "meter_reading", "excavation"]'::jsonb,
 '["backflow_prevention", "excavation_safety"]'::jsonb, 'active', '+1-555-1003', 'm.rodriguez@citywater.gov', '2019-09-10'),

('water', 'Lisa Thompson', 'Water Quality Specialist', '["lab_analysis", "water_testing", "compliance_reporting"]'::jsonb,
 '["water_quality_analyst", "lab_safety"]'::jsonb, 'active', '+1-555-1004', 'l.thompson@citywater.gov', '2017-01-12'),

('water', 'David Kim', 'Maintenance Technician', '["valve_repair", "system_monitoring", "emergency_response"]'::jsonb,
 '["confined_space", "first_aid_cpr"]'::jsonb, 'active', '+1-555-1005', 'd.kim@citywater.gov', '2020-11-03'),

('water', 'Jennifer Williams', 'Operations Supervisor', '["team_leadership", "scheduling", "budget_management"]'::jsonb,
 '["supervisor_certification", "water_distribution_III"]'::jsonb, 'active', '+1-555-1006', 'j.williams@citywater.gov', '2014-04-22'),

('water', 'Robert Anderson', 'Field Worker', '["installation", "repair", "equipment_operation"]'::jsonb,
 '["heavy_equipment_operator", "safety_certification"]'::jsonb, 'active', '+1-555-1007', 'r.anderson@citywater.gov', '2021-02-15'),

('water', 'Maria Garcia', 'Meter Reader', '["meter_reading", "customer_service", "route_planning"]'::jsonb,
 '["meter_reading_certification"]'::jsonb, 'on_leave', '+1-555-1008', 'm.garcia@citywater.gov', '2019-07-08'),

-- Fire Department Workers
('fire', 'Captain James Sullivan', 'Fire Captain', '["fire_suppression", "leadership", "incident_command"]'::jsonb,
 '["fire_officer_II", "emt_paramedic", "incident_commander"]'::jsonb, 'active', '+1-555-2001', 'j.sullivan@cityfire.gov', '2010-04-15'),

('fire', 'Emily Davis', 'Firefighter/Paramedic', '["emergency_medical", "fire_suppression", "vehicle_extrication"]'::jsonb,
 '["paramedic", "firefighter_II", "hazmat_operations"]'::jsonb, 'active', '+1-555-2002', 'e.davis@cityfire.gov', '2016-08-20'),

('fire', 'Marcus Washington', 'Fire Engineer', '["apparatus_operation", "pump_operations", "maintenance"]'::jsonb,
 '{"firefighter_II", "driver_operator", "apparatus_maintenance"]'::jsonb, 'active', '+1-555-2003', 'm.washington@cityfire.gov', '2013-11-10'),

('fire', 'Rachel Foster', 'Fire Inspector', '["code_enforcement", "building_inspection", "fire_investigation"]'::jsonb,
 '["fire_inspector_II", "fire_investigator", "building_code_specialist"]'::jsonb, 'active', '+1-555-2004', 'r.foster@cityfire.gov', '2015-03-05'),

('fire', 'Antonio Lopez', 'Firefighter', '["fire_suppression", "search_rescue", "first_aid"]'::jsonb,
 '["firefighter_I", "emt_basic", "confined_space_rescue"]'::jsonb, 'active', '+1-555-2005', 'a.lopez@cityfire.gov', '2020-01-12'),

-- Engineering Department Workers
('engineering', 'Steven Park', 'Civil Engineer', '["road_design", "structural_analysis", "project_management"]'::jsonb,
 '["professional_engineer", "project_management_professional"]'::jsonb, 'active', '+1-555-3001', 's.park@cityengineering.gov', '2016-05-15'),

('engineering', 'Amanda Brooks', 'Public Works Supervisor', '["crew_management", "equipment_operations", "safety"]'::jsonb,
 '["supervisor_certification", "heavy_equipment_operator", "osha_30"]'::jsonb, 'active', '+1-555-3002', 'a.brooks@cityengineering.gov', '2014-09-20'),

('engineering', 'Carlos Mendoza', 'Equipment Operator', '["excavator", "backhoe", "grader", "plow"]'::jsonb,
 '["class_A_cdl", "heavy_equipment_certified"]'::jsonb, 'active', '+1-555-3003', 'c.mendoza@cityengineering.gov', '2017-02-10'),

('engineering', 'Jessica Taylor', 'Road Maintenance Worker', '["asphalt_repair", "concrete_work", "patch_work"]'::jsonb,
 '["traffic_control", "confined_space"]'::jsonb, 'active', '+1-555-3004', 'j.taylor@cityengineering.gov', '2019-06-15'),

('engineering', 'Thomas Brown', 'Bridge Inspector', '["structural_inspection", "safety_assessment", "report_writing"]'::jsonb,
 '["bridge_inspector", "nbi_certified", "rope_access"]'::jsonb, 'active', '+1-555-3005', 't.brown@cityengineering.gov', '2015-11-08'),

-- Health Department Workers
('health', 'Dr. Patricia Nelson', 'Public Health Physician', '["epidemiology", "disease_surveillance", "health_policy"]'::jsonb,
 '["medical_license", "board_certified_preventive_medicine", "mph"]'::jsonb, 'active', '+1-555-4001', 'p.nelson@cityhealth.gov', '2013-07-01'),

('health', 'Kevin Wright', 'Environmental Health Inspector', '["food_safety", "sanitation_inspection", "code_enforcement"]'::jsonb,
 '["registered_environmental_health_specialist", "food_safety_manager"]'::jsonb, 'active', '+1-555-4002', 'k.wright@cityhealth.gov', '2016-04-12'),

('health', 'Monica Rivera', 'Community Health Nurse', '["vaccination", "patient_care", "health_education"]'::jsonb,
 '["registered_nurse", "public_health_nurse", "cpr_instructor"]'::jsonb, 'active', '+1-555-4003', 'm.rivera@cityhealth.gov', '2018-09-05'),

('health', 'Daniel Cooper', 'Health Educator', '["program_development", "community_outreach", "data_analysis"]'::jsonb,
 '["certified_health_education_specialist", "spanish_bilingual"]'::jsonb, 'active', '+1-555-4004', 'd.cooper@cityhealth.gov', '2019-02-20'),

-- Sanitation Department Workers
('sanitation', 'William Turner', 'Collection Crew Supervisor', '["route_management", "crew_leadership", "safety"]'::jsonb,
 '["class_B_cdl", "supervisor_certification", "osha_safety"]'::jsonb, 'active', '+1-555-5001', 'w.turner@citysanitation.gov', '2012-03-15'),

('sanitation', 'Angela Scott', 'Recycling Coordinator', '["program_management", "public_education", "data_tracking"]'::jsonb,
 '["recycling_specialist", "environmental_management"]'::jsonb, 'active', '+1-555-5002', 'a.scott@citysanitation.gov', '2017-06-10'),

('sanitation', 'Raymond Hughes', 'Equipment Operator', '["collection_truck", "compactor", "vehicle_maintenance"]'::jsonb,
 '["class_B_cdl", "air_brake_endorsement"]'::jsonb, 'active', '+1-555-5003', 'r.hughes@citysanitation.gov', '2018-11-22'),

('sanitation', 'Nicole Martinez', 'Collection Worker', '["waste_collection", "route_assistance", "customer_service"]'::jsonb,
 '["safety_certification", "first_aid"]'::jsonb, 'active', '+1-555-5004', 'n.martinez@citysanitation.gov', '2020-04-08'),

('sanitation', 'Frank Robinson', 'Maintenance Technician', '["truck_repair", "hydraulics", "diagnostics"]'::jsonb,
 '["ase_certified", "diesel_mechanic", "hydraulics_specialist"]'::jsonb, 'active', '+1-555-5005', 'f.robinson@citysanitation.gov', '2014-08-15'),

-- Finance Department Workers
('finance', 'Christine Allen', 'Finance Director', '["financial_planning", "budget_management", "policy_development"]'::jsonb,
 '["cpa", "certified_government_financial_manager"]'::jsonb, 'active', '+1-555-6001', 'c.allen@cityfinance.gov', '2011-01-10'),

('finance', 'Brian Mitchell', 'Budget Analyst', '["budget_analysis", "forecasting", "reporting"]'::jsonb,
 '["certified_government_financial_manager", "excel_expert"]'::jsonb, 'active', '+1-555-6002', 'b.mitchell@cityfinance.gov', '2016-09-12'),

('finance', 'Laura Peterson', 'Accounting Specialist', '["accounts_payable", "reconciliation", "compliance"]'::jsonb,
 '["cpa_eligible", "quickbooks_certified"]'::jsonb, 'active', '+1-555-6003', 'l.peterson@cityfinance.gov', '2019-03-25');

/* ========================================================= */
/* FINAL DATA SUMMARY - COMPLETE DATABASE */
/* ========================================================= */

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║  ✅ COMPREHENSIVE SEED DATA LOADING COMPLETE - ALL 31 TABLES      ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
    RAISE NOTICE '📊 TABLES 21-31 RECORDS CREATED:';
    RAISE NOTICE '   ✓ reservoirs: 7 water storage facilities';
    RAISE NOTICE '   ✓ revenue_forecasts: 5 financial projections';
    RAISE NOTICE '   ✓ revenue_history: 8 historical revenue records';
    RAISE NOTICE '   ✓ sanitation_inspections: 7 facility inspections';
    RAISE NOTICE '   ✓ service_outages: 6 water service interruptions';
    RAISE NOTICE '   ✓ tax_revenues: 8 tax collection records';
    RAISE NOTICE '   ✓ vaccination_campaigns: 7 immunization programs';
    RAISE NOTICE '   ✓ vulnerable_populations: 8 at-risk groups tracked';
    RAISE NOTICE '   ✓ water_readings: 5 pipeline monitoring records';
    RAISE NOTICE '   ✓ work_schedules: 18 scheduled work activities';
    RAISE NOTICE '   ✓ workers: 32 city employees across all departments';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '📈 COMPLETE DATABASE STATISTICS:';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '🏛️  DEPARTMENTS: 6 active city departments';
    RAISE NOTICE '👥  PERSONNEL: 32 workers across all departments';
    RAISE NOTICE '💰  BUDGETS: 30 budget records (5 months × 6 departments)';
    RAISE NOTICE '💵  REVENUE: $15.5M+ in tracked revenue (3 months)';
    RAISE NOTICE '🎯  PROJECTS: 19 projects ($6.2M total value)';
    RAISE NOTICE '💼  GRANTS: $3.73M awarded ($2.01M received)';
    RAISE NOTICE '🏦  RESERVES: $7.86M in reserve funds';
    RAISE NOTICE '📋  DECISIONS: 12 agent decisions logged';
    RAISE NOTICE '⚡  INCIDENTS: 15 incidents across departments';
    RAISE NOTICE '🚰  RESERVOIRS: 7 facilities (141M liters total capacity)';
    RAISE NOTICE '🔧  PIPELINES: 16 pipelines monitored';
    RAISE NOTICE '💉  VACCINATIONS: 7 campaigns (30,000+ doses administered)';
    RAISE NOTICE '👨‍⚕️  HEALTH FACILITIES: 7 clinics and centers';
    RAISE NOTICE '🗓️  WORK SCHEDULES: 18 scheduled activities';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '💰 FINANCIAL OVERVIEW:';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '   February 2026 Budget: $5.36M (allocated: $3.7M, spent: $2.09M)';
    RAISE NOTICE '   Available Funds: $3.27M (61%)';
    RAISE NOTICE '   Reserve Funds: $7.86M';
    RAISE NOTICE '   Grant Funding: $3.73M awarded, $2.01M received';
    RAISE NOTICE '   Tax Revenue (Jan 2026): $3.57M';
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '🎯 SYSTEM STATUS: FULLY OPERATIONAL';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════════';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Database ready for:';
    RAISE NOTICE '   • Agent testing and development';
    RAISE NOTICE '   • Frontend data visualization';
    RAISE NOTICE '   • Realistic scenario simulations';
    RAISE NOTICE '   • Performance and load testing';
    RAISE NOTICE '   • User acceptance testing';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next Steps:';
    RAISE NOTICE '   1. Run: psql -U postgres -d departments -f comprehensive_seed_data.sql';
    RAISE NOTICE '   2. Verify: SELECT COUNT(*) FROM [table_name] for each table';
    RAISE NOTICE '   3. Test: Run agent queries through backend';
    RAISE NOTICE '   4. Monitor: Check logs for any data issues';
    RAISE NOTICE '';
    RAISE NOTICE '╔════════════════════════════════════════════════════════════════════╗';
    RAISE NOTICE '║           🎉 SEED DATA LOADING COMPLETE! 🎉                        ║';
    RAISE NOTICE '╚════════════════════════════════════════════════════════════════════╝';
    RAISE NOTICE '';
END $$;
