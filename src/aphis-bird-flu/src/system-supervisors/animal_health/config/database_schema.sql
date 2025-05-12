-- APHIS Bird Flu Tracking System Database Schema
-- This schema defines the PostgreSQL database structure for storing
-- avian influenza surveillance data and related entities.

-- Enable PostGIS extension for spatial data support
CREATE EXTENSION IF NOT EXISTS postgis;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE site_type AS ENUM (
    'commercial_poultry',
    'backyard_poultry',
    'live_bird_market',
    'wild_bird_habitat',
    'waterfowl_rest_area',
    'poultry_exhibition',
    'rendering_plant',
    'feed_mill',
    'processing_plant',
    'hatchery',
    'other'
);

CREATE TYPE site_status AS ENUM (
    'active',
    'inactive',
    'quarantined',
    'infected',
    'cleaned_disinfected',
    'unknown'
);

CREATE TYPE risk_level AS ENUM (
    'negligible',
    'low',
    'medium',
    'high',
    'very_high',
    'unknown'
);

CREATE TYPE case_status AS ENUM (
    'suspected',
    'confirmed',
    'ruled_out',
    'recovered',
    'deceased',
    'unknown'
);

CREATE TYPE detection_method AS ENUM (
    'pcr_test',
    'rapid_test',
    'serology',
    'clinical_signs',
    'necropsy',
    'routine_surveillance',
    'other'
);

CREATE TYPE virus_subtype AS ENUM (
    'h5n1',
    'h5n2',
    'h5n8',
    'h7n3',
    'h7n9',
    'h9n2',
    'other',
    'unknown'
);

CREATE TYPE pathogenicity_level AS ENUM (
    'highly_pathogenic',
    'low_pathogenic',
    'unknown'
);

CREATE TYPE species_category AS ENUM (
    'domestic_poultry',
    'domestic_waterfowl',
    'wild_waterfowl',
    'wild_gallinaceous',
    'wild_other',
    'captive_wild',
    'other'
);

CREATE TYPE allocation_strategy AS ENUM (
    'equal_allocation',
    'risk_based',
    'response_adaptive',
    'optimized',
    'manual'
);

-- Create base tables

-- Regions table (counties, states, etc.)
CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    region_type VARCHAR(50) NOT NULL,
    boundary GEOMETRY(POLYGON, 4326) NOT NULL,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Surveillance sites
CREATE TABLE surveillance_sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL,
    site_type site_type NOT NULL,
    jurisdiction VARCHAR(255) NOT NULL,
    population INTEGER,
    status site_status NOT NULL DEFAULT 'active',
    risk_level risk_level NOT NULL DEFAULT 'unknown',
    risk_factors JSONB DEFAULT '{}',
    contact_info JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on surveillance site location
CREATE INDEX idx_surveillance_sites_location ON surveillance_sites USING GIST(location);

