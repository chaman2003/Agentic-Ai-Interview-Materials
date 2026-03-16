"""
03_hybrid_search.py — Advanced Retrieval Strategies for RAG
============================================================
Covers:
  1. Dense retrieval  (vector similarity with pgvector)
  2. Sparse retrieval (BM25 keyword search)
  3. Hybrid retrieval (RRF — Reciprocal Rank Fusion)
  4. Reranking        (Cohere Rerank / cross-encoder)
  5. HyDE             (Hypothetical Document Embeddings)
  6. Contextual compression retriever
  7. MMR              (Maximum Marginal Relevance)
"""

import os
import math
import json
from typing import Any
from collections import defaultdict

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# ─────────────────────────────────────────────────────────────────────────────
## SAMPLE DOCUMENT CORPUS
# ─────────────────────────────────────────────────────────────────────────────

DOCUMENTS = [
    Document(page_content="Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms including object-oriented, functional, and procedural programming.",
             metadata={"source": "python_intro.txt", "topic": "programming"}),
    Document(page_content="Machine learning is a subset of artificial intelligence that enables systems to learn from data. Common algorithms include linear regression, decision trees, random forests, and neural networks.",
             metadata={"source": "ml_overview.txt", "topic": "AI"}),
    Document(page_content="PostgreSQL is a powerful open-source relational database system. It supports advanced SQL features, JSON storage, and extensions like pgvector for vector similarity search.",
             metadata={"source": "postgres_guide.txt", "topic": "database"}),
    Document(page_content="Docker is a containerization platform that packages applications and their dependencies into portable containers. This ensures consistent behavior across development, staging, and production environments.",
             metadata={"source": "docker_intro.txt", "topic": "devops"}),
    Document(page_content="FastAPI is a modern Python web framework for building APIs. It features automatic OpenAPI documentation, async support, and Pydantic models for request/response validation.",
             metadata={"source": "fastapi_guide.txt", "topic": "web"}),
    Document(page_content="Vector databases store high-dimensional embedding vectors and support approximate nearest neighbor search. Popular options include Pinecone, Qdrant, Weaviate, and pgvector.",
             metadata={"source": "vector_db_guide.txt", "topic": "database"}),
    Document(page_content="RAG (Retrieval Augmented Generation) combines vector search with LLM generation. The pipeline: chunk documents, embed them, store vectors, retrieve relevant chunks for each query, and use them as LLM context.",
             metadata={"source": "rag_guide.txt", "topic": "AI"}),
    Document(page_content="Redis is an in-memory data structure store used as a cache, message broker, and database. It supports strings, hashes, lists, sets, sorted sets, and streams with sub-millisecond latency.",
             metadata={"source": "redis_guide.txt", "topic": "database"}),
    Document(page_content="Kubernetes is an open-source container orchestration system. It automates deployment, scaling, and management of containerized applications across clusters of machines.",
             metadata={"source": "k8s_guide.txt", "topic": "devops"}),
    Document(page_content="Transformers are deep learning models based on self-attention mechanisms. BERT uses bidirectional encoders for understanding tasks, while GPT uses autoregressive decoders for generation tasks.",
             metadata={"source": "transformers_guide.txt", "topic": "AI"}),
]


# ─────────────────────────────────────────────────────────────────────────────
## 1. DENSE RETRIEVAL (Vector Similarity Search)
# ─────────────────────────────────────────────────────────────────────────────

