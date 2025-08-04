DO $$
BEGIN
    -- Cek dan buat type ENUM jika belum ada
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'log_level') THEN
        CREATE TYPE log_level AS ENUM ('INFO', 'WARNING', 'ERROR', 'DEBUG');
    END IF;
END
$$;

-- Buat tabel jika belum ada
CREATE TABLE IF NOT EXISTS system_log (
    pk_system_log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    level log_level NOT NULL,
    component TEXT NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB
);
