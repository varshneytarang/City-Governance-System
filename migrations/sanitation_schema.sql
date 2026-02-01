/* =========================================================
   SANITATION/SOLID WASTE MANAGEMENT SCHEMA
   Extension to City Governance System
   Database: departments
   ========================================================= */

/* ---------- DROP SANITATION TABLES IF EXIST ---------- */

DROP TABLE IF EXISTS complaints CASCADE;
DROP TABLE IF EXISTS recycling_centers CASCADE;
DROP TABLE IF EXISTS landfills CASCADE;
DROP TABLE IF EXISTS waste_bins CASCADE;
DROP TABLE IF EXISTS collection_schedules CASCADE;
DROP TABLE IF EXISTS waste_trucks CASCADE;
DROP TABLE IF EXISTS sanitation_routes CASCADE;

/* ========================================================= */
/* SANITATION ROUTES */
/* ========================================================= */

CREATE TABLE sanitation_routes (
    route_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    route_name VARCHAR(255) NOT NULL,
    zone VARCHAR(50) NOT NULL,
    
    -- Route specifications
    route_type VARCHAR(30) CHECK (route_type IN ('residential', 'commercial', 'industrial', 'mixed')),
    service_frequency VARCHAR(20) CHECK (service_frequency IN ('daily', 'twice_weekly', 'weekly', 'biweekly', 'monthly')),
    
    -- Coverage area
    coverage_area JSONB,  -- GeoJSON or area description
    estimated_stops INTEGER,
    estimated_duration_minutes INTEGER,
    
    -- Capacity
    avg_waste_volume_tons NUMERIC(8, 2),
    peak_waste_volume_tons NUMERIC(8, 2),
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'under_review', 'modified')),
    
    -- Assignments
    primary_truck_id UUID,
    backup_truck_id UUID,
    assigned_crew_size INTEGER DEFAULT 3,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_serviced TIMESTAMP,
    notes TEXT
);

-- Indexes for route queries
CREATE INDEX idx_routes_zone ON sanitation_routes(zone);
CREATE INDEX idx_routes_type ON sanitation_routes(route_type);
CREATE INDEX idx_routes_status ON sanitation_routes(status);
CREATE INDEX idx_routes_frequency ON sanitation_routes(service_frequency);


/* ========================================================= */
/* WASTE TRUCKS/VEHICLES */
/* ========================================================= */

CREATE TABLE waste_trucks (
    truck_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    truck_number VARCHAR(50) UNIQUE NOT NULL,
    
    -- Vehicle specifications
    truck_type VARCHAR(30) CHECK (truck_type IN ('compactor', 'side_loader', 'rear_loader', 'roll_off', 'recycling')),
    capacity_tons NUMERIC(6, 2) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    
    -- Operational status
    operational_status VARCHAR(20) CHECK (operational_status IN ('active', 'maintenance', 'repair', 'retired', 'out_of_service')),
    
    -- Condition monitoring
    mileage NUMERIC(10, 2),
    fuel_level_percent NUMERIC(5, 2) CHECK (fuel_level_percent BETWEEN 0 AND 100),
    last_maintenance_date DATE,
    next_maintenance_due DATE,
    
    -- Current assignment
    current_route_id UUID REFERENCES sanitation_routes(route_id) ON DELETE SET NULL,
    current_location TEXT,
    
    -- Health metrics
    engine_condition VARCHAR(20) CHECK (engine_condition IN ('excellent', 'good', 'fair', 'poor', 'critical')),
    compactor_condition VARCHAR(20) CHECK (compactor_condition IN ('excellent', 'good', 'fair', 'poor', 'critical')),
    hydraulics_condition VARCHAR(20) CHECK (hydraulics_condition IN ('excellent', 'good', 'fair', 'poor', 'critical')),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for truck queries
CREATE INDEX idx_trucks_type ON waste_trucks(truck_type);
CREATE INDEX idx_trucks_status ON waste_trucks(operational_status);
CREATE INDEX idx_trucks_route ON waste_trucks(current_route_id);
CREATE INDEX idx_trucks_fuel ON waste_trucks(fuel_level_percent);


/* ========================================================= */
/* COLLECTION SCHEDULES */
/* ========================================================= */

CREATE TABLE collection_schedules (
    schedule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    route_id UUID REFERENCES sanitation_routes(route_id) ON DELETE CASCADE,
    truck_id UUID REFERENCES waste_trucks(truck_id) ON DELETE SET NULL,
    
    -- Scheduling
    scheduled_date DATE NOT NULL,
    scheduled_start_time TIME,
    scheduled_end_time TIME,
    
    -- Actual execution
    actual_start_time TIMESTAMP,
    actual_end_time TIMESTAMP,
    actual_waste_collected_tons NUMERIC(8, 2),
    
    -- Crew assignment
    crew_leader VARCHAR(255),
    crew_members JSONB,  -- Array of worker IDs or names
    crew_size INTEGER,
    
    -- Status
    status VARCHAR(20) CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'delayed')),
    delay_reason TEXT,
    
    -- Performance metrics
    stops_completed INTEGER,
    stops_missed INTEGER,
    missed_locations JSONB,
    
    -- Related to agent decision
    agent_decision_id UUID REFERENCES agent_decisions(id) ON DELETE SET NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for schedule queries
