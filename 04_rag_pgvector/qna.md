# RAG + PGVector Q&A — Interview Ready

---

## RAG FUNDAMENTALS

**Q: What is RAG and why is it better than fine-tuning for knowledge?**
A: Retrieval Augmented Generation retrieves relevant documents at query time and includes them as context in the prompt. Better than fine-tuning for knowledge because:
- Fine-tuning bakes knowledge into weights — knowledge becomes stale, hard to update
- RAG retrieves live, up-to-date documents — update the database, not the model
- RAG gives the model citations and evidence — verifiable, auditable
- Fine-tuning requires 50-100+ examples and is expensive — RAG needs no training
- Fine-tuning teaches style/format, not new facts (models often hallucinate fine-tuned facts)

Use fine-tuning for: tone, style, format, domain vocabulary. Use RAG for: factual knowledge retrieval.

**Q: What are the 5 stages of a RAG pipeline in detail?**
A:
1. **Ingestion (offline)**: Load documents → chunk them → embed chunks → store (chunk text + embedding + metadata) in vector DB.
2. **Query processing**: Embed the user's question using the same embedding model used at ingestion.
3. **Retrieval**: Find top-k chunks most similar to the query vector. May use dense, sparse, or hybrid search.
4. **Context assembly**: Format retrieved chunks with their source metadata into a prompt.
5. **Generation**: Pass assembled prompt to LLM. Model answers grounded in the retrieved context.

**Q: What is naive RAG vs. advanced RAG vs. modular RAG?**
A:
- **Naive RAG**: Simple retrieve-then-generate. One embedding model, one vector search, one LLM call. Works for simple Q&A but fails on: complex queries, temporal reasoning, multi-hop questions.
- **Advanced RAG**: Adds pre-retrieval (query rewriting, HyDE) and post-retrieval (reranking, context compression) steps. Better accuracy.
- **Modular RAG**: Treats each component as a swappable module. Mix-and-match retrievers, rerankers, generators. Routing logic to pick different pipelines per query type.

**Q: What is the role of the embedding model in RAG and how does it affect quality?**
A: The embedding model converts text to vectors. Query and document embeddings must use the SAME model — different models create incompatible vector spaces. Better embedding models = better retrieval = better final answers. The embedding model is the most impactful component for retrieval quality. Evaluate with retrieval metrics (recall@k, MRR) independently from generation quality.

**Q: What is the context window utilization problem in RAG?**
A: You retrieve top-k chunks but the model's context window has a limit. If each chunk is 500 tokens and you retrieve k=10, that's 5000 tokens just for context — plus system prompt and history. Balance: more chunks = more coverage but less focus, higher cost, and "lost in the middle" degradation. Typical production: k=3-5 well-ranked chunks.

**Q: What is the "lost in the middle" problem specific to RAG?**
A: Studies show LLMs perform best at the beginning and end of their context. In a 10-chunk context, chunks 4-7 (the middle) are often under-utilized. Mitigation: use fewer, higher-quality chunks rather than many chunks, put most relevant chunks first, use reranking to put the best chunks at position 1.

**Q: What is query transformation and why does it improve retrieval?**
A: The user's question might not match document language. Transformations:
- **Query rewriting**: "What did Apple make?" → "Apple Inc. product announcements and releases"
- **Multi-query**: generate 3-5 variants of the query, retrieve for each, union results
- **Step-back prompting**: abstract the question before searching ("What's the general principle behind X?")
- **HyDE** (Hypothetical Document Embeddings): generate a fake answer, embed it, search with that embedding

**Q: How do you evaluate RAG quality?**
A: Use RAGAS framework (see evaluation section) or manual inspection:
1. **Retrieval quality**: are the right chunks retrieved? (precision@k, recall@k)
2. **Context relevance**: are retrieved chunks actually relevant to the question?
3. **Faithfulness**: does the answer follow from the retrieved context?
4. **Answer relevance**: does the answer address the question?
5. **End-to-end accuracy**: is the final answer correct? (requires ground truth)

---

## CHUNKING STRATEGIES