class DenseRetriever:
    """
    Pure vector similarity retrieval using OpenAI embeddings.
    Stores embeddings in memory (use pgvector/Chroma/Qdrant in production).
    """

    def __init__(self, documents: list[Document], embedding_model: str = "text-embedding-3-small"):
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.documents = documents
        self.doc_embeddings: list[list[float]] = []
        self._build_index()

    def _build_index(self):
        print("Building dense index...")
        texts = [doc.page_content for doc in self.documents]
        self.doc_embeddings = self.embeddings.embed_documents(texts)
        print(f"  Indexed {len(self.documents)} documents (dim={len(self.doc_embeddings[0])})")

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def retrieve(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        """Return top-k documents with their cosine similarity scores."""
        query_embedding = self.embeddings.embed_query(query)
        scored = [
            (doc, self._cosine_similarity(query_embedding, doc_emb))
            for doc, doc_emb in zip(self.documents, self.doc_embeddings)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def as_langchain_retriever(self, k: int = 3):
        """Wrap as a LangChain Retriever interface."""
        from langchain_core.retrievers import BaseRetriever
        from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
        from pydantic import Field

        dense = self

        class _DenseRetriever(BaseRetriever):
            top_k: int = Field(default=k)

            def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
                results = dense.retrieve(query, k=self.top_k)
                return [doc for doc, score in results]

        return _DenseRetriever(top_k=k)


# ─────────────────────────────────────────────────────────────────────────────
## 2. SPARSE RETRIEVAL (BM25)
# ─────────────────────────────────────────────────────────────────────────────

class BM25Retriever:
    """
    BM25 (Best Match 25) — a classic TF-IDF-based ranking algorithm.

    Formula:
      score(D, Q) = sum over t in Q of:
        IDF(t) * (f(t,D) * (k1+1)) / (f(t,D) + k1 * (1 - b + b * |D|/avgdl))

    Parameters:
      k1 (1.2-2.0): term saturation — how much repetition matters
      b  (0.0-1.0): length normalization — 0=no normalization, 1=full normalization
    """

    def __init__(self, documents: list[Document], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self._tokenized_docs: list[list[str]] = []
        self._df: dict[str, int] = defaultdict(int)  # document frequency
        self._avgdl: float = 0.0
        self._build_index()

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercase tokenizer. Use spaCy/NLTK in production."""
        import re
        return re.sub(r'[^\w\s]', '', text.lower()).split()

    def _build_index(self):
        print("Building BM25 index...")
        self._tokenized_docs = [self._tokenize(doc.page_content) for doc in self.documents]
        total_len = sum(len(tokens) for tokens in self._tokenized_docs)
        self._avgdl = total_len / len(self._tokenized_docs)

        # Build document frequency
        for tokens in self._tokenized_docs:
            for term in set(tokens):
                self._df[term] += 1

        print(f"  Indexed {len(self.documents)} documents, vocab size={len(self._df)}")

    def _idf(self, term: str) -> float:
        """Robertson-Sparck Jones IDF formula (BM25 variant)."""
        n = len(self.documents)
        df = self._df.get(term, 0)
        return math.log((n - df + 0.5) / (df + 0.5) + 1)

    def _score_document(self, query_terms: list[str], doc_tokens: list[str]) -> float:
        doc_len = len(doc_tokens)
        tf_map = defaultdict(int)
        for t in doc_tokens:
            tf_map[t] += 1

        score = 0.0
        for term in query_terms:
            if term not in tf_map:
                continue
            tf = tf_map[term]
            idf = self._idf(term)
            numerator   = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self._avgdl))
            score += idf * (numerator / denominator)
        return score

    def retrieve(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        """Return top-k documents with BM25 scores."""
        query_terms = self._tokenize(query)
        scored = [
            (doc, self._score_document(query_terms, tokens))
            for doc, tokens in zip(self.documents, self._tokenized_docs)
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:k]

    def as_langchain_retriever(self, k: int = 3):
        """Return a LangChain-compatible retriever."""
        # Use built-in LangChain BM25 if available
        try:
            from langchain_community.retrievers import BM25Retriever as LC_BM25
            retriever = LC_BM25.from_documents(self.documents, k=k)
            return retriever
        except ImportError:
            pass

        # Fallback: wrap our implementation
        from langchain_core.retrievers import BaseRetriever
        from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
        from pydantic import Field

        bm25 = self

        class _BM25Retriever(BaseRetriever):
            top_k: int = Field(default=k)

            def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
                results = bm25.retrieve(query, k=self.top_k)
                return [doc for doc, score in results]

        return _BM25Retriever(top_k=k)


# ─────────────────────────────────────────────────────────────────────────────
## 3. HYBRID RETRIEVAL (RRF — Reciprocal Rank Fusion)
# ─────────────────────────────────────────────────────────────────────────────

class HybridRetriever:
    """
    Combines dense (vector) and sparse (BM25) retrieval using RRF.

    RRF Formula:
      score(doc) = sum_over_retrievers( 1 / (k + rank_in_retriever) )
      k = 60 (standard constant that prevents high influence of top ranks)

    Why RRF works: avoids score normalization problems (dense scores are
    cosine similarities 0-1, BM25 scores are unbounded). RRF uses only
    rank positions which are comparable across retrievers.
    """

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: BM25Retriever,
        k: int = 60,          # RRF constant
        dense_k: int = 10,    # candidates from dense
        sparse_k: int = 10,   # candidates from sparse
    ):
        self.dense   = dense_retriever
        self.sparse  = sparse_retriever
        self.k       = k
        self.dense_k = dense_k
        self.sparse_k = sparse_k

    def retrieve(self, query: str, top_n: int = 5) -> list[tuple[Document, float]]:
        """Return top-n documents fused from dense and sparse results."""
        # Get candidates from each retriever
        dense_results  = self.dense.retrieve(query, k=self.dense_k)
        sparse_results = self.sparse.retrieve(query, k=self.sparse_k)

        # Build ranked lists (just the doc content as unique ID)
        def doc_id(doc: Document) -> str:
            return doc.page_content[:50]  # use content prefix as ID

        dense_ids  = [doc_id(d) for d, _ in dense_results]
        sparse_ids = [doc_id(d) for d, _ in sparse_results]

        # Map content prefix → full document
        doc_map: dict[str, Document] = {}
        for d, _ in dense_results + sparse_results:
            doc_map[doc_id(d)] = d

        # RRF scoring
        rrf_scores: dict[str, float] = defaultdict(float)
        for rank, did in enumerate(dense_ids):
            rrf_scores[did] += 1.0 / (self.k + rank + 1)
        for rank, did in enumerate(sparse_ids):
            rrf_scores[did] += 1.0 / (self.k + rank + 1)

        # Sort by fused score
        sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        return [(doc_map[did], score) for did, score in sorted_ids[:top_n] if did in doc_map]

    def as_langchain_retriever(self, top_n: int = 5):
        """Wrap as LangChain retriever."""
        from langchain_core.retrievers import BaseRetriever
        from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
        from pydantic import Field

        hybrid = self

        class _HybridRetriever(BaseRetriever):
            n: int = Field(default=top_n)

            def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
                results = hybrid.retrieve(query, top_n=self.n)
                return [doc for doc, score in results]

        return _HybridRetriever(n=top_n)


def demo_hybrid_vs_individual(query: str, dense: DenseRetriever, bm25: BM25Retriever, hybrid: HybridRetriever):
    print(f"\nQuery: '{query}'")
    print("-" * 60)

    print("\nDense results:")
    for doc, score in dense.retrieve(query, k=3):
        print(f"  [{score:.3f}] {doc.page_content[:80]}...")

    print("\nBM25 results:")
    for doc, score in bm25.retrieve(query, k=3):
        print(f"  [{score:.3f}] {doc.page_content[:80]}...")

    print("\nHybrid (RRF) results:")
    for doc, score in hybrid.retrieve(query, top_n=3):
        print(f"  [{score:.4f}] {doc.page_content[:80]}...")


# ─────────────────────────────────────────────────────────────────────────────
## 4. RERANKING
# ─────────────────────────────────────────────────────────────────────────────

class CohereReranker:
    """
    Reranking using Cohere's Rerank API.
    Requires: pip install cohere, COHERE_API_KEY env var.

    A cross-encoder takes (query, document) together and produces a single
    relevance score — much more accurate than bi-encoder (separate embeddings).
    Typical pattern: retrieve top-50 with fast ANN, rerank, return top-5.
    """

    def __init__(self, model: str = "rerank-english-v3.0"):
        self.model = model
        try:
            import cohere
            self.client = cohere.Client(os.getenv("COHERE_API_KEY", ""))
            self.available = True
        except ImportError:
            print("Cohere not installed. Run: pip install cohere")
            self.available = False

    def rerank(self, query: str, documents: list[Document], top_n: int = 3) -> list[tuple[Document, float]]:
        if not self.available:
            print("Cohere not available — returning original order")
            return [(d, 1.0 / (i + 1)) for i, d in enumerate(documents[:top_n])]

        texts = [doc.page_content for doc in documents]
        response = self.client.rerank(
            query=query,
            documents=texts,
            model=self.model,
            top_n=top_n
        )
        return [(documents[r.index], r.relevance_score) for r in response.results]


class CrossEncoderReranker:
    """
    Local cross-encoder reranker using HuggingFace sentence-transformers.
    Requires: pip install sentence-transformers
    Free, no API key, runs on CPU (slow) or GPU (fast).
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        try:
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)
            self.available = True
            print(f"Loaded cross-encoder: {model_name}")
        except ImportError:
            print("sentence-transformers not installed. Run: pip install sentence-transformers")
            self.available = False

    def rerank(self, query: str, documents: list[Document], top_n: int = 3) -> list[tuple[Document, float]]:
        if not self.available:
            return [(d, 1.0 / (i + 1)) for i, d in enumerate(documents[:top_n])]

        # Cross-encoder takes (query, passage) pairs
        pairs = [(query, doc.page_content) for doc in documents]
        scores = self.model.predict(pairs)

        # Sort by score descending
        scored = sorted(zip(documents, scores.tolist()), key=lambda x: x[1], reverse=True)
        return scored[:top_n]


def rerank_pipeline_demo(query: str, retriever: HybridRetriever):
    """Full pipeline: hybrid retrieval → cross-encoder reranking."""
    print(f"\nQuery: '{query}'")

    # Step 1: Retrieve broad candidates
    candidates = retriever.retrieve(query, top_n=6)
    print(f"\nBefore reranking ({len(candidates)} candidates):")
    for i, (doc, score) in enumerate(candidates):
        print(f"  {i+1}. [{score:.4f}] {doc.page_content[:70]}...")

    # Step 2: Rerank with cross-encoder
    reranker = CrossEncoderReranker()
    if reranker.available:
        docs_only = [doc for doc, _ in candidates]
        reranked = reranker.rerank(query, docs_only, top_n=3)
        print(f"\nAfter reranking (top 3):")
        for i, (doc, score) in enumerate(reranked):
            print(f"  {i+1}. [{score:.4f}] {doc.page_content[:70]}...")


# ─────────────────────────────────────────────────────────────────────────────
## 5. HyDE (Hypothetical Document Embeddings)
# ─────────────────────────────────────────────────────────────────────────────

class HyDERetriever:
    """
    HyDE: Generate a hypothetical answer to the query, then embed THAT
    to find real documents. More effective when query phrasing differs
    from document phrasing.

    Trade-off: adds one LLM call per query (~100-300ms latency, small cost).
    """

    def __init__(self, dense_retriever: DenseRetriever, llm_model: str = "gpt-4o-mini"):
        self.dense = dense_retriever
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)

    def _generate_hypothesis(self, query: str) -> str:
        """Ask LLM to write a hypothetical document that would answer the query."""
        prompt = f"""Write a short, factual paragraph (3-5 sentences) that would directly answer this question.
Be specific and informative. This is a hypothetical document for search purposes.

Question: {query}

Hypothetical answer paragraph:"""
        return self.llm.invoke(prompt).content

    def retrieve(self, query: str, k: int = 3) -> list[tuple[Document, float]]:
        """Retrieve using HyDE: generate hypothesis → embed → search."""
        print(f"\n[HyDE] Generating hypothesis for: '{query}'")
        hypothesis = self._generate_hypothesis(query)
        print(f"[HyDE] Hypothesis: {hypothesis[:150]}...")

        # Search using the hypothesis instead of the raw query
        results = self.dense.retrieve(hypothesis, k=k)
        return results

    def retrieve_with_comparison(self, query: str, k: int = 3):
        """Compare HyDE vs standard dense retrieval."""
        print(f"\n{'='*60}")
        print(f"Query: '{query}'")

        standard = self.dense.retrieve(query, k=k)
        hyde = self.retrieve(query, k=k)

        print("\nStandard dense retrieval:")
        for doc, score in standard:
            print(f"  [{score:.3f}] {doc.page_content[:80]}...")

        print("\nHyDE retrieval:")
        for doc, score in hyde:
            print(f"  [{score:.3f}] {doc.page_content[:80]}...")


# ─────────────────────────────────────────────────────────────────────────────
## 6. CONTEXTUAL COMPRESSION RETRIEVER
# ─────────────────────────────────────────────────────────────────────────────

class ContextualCompressionRetriever:
    """
    After retrieving documents, use an LLM to extract only the
    sentences most relevant to the query. Reduces noise in context.

    LangChain provides this built-in:
      from langchain.retrievers import ContextualCompressionRetriever
      from langchain.retrievers.document_compressors import LLMChainExtractor

    Here we implement the core logic manually for clarity.
    """

    def __init__(self, base_retriever, llm_model: str = "gpt-4o-mini"):
        self.retriever = base_retriever
        self.llm = ChatOpenAI(model=llm_model, temperature=0)

    def _compress_document(self, query: str, document: Document) -> Document | None:
        """Extract only query-relevant content from a document."""
        prompt = f"""Given the following context and question, extract ONLY the sentences from the context
that are directly relevant to answering the question. If no sentences are relevant, respond with 'IRRELEVANT'.

Context:
{document.page_content}

Question: {query}

Relevant sentences only (or 'IRRELEVANT'):"""

        compressed = self.llm.invoke(prompt).content.strip()
        if compressed.upper() == "IRRELEVANT" or len(compressed) < 20:
            return None

        return Document(
            page_content=compressed,
            metadata={**document.metadata, "compressed": True, "original_length": len(document.page_content)}
        )

    def retrieve(self, query: str, k: int = 3) -> list[Document]:
        """Retrieve and compress documents."""
        # Get more candidates since some will be filtered as irrelevant
        if hasattr(self.retriever, "retrieve"):
            raw = [doc for doc, _ in self.retriever.retrieve(query, k=k * 2)]
        else:
            raw = self.retriever.get_relevant_documents(query)[:k * 2]

        compressed = []
        for doc in raw:
            compressed_doc = self._compress_document(query, doc)
            if compressed_doc:
                compressed.append(compressed_doc)
                if len(compressed) >= k:
                    break

        return compressed


def demo_langchain_compression(query: str, documents: list[Document]):
    """Using LangChain's built-in ContextualCompressionRetriever."""
    try:
        from langchain_community.vectorstores import Chroma
        from langchain.retrievers import ContextualCompressionRetriever
        from langchain.retrievers.document_compressors import LLMChainExtractor

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = Chroma.from_documents(documents, embeddings)
        base_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

        compressor = LLMChainExtractor.from_llm(
            ChatOpenAI(model="gpt-4o-mini", temperature=0)
        )
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )

        print(f"\n[Compression] Query: '{query}'")
        compressed_docs = compression_retriever.get_relevant_documents(query)
        for doc in compressed_docs:
            print(f"\n  Source: {doc.metadata.get('source', 'unknown')}")
            print(f"  Content: {doc.page_content}")
    except ImportError as e:
        print(f"LangChain community not fully available: {e}")


