CREATE TABLE IF NOT EXISTS render_registry (
    pk_render_id UUID PRIMARY KEY,
    fk_detection_id UUID REFERENCES detection_jobs(pk_detection_id) ON DELETE CASCADE,
    video_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
