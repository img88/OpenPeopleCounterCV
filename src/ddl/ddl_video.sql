CREATE TABLE IF NOT EXISTS video_registry (
    pk_video_id UUID PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    url TEXT NOT NULL,
    duration INT NOT NULL,
    output_folder TEXT NOT NULL,
    output_path TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