**Q: What is chunking and why does chunk size matter so much?**
A: Chunking splits documents into pieces for embedding and retrieval. Chunk size is a critical hyperparameter:
- **Too small** (50-100 chars): chunks lack context, embeddings are noisy, single sentences may be ambiguous
- **Too large** (2000+ chars): embeddings are diluted (average of too many topics), retrieved chunks contain irrelevant information
- **Sweet spot**: 256-1024 chars with 10-20% overlap. Must be tuned to your content and use case.

**Q: What is fixed-size (character/token) chunking?**
A: Split text every N characters or tokens, with optional overlap.
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""]  # tries these in order
)
chunks = splitter.split_text(document_text)
```
Pros: simple, fast, predictable. Cons: splits mid-sentence, ignores document structure.

**Q: What is sentence-based chunking?**
A: Split on sentence boundaries using NLP tools (spacy, NLTK). Preserves complete sentences. Can group N sentences per chunk. Better semantic coherence than character splits.

```python
import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp(text)
sentences = [sent.text.strip() for sent in doc.sents]
# Group into chunks of 3-5 sentences
chunks = [" ".join(sentences[i:i+4]) for i in range(0, len(sentences), 3)]
```

**Q: What is recursive character text splitting and why is it preferred?**
A: LangChain's `RecursiveCharacterTextSplitter` tries to split on a hierarchy of separators: first `\n\n` (paragraph), then `\n` (line), then `. ` (sentence), then ` ` (word), then character. This preserves natural structure when possible. Most versatile for general text.

**Q: What is semantic chunking?**
A: Embed each sentence individually, then group sentences with high cosine similarity into the same chunk. Uses a threshold: when consecutive sentences become semantically dissimilar (topic shift), start a new chunk. Produces semantically coherent chunks but requires running the embedding model at ingestion time (slower, more expensive).

```python
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings

splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # or "standard_deviation", "interquartile"
    breakpoint_threshold_amount=95
)
chunks = splitter.split_text(text)
```

**Q: What is document-structure-aware chunking?**
A: Use the document's natural structure as chunk boundaries:
- HTML: split on `<h2>`, `<section>` tags
- Markdown: split on `##` headers
- PDF: use PDFMiner to extract paragraphs/sections
- Code: split on function/class definitions
- JSON/CSV: each record as a chunk

Produces the most contextually coherent chunks. Requires document-type-specific parsers.

**Q: What is parent document retrieval?**
A: Store small chunks for precise retrieval but link them to larger parent chunks. At query time: retrieve small chunks, then return their parent documents for LLM context. This way: precise matching + sufficient context.

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore

