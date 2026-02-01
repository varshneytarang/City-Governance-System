-- ============================================================
-- FIRE/EMERGENCY SERVICES DEPARTMENT SCHEMA
-- ============================================================
-- Purpose: Store fire stations, trucks, firefighters, equipment,
--          emergency calls, hydrants, and incident history
-- ============================================================

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS fire_incidents CASCADE;
DROP TABLE IF EXISTS emergency_calls CASCADE;
DROP TABLE IF EXISTS fire_hydrants CASCADE;
DROP TABLE IF EXISTS fire_equipment CASCADE;
DROP TABLE IF EXISTS firefighters CASCADE;
DROP TABLE IF EXISTS fire_trucks CASCADE;
DROP TABLE IF EXISTS fire_stations CASCADE;


-- ============================================================
-- 1. FIRE STATIONS
-- ============================================================
CREATE TABLE fire_stations (
    station_id SERIAL PRIMARY KEY,
    station_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    coverage_zones TEXT[],
    capacity INTEGER DEFAULT 20,
    current_staffing INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'operational', -- operational, maintenance, closed
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    response_time_avg_minutes INTEGER DEFAULT 8,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO fire_stations (station_name, location, coverage_zones, capacity, current_staffing, status, latitude, longitude, response_time_avg_minutes) VALUES
('Station 1 - Central', 'Downtown Center', ARRAY['Zone-1', 'Zone-2'], 25, 18, 'operational', 40.7128, -74.0060, 6),
('Station 2 - North', 'North District', ARRAY['Zone-3', 'Zone-4'], 20, 15, 'operational', 40.7580, -73.9855, 7),
('Station 3 - East', 'East Side', ARRAY['Zone-5', 'Zone-6'], 22, 16, 'operational', 40.7489, -73.9680, 8),
('Station 4 - West', 'West End', ARRAY['Zone-7', 'Zone-8'], 20, 14, 'operational', 40.7061, -74.0155, 9),
('Station 5 - South', 'South Quarter', ARRAY['Zone-9', 'Zone-10'], 18, 12, 'maintenance', 40.6892, -74.0445, 12);


-- ============================================================
-- 2. FIRE TRUCKS
-- ============================================================
CREATE TABLE fire_trucks (
    truck_id SERIAL PRIMARY KEY,
    station_id INTEGER REFERENCES fire_stations(station_id),
    truck_type VARCHAR(50) NOT NULL, -- engine, ladder, rescue, hazmat, tanker
    truck_number VARCHAR(20) NOT NULL,
    status VARCHAR(50) DEFAULT 'available', -- available, dispatched, maintenance, out_of_service
    fuel_percent INTEGER DEFAULT 100,
    water_capacity_gallons INTEGER DEFAULT 500,
    current_water_level_gallons INTEGER DEFAULT 500,
    last_maintenance DATE,
    next_maintenance_due DATE,
    equipment_check_status VARCHAR(50) DEFAULT 'passed', -- passed, needs_check, failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO fire_trucks (station_id, truck_type, truck_number, status, fuel_percent, water_capacity_gallons, current_water_level_gallons, last_maintenance, next_maintenance_due, equipment_check_status) VALUES
(1, 'engine', 'E-101', 'available', 95, 500, 500, '2026-01-15', '2026-02-15', 'passed'),
(1, 'ladder', 'L-101', 'available', 90, 300, 300, '2026-01-10', '2026-02-10', 'passed'),
(2, 'engine', 'E-201', 'available', 85, 500, 450, '2026-01-20', '2026-02-20', 'passed'),
(2, 'rescue', 'R-201', 'dispatched', 75, 200, 200, '2026-01-18', '2026-02-18', 'passed'),
(3, 'engine', 'E-301', 'available', 92, 500, 500, '2026-01-12', '2026-02-12', 'passed'),
(3, 'hazmat', 'H-301', 'available', 88, 100, 100, '2026-01-25', '2026-02-25', 'needs_check'),
(4, 'engine', 'E-401', 'available', 80, 500, 400, '2026-01-22', '2026-02-22', 'passed'),
(4, 'tanker', 'T-401', 'available', 70, 2000, 2000, '2026-01-08', '2026-02-08', 'passed'),
(5, 'engine', 'E-501', 'maintenance', 40, 500, 0, '2025-12-20', '2026-01-20', 'failed');


-- ============================================================
-- 3. FIREFIGHTERS
-- ============================================================
CREATE TABLE firefighters (
    firefighter_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    station_id INTEGER REFERENCES fire_stations(station_id),
    rank VARCHAR(50) NOT NULL, -- firefighter, driver, captain, battalion_chief
    status VARCHAR(50) DEFAULT 'on_duty', -- on_duty, off_duty, on_call, on_leave, dispatched
    certifications TEXT[], -- emt, hazmat, rescue, driver, incident_command
    years_of_service INTEGER DEFAULT 0,
    shift VARCHAR(20) DEFAULT 'A', -- A, B, C
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO firefighters (name, station_id, rank, status, certifications, years_of_service, shift) VALUES
('John Smith', 1, 'captain', 'on_duty', ARRAY['emt', 'incident_command'], 12, 'A'),
('Sarah Johnson', 1, 'firefighter', 'on_duty', ARRAY['emt'], 5, 'A'),
('Mike Davis', 1, 'driver', 'on_duty', ARRAY['driver', 'emt'], 8, 'A'),
('Emily White', 2, 'captain', 'on_duty', ARRAY['emt', 'rescue'], 10, 'A'),
('Chris Brown', 2, 'firefighter', 'dispatched', ARRAY['hazmat', 'emt'], 6, 'A'),
('Lisa Anderson', 3, 'firefighter', 'on_duty', ARRAY['emt'], 4, 'A'),
('David Wilson', 3, 'driver', 'on_duty', ARRAY['driver'], 7, 'A'),
('Jennifer Taylor', 4, 'battalion_chief', 'on_duty', ARRAY['emt', 'incident_command', 'hazmat'], 15, 'A'),
('Robert Martinez', 4, 'firefighter', 'on_duty', ARRAY['emt', 'rescue'], 9, 'A'),
('Mary Garcia', 5, 'firefighter', 'off_duty', ARRAY['emt'], 3, 'B');


-- ============================================================
-- 4. FIRE EQUIPMENT
-- ============================================================
CREATE TABLE fire_equipment (
    equipment_id SERIAL PRIMARY KEY,
    station_id INTEGER REFERENCES fire_stations(station_id),
    equipment_type VARCHAR(100) NOT NULL, -- scba, hose, nozzle, ladder, thermal_camera, jaws_of_life
    quantity INTEGER DEFAULT 1,
    condition VARCHAR(50) DEFAULT 'good', -- excellent, good, fair, poor, needs_replacement
    last_inspected DATE,
    next_inspection_due DATE,
    status VARCHAR(50) DEFAULT 'available', -- available, in_use, maintenance, out_of_service
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO fire_equipment (station_id, equipment_type, quantity, condition, last_inspected, next_inspection_due, status) VALUES
(1, 'scba', 20, 'good', '2026-01-15', '2026-07-15', 'available'),
(1, 'hose', 30, 'good', '2026-01-10', '2026-07-10', 'available'),
(1, 'thermal_camera', 2, 'excellent', '2026-01-05', '2027-01-05', 'available'),
(2, 'scba', 15, 'good', '2026-01-12', '2026-07-12', 'available'),
(2, 'jaws_of_life', 2, 'good', '2026-01-08', '2026-07-08', 'available'),
(3, 'scba', 18, 'fair', '2025-12-20', '2026-06-20', 'available'),
(3, 'ladder', 5, 'good', '2026-01-18', '2026-07-18', 'available'),
(4, 'scba', 16, 'good', '2026-01-14', '2026-07-14', 'available'),
(4, 'hose', 25, 'good', '2026-01-11', '2026-07-11', 'available'),
(5, 'scba', 12, 'poor', '2025-11-15', '2026-05-15', 'maintenance');


-- ============================================================
-- 5. EMERGENCY CALLS
-- ============================================================
CREATE TABLE emergency_calls (
    call_id SERIAL PRIMARY KEY,
    call_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(200) NOT NULL,
    call_type VARCHAR(100) NOT NULL, -- structure_fire, vehicle_fire, medical, rescue, hazmat, false_alarm
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, critical
    status VARCHAR(50) DEFAULT 'received', -- received, dispatched, en_route, on_scene, resolved, cancelled
    assigned_station_id INTEGER REFERENCES fire_stations(station_id),
    assigned_trucks TEXT[], -- truck IDs dispatched
    response_time_minutes INTEGER,
    resolution_time_minutes INTEGER,
    casualties INTEGER DEFAULT 0,
    property_damage_estimate DECIMAL(12, 2),
    notes TEXT
);

-- Sample data
INSERT INTO emergency_calls (call_timestamp, location, call_type, priority, status, assigned_station_id, assigned_trucks, response_time_minutes, resolution_time_minutes, casualties, property_damage_estimate, notes) VALUES
('2026-01-29 08:30:00', 'Zone-1, Main Street', 'structure_fire', 'critical', 'resolved', 1, ARRAY['E-101', 'L-101'], 5, 120, 0, 50000.00, 'Residential building, electrical fire'),
('2026-01-29 14:15:00', 'Zone-3, Highway 101', 'vehicle_fire', 'high', 'resolved', 2, ARRAY['E-201'], 6, 45, 1, 15000.00, 'Car fire after collision'),
('2026-01-30 02:00:00', 'Zone-5, Industrial Park', 'hazmat', 'critical', 'on_scene', 3, ARRAY['E-301', 'H-301'], 8, NULL, 0, NULL, 'Chemical spill, ongoing'),
('2026-01-28 19:45:00', 'Zone-7, Shopping Mall', 'false_alarm', 'low', 'resolved', 4, ARRAY['E-401'], 7, 20, 0, 0.00, 'Smoke detector malfunction'),
('2026-01-27 11:20:00', 'Zone-2, School Building', 'medical', 'high', 'resolved', 1, ARRAY['R-201'], 4, 35, 0, 0.00, 'Cardiac arrest, patient stabilized'),
('2026-01-26 16:30:00', 'Zone-4, Apartment Complex', 'structure_fire', 'critical', 'resolved', 2, ARRAY['E-201', 'R-201'], 6, 180, 2, 120000.00, 'Kitchen fire spread to multiple units'),
('2026-01-25 09:00:00', 'Zone-6, Park Area', 'rescue', 'medium', 'resolved', 3, ARRAY['R-301'], 10, 60, 0, 0.00, 'Person trapped in elevator'),
('2026-01-24 22:15:00', 'Zone-8, Restaurant Row', 'structure_fire', 'high', 'resolved', 4, ARRAY['E-401'], 8, 90, 0, 30000.00, 'Grease fire contained to kitchen'),
('2026-01-23 07:45:00', 'Zone-1, Office Tower', 'medical', 'medium', 'resolved', 1, ARRAY['E-101'], 5, 25, 0, 0.00, 'Fall injury'),
('2026-01-22 13:30:00', 'Zone-9, Warehouse District', 'hazmat', 'high', 'resolved', 5, ARRAY['E-501'], 15, 240, 0, 5000.00, 'Gas leak, area evacuated');


-- ============================================================
-- 6. FIRE HYDRANTS
-- ============================================================
CREATE TABLE fire_hydrants (
    hydrant_id SERIAL PRIMARY KEY,
    location VARCHAR(200) NOT NULL,
    zone VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'operational', -- operational, maintenance, out_of_service
    flow_rate_gpm INTEGER DEFAULT 1000, -- gallons per minute
    last_inspected DATE,
    next_inspection_due DATE,
    pressure_psi INTEGER DEFAULT 60,
    condition VARCHAR(50) DEFAULT 'good', -- excellent, good, fair, poor
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO fire_hydrants (location, zone, status, flow_rate_gpm, last_inspected, next_inspection_due, pressure_psi, condition, latitude, longitude) VALUES
('Main St & 1st Ave', 'Zone-1', 'operational', 1500, '2026-01-10', '2026-07-10', 65, 'excellent', 40.7128, -74.0060),
('Main St & 5th Ave', 'Zone-1', 'operational', 1200, '2026-01-12', '2026-07-12', 60, 'good', 40.7138, -74.0050),
('North Blvd & Park Rd', 'Zone-3', 'operational', 1000, '2026-01-15', '2026-07-15', 58, 'good', 40.7580, -73.9855),
('North Blvd & Lake St', 'Zone-4', 'operational', 1100, '2026-01-08', '2026-07-08', 62, 'good', 40.7590, -73.9845),
('East Side Plaza', 'Zone-5', 'operational', 900, '2026-01-18', '2026-07-18', 55, 'fair', 40.7489, -73.9680),
('East Industrial Park', 'Zone-6', 'maintenance', 800, '2025-12-20', '2026-06-20', 45, 'poor', 40.7499, -73.9670),
('West End Market', 'Zone-7', 'operational', 1300, '2026-01-20', '2026-07-20', 68, 'excellent', 40.7061, -74.0155),
('West River Road', 'Zone-8', 'operational', 1000, '2026-01-14', '2026-07-14', 60, 'good', 40.7051, -74.0165),
('South Quarter Center', 'Zone-9', 'operational', 950, '2026-01-16', '2026-07-16', 57, 'good', 40.6892, -74.0445),
('South Residential Area', 'Zone-10', 'out_of_service', 0, '2025-11-10', '2026-05-10', 0, 'poor', 40.6882, -74.0455);


-- ============================================================
-- 7. FIRE INCIDENTS (Historical Data)
-- ============================================================
CREATE TABLE fire_incidents (
    incident_id SERIAL PRIMARY KEY,
    call_id INTEGER REFERENCES emergency_calls(call_id),
    incident_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location VARCHAR(200) NOT NULL,
    incident_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) DEFAULT 'minor', -- minor, moderate, major, catastrophic
    cause VARCHAR(200),
    casualties INTEGER DEFAULT 0,
    injuries INTEGER DEFAULT 0,
    property_damage_estimate DECIMAL(12, 2),
    response_units TEXT[],
    duration_minutes INTEGER,
    investigation_status VARCHAR(50) DEFAULT 'pending', -- pending, ongoing, closed
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO fire_incidents (call_id, incident_date, location, incident_type, severity, cause, casualties, injuries, property_damage_estimate, response_units, duration_minutes, investigation_status, notes) VALUES
(1, '2026-01-29 08:30:00', 'Zone-1, Main Street', 'structure_fire', 'moderate', 'Electrical short circuit', 0, 2, 50000.00, ARRAY['E-101', 'L-101'], 120, 'closed', 'Building saved, minor injuries'),
(2, '2026-01-29 14:15:00', 'Zone-3, Highway 101', 'vehicle_fire', 'moderate', 'Post-collision fuel leak', 1, 3, 15000.00, ARRAY['E-201'], 45, 'ongoing', 'Investigation in progress'),
(3, '2026-01-30 02:00:00', 'Zone-5, Industrial Park', 'hazmat', 'major', 'Chemical storage failure', 0, 0, NULL, ARRAY['E-301', 'H-301'], NULL, 'ongoing', 'Containment ongoing'),
(6, '2026-01-26 16:30:00', 'Zone-4, Apartment Complex', 'structure_fire', 'major', 'Unattended cooking', 2, 5, 120000.00, ARRAY['E-201', 'R-201'], 180, 'closed', 'Multiple units destroyed'),
(8, '2026-01-24 22:15:00', 'Zone-8, Restaurant Row', 'structure_fire', 'moderate', 'Grease fire', 0, 1, 30000.00, ARRAY['E-401'], 90, 'closed', 'Kitchen only, contained quickly'),
(10, '2026-01-22 13:30:00', 'Zone-9, Warehouse District', 'hazmat', 'moderate', 'Equipment malfunction', 0, 0, 5000.00, ARRAY['E-501'], 240, 'closed', 'Area evacuated, no contamination');


-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_fire_stations_status ON fire_stations(status);
CREATE INDEX idx_fire_trucks_station ON fire_trucks(station_id);
CREATE INDEX idx_fire_trucks_status ON fire_trucks(status);
CREATE INDEX idx_firefighters_station ON firefighters(station_id);
CREATE INDEX idx_firefighters_status ON firefighters(status);
CREATE INDEX idx_emergency_calls_status ON emergency_calls(status);
CREATE INDEX idx_emergency_calls_timestamp ON emergency_calls(call_timestamp);
CREATE INDEX idx_fire_hydrants_zone ON fire_hydrants(zone);
CREATE INDEX idx_fire_hydrants_status ON fire_hydrants(status);
CREATE INDEX idx_fire_incidents_date ON fire_incidents(incident_date);


-- ============================================================
-- SUMMARY
-- ============================================================
-- 7 Tables:
-- - fire_stations: 5 stations across 10 zones
-- - fire_trucks: 9 trucks (engines, ladders, rescue, hazmat, tankers)
-- - firefighters: 10 firefighters with various ranks and certifications
-- - fire_equipment: 10 equipment items (SCBA, hoses, thermal cameras, etc.)
-- - emergency_calls: 10 recent emergency calls
-- - fire_hydrants: 10 hydrants across zones
-- - fire_incidents: 6 historical incidents
-- ============================================================
