CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL,
    status VARCHAR(50),
    confidence FLOAT,
    agent_triggered BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS post_mortems (
    id SERIAL PRIMARY KEY,
    incident_date TIMESTAMP,
    title VARCHAR(255),
    content TEXT,
    root_cause TEXT,
    resolution TEXT,
    embedding vector(4096), -- Depending on the model, Ollama outputs might be 4096 dim for Llama3/Mistral
    text_search tsvector GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, '') || ' ' || coalesce(root_cause, '') || ' ' || coalesce(resolution, ''))
    ) STORED
);

CREATE INDEX IF NOT EXISTS text_search_idx ON post_mortems USING GIN (text_search);

CREATE TABLE IF NOT EXISTS agent_analyses (
    id SERIAL PRIMARY KEY,
    log_id INTEGER REFERENCES logs(id),
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    root_cause TEXT,
    suggested_fix TEXT,
    slack_alert TEXT
);