retriever = ParentDocumentRetriever(
    vectorstore=vector_db,
    docstore=InMemoryStore(),
    child_splitter=RecursiveCharacterTextSplitter(chunk_size=200),
    parent_splitter=RecursiveCharacterTextSplitter(chunk_size=2000),
)
```

**Q: What is the optimal overlap percentage for chunks?**
A: Typically 10-20% of chunk size. For 500-char chunks: 50-100 char overlap. Too little overlap: important context at boundaries gets lost. Too much overlap: redundant data, higher storage cost, similar chunks retrieved at the same time. Overlap is especially important for chunks that end mid-sentence or mid-thought.

---

## EMBEDDING MODELS

**Q: Compare OpenAI, Cohere, HuggingFace, and BGE embedding models.**
A:
| Model | Dimensions | Context | Speed | Quality | Cost |
|---|---|---|---|---|---|
| OpenAI text-embedding-3-small | 1536 | 8192 tokens | Fast (API) | Very Good | $0.02/1M |
| OpenAI text-embedding-3-large | 3072 | 8192 tokens | Fast (API) | Excellent | $0.13/1M |
| Cohere embed-v3 | 1024 | 512 tokens | Fast (API) | Excellent | ~$0.10/1M |
| BGE-large-en | 1024 | 512 tokens | Fast (local) | Excellent | Free |
| BGE-m3 | 1024 | 8192 tokens | Medium (local) | Excellent | Free |
| all-MiniLM-L6-v2 | 384 | 256 tokens | Very Fast (local) | Good | Free |
| E5-large | 1024 | 512 tokens | Fast (local) | Excellent | Free |

**Q: What is the difference between symmetric and asymmetric embeddings?**
A:
- **Symmetric**: query and documents have similar length and structure. Use for: duplicate detection, semantic similarity, clustering. Model: all-MiniLM-L6-v2.
- **Asymmetric**: short query vs. long document. The question and answer have different forms. Use for: Q&A retrieval, search. Models: BGE, E5, OpenAI ada-002 (all optimized for asymmetric search).
Most RAG use cases are asymmetric — always check if your embedding model is optimized for it.

**Q: What is a Matryoshka embedding model?**
A: Models trained to allow truncating their output to fewer dimensions while preserving quality. OpenAI text-embedding-3-* uses this. You can use 512 or 256 dimensions instead of 3072, saving storage and compute at some quality cost. Useful when storing millions of vectors.

**Q: When should you use a local embedding model vs. API?**
A: Local (BGE, E5, all-MiniLM):
- Free, no API dependency, data stays on-premise
- Slower for large batch ingestion (GPU helps significantly)
- Must manage model loading and infrastructure
- Best for: privacy-sensitive data, cost-sensitive high-volume

API (OpenAI, Cohere):
- Simple, fast, no infrastructure
- Costs money at scale
- Requires sending data to third party
- Best for: prototyping, low-volume, time-to-market priority

---

## RETRIEVAL STRATEGIES

**Q: What is dense retrieval and how does it work?**
A: Dense retrieval embeds both queries and documents into vectors and uses Approximate Nearest Neighbor (ANN) search to find documents whose vectors are most similar to the query vector. Uses cosine similarity or dot product. Good at semantic matching: finds conceptually similar content even with different words. Standard approach for RAG.

**Q: What is sparse retrieval (BM25) and when is it better?**
A: BM25 (Best Match 25) is a traditional term-frequency-based ranking algorithm. It scores documents based on term overlap with the query, normalized by document length. Better than dense retrieval for:
- Exact keyword matches ("error code 0x80070005")
- Named entities, product codes, technical terms
- Cases where the embedding model has never seen the terminology
Does not require pre-computed embeddings for documents — can search over new documents immediately.

**Q: What is hybrid search and how does it work?**
A: Combines dense (vector) and sparse (BM25/keyword) retrieval results. Both retrievals return ranked lists, which are merged using a fusion algorithm. Outperforms either alone because:
- Dense catches semantic matches
- Sparse catches exact keyword matches
- Together they handle a wider variety of queries

Two common fusion methods:
1. **RRF** (Reciprocal Rank Fusion): `score(d) = sum(1 / (k + rank_i(d)))` for each retriever i, k=60 typical
2. **Linear combination**: `score = α * dense_score + (1-α) * sparse_score`, α is tuned on validation set

**Q: What is Reciprocal Rank Fusion (RRF) in detail?**
A: RRF merges multiple ranked lists without needing to normalize scores (which have incompatible scales from different retrievers). Formula: for each document d, sum `1 / (k + rank)` across all lists where it appears. k=60 is the standard constant. Higher = better. Documents appearing high in multiple lists get the best combined scores.

```python
def reciprocal_rank_fusion(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranked_list in ranked_lists:
        for rank, doc_id in enumerate(ranked_list):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)
