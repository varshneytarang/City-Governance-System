/* =========================================================
   WATER & FIRE AGENT TABLES MIGRATION
   Run this in pgAdmin after the core schema is set up
   Database: city_mas
   ========================================================= */


/* ---------- WATER SUPPLY & DRAINAGE AGENT ---------- */

-- Water Infrastructure (Pipelines, Drainage Systems)
CREATE TABLE IF NOT EXISTS water_infrastructure (
    pipeline_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    location TEXT NOT NULL,
    zone TEXT NOT NULL,
    
    -- Geospatial coordinates (can upgrade to PostGIS later)
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    
    -- Pipeline details
    pipeline_type TEXT NOT NULL CHECK (pipeline_type IN ('supply', 'drainage', 'sewage')),
    diameter_mm INT,
    material TEXT,
    
    -- Condition & capacity
    condition TEXT CHECK (condition IN ('excellent', 'good', 'fair', 'poor', 'critical')),
    capacity_liters_per_min INT,
    
    -- Maintenance tracking
    installation_date DATE,
    last_maintenance DATE,
    next_maintenance_due DATE,
    
    -- Risk management
    risk_level TEXT CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    operational_status TEXT CHECK (operational_status IN ('active', 'inactive', 'under_repair')),
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Water Incidents (Leakages, Blockages, etc.)
CREATE TABLE IF NOT EXISTS water_incidents (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    incident_type TEXT NOT NULL CHECK (incident_type IN ('leakage', 'blockage', 'contamination', 'pressure_drop')),
    location TEXT NOT NULL,
    
    pipeline_id UUID REFERENCES water_infrastructure(pipeline_id) ON DELETE SET NULL,
    
    -- Severity & priority
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    
    -- Reporting
    reported_by TEXT,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    description TEXT,
    estimated_impact TEXT,
    
    -- Response tracking
    status TEXT CHECK (status IN ('reported', 'assigned', 'in_progress', 'resolved', 'closed')),
    assigned_crew_id UUID,
    
    response_time_minutes INT,
    resolution_time_minutes INT,
    
    action_taken TEXT,
    cost NUMERIC,
    
    -- Timestamps
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Water Resources (Reservoirs, Pumps, Treatment Plants)
CREATE TABLE IF NOT EXISTS water_resources (
    resource_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    resource_type TEXT NOT NULL CHECK (resource_type IN ('reservoir', 'pump', 'treatment_plant', 'storage_tank')),
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    
    -- Capacity tracking
    capacity_liters INT,
    current_level_liters INT,
    level_percentage NUMERIC(5, 2),
    
    operational_status TEXT CHECK (operational_status IN ('active', 'inactive', 'maintenance', 'emergency')),
    
    last_reading TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* ---------- FIRE & EMERGENCY SERVICES AGENT ---------- */

-- Fire Stations
CREATE TABLE IF NOT EXISTS fire_stations (
    station_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    zone TEXT NOT NULL,
    
    -- Geospatial
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    
    -- Resources
    total_vehicles INT DEFAULT 0,
    available_vehicles INT DEFAULT 0,
    
    total_crew INT DEFAULT 0,
    available_crew INT DEFAULT 0,
    
    coverage_radius_km NUMERIC(5, 2),
    
    operational_status TEXT CHECK (operational_status IN ('active', 'limited', 'inactive')),
    
    -- Equipment inventory (JSON)
    equipment_list JSONB,
    
    contact_number TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emergency Incidents
CREATE TABLE IF NOT EXISTS emergency_incidents (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    incident_type TEXT NOT NULL CHECK (incident_type IN ('fire', 'flood', 'accident', 'medical', 'rescue', 'hazmat')),
    location TEXT NOT NULL,
    
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    
    -- Severity & priority
    severity TEXT CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    priority TEXT CHECK (priority IN ('routine', 'urgent', 'emergency', 'disaster')),
    
    -- Reporting
    reported_by TEXT,
    reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    description TEXT,
    building_info JSONB,
    
    -- Response tracking
    status TEXT CHECK (status IN ('reported', 'dispatched', 'on_scene', 'active', 'contained', 'resolved', 'closed')),
    
    responding_station_id UUID REFERENCES fire_stations(station_id) ON DELETE SET NULL,
    units_dispatched INT DEFAULT 0,
    personnel_count INT DEFAULT 0,
    
    -- Timeline
    dispatch_time TIMESTAMP,
    arrival_time TIMESTAMP,
    contained_time TIMESTAMP,
    resolved_time TIMESTAMP,
    closed_time TIMESTAMP,
    
    -- Metrics
    response_time_minutes INT,
    total_duration_minutes INT,
    
    casualties INT DEFAULT 0,
    injuries INT DEFAULT 0,
    property_damage_estimate NUMERIC,
    
    -- Actions
    action_taken TEXT,
    resources_used JSONB,
    
    -- Inter-agent coordination
    coordination_required JSONB,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* ---------- INTER-AGENT MESSAGING ---------- */

-- Agent-to-Agent Communication
CREATE TABLE IF NOT EXISTS agent_messages (
    message_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    
    message_type TEXT NOT NULL CHECK (message_type IN ('alert', 'request', 'response', 'notification')),
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    
    subject TEXT,
    payload JSONB NOT NULL,
    
    status TEXT CHECK (status IN ('pending', 'delivered', 'acknowledged', 'processed', 'failed')),
    
    -- Timestamps
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivered_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    
    -- Response tracking
    response_required BOOLEAN DEFAULT FALSE,
    response_message_id UUID REFERENCES agent_messages(message_id) ON DELETE SET NULL,
    
    -- Error handling
    retry_count INT DEFAULT 0,
    error_message TEXT,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* ---------- INDEXES FOR PERFORMANCE ---------- */

-- Water infrastructure indexes
CREATE INDEX IF NOT EXISTS idx_water_infra_location ON water_infrastructure(location);
CREATE INDEX IF NOT EXISTS idx_water_infra_risk ON water_infrastructure(risk_level);
CREATE INDEX IF NOT EXISTS idx_water_infra_status ON water_infrastructure(operational_status);

-- Water incident indexes
CREATE INDEX IF NOT EXISTS idx_water_incident_status ON water_incidents(status);
CREATE INDEX IF NOT EXISTS idx_water_incident_severity ON water_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_water_incident_type ON water_incidents(incident_type);

-- Water resource indexes
CREATE INDEX IF NOT EXISTS idx_water_resource_type ON water_resources(resource_type);
CREATE INDEX IF NOT EXISTS idx_water_resource_status ON water_resources(operational_status);

-- Fire station indexes
CREATE INDEX IF NOT EXISTS idx_fire_station_zone ON fire_stations(zone);
CREATE INDEX IF NOT EXISTS idx_fire_station_status ON fire_stations(operational_status);

-- Emergency incident indexes
CREATE INDEX IF NOT EXISTS idx_emergency_incident_type ON emergency_incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_emergency_incident_status ON emergency_incidents(status);
CREATE INDEX IF NOT EXISTS idx_emergency_incident_severity ON emergency_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_emergency_incident_reported ON emergency_incidents(reported_at);

-- Agent message indexes
CREATE INDEX IF NOT EXISTS idx_agent_message_from ON agent_messages(from_agent);
CREATE INDEX IF NOT EXISTS idx_agent_message_to ON agent_messages(to_agent);
CREATE INDEX IF NOT EXISTS idx_agent_message_status ON agent_messages(status);
CREATE INDEX IF NOT EXISTS idx_agent_message_priority ON agent_messages(priority);
CREATE INDEX IF NOT EXISTS idx_agent_message_sent ON agent_messages(sent_at);


/* ---------- SAMPLE DATA FOR TESTING ---------- */

-- Insert sample fire stations
INSERT INTO fire_stations (name, location, zone, latitude, longitude, total_vehicles, available_vehicles, total_crew, available_crew, coverage_radius_km, operational_status, equipment_list)
VALUES 
    ('Central Fire Station', 'Downtown Main St', 'Zone-1', 28.6139, 77.2090, 5, 4, 20, 18, 5.0, 'active', '{"pumpers": 2, "ladder_trucks": 1, "ambulances": 2}'::jsonb),
    ('East Fire Station', 'East Side Ave', 'Zone-2', 28.6289, 77.2195, 4, 3, 15, 12, 4.5, 'active', '{"pumpers": 2, "ambulances": 2}'::jsonb),
    ('North Fire Station', 'North Highway', 'Zone-3', 28.6500, 77.2100, 3, 3, 12, 10, 4.0, 'active', '{"pumpers": 1, "ladder_trucks": 1, "ambulances": 1}'::jsonb);

-- Insert sample water resources
INSERT INTO water_resources (resource_type, name, location, capacity_liters, current_level_liters, level_percentage, operational_status)
VALUES 
    ('reservoir', 'Main City Reservoir', 'North District', 50000000, 42000000, 84.00, 'active'),
    ('reservoir', 'East Reservoir', 'East District', 30000000, 21000000, 70.00, 'active'),
    ('treatment_plant', 'Central Treatment Plant', 'Downtown', 10000000, NULL, NULL, 'active'),
    ('pump', 'Zone-1 Pump Station', 'Zone-1', NULL, NULL, NULL, 'active');

-- Insert sample water infrastructure
INSERT INTO water_infrastructure (location, zone, latitude, longitude, pipeline_type, diameter_mm, material, condition, capacity_liters_per_min, risk_level, operational_status, installation_date, last_maintenance)
VALUES 
    ('Main St - Block A', 'Zone-1', 28.6139, 77.2090, 'supply', 300, 'cast_iron', 'fair', 5000, 'medium', 'active', '2010-05-15', '2025-06-10'),
    ('East Ave - Block B', 'Zone-2', 28.6289, 77.2195, 'supply', 250, 'PVC', 'good', 4000, 'low', 'active', '2018-03-20', '2025-11-05'),
    ('Downtown Drainage', 'Zone-1', 28.6150, 77.2100, 'drainage', 400, 'concrete', 'poor', 8000, 'high', 'active', '2005-08-10', '2024-12-15');


/* ---------- SUCCESS MESSAGE ---------- */

DO $$
BEGIN
    RAISE NOTICE '✅ Water & Fire Agent tables created successfully!';
    RAISE NOTICE '✅ Sample data inserted for testing';
    RAISE NOTICE '📊 Tables created:';
    RAISE NOTICE '   - water_infrastructure';
    RAISE NOTICE '   - water_incidents';
    RAISE NOTICE '   - water_resources';
    RAISE NOTICE '   - fire_stations';
    RAISE NOTICE '   - emergency_incidents';
    RAISE NOTICE '   - agent_messages';
END $$;
