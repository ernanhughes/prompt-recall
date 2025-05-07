CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS chat_turns (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    turn_index INT NOT NULL,
    role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1024),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS alt_completions (
    id SERIAL PRIMARY KEY,
    turn_id INT REFERENCES chat_turns(id),
    model_name TEXT,
    alt_response TEXT,
    notes TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    flagged BOOLEAN DEFAULT FALSE,
    flagged_reason TEXT,
    generated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS app_config (
    key TEXT PRIMARY KEY,             -- Identifier for the config item (e.g., 'watch_dir')
    value TEXT NOT NULL,              -- Value of the config setting
    comment TEXT                      -- Human-readable explanation of what this config is
);

INSERT INTO app_config (key, value, comment)
VALUES ('watch_dir', 'downloads', 'Folder to monitor for new .md chat exports');