```

**Q: What is MMR (Maximum Marginal Relevance)?**
A: MMR balances relevance and diversity. Standard retrieval returns the k most similar documents — but they're often very similar to each other (redundant). MMR iteratively selects documents that are: (a) most similar to the query AND (b) least similar to already-selected documents.

```python
# LangChain implementation
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5}
    # lambda_mult: 1.0 = pure relevance, 0.0 = pure diversity
)
```

**Q: What is reranking and when should you add it?**
A: A second-pass ranking step that uses a more accurate (but slower) model to re-score the top-k retrieved candidates. Typical pipeline: retrieve top-50 with fast ANN, rerank with cross-encoder, return top-5.

Cross-encoder: processes query + document together (not as separate embeddings), much higher quality scores. Cohere Rerank API, `cross-encoder/ms-marco-MiniLM-L-6-v2` (HuggingFace) are popular options.

Add reranking when: retrieval quality is insufficient, you have a small k but need high precision.

**Q: What is contextual compression retrieval?**
A: After retrieving a chunk, use an LLM to extract only the portion relevant to the query. Removes noise from large chunks so only the pertinent sentences end up in the prompt. Trade-off: extra LLM call adds latency and cost.

---

## VECTOR DATABASES COMPARISON

**Q: When should you use pgvector vs. Pinecone vs. Qdrant vs. Weaviate?**
A:
- **pgvector**: best when you already use PostgreSQL. Join vectors with relational data, filter with SQL, no extra infrastructure. Scales to ~10M vectors well.
- **Pinecone**: fully managed SaaS, zero ops, auto-scales, globally available. Best for teams that want to focus on the application, not infrastructure. More expensive at scale.
- **Qdrant**: high-performance open-source, supports rich payload filtering, on-disk indexing for large datasets, very fast. Best for self-hosted high-performance needs.
- **Weaviate**: open-source with schema-based design, strong GraphQL API, supports multi-tenancy natively. Good for enterprise with complex data models.
- **Chroma**: zero-ops for local development and small apps. Embeds directly in-process.

**Q: What is multi-tenancy in vector databases?**
A: Isolating different users'/customers' data in the same database. Approaches:
1. **Namespace/partition**: logical separation in same index (Pinecone namespaces, Qdrant collections)
2. **Metadata filter**: all tenants in one collection, filter by `tenant_id` metadata on every query
3. **Separate collection per tenant**: full isolation but high overhead for many small tenants

Metadata filter is simplest but adds security risk if filter is accidentally omitted. Namespace is safer.

**Q: What are the pgvector index types and when to use each?**
A:
```sql
-- IVFFlat: faster to build, less memory, approximate
-- lists = sqrt(num_rows) is a good starting point
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
-- Must set: SET ivfflat.probes = 10; (higher = more accurate, slower)

-- HNSW: slower to build, more memory, better accuracy, faster queries
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
-- ef_search controls query accuracy: SET hnsw.ef_search = 100;
```
For < 1M rows: either works. For larger datasets or when query accuracy is critical: HNSW. For memory-constrained: IVFFlat.

**Q: What are the pgvector similarity operators?**
A:
- `<->` L2 (Euclidean) distance: `ORDER BY embedding <-> query_vec LIMIT 5`
- `<=>` Cosine distance: best for normalized NLP embeddings
- `<#>` Negative inner product: use when embeddings are not normalized (faster than cosine if not normalized)

Always use cosine distance for NLP/text embeddings. Normalize vectors before storage for best performance.

**Q: How does Qdrant's payload filtering work and why is it efficient?**
A: Qdrant stores arbitrary JSON payloads alongside vectors. Filters are applied during HNSW traversal (pre-filtering), not as a post-processing step. This means filtered queries are almost as fast as unfiltered ones. Supports complex conditions: must/should/must_not, range, geo, nested. Pinecone's metadata filtering is similar. pgvector uses SQL WHERE clauses (post-filtering, slightly less efficient).

---

## EVALUATION METRICS (RAGAS)

**Q: What is RAGAS and what metrics does it measure?**
A: RAGAS (Retrieval Augmented Generation Assessment) is a framework for evaluating RAG pipelines using LLMs as judges. Key metrics:
- **Faithfulness**: is the answer factually consistent with the retrieved context? (detects hallucination)
- **Answer Relevancy**: does the answer address the question asked?
- **Context Precision**: are the retrieved chunks relevant to the question? (retrieval quality)
- **Context Recall**: do the retrieved chunks contain the information needed to answer? (retrieval completeness)
- **Answer Correctness**: is the answer actually correct? (requires ground truth)

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