CREATE INDEX idx_collection_schedules_route ON collection_schedules(route_id);
CREATE INDEX idx_collection_schedules_truck ON collection_schedules(truck_id);
CREATE INDEX idx_collection_schedules_date ON collection_schedules(scheduled_date);
CREATE INDEX idx_collection_schedules_status ON collection_schedules(status);


/* ========================================================= */
/* WASTE BINS/CONTAINERS */
/* ========================================================= */

CREATE TABLE waste_bins (
    bin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    bin_identifier VARCHAR(100) UNIQUE NOT NULL,
    location TEXT NOT NULL,
    zone VARCHAR(50),
    
    -- Bin specifications
    bin_type VARCHAR(30) CHECK (bin_type IN ('residential', 'commercial', 'industrial', 'public', 'recycling')),
    capacity_liters INTEGER NOT NULL,
    
    -- Fill level monitoring
    current_fill_percent NUMERIC(5, 2) CHECK (current_fill_percent BETWEEN 0 AND 100),
    last_emptied TIMESTAMP,
    
    -- Status
    operational_status VARCHAR(20) CHECK (operational_status IN ('active', 'full', 'damaged', 'missing', 'inactive')),
    
    -- Assignment
    assigned_route_id UUID REFERENCES sanitation_routes(route_id) ON DELETE SET NULL,
    
    -- Health
    condition VARCHAR(20) CHECK (condition IN ('excellent', 'good', 'fair', 'poor', 'damaged')),
    
    -- Sensor data (if smart bins)
    has_sensor BOOLEAN DEFAULT FALSE,
    last_sensor_reading TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for bin queries
CREATE INDEX idx_bins_location ON waste_bins(location);
CREATE INDEX idx_bins_zone ON waste_bins(zone);
CREATE INDEX idx_bins_type ON waste_bins(bin_type);
CREATE INDEX idx_bins_status ON waste_bins(operational_status);
CREATE INDEX idx_bins_fill_level ON waste_bins(current_fill_percent);
CREATE INDEX idx_bins_route ON waste_bins(assigned_route_id);


/* ========================================================= */
/* LANDFILLS */
/* ========================================================= */

CREATE TABLE landfills (
    landfill_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    
    -- Capacity
    total_capacity_tons BIGINT NOT NULL,
    current_usage_tons BIGINT DEFAULT 0,
    
    -- Calculated field
    utilization_percent NUMERIC(5, 2) GENERATED ALWAYS AS 
        (CASE WHEN total_capacity_tons > 0 THEN (current_usage_tons::NUMERIC / total_capacity_tons) * 100 ELSE 0 END) STORED,
    
    -- Accepted waste types
    accepted_waste_types JSONB,  -- ['general', 'organic', 'construction', etc.]
    
    -- Operational info
    operational_status VARCHAR(20) CHECK (operational_status IN ('active', 'full', 'closed', 'maintenance')),
    daily_intake_limit_tons NUMERIC(8, 2),
    
    -- Environmental monitoring
    methane_level VARCHAR(20) CHECK (methane_level IN ('safe', 'moderate', 'high', 'critical')),
    leachate_status VARCHAR(20) CHECK (leachate_status IN ('normal', 'elevated', 'critical')),
    
    -- Distance/accessibility
    distance_from_city_km NUMERIC(6, 2),
    access_road_condition VARCHAR(20) CHECK (access_road_condition IN ('excellent', 'good', 'fair', 'poor')),
    
    -- Metadata
    opened_date DATE,
    estimated_closure_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for landfill queries
CREATE INDEX idx_landfills_status ON landfills(operational_status);
CREATE INDEX idx_landfills_utilization ON landfills(utilization_percent);


/* ========================================================= */
/* RECYCLING CENTERS */
/* ========================================================= */

CREATE TABLE recycling_centers (
    center_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    
    -- Capacity
    processing_capacity_tons_per_day NUMERIC(8, 2),
    current_load_tons NUMERIC(8, 2) DEFAULT 0,
    
    -- Materials accepted
    accepted_materials JSONB,  -- ['plastic', 'paper', 'metal', 'glass', 'electronics']
    
    -- Operational status
    operational_status VARCHAR(20) CHECK (operational_status IN ('active', 'at_capacity', 'maintenance', 'closed')),
    
    -- Performance metrics
    processing_efficiency_percent NUMERIC(5, 2),
    contamination_rate_percent NUMERIC(5, 2),
    
    -- Operating hours
    operating_hours JSONB,  -- {monday: '8am-5pm', ...}
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Indexes for recycling center queries
CREATE INDEX idx_recycling_centers_status ON recycling_centers(operational_status);


/* ========================================================= */
/* CITIZEN COMPLAINTS */
/* ========================================================= */

CREATE TABLE complaints (
    complaint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Complainant info
    complainant_name VARCHAR(255),
    complainant_phone VARCHAR(20),
    complainant_email VARCHAR(255),
    
    -- Complaint details
    complaint_type VARCHAR(50) CHECK (complaint_type IN ('missed_collection', 'overflow', 'odor', 'spill', 'damaged_bin', 'illegal_dumping', 'schedule_issue', 'other')),
    location TEXT NOT NULL,
    zone VARCHAR(50),
    
    description TEXT,
    
    -- Severity
    priority VARCHAR(20) CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    
    -- Reporting
    reported_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Status tracking
    status VARCHAR(20) CHECK (status IN ('submitted', 'acknowledged', 'investigating', 'in_progress', 'resolved', 'closed')),
    
    -- Resolution
    assigned_to VARCHAR(255),
    resolution_date TIMESTAMP,
    resolution_notes TEXT,
    resolution_time_hours NUMERIC(8, 2),
    
    -- Related entities
    related_route_id UUID REFERENCES sanitation_routes(route_id) ON DELETE SET NULL,
    related_bin_id UUID REFERENCES waste_bins(bin_id) ON DELETE SET NULL,
    agent_decision_id UUID REFERENCES agent_decisions(id) ON DELETE SET NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for complaint queries
CREATE INDEX idx_complaints_type ON complaints(complaint_type);
CREATE INDEX idx_complaints_location ON complaints(location);
CREATE INDEX idx_complaints_zone ON complaints(zone);
CREATE INDEX idx_complaints_priority ON complaints(priority);
CREATE INDEX idx_complaints_status ON complaints(status);
CREATE INDEX idx_complaints_reported_date ON complaints(reported_date DESC);


/* ========================================================= */
/* UPDATE TIMESTAMP TRIGGERS */
/* ========================================================= */

CREATE TRIGGER update_sanitation_routes_updated_at BEFORE UPDATE ON sanitation_routes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_waste_trucks_updated_at BEFORE UPDATE ON waste_trucks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_collection_schedules_updated_at BEFORE UPDATE ON collection_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_waste_bins_updated_at BEFORE UPDATE ON waste_bins
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_landfills_updated_at BEFORE UPDATE ON landfills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recycling_centers_updated_at BEFORE UPDATE ON recycling_centers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_complaints_updated_at BEFORE UPDATE ON complaints
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


/* ========================================================= */
/* SAMPLE DATA FOR TESTING */
/* ========================================================= */

-- Insert sample sanitation routes (10 routes)
INSERT INTO sanitation_routes (route_name, zone, route_type, service_frequency, estimated_stops, estimated_duration_minutes, avg_waste_volume_tons, peak_waste_volume_tons, status, assigned_crew_size)
VALUES 
    ('Downtown Residential A', 'Zone-1', 'residential', 'twice_weekly', 150, 240, 3.5, 5.0, 'active', 3),
    ('Downtown Commercial', 'Zone-1', 'commercial', 'daily', 80, 180, 8.0, 12.0, 'active', 3),
    ('East Zone Residential', 'Zone-2', 'residential', 'twice_weekly', 200, 300, 4.2, 6.5, 'active', 3),
    ('East Zone Industrial', 'Zone-2', 'industrial', 'weekly', 45, 240, 15.0, 20.0, 'active', 4),
    ('West Zone Mixed A', 'Zone-3', 'mixed', 'twice_weekly', 120, 210, 5.5, 8.0, 'active', 3),
    ('West Zone Mixed B', 'Zone-3', 'mixed', 'weekly', 100, 180, 4.0, 6.0, 'active', 3),
    ('North District Residential', 'Zone-4', 'residential', 'twice_weekly', 180, 270, 3.8, 5.5, 'active', 3),
    ('South District Commercial', 'Zone-5', 'commercial', 'daily', 60, 150, 6.5, 9.0, 'active', 3),
    ('Industrial Park Route', 'Industrial-A', 'industrial', 'weekly', 35, 200, 18.0, 25.0, 'active', 4),
    ('Recycling Route Central', 'Zone-1', 'mixed', 'weekly', 250, 360, 2.0, 3.5, 'active', 3);

-- Insert sample waste trucks (5 trucks)
INSERT INTO waste_trucks (truck_number, truck_type, capacity_tons, manufacturer, model, year, operational_status, mileage, fuel_level_percent, engine_condition, compactor_condition, hydraulics_condition, last_maintenance_date, next_maintenance_due)
VALUES 
    ('SW-101', 'compactor', 12.0, 'Peterbilt', '320', 2020, 'active', 45000, 75.0, 'good', 'good', 'excellent', '2026-01-15', '2026-02-15'),
    ('SW-102', 'side_loader', 10.0, 'Mack', 'LR', 2019, 'active', 62000, 60.0, 'fair', 'good', 'good', '2026-01-10', '2026-02-10'),
    ('SW-103', 'rear_loader', 14.0, 'Freightliner', 'M2', 2021, 'active', 28000, 85.0, 'excellent', 'excellent', 'excellent', '2026-01-20', '2026-02-20'),
    ('SW-104', 'compactor', 12.0, 'Peterbilt', '320', 2018, 'maintenance', 98000, 40.0, 'fair', 'poor', 'fair', '2026-01-05', '2026-02-05'),
    ('SW-105', 'recycling', 8.0, 'Mack', 'LEU', 2022, 'active', 15000, 90.0, 'excellent', 'excellent', 'excellent', '2026-01-25', '2026-02-25');

-- Insert sample waste bins (50 bins - simplified to 10 for brevity)
INSERT INTO waste_bins (bin_identifier, location, zone, bin_type, capacity_liters, current_fill_percent, operational_status, condition, has_sensor, last_emptied)
VALUES 
    ('BIN-DT-001', 'Downtown Main St', 'Zone-1', 'commercial', 1100, 85.0, 'active', 'good', TRUE, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('BIN-DT-002', 'Downtown 2nd Ave', 'Zone-1', 'commercial', 1100, 45.0, 'active', 'excellent', TRUE, CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('BIN-EZ-001', 'East Zone Park', 'Zone-2', 'public', 240, 92.0, 'full', 'good', FALSE, CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('BIN-EZ-002', 'East Zone Residential Block A', 'Zone-2', 'residential', 360, 70.0, 'active', 'good', FALSE, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('BIN-WZ-001', 'West Zone Shopping Center', 'Zone-3', 'commercial', 1100, 55.0, 'active', 'fair', TRUE, CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('BIN-WZ-002', 'West Zone Industrial Area', 'Zone-3', 'industrial', 2200, 88.0, 'active', 'good', TRUE, CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('BIN-ND-001', 'North District School', 'Zone-4', 'public', 360, 60.0, 'active', 'excellent', FALSE, CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('BIN-RC-001', 'Central Recycling Station', 'Zone-1', 'recycling', 1100, 40.0, 'active', 'excellent', TRUE, CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('BIN-IP-001', 'Industrial Park Main', 'Industrial-A', 'industrial', 2200, 95.0, 'full', 'good', TRUE, CURRENT_TIMESTAMP - INTERVAL '4 days'),
    ('BIN-DT-003', 'Downtown Restaurant Row', 'Zone-1', 'commercial', 1100, 78.0, 'active', 'fair', FALSE, CURRENT_TIMESTAMP - INTERVAL '1 day');

-- Insert sample landfills (2 landfills)
INSERT INTO landfills (name, location, total_capacity_tons, current_usage_tons, accepted_waste_types, operational_status, daily_intake_limit_tons, methane_level, leachate_status, distance_from_city_km, access_road_condition, opened_date, estimated_closure_date)
VALUES 
    ('North County Landfill', 'North County Region', 500000, 380000, '["general", "construction", "organic"]'::jsonb, 'active', 200, 'safe', 'normal', 25.5, 'good', '2010-01-01', '2035-12-31'),
    ('East Regional Landfill', 'East Regional Area', 300000, 245000, '["general", "industrial"]'::jsonb, 'active', 150, 'moderate', 'normal', 18.0, 'excellent', '2015-06-15', '2040-06-15');

-- Insert sample recycling centers (2 centers)
INSERT INTO recycling_centers (name, location, processing_capacity_tons_per_day, current_load_tons, accepted_materials, operational_status, processing_efficiency_percent, contamination_rate_percent, operating_hours)
VALUES 
    ('Central Recycling Facility', 'Downtown Industrial Park', 50, 32, '["plastic", "paper", "metal", "glass", "cardboard"]'::jsonb, 'active', 85.0, 8.5, '{"monday": "6am-6pm", "tuesday": "6am-6pm", "wednesday": "6am-6pm", "thursday": "6am-6pm", "friday": "6am-6pm", "saturday": "8am-2pm"}'::jsonb),
    ('East Side Recycling Center', 'East Zone Industrial', 30, 28, '["plastic", "paper", "metal", "electronics"]'::jsonb, 'active', 78.0, 12.0, '{"monday": "7am-5pm", "tuesday": "7am-5pm", "wednesday": "7am-5pm", "thursday": "7am-5pm", "friday": "7am-5pm"}'::jsonb);

-- Insert sample complaints (10 complaints)
INSERT INTO complaints (complainant_name, complainant_phone, complaint_type, location, zone, description, priority, status, reported_date)
VALUES 
    ('John Citizen', '555-0101', 'missed_collection', 'Downtown 5th Street', 'Zone-1', 'Bins not collected for 2 days', 'high', 'in_progress', CURRENT_TIMESTAMP - INTERVAL '6 hours'),
    ('Jane Resident', '555-0102', 'overflow', 'East Zone Park', 'Zone-2', 'Public bins overflowing, attracting pests', 'urgent', 'acknowledged', CURRENT_TIMESTAMP - INTERVAL '3 hours'),
    ('Bob Business', '555-0103', 'odor', 'West Zone Restaurant District', 'Zone-3', 'Strong odor from commercial bins', 'medium', 'investigating', CURRENT_TIMESTAMP - INTERVAL '12 hours'),
    ('Alice Homeowner', '555-0104', 'damaged_bin', 'North District Elm Street', 'Zone-4', 'Residential bin lid broken', 'low', 'submitted', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('Mike Manager', '555-0105', 'illegal_dumping', 'Industrial Park Access Road', 'Industrial-A', 'Construction debris illegally dumped', 'high', 'in_progress', CURRENT_TIMESTAMP - INTERVAL '8 hours'),
    ('Sarah Store', '555-0106', 'schedule_issue', 'Downtown Shopping Center', 'Zone-1', 'Collection time conflicts with business hours', 'medium', 'resolved', CURRENT_TIMESTAMP - INTERVAL '3 days'),
    ('Tom Tenant', '555-0107', 'missed_collection', 'East Zone Apartment Complex', 'Zone-2', 'Recycling not picked up this week', 'medium', 'closed', CURRENT_TIMESTAMP - INTERVAL '5 days'),
    ('Lisa Property', '555-0108', 'spill', 'West Zone Main Avenue', 'Zone-3', 'Truck spilled waste during collection', 'high', 'resolved', CURRENT_TIMESTAMP - INTERVAL '2 days'),
    ('Robert Office', '555-0109', 'overflow', 'North District Office Park', 'Zone-4', 'Commercial bins at capacity mid-week', 'medium', 'investigating', CURRENT_TIMESTAMP - INTERVAL '1 day'),
    ('Emma Community', '555-0110', 'other', 'Downtown Community Center', 'Zone-1', 'Request for additional recycling bins', 'low', 'submitted', CURRENT_TIMESTAMP - INTERVAL '4 days');

-- Insert sanitation budget
INSERT INTO department_budgets (department, year, month, total_budget, spent, status)
VALUES 
    ('sanitation', 2026, 1, 650000, 280000, 'active');

-- Insert sanitation workers
INSERT INTO workers (department, worker_name, role, status, skills)
VALUES 
    ('sanitation', 'Carlos Martinez', 'Truck Driver', 'active', '["commercial_driving", "vehicle_maintenance"]'::jsonb),
    ('sanitation', 'David Chen', 'Collection Crew Lead', 'active', '["crew_management", "route_planning"]'::jsonb),
    ('sanitation', 'Maria Rodriguez', 'Equipment Operator', 'active', '["heavy_equipment", "compactor_operation"]'::jsonb),
    ('sanitation', 'James Wilson', 'Collection Worker', 'active', '["waste_handling", "safety"]'::jsonb),
    ('sanitation', 'Linda Johnson', 'Route Supervisor', 'active', '["logistics", "scheduling"]'::jsonb),
    ('sanitation', 'Ahmed Hassan', 'Truck Driver', 'active', '["commercial_driving", "navigation"]'::jsonb),
    ('sanitation', 'Patricia Lee', 'Recycling Specialist', 'active', '["recycling", "sorting", "education"]'::jsonb),
    ('sanitation', 'Michael Brown', 'Collection Worker', 'on_leave', '["waste_handling", "safety"]'::jsonb);


/* ========================================================= */
/* SUCCESS MESSAGE */
/* ========================================================= */

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '====================================================';
    RAISE NOTICE '✅ SANITATION SCHEMA CREATED SUCCESSFULLY!';
    RAISE NOTICE '====================================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Tables Created:';
    RAISE NOTICE '   ✓ sanitation_routes (10 sample routes)';
    RAISE NOTICE '   ✓ waste_trucks (5 sample trucks)';
    RAISE NOTICE '   ✓ collection_schedules';
    RAISE NOTICE '   ✓ waste_bins (10 sample bins)';
    RAISE NOTICE '   ✓ landfills (2 sample landfills)';
    RAISE NOTICE '   ✓ recycling_centers (2 sample centers)';
    RAISE NOTICE '   ✓ complaints (10 sample complaints)';
    RAISE NOTICE '';
    RAISE NOTICE '👥 Personnel:';
    RAISE NOTICE '   ✓ 8 sanitation workers added';
    RAISE NOTICE '';
    RAISE NOTICE '💰 Budget:';
    RAISE NOTICE '   ✓ Sanitation budget for Jan 2026 added';
    RAISE NOTICE '';
    RAISE NOTICE '🔧 Features:';
    RAISE NOTICE '   ✓ Update triggers configured';
    RAISE NOTICE '   ✓ Indexes created for performance';
    RAISE NOTICE '   ✓ Foreign key constraints';
    RAISE NOTICE '   ✓ Check constraints for data integrity';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Ready for Sanitation Agent!';
    RAISE NOTICE '====================================================';
END $$;