# ─────────────────────────────────────────────────────────────────────────────
## 7. MMR (Maximum Marginal Relevance)
# ─────────────────────────────────────────────────────────────────────────────

class MMRRetriever:
    """
    Maximum Marginal Relevance: select documents that are
    (a) most similar to query AND (b) least similar to already-selected docs.

    MMR score = λ * sim(doc, query) - (1-λ) * max_sim(doc, selected)
    λ = 1.0 → pure relevance (standard retrieval)
    λ = 0.0 → pure diversity (maximize coverage)
    λ = 0.5 → balanced (typical production value)
    """

    def __init__(self, dense_retriever: DenseRetriever):
        self.dense = dense_retriever

    def retrieve(self, query: str, k: int = 3, lambda_mult: float = 0.5, fetch_k: int = 20) -> list[Document]:
        """
        Retrieve k diverse documents using MMR.

        Args:
            query: The search query
            k: Number of documents to return
            lambda_mult: 1.0=relevance only, 0.0=diversity only
            fetch_k: Candidates to consider (should be >> k)
        """
        embeddings = self.dense.embeddings

        # Get query embedding
        query_emb = embeddings.embed_query(query)

        # Get candidates (more than k to choose from)
        candidates = self.dense.retrieve(query, k=fetch_k)

        if not candidates:
            return []

        # Embed all candidates
        candidate_texts = [doc.page_content for doc, _ in candidates]
        candidate_embs  = embeddings.embed_documents(candidate_texts)

        selected_docs: list[Document] = []
        selected_embs: list[list[float]] = []
        remaining = list(zip([doc for doc, _ in candidates], candidate_embs))

        for _ in range(min(k, len(remaining))):
            best_doc  = None
            best_emb  = None
            best_score = float("-inf")

            for doc, emb in remaining:
                # Relevance: similarity to query
                relevance = DenseRetriever._cosine_similarity(emb, query_emb)

                # Redundancy: max similarity to already selected
                if selected_embs:
                    redundancy = max(
                        DenseRetriever._cosine_similarity(emb, sel_emb)
                        for sel_emb in selected_embs
                    )
                else:
                    redundancy = 0.0

                # MMR score
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * redundancy

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_doc   = doc
                    best_emb   = emb

            if best_doc:
                selected_docs.append(best_doc)
                selected_embs.append(best_emb)
                remaining = [(d, e) for d, e in remaining if d.page_content != best_doc.page_content]

        return selected_docs

    def compare_with_standard(self, query: str, k: int = 4):
        """Show how MMR produces more diverse results."""
        print(f"\nQuery: '{query}'")

        standard = [doc for doc, _ in self.dense.retrieve(query, k=k)]
        mmr_docs  = self.retrieve(query, k=k, lambda_mult=0.5)

        print(f"\nStandard retrieval (k={k}) — may have redundancy:")
        for i, doc in enumerate(standard, 1):
            print(f"  {i}. {doc.page_content[:80]}...")

        print(f"\nMMR retrieval (k={k}, λ=0.5) — diverse results:")
        for i, doc in enumerate(mmr_docs, 1):
            print(f"  {i}. {doc.page_content[:80]}...")


