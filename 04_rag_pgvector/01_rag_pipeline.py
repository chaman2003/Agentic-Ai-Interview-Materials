# ============================================================
# RAG PIPELINE — Build Every Step from Scratch
# ============================================================
# RAG = Retrieval Augmented Generation
# Instead of asking LLM from memory → find relevant docs first → put in prompt
# Like giving the LLM an OPEN-BOOK EXAM instead of closed-book

# pip install openai numpy

import os
import json
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ============================================================
# STEP 1: CHUNK TEXT
# Break large text into smaller overlapping pieces
# ============================================================
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    overlap: how many chars from prev chunk to include at start of next
    (helps preserve context at chunk boundaries)
    """
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i : i + chunk_size]
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

# Example
sample_text = """
LegalTech AI is a technology company that resolves disputes online.
They have handled over millions of cases across the country.
The platform uses AI to match parties with mediators and track case progress.
The platform processes cases 10x faster than traditional courts.
The company is profitable, grew 80-100% annually.
""" * 10   # repeat to simulate longer doc

chunks = chunk_text(sample_text, chunk_size=200, overlap=30)
print(f"Created {len(chunks)} chunks")
print(f"First chunk: {chunks[0][:100]}...")


# ============================================================
# STEP 2: EMBED CHUNKS
# Convert each chunk to a vector (list of 1536 floats)
# Similar text → similar vectors (close in vector space)
# ============================================================
def embed_text(text: str) -> list[float]:
    """Convert text to embedding vector"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding   # 1536 floats

# Embed all chunks (in production: batch these, use async)
# embeddings = [embed_text(chunk) for chunk in chunks]


# ============================================================
# STEP 3: STORE EMBEDDINGS
# In production: use PGVector or a vector DB
# Here: store in memory as a list of dicts
# ============================================================
def build_knowledge_base(texts: list[str]) -> list[dict]:
    """Embed all texts and store with their content"""
    knowledge_base = []
    for i, text in enumerate(texts):
        print(f"Embedding chunk {i+1}/{len(texts)}...")
        # embedding = embed_text(text)   # comment out to avoid API calls in demo
        embedding = [0.0] * 1536        # mock embedding for demo
        knowledge_base.append({
            "text":      text,
            "embedding": embedding,
            "id":        i
        })
    return knowledge_base

# Save to JSON file (simple persistence)
def save_knowledge_base(kb: list[dict], filepath: str):
    with open(filepath, "w") as f:
        json.dump(kb, f)

def load_knowledge_base(filepath: str) -> list[dict]:
    with open(filepath, "r") as f:
        return json.load(f)


# ============================================================
# STEP 4: RETRIEVE RELEVANT CHUNKS
# Embed query → compare with all stored embeddings → return top-k
# ============================================================
def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Cosine similarity = dot product / (magnitude of a * magnitude of b)
    Range: -1 to 1. Higher = more similar.
    """
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def retrieve_relevant_chunks(query: str, knowledge_base: list[dict], top_k: int = 3) -> list[str]:
    """Find the most relevant chunks for a query"""
    # Embed the query
    query_embedding = embed_text(query)

    # Compute similarity with every stored chunk
    scored = []
    for item in knowledge_base:
        score = cosine_similarity(query_embedding, item["embedding"])
        scored.append((score, item["text"]))

    # Sort by score (highest first) and return top-k texts
    scored.sort(key=lambda x: x[0], reverse=True)
    return [text for score, text in scored[:top_k]]


# ============================================================
# STEP 5: GENERATE ANSWER
# Put retrieved chunks in prompt → ask LLM → return answer
# ============================================================
def generate_answer(query: str, relevant_chunks: list[str]) -> str:
    """Generate answer using retrieved context"""
    context = "\n\n".join(relevant_chunks)

    prompt = f"""Answer the question based ONLY on the context below.
If the answer is not in the context, say "I don't know based on the provided information."

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0   # deterministic for factual Q&A
    )
    return response.choices[0].message.content


# ============================================================
# FULL RAG PIPELINE — end to end
# ============================================================
def rag_query(query: str, knowledge_base: list[dict]) -> str:
    """Complete RAG pipeline: retrieve + generate"""
    print(f"\nQuery: {query}")
    print("Step 1: Retrieving relevant chunks...")
    chunks = retrieve_relevant_chunks(query, knowledge_base, top_k=3)

    print(f"Step 2: Found {len(chunks)} relevant chunks")
    print("Step 3: Generating answer...")
    answer = generate_answer(query, chunks)

    return answer


# ── MOCK DEMO (no API calls) ──────────────────────────────────
def demo_without_api():
    """Demonstrate the pipeline structure without real API calls"""

    # Sample knowledge base
    docs = [
        "LegalTech AI resolves disputes online. They handled millions of cases.",
        "The platform grew 80-100% annually and is profitable.",
        "The platform uses AI to match parties with mediators.",
        "The company won multiple industry awards for innovation.",
        "Cases are processed 10x faster than traditional courts.",
    ]

    # Simulate: pretend each doc has a distinct embedding by using index
    kb = [{"text": doc, "embedding": [float(i)] * 1536, "id": i}
          for i, doc in enumerate(docs)]

    # For demo, just return the first 2 docs as "retrieved"
    query = "How fast does the platform process cases?"
    retrieved = docs[:2]   # mock retrieval

    context = "\n".join(retrieved)
    print(f"Query: {query}")
    print(f"Retrieved context:\n{context}")
    print("\nIn production: LLM would generate an answer from this context")

demo_without_api()