-- Bird flu cases
CREATE TABLE bird_flu_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location GEOMETRY(POINT, 4326) NOT NULL,
    detection_date DATE NOT NULL,
    species VARCHAR(255) NOT NULL,
    species_category species_category NOT NULL,
    status case_status NOT NULL DEFAULT 'suspected',
    subtype virus_subtype NOT NULL DEFAULT 'unknown',
    pathogenicity pathogenicity_level NOT NULL DEFAULT 'unknown',
    detection_method detection_method NOT NULL DEFAULT 'routine_surveillance',
    sample_id UUID,
    genetic_sequence_id UUID,
    reported_by VARCHAR(255),
    flock_size INTEGER,
    mortality_count INTEGER,
    site_id UUID REFERENCES surveillance_sites(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on bird flu cases
CREATE INDEX idx_bird_flu_cases_location ON bird_flu_cases USING GIST(location);
CREATE INDEX idx_bird_flu_cases_detection_date ON bird_flu_cases(detection_date);
CREATE INDEX idx_bird_flu_cases_subtype ON bird_flu_cases(subtype);
CREATE INDEX idx_bird_flu_cases_status ON bird_flu_cases(status);
CREATE INDEX idx_bird_flu_cases_site_id ON bird_flu_cases(site_id);

-- Related cases table (many-to-many relationship)
CREATE TABLE related_cases (
    case_id UUID REFERENCES bird_flu_cases(id) ON DELETE CASCADE,
    related_case_id UUID REFERENCES bird_flu_cases(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) DEFAULT 'related',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (case_id, related_case_id)
);

-- Laboratory samples
CREATE TABLE laboratory_samples (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES bird_flu_cases(id) ON DELETE CASCADE,
    collection_date DATE NOT NULL,
    sample_type VARCHAR(255) NOT NULL,
    collected_by VARCHAR(255) NOT NULL,
    lab_id VARCHAR(255),
    received_date DATE,
    testing_status VARCHAR(50) DEFAULT 'pending',
    results JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_laboratory_samples_case_id ON laboratory_samples(case_id);
CREATE INDEX idx_laboratory_samples_collection_date ON laboratory_samples(collection_date);

-- Genetic sequences
CREATE TABLE genetic_sequences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_id UUID REFERENCES bird_flu_cases(id) ON DELETE CASCADE,
    sample_id UUID REFERENCES laboratory_samples(id) ON DELETE CASCADE,
    sequence_data TEXT NOT NULL,
    sequencing_method VARCHAR(255) NOT NULL,
    sequencing_date DATE NOT NULL,
    gene_segments JSONB NOT NULL,
    sequence_quality FLOAT NOT NULL,
    external_database_ids JSONB DEFAULT '{}',
    analysis_results JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_genetic_sequences_case_id ON genetic_sequences(case_id);
CREATE INDEX idx_genetic_sequences_sample_id ON genetic_sequences(sample_id);

-- Adaptive sampling plans
CREATE TABLE adaptive_sampling_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    region_id UUID REFERENCES regions(id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    allocation_strategy allocation_strategy NOT NULL DEFAULT 'risk_based',
    current_stage INTEGER NOT NULL DEFAULT 0,
    max_stages INTEGER NOT NULL DEFAULT 3,
    total_resources JSONB DEFAULT '{}',
    stage_results JSONB DEFAULT '[]',
    adaptation_rules JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_adaptive_sampling_plans_region_id ON adaptive_sampling_plans(region_id);
CREATE INDEX idx_adaptive_sampling_plans_dates ON adaptive_sampling_plans(start_date, end_date);

-- Sampling plan sites (many-to-many relationship)
CREATE TABLE sampling_plan_sites (
    plan_id UUID REFERENCES adaptive_sampling_plans(id) ON DELETE CASCADE,
    site_id UUID REFERENCES surveillance_sites(id) ON DELETE CASCADE,
    allocation_proportion FLOAT DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (plan_id, site_id)
);

-- Surveillance events
CREATE TABLE surveillance_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID NOT NULL REFERENCES surveillance_sites(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES adaptive_sampling_plans(id) ON DELETE SET NULL,
    event_date DATE NOT NULL,
    collector VARCHAR(255) NOT NULL,
    samples_collected INTEGER NOT NULL DEFAULT 0,
    sample_types JSONB NOT NULL,
    target_species JSONB NOT NULL,
    weather_conditions JSONB DEFAULT '{}',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_surveillance_events_site_id ON surveillance_events(site_id);
CREATE INDEX idx_surveillance_events_plan_id ON surveillance_events(plan_id);
CREATE INDEX idx_surveillance_events_event_date ON surveillance_events(event_date);

-- Event samples (many-to-many relationship)
CREATE TABLE event_samples (
    event_id UUID REFERENCES surveillance_events(id) ON DELETE CASCADE,
    sample_id UUID REFERENCES laboratory_samples(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (event_id, sample_id)
);

-- Forecasts
CREATE TABLE forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forecast_date DATE NOT NULL,
    days_ahead INTEGER NOT NULL DEFAULT 7,
    model_info JSONB NOT NULL,
    risk_by_region JSONB NOT NULL,
    predicted_case_count JSONB NOT NULL,
    confidence_intervals JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecasts_forecast_date ON forecasts(forecast_date);

-- Notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    content JSONB NOT NULL,
    recipients JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    source_id UUID,  -- Can be a case ID, forecast ID, etc.
    source_type VARCHAR(50),
    delivery_stats JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_notifications_alert_type ON notifications(alert_type);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer',
    organization VARCHAR(255),
    notification_preferences JSONB DEFAULT '{}',
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(255) NOT NULL,
    entity_id UUID,
    details JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);

-- Create timestamp update trigger function
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply timestamp trigger to all tables with updated_at column
DO $$
DECLARE
    tables CURSOR FOR
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename NOT IN ('forecasts', 'audit_log', 'related_cases', 'event_samples');
BEGIN
    FOR table_record IN tables LOOP
        EXECUTE format('
            CREATE TRIGGER update_%s_timestamp
            BEFORE UPDATE ON %s
            FOR EACH ROW
            EXECUTE FUNCTION update_timestamp();',
            table_record.tablename, table_record.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create spatial views for GIS integration

-- View for case spatial distribution
CREATE OR REPLACE VIEW case_spatial_distribution AS
SELECT 
    c.id,
    c.location,
    c.detection_date,
    c.species,
    c.species_category,
    c.status,
    c.subtype,
    c.pathogenicity,
    c.detection_method,
    CASE 
        WHEN c.status = 'confirmed' THEN 1.0
        WHEN c.status = 'suspected' THEN 0.5
        ELSE 0.0
    END AS case_weight,
    s.name AS site_name,
    s.site_type,
    s.jurisdiction
FROM 
    bird_flu_cases c
LEFT JOIN 
    surveillance_sites s ON c.site_id = s.id
WHERE 
    c.status IN ('confirmed', 'suspected');

-- View for active surveillance
CREATE OR REPLACE VIEW active_surveillance AS
SELECT 
    s.id,
    s.name,
    s.location,
    s.site_type,
    s.jurisdiction,
    s.risk_level,
    COUNT(e.id) AS event_count,
    SUM(e.samples_collected) AS total_samples,
    MAX(e.event_date) AS last_event_date
FROM 
    surveillance_sites s
LEFT JOIN 
    surveillance_events e ON s.id = e.site_id
WHERE 
    s.status = 'active'
GROUP BY 
    s.id, s.name, s.location, s.site_type, s.jurisdiction, s.risk_level;

-- View for risk map by region
CREATE OR REPLACE VIEW region_risk_map AS
SELECT 
    r.id,
    r.name,
    r.region_type,
    r.boundary,
    COALESCE(
        (SELECT MAX(f.risk_by_region::jsonb->r.id::text)::FLOAT 
         FROM forecasts f 
         WHERE f.forecast_date = CURRENT_DATE
         ORDER BY f.created_at DESC 
         LIMIT 1),
        0.0
    ) AS current_risk,
    COUNT(c.id) AS case_count,
    COUNT(c.id) FILTER (WHERE c.detection_date >= CURRENT_DATE - INTERVAL '14 days') AS recent_cases
FROM 
    regions r
LEFT JOIN 
    bird_flu_cases c ON ST_Contains(r.boundary, c.location)
GROUP BY 
    r.id, r.name, r.region_type, r.boundary;

-- Add comments to tables and columns for documentation
COMMENT ON TABLE bird_flu_cases IS 'Confirmed or suspected cases of avian influenza';
COMMENT ON TABLE surveillance_sites IS 'Locations where surveillance is being conducted';
COMMENT ON TABLE adaptive_sampling_plans IS 'Plans for adapting sampling based on real-time data';
COMMENT ON TABLE laboratory_samples IS 'Samples collected for laboratory testing';
COMMENT ON TABLE genetic_sequences IS 'Genetic sequences from avian influenza viruses';
COMMENT ON TABLE surveillance_events IS 'Surveillance sampling events at particular sites';
COMMENT ON TABLE forecasts IS 'Predictive forecasts for avian influenza spread';
COMMENT ON TABLE notifications IS 'System notifications and alerts';
COMMENT ON TABLE users IS 'System users and their roles';
COMMENT ON TABLE audit_log IS 'Audit trail of user actions and system events';