# ─────────────────────────────────────────────────────────────────────────────
## COMPLETE ADVANCED RAG PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def build_advanced_rag_chain(documents: list[Document]):
    """
    Full RAG pipeline with hybrid retrieval + reranking.

    Pipeline:
      query
        → BM25 (top 10) + dense (top 10)
        → RRF fusion (top 6)
        → cross-encoder reranking (top 3)
        → LLM generation with retrieved context
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Build retrievers
    dense  = DenseRetriever(documents)
    sparse = BM25Retriever(documents)
    hybrid = HybridRetriever(dense, sparse, dense_k=8, sparse_k=8)
    reranker = CrossEncoderReranker()

    def retrieve_and_rerank(query: str) -> list[Document]:
        # Step 1: Hybrid retrieval
        candidates = hybrid.retrieve(query, top_n=6)
        docs = [doc for doc, _ in candidates]

        # Step 2: Rerank if available
        if reranker.available:
            reranked = reranker.rerank(query, docs, top_n=3)
            docs = [doc for doc, _ in reranked]
        else:
            docs = docs[:3]

        return docs

    def format_context(docs: list[Document]) -> str:
        sections = []
        for i, doc in enumerate(docs, 1):
            src = doc.metadata.get("source", "unknown")
            sections.append(f"[Source {i}: {src}]\n{doc.page_content}")
        return "\n\n".join(sections)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a knowledgeable assistant. Answer the question based ONLY on the provided context.
If the answer is not fully covered by the context, say what you can and note the limitation.
Always mention which sources you used."""),
        ("human", "Context:\n{context}\n\nQuestion: {question}")
    ])

    # LCEL chain
    chain = (
        {
            "context": RunnableLambda(lambda x: format_context(retrieve_and_rerank(x["question"]))),
            "question": RunnablePassthrough() | RunnableLambda(lambda x: x["question"])
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# ─────────────────────────────────────────────────────────────────────────────
## MAIN — Run all demonstrations
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("HYBRID SEARCH AND ADVANCED RETRIEVAL DEMONSTRATIONS")
    print("=" * 60)

    # --- Build indices ---
    dense  = DenseRetriever(DOCUMENTS)
    bm25   = BM25Retriever(DOCUMENTS)
    hybrid = HybridRetriever(dense, bm25)

    # --- Demo 1: Compare individual vs hybrid ---
    print("\n### Demo 1: Dense vs BM25 vs Hybrid ###")
    # This query tests semantic understanding
    demo_hybrid_vs_individual(
        "similarity search in databases",
        dense, bm25, hybrid
    )
    # This query tests exact keyword matching
    demo_hybrid_vs_individual(
        "pgvector IVFFlat HNSW index",
        dense, bm25, hybrid
    )

    # --- Demo 2: Reranking ---
    print("\n### Demo 2: Reranking Pipeline ###")
    rerank_pipeline_demo("how to store and search vectors", hybrid)

    # --- Demo 3: HyDE ---
    print("\n### Demo 3: HyDE (Hypothetical Document Embeddings) ###")
    hyde = HyDERetriever(dense)
    hyde.retrieve_with_comparison("What should I use to make my API fast and documented?")

    # --- Demo 4: MMR diversity ---
    print("\n### Demo 4: MMR vs Standard Retrieval ###")
    mmr = MMRRetriever(dense)
    mmr.compare_with_standard("database technology comparison", k=4)

    # --- Demo 5: Full RAG chain ---
    print("\n### Demo 5: Full Advanced RAG Pipeline ###")
    rag_chain = build_advanced_rag_chain(DOCUMENTS)
    test_queries = [
        "What is RAG and how does it work?",
        "Compare PostgreSQL and Redis for data storage",
        "How does Docker differ from Kubernetes?",
    ]
    for query in test_queries:
        print(f"\nQ: {query}")
        answer = rag_chain.invoke({"question": query})
        print(f"A: {answer}")

    print("\n" + "=" * 60)
    print("All hybrid search demos complete.")
    print("=" * 60)
