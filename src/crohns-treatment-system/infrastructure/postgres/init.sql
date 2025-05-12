-- Initialize the database for the Crohn's Disease Treatment System

-- Create required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS patient;
CREATE SCHEMA IF NOT EXISTS trial;
CREATE SCHEMA IF NOT EXISTS research;
CREATE SCHEMA IF NOT EXISTS auth;

-- Create patient tables
CREATE TABLE IF NOT EXISTS patient.patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100) UNIQUE,
    family_name VARCHAR(100) NOT NULL,
    given_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patient.addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    address_type VARCHAR(20) NOT NULL,
    line1 VARCHAR(100) NOT NULL,
    line2 VARCHAR(100),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patient.contact_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    contact_type VARCHAR(20) NOT NULL,
    value VARCHAR(100) NOT NULL,
    use VARCHAR(20),
    rank INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patient.observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    code VARCHAR(50) NOT NULL,
    code_system VARCHAR(100) NOT NULL,
    code_display VARCHAR(100),
    effective_date TIMESTAMP WITH TIME ZONE NOT NULL,
    value_quantity DECIMAL,
    value_unit VARCHAR(20),
    value_code VARCHAR(50),
    value_string TEXT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patient.crohns_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    crohns_type VARCHAR(20) NOT NULL, -- ileal, colonic, ileocolonic, perianal
    diagnosis_date DATE,
    last_assessment_date DATE,
    cdai_score INTEGER,
    ses_cd_score INTEGER,
    fecal_calprotectin DECIMAL,
    crp DECIMAL,
    esr INTEGER,
    microbiome_diversity DECIMAL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patient.genetic_markers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    gene VARCHAR(50) NOT NULL,
    variant VARCHAR(50) NOT NULL,
    zygosity VARCHAR(20) NOT NULL,
    clinical_significance VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(patient_id, gene, variant)
);

CREATE TABLE IF NOT EXISTS patient.treatment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    medication VARCHAR(100) NOT NULL,
    dosage VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE,
    response VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS patient.adverse_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    treatment_id UUID NOT NULL REFERENCES patient.treatment_history(id) ON DELETE CASCADE,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    onset_date DATE NOT NULL,
    resolution_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create clinical trial tables
CREATE TABLE IF NOT EXISTS trial.trial_protocols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    phase INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trial.trial_arms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id UUID NOT NULL REFERENCES trial.trial_protocols(id) ON DELETE CASCADE,
    arm_id VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    medication VARCHAR(100) NOT NULL,
    dosage DECIMAL NOT NULL,
    unit VARCHAR(20) NOT NULL,
    frequency VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trial_id, arm_id)
);

CREATE TABLE IF NOT EXISTS trial.biomarker_stratification (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arm_id UUID NOT NULL REFERENCES trial.trial_arms(id) ON DELETE CASCADE,
    biomarker VARCHAR(50) NOT NULL,
    criteria VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trial.adaptive_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id UUID NOT NULL REFERENCES trial.trial_protocols(id) ON DELETE CASCADE,
    trigger_condition VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trial.endpoints (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id UUID NOT NULL REFERENCES trial.trial_protocols(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    endpoint_type VARCHAR(20) NOT NULL, -- primary, secondary
    metric VARCHAR(100) NOT NULL,
    timepoint VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trial.patient_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id UUID NOT NULL REFERENCES trial.trial_protocols(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    arm_id UUID REFERENCES trial.trial_arms(id),
    enrollment_date DATE NOT NULL,
    exit_date DATE,
    exit_reason VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trial_id, patient_id)
);

CREATE TABLE IF NOT EXISTS trial.patient_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    enrollment_id UUID NOT NULL REFERENCES trial.patient_enrollments(id) ON DELETE CASCADE,
    assessment_date DATE NOT NULL,
    cdai_score INTEGER,
    ses_cd_score INTEGER,
    fecal_calprotectin DECIMAL,
    crp DECIMAL,
    esr INTEGER,
    microbiome_diversity DECIMAL,
    response_score DECIMAL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trial.trial_adaptations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trial_id UUID NOT NULL REFERENCES trial.trial_protocols(id) ON DELETE CASCADE,
    adaptation_type VARCHAR(50) NOT NULL,
    trigger_condition VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create research tables
CREATE TABLE IF NOT EXISTS research.treatment_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    treatment_plan JSONB NOT NULL,
    fitness DECIMAL NOT NULL,
    confidence DECIMAL NOT NULL,
    explanations JSONB,
    biomarker_influences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS research.genetic_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patient.patients(id) ON DELETE CASCADE,
    analysis_id VARCHAR(100) NOT NULL,
    variants JSONB,
    risk_assessment JSONB,
    treatment_recommendations JSONB,
    analysis_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create auth tables
CREATE TABLE IF NOT EXISTS auth.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth.roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth.user_roles (
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES auth.roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (user_id, role_id)
);

-- Insert default roles
INSERT INTO auth.roles (name, description) VALUES
('admin', 'System administrator with full access'),
('researcher', 'Can design and manage clinical trials'),
('provider', 'Healthcare provider with patient access'),
('patient', 'Patient role with limited access to own data')
ON CONFLICT (name) DO NOTHING;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_patient_external_id ON patient.patients(external_id);
CREATE INDEX IF NOT EXISTS idx_patient_name ON patient.patients(family_name, given_name);
CREATE INDEX IF NOT EXISTS idx_observations_patient ON patient.observations(patient_id);
CREATE INDEX IF NOT EXISTS idx_observations_code ON patient.observations(code);
CREATE INDEX IF NOT EXISTS idx_genetic_markers_patient ON patient.genetic_markers(patient_id);
CREATE INDEX IF NOT EXISTS idx_genetic_markers_gene ON patient.genetic_markers(gene, variant);
CREATE INDEX IF NOT EXISTS idx_treatment_history_patient ON patient.treatment_history(patient_id);
CREATE INDEX IF NOT EXISTS idx_treatment_history_medication ON patient.treatment_history(medication);
CREATE INDEX IF NOT EXISTS idx_trial_protocols_trial_id ON trial.trial_protocols(trial_id);
CREATE INDEX IF NOT EXISTS idx_trial_arms_trial_id ON trial.trial_arms(trial_id);
CREATE INDEX IF NOT EXISTS idx_patient_enrollments_trial_patient ON trial.patient_enrollments(trial_id, patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_outcomes_enrollment ON trial.patient_outcomes(enrollment_id);
CREATE INDEX IF NOT EXISTS idx_treatment_recommendations_patient ON research.treatment_recommendations(patient_id);
CREATE INDEX IF NOT EXISTS idx_genetic_analyses_patient ON research.genetic_analyses(patient_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON auth.users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON auth.users(email);