-- Health schema additions for Health Department Agent

CREATE TABLE disease_incidents (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_type VARCHAR(100) NOT NULL,
    location TEXT NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('low','medium','high','critical')),
    reported_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vaccination_campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    location TEXT,
    start_date DATE,
    end_date DATE,
    target_groups JSONB,
    coverage_percent NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sanitation_inspections (
    inspection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location TEXT,
    facility VARCHAR(255),
    inspection_date TIMESTAMP,
    outcome VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vulnerable_populations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location TEXT,
    population_group VARCHAR(255),
    population_count INTEGER,
    vulnerability_index NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE health_facilities (
    facility_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    location TEXT,
    capacity INTEGER,
    services JSONB,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
