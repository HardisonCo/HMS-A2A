-- Initialize database schema for the Agency Implementation System

-- Create schema
CREATE SCHEMA IF NOT EXISTS agency_system;

-- Create users table
CREATE TABLE IF NOT EXISTS agency_system.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    agency_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create agencies table
CREATE TABLE IF NOT EXISTS agency_system.agencies (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    api_endpoint VARCHAR(255),
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create federation_participants table
CREATE TABLE IF NOT EXISTS agency_system.federation_participants (
    id SERIAL PRIMARY KEY,
    federation_id VARCHAR(50) NOT NULL,
    agency_id VARCHAR(50) NOT NULL REFERENCES agency_system.agencies(id),
    api_key VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(federation_id, agency_id)
);

-- Create audit_logs table
CREATE TABLE IF NOT EXISTS agency_system.audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES agency_system.users(id),
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id VARCHAR(255),
    changes JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS agency_system.alerts (
    id SERIAL PRIMARY KEY,
    agency_id VARCHAR(50) REFERENCES agency_system.agencies(id),
    alert_type VARCHAR(100) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    data JSONB,
    location JSONB,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create stakeholders table
CREATE TABLE IF NOT EXISTS agency_system.stakeholders (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    organization VARCHAR(255),
    role VARCHAR(100),
    notification_preferences JSONB,
    alert_types JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create notification_logs table
CREATE TABLE IF NOT EXISTS agency_system.notification_logs (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES agency_system.alerts(id),
    stakeholder_id INTEGER REFERENCES agency_system.stakeholders(id),
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    delivery_status VARCHAR(50),
    error_message TEXT,
    metadata JSONB
);

-- Create federation_queries table
CREATE TABLE IF NOT EXISTS agency_system.federation_queries (
    id SERIAL PRIMARY KEY,
    federation_id VARCHAR(50) NOT NULL,
    source_agency_id VARCHAR(50) REFERENCES agency_system.agencies(id),
    query_type VARCHAR(100) NOT NULL,
    query_parameters JSONB,
    response_size INTEGER,
    execution_time_ms INTEGER,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_alerts_agency_severity ON agency_system.alerts(agency_id, severity);
CREATE INDEX IF NOT EXISTS idx_alerts_type_time ON agency_system.alerts(alert_type, created_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_action ON agency_system.audit_logs(user_id, action);
CREATE INDEX IF NOT EXISTS idx_federation_queries_source ON agency_system.federation_queries(source_agency_id, query_type);

-- Insert default agencies
INSERT INTO agency_system.agencies (id, name, description)
VALUES 
('cdc', 'Centers for Disease Control and Prevention', 'Federal agency focused on public health and disease prevention'),
('epa', 'Environmental Protection Agency', 'Federal agency focused on environmental protection'),
('fema', 'Federal Emergency Management Agency', 'Federal agency focused on disaster response and recovery')
ON CONFLICT (id) DO NOTHING;

-- Insert admin user (password is 'admin_password' - change in production!)
INSERT INTO agency_system.users (username, email, password_hash, full_name, role)
VALUES 
('admin', 'admin@example.com', '$2a$10$JKbfkdasu7JH35asd8f3iu9aJH35JKHKJHasf8as7f', 'System Administrator', 'admin')
ON CONFLICT (username) DO NOTHING;