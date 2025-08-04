-- Table: detection_jobs
CREATE TABLE IF NOT EXISTS detection_jobs (
    pk_detection_id UUID PRIMARY KEY,
    fk_video_id UUID REFERENCES video_registry(pk_video_id),
    name VARCHAR(100),
    description TEXT,
    classes INTEGER[],
    model_name VARCHAR(100),
    tracker VARCHAR(100),
    max_frame INT,
    output_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: detection_event
CREATE TABLE IF NOT EXISTS detection_event (
    pk_detection_event_id UUID PRIMARY KEY,
    fk_detection_id UUID REFERENCES detection_jobs(pk_detection_id) ON DELETE CASCADE,
    fk_region_id UUID REFERENCES region_registry(pk_region_id),
    frame_number INT,
    timestamp TIMESTAMP,
    count INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: detection_objects
CREATE TABLE IF NOT EXISTS detection_objects (
    pk_object_id UUID PRIMARY KEY,
    fk_detection_event_id UUID REFERENCES detection_event(pk_detection_event_id) ON DELETE CASCADE,
    tracker_id INT,
    bbox INTEGER[],
    confidence DOUBLE PRECISION,
    inside_region BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: detect_region_mapping
CREATE TABLE IF NOT EXISTS detect_region_mapping (
    fk_region_id UUID REFERENCES region_registry(pk_region_id) ON DELETE CASCADE,
    fk_detection_id UUID REFERENCES detection_jobs(pk_detection_id) ON DELETE CASCADE,
    PRIMARY KEY (fk_region_id, fk_detection_id)
);