data = Dataset.from_list([{
    "question": "What is RAG?",
    "answer": "RAG is Retrieval Augmented Generation.",
    "contexts": ["RAG stands for Retrieval Augmented Generation, a technique that..."],
    "ground_truth": "RAG is a technique that retrieves relevant documents..."
}])
result = evaluate(data, metrics=[faithfulness, answer_relevancy, context_precision, context_recall])
```

**Q: How is faithfulness measured in RAGAS?**
A: RAGAS asks the LLM to decompose the answer into individual claims, then checks whether each claim can be inferred from the retrieved context. `faithfulness = faithful_claims / total_claims`. A score < 0.8 indicates significant hallucination.

**Q: What other evaluation approaches exist besides RAGAS?**
A:
- **Human evaluation**: gold standard, expensive, slow
- **LLM-as-judge**: use GPT-4 to score responses on rubrics (accuracy, relevance, fluency). Customize criteria for your domain.
- **TruLens** / **DeepEval**: alternative frameworks with similar metrics
- **BLEU/ROUGE**: for generation quality (less suited for RAG, designed for translation/summarization)
- **MRR / NDCG / Recall@k**: pure retrieval metrics, measure if correct chunks are retrieved

---

## PRODUCTION RAG

**Q: How do you ingest large document collections efficiently?**
A: Use batch processing:
```python
# Process documents in batches to avoid memory and rate limit issues
BATCH_SIZE = 100
all_chunks = []
for doc_batch in chunked(documents, BATCH_SIZE):
    chunks = splitter.split_documents(doc_batch)
    all_chunks.extend(chunks)

# Batch embed
EMBED_BATCH = 500
for i in range(0, len(all_chunks), EMBED_BATCH):
    batch = all_chunks[i:i+EMBED_BATCH]
    vector_store.add_documents(batch)
    print(f"Ingested {min(i+EMBED_BATCH, len(all_chunks))}/{len(all_chunks)}")
```
Also: use async API calls, track progress with a database (mark which docs are ingested), handle failures with a queue (Celery, RQ).

**Q: How do you handle incremental updates (new/modified documents)?**
A: Store a checksum (MD5/SHA256) of each source document alongside its chunks. On update:
1. Hash the new version of the document
2. If hash changed: delete old chunks by document ID, re-ingest
3. If hash unchanged: skip

```python
import hashlib

def get_doc_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()

# Store: {doc_id: hash} in a database
# On ingest: compare hash, skip if unchanged
```

**Q: How do you implement RAG response caching?**
A: Cache at two levels:
1. **Embedding cache**: same query text → same embedding (save OpenAI API calls). Use a dict or Redis TTL cache keyed by query text.
2. **Full response cache**: same query + same retrieved context → same answer. Use semantic caching (embed the query, find cached queries within cosine distance threshold). LangChain provides `GPTCache` / `RedisSemanticCache` integration.

Semantic caching is more powerful: "What is ML?" and "Explain machine learning" might hit the same cache entry.

**Q: What is the latency breakdown of a RAG query and how do you optimize it?**
A: Typical latency:
- Query embedding: ~50-100ms (API call) or ~5-20ms (local model)
- Vector search: ~10-50ms (depends on DB, index size)
- Reranking: ~100-500ms (cross-encoder)
- LLM generation: ~500-2000ms (depends on response length)

Optimizations:
- Cache embeddings for repeated queries
- Use smaller embedding models for speed
- Pre-warm connection pools
- Stream LLM response to reduce perceived latency
- Async all I/O operations

---

## ADVANCED PATTERNS

**Q: What is HyDE (Hypothetical Document Embeddings)?**
A: Instead of embedding the raw question, ask the LLM to generate a hypothetical answer, then embed that answer to use as the query vector. The hypothesis resembles the structure of real answers, producing better semantic alignment with the document space.

```python
def hyde_retrieve(question: str, llm, retriever) -> list:
    # Generate a hypothetical answer
    hypothesis = llm.invoke(
        f"Write a short paragraph answering: {question}\n"
        "This is just a hypothesis, be brief and informative."
    ).content
    # Use the hypothesis embedding to retrieve real documents
    return retriever.invoke(hypothesis)
