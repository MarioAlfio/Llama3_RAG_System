-- Abilita l'estensione pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabella per i documenti caricati
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT
);

-- Tabella per i chunk di testo e i relativi embedding
CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    embedding vector(1536), -- Sostituisci 1536 con la dimensione del tuo embedding
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabella per le interazioni utente
CREATE TABLE IF NOT EXISTS interactions (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    question_embedding vector(1536), -- Sostituisci 1536 con la dimensione del tuo embedding
    answer_embedding vector(1536),   -- Sostituisci 1536 con la dimensione del tuo embedding
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    label INTEGER -- 1=corretta, 0=errata, NULL=non etichettata
);