-- ============================================================
-- PGVECTOR — Store and Search Vectors in Postgres
-- ============================================================
-- PGVector = Postgres extension for vector similarity search
-- Use this for searching similar legal cases/documents

-- ── SETUP ──────────────────────────────────────────────────
-- Enable the extension (run once per database)
CREATE EXTENSION IF NOT EXISTS vector;


-- ── CREATE TABLE WITH VECTOR COLUMN ────────────────────────
-- vector(1536) = 1536-dimensional vector (OpenAI ada-002 size)
CREATE TABLE IF NOT EXISTS documents (
    id        SERIAL PRIMARY KEY,
    title     TEXT,
    content   TEXT NOT NULL,
    embedding vector(1536),        -- the vector column!
    doc_type  VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Example: legal cases table
CREATE TABLE IF NOT EXISTS cases (
    id          SERIAL PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE,
    description TEXT,
    embedding   vector(1536),
    status      VARCHAR(20) DEFAULT 'open',
    party_a     VARCHAR(200),
    party_b     VARCHAR(200),
    amount      DECIMAL(12,2),
    created_at  TIMESTAMP DEFAULT NOW()
);


-- ── INSERT WITH EMBEDDING ─────────────────────────────────
-- In Python: pass the embedding as a list of floats
-- psycopg2 and pgvector library handle the conversion
--
-- Python code:
-- cursor.execute(
--     "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
--     (chunk_text, embedding_list)   # embedding_list = [0.1, 0.2, ...]
-- )

-- Direct SQL insert (for testing — use Python arrays '[0.1, 0.2, ...]' format)
INSERT INTO documents (content, embedding) VALUES
    ('LegalTech AI resolves disputes online', '[0.1, 0.2, 0.3]'::vector);


-- ── SIMILARITY SEARCH ─────────────────────────────────────
-- <->  = L2 (Euclidean) distance — lower is more similar
-- <=>  = Cosine distance — lower is more similar (most common)
-- <#>  = Inner product — higher is more similar

-- Find 5 most similar documents to a query embedding
-- Replace '[0.1, 0.2, 0.3]' with actual query embedding in Python
SELECT
    id,
    content,
    embedding <=> '[0.1, 0.2, 0.3]'::vector AS cosine_distance
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, 0.3]'::vector   -- ORDER BY distance
LIMIT 5;


-- Find similar cases by description embedding
SELECT
    case_number,
    description,
    party_a,
    party_b,
    amount,
    embedding <=> %s AS similarity_score
FROM cases
WHERE status = 'open'
ORDER BY embedding <=> %s
LIMIT 10;


-- ── INDEXING (for performance) ────────────────────────────
-- Without index: every query scans ALL rows (slow for 1M+ records)
-- With index: approximate nearest neighbor search (much faster)

-- IVFFlat index — fast queries, less memory
-- lists=100 → divides vectors into 100 clusters
-- Good balance of speed vs accuracy for most use cases
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- HNSW index — more accurate, more memory, faster query time
-- Better for high-accuracy requirements
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- IVFFlat vs HNSW:
-- IVFFlat: less memory, slower to build, sometimes less accurate
-- HNSW:    more memory, slower to build, more accurate, faster queries
-- For interviews: know the tradeoff, Supabase uses pgvector under the hood


-- ── PYTHON INTEGRATION ────────────────────────────────────
-- pip install psycopg2-binary pgvector

/*
import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np

conn = psycopg2.connect("postgresql://user:pass@localhost/mydb")
register_vector(conn)   # register the vector type

cur = conn.cursor()

# Insert with embedding
embedding = [0.1, 0.2, ...]  # your 1536-dim vector
cur.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("Some text content", embedding)
)
conn.commit()

# Search
query_embedding = [0.15, 0.25, ...]  # embed the query
cur.execute(
    "SELECT content, embedding <=> %s AS dist FROM documents ORDER BY dist LIMIT 5",
    (query_embedding,)
)
results = cur.fetchall()
for content, distance in results:
    print(f"Distance: {distance:.4f} | Content: {content}")

cur.close()
conn.close()
*/
