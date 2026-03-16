# HLD — High Level System Design

---

## HOW TO ANSWER A SYSTEM DESIGN QUESTION

1. **Clarify requirements** (2 min) — ask questions before designing
2. **Estimate scale** — users, requests/sec, storage
3. **Draw components** — client → API → service → DB
4. **Design APIs** — key endpoints
5. **Design data model** — key tables/collections
6. **Handle scaling** — where are the bottlenecks? How to scale?
7. **Handle failures** — what happens if X goes down?

---

## KEY HLD COMPONENTS (know all of these)

| Component | What it does | When you need it |
|-----------|-------------|-----------------|
| Load Balancer | Distributes requests across servers | Multiple app servers |
| CDN | Serves static assets from edge nodes | Images, JS, CSS |
| Cache (Redis) | In-memory fast reads | Read-heavy, repeated queries |
| Message Queue | Async task processing | Sending emails, processing uploads |
| Database | Persistent storage | All data |
| Search Engine (Elasticsearch) | Full-text search | Search features |
| Object Storage (S3) | Store files/blobs | Images, documents, exports |

---

## CAP THEOREM

You can only have 2 of 3:
- **C**onsistency — all nodes see the same data at the same time
- **A**vailability — every request gets a response (even if stale)
- **P**artition tolerance — system works even if network splits

**In practice:** partition tolerance is required (networks fail). So you choose C or A:
- **CP** (consistent): MongoDB, Zookeeper. Data might be unavailable during partition.
- **AP** (available): Cassandra, DynamoDB. Returns possibly stale data during partition.
- PostgreSQL is **CA** — assumes no partition (single node or same network).

---

## DESIGN #1 — CASE MANAGEMENT SYSTEM

### Requirements
- Create/view/update/resolve disputes
- 50K cases/day, corporate clients with 100s of cases
- Real-time status updates to parties
- Search cases by keyword, status, date
- Document uploads (contracts, evidence)

### Components
```
Client (React)
    ↓ HTTPS
[Load Balancer (Nginx)]
    ↓
[Node.js/Express API — 3 instances]
    ↓              ↓           ↓
[MongoDB]     [Redis Cache]  [S3 (docs)]
                              ↓
                        [RabbitMQ / Queue]
                              ↓
                    [Worker: Notification Service]
                    [Worker: Document Processor]
```

### API Design
```
POST   /api/v1/cases             → create case (201)
GET    /api/v1/cases             → list + filter (200)
GET    /api/v1/cases/:id         → case detail (200)
PUT    /api/v1/cases/:id/status  → update status (200)
POST   /api/v1/cases/:id/docs    → upload document (201)
GET    /api/v1/cases/:id/docs    → list documents (200)
GET    /api/v1/clients/:id/stats → cases by status for client (200)
```

### Data Model (MongoDB)
```json
// cases collection
{
  "_id": "64a7f...",
  "caseNumber": "CASE-2024-001",
  "title": "Smith vs Jones",
  "status": "open",        // open|in_progress|resolved|closed
  "clientId": "CLIENT-123",
  "partyA": { "name": "Smith", "email": "smith@co.com" },
  "partyB": { "name": "Jones", "email": "jones@co.com" },
  "amount": 50000,
  "mediatorId": "MED-001",
  "documents": ["s3://bucket/doc1.pdf"],
  "timeline": [
    { "action": "Case created", "at": "2024-01-15T10:00:00Z" }
  ],
  "createdAt": "2024-01-15T10:00:00Z",
  "resolvedAt": null
}
```

### Scaling Decisions
- **Read-heavy queries** (list/filter) → Redis cache with 5-min TTL
- **Document uploads** → direct S3 upload via pre-signed URL (don't proxy through API)
- **Notifications** → async queue (email doesn't slow down case creation API)
- **Real-time updates** → Socket.IO rooms per case
- **Full-text search** → MongoDB text index or Elasticsearch

---

## DESIGN #2 — DOCUMENT PROCESSING PIPELINE

### Requirements
- Upload documents (PDF, images, audio)
- 12-stage OCR + extraction pipeline
- 1000 documents/hour, each takes 10-30s to process
- Real-time progress updates
- Store extracted structured data

### Components
```
Client (React)
    ↓
[API Server (Flask/FastAPI)]
    ↓ upload          ↓ status poll
[S3 Storage]     [Redis (job status)]
    ↓
[Message Queue (Celery + Redis)]
    ↓
[Worker Pool — 10 workers]
  Stage 1: Image preprocessing (OpenCV)
  Stage 2: OCR (Tesseract)
  Stage 3: Audio transcription (GPU Whisper)
  ...
  Stage 12: JSON output formatting
    ↓
[MongoDB (extracted results)]
    ↓
[WebSocket (Flask-SocketIO) — progress events]
```

### Why async queue instead of sync?
- OCR takes 10-30s → sync API would timeout
- Multiple documents → parallel processing
- Worker crashes don't affect API
- Scale workers independently from API

### Scaling for 1000 docs/hour
- 1000 docs/60min = ~17 docs/min
- Each doc takes 30s → need ~9 workers running in parallel
- Add more Celery workers horizontally (each is a process)
- GPU workers for Whisper (more expensive, scale separately)

---

## DESIGN #3 — RAG SYSTEM

### Requirements
- 100K document chunks stored
- Query latency < 500ms
- Support multiple knowledge bases (per client)
- Incremental updates (new docs added regularly)

### Components
```
[FastAPI Server]
    ↓ embed query
[OpenAI Embeddings API]
    ↓ similarity search
[PGVector on Postgres]
    ↓ top-k chunks
[LLM (GPT-4)]
    ↓ answer
[Response to client]
```

### Optimizations for 500ms latency
1. Cache frequent queries in Redis (hit rate ~40%)
2. IVFFlat index on embedding column (10x faster search)
3. Pre-filter by metadata (client_id, doc_type) before vector search
4. Async embedding + search with `asyncio.gather`

---

## DESIGN #4 — URL SHORTENER (Classic Interview Problem)

### Requirements
- Shorten long URLs → 6-char code (bit.ly style)
- 1M URLs/day writes, 100M reads/day (100:1 read:write)
- Redirect in < 100ms

### Key Design Decisions
- **Encoding:** Base62 (a-z, A-Z, 0-9) → 62^6 = 56 billion combinations
- **Storage:** Postgres (SERIAL id → Base62 encode → short code)
- **Cache:** Redis for top 20% URLs (handles 80% of traffic)
- **CDN:** Cache redirects at edge nodes

### Flow
```
POST /shorten → generate ID → base62 encode → store in Postgres → return short URL
GET /{code}  → Redis check → if miss: Postgres lookup → 301 redirect → async cache update
```

---

## COMMON SYSTEM DESIGN VOCABULARY

| Term | Meaning |
|------|---------|
| Horizontal scaling | Add more servers |
| Vertical scaling | Make one server bigger |
| Sharding | Split DB across multiple servers by a key |
| Replication | Copy data to multiple servers (for availability) |
| Cache-aside | Check cache → miss → query DB → write to cache |
| Write-through | Write to cache AND DB simultaneously |
| CDN | Edge servers that cache static content close to users |
| Message queue | Async task processing (RabbitMQ, Celery, SQS) |
| Idempotency | Same request → same result (safe to retry) |