```

Best for: questions phrased very differently from how answers are phrased in documents. Adds one LLM call per query (cost/latency tradeoff).

**Q: What is FLARE (Forward-Looking Active REtrieval)?**
A: The LLM generates its answer incrementally. When it's about to generate a sentence with low-confidence tokens (uncertain), it pauses, formulates a search query based on what it was going to say, retrieves more context, and continues. This iterative retrieval is more targeted than upfront retrieval for long-form generation tasks.

**Q: What is multi-hop RAG?**
A: For questions requiring multiple reasoning steps across different documents ("Who is the CEO of the company that acquired Slack?"), a single retrieval pass isn't enough. Multi-hop retrieval:
1. Initial retrieval based on original question
2. LLM identifies what additional information is needed
3. Second retrieval based on intermediate answer
4. LLM synthesizes final answer from all retrieved documents

Also called "iterative RAG" or "agentic RAG" (the agent decides when to retrieve more).

**Q: What is Graph RAG?**
A: Instead of or in addition to vector search, build a knowledge graph from documents (entities as nodes, relationships as edges). At query time: traverse the graph to find related entities, then retrieve associated documents. Microsoft's GraphRAG preprocesses documents into a hierarchical community structure, enabling global questions ("What are the main themes in this corpus?") that vector search handles poorly.

**Q: What is contextual retrieval (Anthropic's technique)?**
A: Before embedding each chunk, prepend a concise context sentence generated by an LLM that describes where this chunk fits in the larger document. Example: "This chunk is from a 2024 financial report, section 3, discussing Q3 revenue." This context is embedded with the chunk, dramatically improving retrieval for ambiguous chunks.

---

## COMMON PROBLEMS

**Q: Retrieval returns no relevant results — how do you debug?**
A: Systematic check:
1. Verify embedding model is same at ingestion and query time
2. Check similarity threshold (if filtering by score) — lower it
3. Increase k (retrieve more candidates)
4. Print the actual query embedding and inspect
5. Check if the relevant document was actually ingested (query for it directly by text)
6. Try different query phrasings — user question vs. document language mismatch
7. Switch to hybrid search (BM25 may catch exact keyword matches)

**Q: Retrieval returns irrelevant results — how do you fix it?**
A: Several causes and fixes:
- **Chunk size too large**: diluted embeddings. Reduce chunk size.
- **No metadata filtering**: results from wrong sections/sources. Add filters.
- **Embedding model mismatch**: wrong model for your domain. Try domain-specific or larger models.
- **Query is too short/ambiguous**: add query expansion or HyDE.
- **Not enough data**: few relevant documents → model retrieves whatever is closest even if irrelevant. Add a relevance score threshold.

**Q: Answer hallucinates despite relevant context being retrieved — why?**
A: The retrieved context IS there, but the model ignores or distorts it:
1. **"Lost in the middle"**: relevant chunk is in the middle of a long context. Move it to the beginning.
2. **Too much irrelevant context**: noise distracts the model. Use better reranking, reduce k.
3. **Conflicting information**: retrieved chunks contradict each other. Add source date filtering.
4. **Model temperature too high**: reduce to 0 for factual tasks.
5. **Weak prompt**: strengthen the instruction: "Answer ONLY based on the provided context. If the answer is not in the context, say 'I don't know.'"
6. **Model size**: smaller models are worse at context utilization. Upgrade to GPT-4o.

**Q: How do you handle documents longer than the context window?**
A: Several approaches:
1. **Chunking + retrieval**: standard RAG — only inject relevant chunks
2. **Map-reduce**: process each chunk independently with the LLM, then combine results
3. **Refine chain**: start with first chunk's answer, iteratively refine with each subsequent chunk
4. **Hierarchical summarization**: summarize at multiple levels (paragraph → section → document)
5. **Streaming context**: if your question requires the whole document, use a model with large context (Claude 200k, Gemini 1M, GPT-4o 128k)

**Q: What is the cold start problem in RAG and how do you handle it?**
A: When first deployed, the vector database has no documents and every query returns empty results. Solutions:
- Pre-populate with a base document set before going live
- Graceful fallback: when no relevant documents found, answer from model knowledge but clearly flag it: "I couldn't find specific information about this in our knowledge base, but generally..."
- Track retrieval failures to prioritize which documents to ingest next

**Q: How do you handle multi-lingual documents in RAG?**
A: Options:
1. Use a multi-lingual embedding model (BGE-M3, multilingual-e5-large) that handles multiple languages in the same vector space
2. Translate all documents to English before ingestion (loses nuance, adds cost)
3. Separate collections per language with language detection routing
4. Cross-lingual retrieval: embed query in English, documents in original language (only works with multilingual models)
