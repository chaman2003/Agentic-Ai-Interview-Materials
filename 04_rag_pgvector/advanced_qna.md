# RAG + PGVector — Advanced Q&A, Strategies & Variations

---

## CHUNKING STRATEGIES

**Q: What are the different chunking strategies?**

| Strategy | When to Use |
|----------|-------------|
| Fixed-size with overlap | Simple, general purpose. Use as default. |
| Sentence-based | Preserve complete thoughts. Better for Q&A. |
| Paragraph/section | Documents with clear structure. |
| Semantic chunking | Split where meaning changes (uses embeddings). Best quality. |
| Recursive character | Try progressively smaller delimiters. LangChain default. |

```python
# Fixed-size (what you built)
def chunk_fixed(text, size=500, overlap=50):
    chunks, i = [], 0
    while i < len(text):
        chunks.append(text[i:i+size])
        i += size - overlap
    return chunks

# Sentence-based (better quality)
import nltk
def chunk_sentences(text, sentences_per_chunk=5):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunks.append(" ".join(sentences[i:i+sentences_per_chunk]))
    return chunks

# LangChain's RecursiveCharacterTextSplitter (best practice)
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_text(text)
```

---

## RETRIEVAL STRATEGIES

**Q: What is hybrid search?**
A: Combines vector similarity search (semantic) with keyword search (BM25/full-text). Gets the best of both:
- Vector search: finds semantically similar docs even with different words
- Keyword search: exact term matching (good for proper nouns like case numbers, names)
- Combine scores (e.g., 70% vector + 30% BM25)

```sql
-- PGVector: cosine similarity
SELECT content, embedding <=> $1 AS vector_score FROM docs ORDER BY vector_score LIMIT 10;

-- Postgres: full-text search
SELECT content, ts_rank(to_tsvector(content), query) AS text_score
FROM docs, to_tsquery($2) query WHERE to_tsvector(content) @@ query;
```

**Q: What is re-ranking?**
A: After initial retrieval (fast), use a more accurate cross-encoder model to re-score and re-order the top results. The initial retriever gets candidates fast, the re-ranker gets accuracy.
```python
# Step 1: Retrieve 20 candidates (fast, approximate)
candidates = retrieve_top_k(query, k=20)

# Step 2: Re-rank with cross-encoder (slower but more accurate)
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores = reranker.predict([(query, doc) for doc in candidates])
reranked = [doc for _, doc in sorted(zip(scores, candidates), reverse=True)]
return reranked[:5]   # return top 5 reranked
```

---

## PGVECTOR DEEP DIVE

**Q: What is Approximate Nearest Neighbor (ANN) search?**
A: Exact nearest neighbor requires comparing the query vector to every stored vector — O(n). ANN trades a tiny bit of accuracy for massive speed (O(log n)). IVFFlat and HNSW are ANN algorithms. For most RAG use cases, ANN is perfectly accurate enough.

**Q: How do you tune IVFFlat for performance?**
```sql
-- Rule of thumb: lists ≈ sqrt(total_rows)
-- 10K rows → lists=100, 1M rows → lists=1000

CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- At query time: probes = how many clusters to search
-- Higher probes = more accurate, slower
SET ivfflat.probes = 10;   -- default is 1, usually set 5-10
```

**Q: What does `<->`, `<=>`, `<#>` mean?**
A:
- `<->` L2 (Euclidean) distance — absolute distance in space
- `<=>` Cosine distance — angle-based, ignores magnitude. Best for text embeddings (use this)
- `<#>` Inner product — equivalent to cosine for normalized vectors

---

## EVALUATING RAG QUALITY

**Q: How do you evaluate RAG pipeline quality?**
A: Two things to evaluate:
1. **Retrieval quality** — are the right chunks being retrieved?
   - Precision: of returned chunks, how many are relevant?
   - Recall: of all relevant chunks, how many were returned?
2. **Generation quality** — is the answer based on the retrieved context?
   - Faithfulness: does the answer stick to the context (no hallucination)?
   - Answer relevancy: does it actually answer the question?

Tools: `ragas` library automates these evaluations using LLM-as-judge.

---

## COMMON RAG PROBLEMS AND FIXES

| Problem | Cause | Fix |
|---------|-------|-----|
| Retrieves wrong chunks | Bad embeddings or chunk size | Adjust chunk size, try different embedding model |
| Answer not in any chunk | Info doesn't exist in knowledge base | Tell model to say "I don't know" |
| Answer contradicts chunks | Model ignores context | Stronger prompt: "Use ONLY the context provided" |
| Slow retrieval | No index on vector column | `CREATE INDEX USING ivfflat` |
| Good retrieval, bad answer | Chunks are too fragmented | Increase chunk size, add more overlap |
| Wrong language/format | Prompt unclear | Be explicit in system prompt about format |

---

## METADATA FILTERING

**Q: How do you filter by metadata before doing vector search?**
A: Pre-filter by metadata (fast) THEN do vector search on the smaller set:
```sql
-- Only search documents from last 30 days
SELECT content, embedding <=> $1 AS dist
FROM documents
WHERE doc_type = 'legal_case'
  AND created_at > NOW() - INTERVAL '30 days'
ORDER BY dist
LIMIT 5;
```
This is much faster than vector search on all documents, and more relevant.

---

## PRODUCTION RAG PATTERNS

**Q: What is a RAG pipeline in production vs prototype?**

| Feature | Prototype | Production |
|---------|-----------|-----------|
| Storage | In-memory list | PGVector / Pinecone |
| Chunking | Fixed size | Recursive + semantic |
| Retrieval | Cosine similarity | Hybrid (vector + BM25) + re-ranking |
| Observability | print() | LangSmith / Langfuse tracing |
| Caching | None | Redis cache for frequent queries |
| Evaluation | Manual | ragas automated evaluation |
| Updates | Rebuild all | Incremental embedding updates |

**Q: How do you handle document updates in a RAG system?**
A: When a document changes, you need to re-embed it. Strategy:
1. Track `document_id` and `last_modified` with each chunk
2. On update: delete old chunks (by document_id), re-chunk, re-embed, re-insert
3. Use soft deletes + versioning if you need history

```sql
-- Delete old chunks for a document
DELETE FROM documents WHERE document_id = $1;

-- Insert new chunks
INSERT INTO documents (document_id, content, embedding, version) VALUES ...
```
