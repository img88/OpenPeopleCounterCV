CREATE TABLE IF NOT EXISTS region_registry (
    pk_region_id UUID PRIMARY KEY,
    region_name VARCHAR(100) NOT NULL,
    region_description TEXT,
    polygon JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
