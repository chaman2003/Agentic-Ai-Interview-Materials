# OpenAI + LangChain — Advanced Q&A & Patterns

---

## TOKENS AND CONTEXT WINDOWS

**Q: What are tokens?**
A: The unit LLMs work in. Not exactly words — roughly 1 token ≈ 4 characters or ¾ of a word. "ChatGPT is great" ≈ 5 tokens. Why it matters: API pricing is per token. Context window limits are in tokens.

**Q: What is a context window?**
A: The maximum amount of text (input + output) an LLM can process at once. GPT-4 Turbo: 128K tokens. Claude: 200K tokens. If your conversation + documents exceed the window, earlier messages are lost.

**Q: How do you handle context window limits in a RAG system?**
A: You can't fit an entire knowledge base in the prompt. Solutions:
1. **Retrieval** — only put the relevant chunks in (RAG approach)
2. **Summarization** — compress earlier conversation history
3. **Sliding window** — keep only last N messages in memory
4. **Map-reduce** — split processing across multiple LLM calls

---

## HALLUCINATION

**Q: What is hallucination?**
A: LLMs sometimes confidently generate false information. The model predicts likely-sounding tokens, not necessarily true facts.

**Q: How do you reduce hallucination?**
A:
1. **RAG** — ground the model in real documents. Instruction: "Answer ONLY from the provided context. If you're unsure, say 'I don't know'."
2. **Temperature=0** — deterministic output for factual tasks
3. **Structured output** — function calling or JSON mode for controlled extraction
4. **Verify programmatically** — don't trust unchecked LLM output in critical paths
5. **Source citation** — ask model to cite which chunk each claim comes from

---

## PROMPT ENGINEERING

**Q: What is few-shot prompting?**
A: Give the LLM 2-3 examples in the prompt so it understands the pattern you want:
```python
prompt = """Extract name and email from text.

Examples:
Text: "Contact Alice at alice@example.com"
Output: {"name": "Alice", "email": "alice@example.com"}

Text: "Reach Bob on bob@test.com"
Output: {"name": "Bob", "email": "bob@test.com"}

Text: "{user_text}"
Output:"""
```

**Q: What is chain-of-thought prompting?**
A: Ask the model to explain its reasoning step by step before giving the answer. Dramatically improves accuracy on complex reasoning tasks.
```
"Solve this step by step: ..."
"Let's think through this carefully: ..."
```

**Q: What is system vs human vs AI message role?**
A:
- `system` — sets the model's persona and rules. "You are a legal assistant. Only answer questions about law."
- `user` / `human` — what the user said
- `assistant` / `ai` — what the model previously responded (for conversation history)

---

## LANGCHAIN PATTERNS

**Q: What is a Runnable in LangChain?**
A: Any component that can be invoked with `.invoke()`, `.stream()`, `.batch()`. Prompt templates, LLMs, output parsers, retrievers are all Runnables. LCEL (`|` pipe) composes Runnables.

**Q: What is `RunnableParallel` and when would you use it?**
A: Run multiple chains simultaneously and merge results:
```python
from langchain_core.runnables import RunnableParallel

parallel_chain = RunnableParallel({
    "summary":   summary_chain,
    "sentiment": sentiment_chain,
    "entities":  entity_chain,
})

result = parallel_chain.invoke({"text": "The platform resolved thousands of disputes"})
# result["summary"] — summary of text
# result["sentiment"] — positive/negative/neutral
# result["entities"] — extracted named entities
```

**Q: What is `RunnablePassthrough`?**
A: Passes input through unchanged — useful for including the original question alongside transformed data:
```python
from langchain_core.runnables import RunnablePassthrough

rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
rag_chain.invoke("What is the platform about?")
```

---

## VECTOR DATABASES COMPARISON

**Q: PGVector vs Pinecone vs ChromaDB vs Weaviate?**

| Feature | PGVector | Pinecone | ChromaDB | Weaviate |
|---------|---------|----------|----------|---------|
| Type | Postgres extension | Managed cloud | Local/cloud | Local/cloud |
| Best for | Already using Postgres | Production scale | Quick prototyping | Hybrid search |
| Cost | Free (self-hosted) | Paid | Free (local) | Free (local) |
| SQL queries | Yes (joins!) | No | No | No |
| Setup | Medium | Easy (API) | Very easy | Medium |

**For a vector DB interview question:** PGVector is ideal because you already have a Postgres database for structured data AND vector search — one less service to manage.

---

## ADVANCED AGENT PATTERNS

**Q: What is a ReAct agent?**
A: Reason + Act. The agent alternates between:
- **Reasoning** — "I need to find the case status, I should use the search_cases tool"
- **Acting** — calls the tool
- **Observing** — reads the tool's output
- Repeats until it has enough to answer

**Q: What is tool_choice in OpenAI function calling?**
A:
- `"auto"` — model decides whether to call a function (default)
- `"none"` — model never calls functions (text only)
- `{"type": "function", "function": {"name": "get_case"}}` — force a specific function call

**Q: How do you make agents more reliable?**
A:
1. Write very clear tool docstrings — the LLM reads these to decide when to use a tool
2. Set `max_iterations` to prevent infinite loops
3. Use `temperature=0` for agents doing structured work
4. Add input validation in tools before executing
5. Log all tool calls → debug agent reasoning showing `verbose=True`

---

## STREAMING AND ASYNC

**Q: How do you stream LangChain responses?**
```python
chain = prompt | llm | StrOutputParser()

# Streaming — yields tokens as they come
for chunk in chain.stream({"question": "Explain RAG"}):
    print(chunk, end="", flush=True)

# Async streaming
async for chunk in chain.astream({"question": "Explain RAG"}):
    print(chunk, end="", flush=True)
```

**Q: Why is streaming important for user experience?**
A: LLMs generate text token by token. Without streaming, user waits 5-10 seconds for the full response. With streaming, they see tokens appear immediately — feels much more responsive. Essential for chatbots.

---

## COMMON LANGCHAIN TRAPS

**Q: What is the difference between `invoke()`, `run()`, and `predict()`?**
A: `invoke()` is the modern LCEL standard — use this. `run()` and `predict()` are older chain methods still found in docs. They all call the chain, but `invoke()` is the unified interface across all Runnable components.

**Q: How do you handle API key safely in LangChain?**
A: Never hardcode. Use environment variables:
```python
import os
from langchain_openai import ChatOpenAI

# Option 1: set before creating LLM
os.environ["OPENAI_API_KEY"] = "..."   # load from .env in prod

# Option 2: pass explicitly
llm = ChatOpenAI(openai_api_key=os.environ["OPENAI_API_KEY"])

# Option 3: use python-dotenv
from dotenv import load_dotenv
load_dotenv()  # reads .env file
```
