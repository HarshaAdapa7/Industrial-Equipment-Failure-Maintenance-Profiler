-- =========================================================
-- Supabase Cloud SQL Schema & Initial Seed Data for PredictSense
-- =========================================================

CREATE TABLE IF NOT EXISTS public.organizations (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    plan_type VARCHAR(50) DEFAULT 'Enterprise',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.users (
    id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) REFERENCES public.organizations(id) ON DELETE CASCADE,
    email VARCHAR(120) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'Technician',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.machines (
    id VARCHAR(36) PRIMARY KEY,
    org_id VARCHAR(36) REFERENCES public.organizations(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    product_type VARCHAR(10) DEFAULT 'M',
    description TEXT,
    asset_criticality FLOAT DEFAULT 1.5,
    failure_cost FLOAT DEFAULT 180000.0,
    pm_cost FLOAT DEFAULT 15000.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.sensor_readings (
    id VARCHAR(36) PRIMARY KEY,
    machine_id VARCHAR(36) REFERENCES public.machines(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    air_temp FLOAT NOT NULL,
    process_temp FLOAT NOT NULL,
    rpm FLOAT NOT NULL,
    torque FLOAT NOT NULL,
    tool_wear FLOAT NOT NULL,
    derived_features JSONB
);

CREATE TABLE IF NOT EXISTS public.predictions (
    id VARCHAR(36) PRIMARY KEY,
    machine_id VARCHAR(36) REFERENCES public.machines(id) ON DELETE CASCADE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    any_failure BOOLEAN DEFAULT FALSE,
    risk_score FLOAT NOT NULL,
    health_score FLOAT NOT NULL,
    anomaly_score FLOAT NOT NULL,
    label_probs JSONB NOT NULL,
    shap_values JSONB
);

CREATE TABLE IF NOT EXISTS public.alerts (
    id VARCHAR(36) PRIMARY KEY,
    machine_id VARCHAR(36) REFERENCES public.machines(id) ON DELETE CASCADE,
    prediction_id VARCHAR(36) REFERENCES public.predictions(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'HIGH',
    priority_score FLOAT DEFAULT 50.0,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS public.maintenance_actions (
    id VARCHAR(36) PRIMARY KEY,
    machine_id VARCHAR(36) REFERENCES public.machines(id) ON DELETE CASCADE,
    alert_id VARCHAR(36) REFERENCES public.alerts(id) ON DELETE SET NULL,
    action_taken TEXT NOT NULL,
    performed_by VARCHAR(100) DEFAULT 'Technician',
    cost FLOAT DEFAULT 0.0,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    result VARCHAR(50) DEFAULT 'SUCCESS'
);

-- Seed Initial Demo Organization and Industrial Machines
INSERT INTO public.organizations (id, name, plan_type) 
VALUES ('org_default_1', 'Industrial Manufacturing Co.', 'Enterprise')
ON CONFLICT (id) DO NOTHING;

INSERT INTO public.machines (id, org_id, name, product_type, description, asset_criticality, failure_cost, pm_cost)
VALUES 
    ('m1_cnc_mill', 'org_default_1', 'CNC Milling Machine #1', 'M', '3-Axis Vertical CNC Milling Center', 2.0, 200000.0, 15000.0),
    ('m2_precision_lathe', 'org_default_1', 'Precision Lathe #2', 'L', 'High Precision Turning Lathe', 1.2, 120000.0, 10000.0),
    ('m3_heavy_mill', 'org_default_1', 'Heavy Industrial Mill #3', 'H', 'Heavy Duty Production Milling Asset', 2.8, 350000.0, 25000.0)
ON CONFLICT (id) DO NOTHING;
