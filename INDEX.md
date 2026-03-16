# Practice Workspace Index

This file is a guided index of the entire workspace — like a textbook table of contents. Each folder is a chapter, each file is a lesson or topic.

---

## Root Overview
- `MASTER_QNA.md` — master list of questions & answers for quick review
- `DETAILED_INDEX.md` — deep-dive descriptions of every file
- `README.md` — project overview and study guide

---

## 01_python/ — Python fundamentals & advanced concepts
- `01_basics.py` — core Python syntax: variables, types, branches, loops
- `02_intermediate.py` — intermediate Python: args/kwargs, comprehensions, exceptions
- `03_oop.py` — object-oriented programming: classes, inheritance, magic methods
- `04_decorators.py` — decorators, wrappers, and `functools.wraps`
- `05_generators_context.py` — generators, `yield`, context managers, `with` blocks
- `06_collections_logging.py` — `collections` module, logging patterns, file I/O
- `07_patterns_and_variations.py` — coding patterns, design ideas, variations
- `08_async_and_typing.py` — asyncio, async/await, gather, Semaphore, Queue, type hints, Protocol, TypeVar, dataclasses, metaclasses, descriptors
- `advanced_qna.md` — deep-dive Q&A for advanced Python topics
- `qna.md` — Q&A: basics, functions, OOP, decorators, generators, asyncio, type hints, dataclasses, metaclasses

## 02_flask/ — Flask web framework
- `01_basics.py` — Flask setup, routes, requests, responses
- `02_intermediate.py` — blueprints, error handling, app factory
- `03_jwt_auth.py` — JSON Web Token authentication with Flask
- `04_django_basics.py` — basic Django concepts (comparison to Flask)
- `advanced_qna.md` — advanced Flask Q&A
- `qna.md` — Flask Q&A: app factory, blueprints, SQLAlchemy, JWT, testing, SocketIO, Django comparison

## 03_openai_langchain/ — OpenAI + LangChain
- `01_openai_basics.py` — OpenAI API basics, requests, responses
- `02_langchain_basics.py` — LangChain chains, prompts, memory, parsers
- `03_langchain_agents.py` — agents, tools, agents with tool calling
- `04_advanced_agents.py` — advanced agent patterns, multi-agent orchestration, ReAct, LangGraph, Anthropic SDK agentic patterns
- `advanced_qna.md` — advanced OpenAI/LangChain Q&A
- `qna.md` — OpenAI/LangChain Q&A: function calling, agents, RAG, prompt engineering

## 04_rag_pgvector/ — Retrieval-Augmented Generation + pgvector
- `01_rag_pipeline.py` — end-to-end RAG pipeline (chunking, embedding, retrieval)
- `02_pgvector.sql` — PostgreSQL `pgvector` setup and schema
- `advanced_qna.md` — advanced RAG & embedding Q&A
- `qna.md` — RAG Q&A: embedding, vector search, hybrid search, reranking, chunking strategies

## 05_javascript_node/ — JavaScript, Node.js, Express & TypeScript
- `01_js_basics.js` — JavaScript syntax, data types, functions
- `02_express_basics.js` — Express.js web server basics
- `03_jwt_auth_node.js` — JWT auth in Node/Express
- `04_typescript_basics.ts` — TypeScript basics and typing
- `05_js_patterns.js` — JavaScript design patterns and best practices
- `06_express_advanced.js` — Express advanced: async error handling, custom errors, middleware, WebSockets/Socket.io, streaming, security (helmet/CORS/sanitize), rate limiting, production patterns (graceful shutdown, health checks)
- `07_nodejs_fundamentals.js` — Node.js core: event loop phases, streams, buffers, file system, clustering, worker threads, EventEmitter
- `advanced_qna.md` — advanced JS/Node Q&A
- `qna.md` — Q&A: JS fundamentals (closure, event loop, generators, WeakMap, Symbol), Node.js, Express, TypeScript

## 06_mongodb_mongoose/ — MongoDB + Mongoose
- `01_mongoose_basics.js` — schema, models, CRUD operations
- `02_pymongo.py` — using MongoDB from Python with PyMongo
- `03_mongodb_advanced.js` — aggregation pipelines ($lookup, $facet, $bucket), indexing (compound, TTL, text, geospatial), ACID transactions, schema design patterns, replication, sharding, performance optimization
- `advanced_qna.md` — advanced MongoDB/Mongoose Q&A
- `qna.md` — MongoDB Q&A: aggregation, indexing, transactions, N+1, schema design, change streams, Atlas

## 07_react/ — React and modern frontend
- `01_hooks.jsx` — React hooks basics (`useState`, `useEffect`)
- `02_intermediate_hooks.jsx` — advanced hook patterns
- `03_typescript_react.tsx` — React with TypeScript
- `04_patterns.jsx` — React patterns and component organization
- `05_react_router_suspense.jsx` — React Router v6, code splitting, Suspense, lazy loading, error boundaries, React Query
- `06_react_testing.jsx` — React Testing Library, Jest, mocking, async tests, user-event
- `advanced_qna.md` — advanced React Q&A
- `qna.md` — React Q&A: hooks, memoization, rendering, React Query, testing

## 08_sql/ — SQL query patterns
- `01_basics.sql` — basic SQL queries and fundamentals
- `02_window_ctes.sql` — window functions and CTEs
- `03_sql_advanced.sql` — advanced SQL: JSONB, full-text search, table partitioning, EXPLAIN ANALYZE, conditional aggregation, recursive CTEs, PIVOT patterns, string/date operations
- `advanced_qna.md` — advanced SQL Q&A
- `qna.md` — SQL Q&A: JOINs, window functions, transactions, ACID, indexes, normalization, optimization, SQL vs NoSQL

## 09_rest_security/ — REST API design + security
- `01_rest_design.md` — REST principles and best practices
- `02_security.js` — security patterns for APIs (auth, rate limiting, JWT, RBAC)
- `advanced_qna.md` — advanced REST/security Q&A: OAuth2, PKCE, mTLS, API keys, XSS, CSRF, SSRF, OWASP
- `qna.md` — REST/security Q&A

## 10_dsa/ — Data structures & algorithms
- `01_basics.py` — DSA basics in Python: arrays, linked lists, stacks, queues, heaps, tries, graphs
- `02_problems.py` — 30+ algorithmic problem solutions: sliding window, two pointers, binary search, backtracking, DP
- `03_js_problems.js` — DSA problems in JavaScript
- `advanced_qna.md` — advanced DSA Q&A: complexity, DP patterns, greedy, graph algorithms
- `qna.md` — DSA Q&A

## 11_docker_cicd/ — Docker & CI/CD
- `Dockerfile` — Docker image build instructions
- `docker-compose.yml` — Docker Compose multi-service configuration
- `github_actions.yml` — GitHub Actions CI workflow
- `02_kubernetes_basics.md` — Kubernetes core concepts: Pods, Deployments, Services, Ingress, HPA, ConfigMaps, PersistentVolumes, Helm
- `advanced_qna.md` — advanced Docker/CI Q&A
- `qna.md` — Docker/CI Q&A

## 12_fastapi/ — FastAPI framework
- `01_fastapi_basics.py` — FastAPI basics (endpoints, request models)
- `02_fastapi_advanced.py` — advanced FastAPI: dependencies, auth, middleware, background tasks
- `03_fastapi_websockets.py` — FastAPI WebSockets: echo, broadcast, rooms, JWT auth, binary data, live dashboard, multi-client chat
- `advanced_qna.md` — advanced FastAPI Q&A: WebSockets, file uploads, Alembic migrations, testing with TestClient/AsyncClient, DI patterns, performance, auth, Pydantic traps
- `qna.md` — FastAPI Q&A

## 13_nltk_pandas/ — NLP + data analysis
- `01_nltk_basics.py` — NLTK text processing basics
- `02_pandas_basics.py` — pandas data manipulation basics
- `advanced_qna.md` — advanced NLTK/pandas Q&A: transformers, TF-IDF, sentiment analysis, MultiIndex, pivot/groupby, time series, performance (vectorization, chunking, dtype optimization), Polars comparison
- `qna.md` — NLTK/pandas Q&A

## 14_llm_guards_eval/ — LLM safety and evaluation
- `01_llm_guards.py` — guardrails and safety checks for LLMs
- `02_llm_evaluation.py` — evaluating LLM outputs (RAGAS, metrics)
- `03_mcp_server.py` — MCP server example
- `advanced_qna.md` — advanced LLM safety Q&A: RAGAS, Langfuse, LangSmith, LLM-as-Judge, prompt injection, jailbreaking, hallucination prevention, output validation (Instructor, Guardrails AI), MCP security
- `qna.md` — LLM safety Q&A

## 15_lld_hld/ — Design patterns & system design
- `01_lld_design_patterns.py` — low-level design patterns (OOP): Singleton, Factory, Observer, Strategy, Command, Decorator
- `02_hld_system_design.md` — high-level system design notes: Twitter, URL shortener, cache, system design framework
- `03_solid_principles.py` — SOLID principles with examples
- `advanced_qna.md` — advanced design Q&A: Command/CoR/Mediator/State Machine/Template Method patterns, Twitter timeline, notification system, rate limiter, distributed cache, chat app, CAP theorem, consistent hashing, Saga, CQRS, service mesh
- `qna.md` — design patterns & system design Q&A

## 16_python_tooling/ — Tools for Python development
- `01_pytest_guide.py` — pytest usage and examples: fixtures, parametrize, mocking, async tests
- `02_venv_poetry.md` — virtual environments and Poetry: pip vs pipenv vs poetry vs uv
- `advanced_qna.md` — advanced tooling Q&A: Black/Ruff/isort, mypy strict, pre-commit hooks, Makefile, tox, profiling (cProfile/line_profiler/memory_profiler), structlog, Docker multi-stage, GitHub Actions CI matrix
- `qna.md` — tooling Q&A

## 17_aws_gcp/ — Cloud basics
- `01_aws_basics.md` — AWS fundamentals: EC2, S3, Lambda, RDS, DynamoDB, SQS, SNS, IAM
- `02_gcp_basics.md` — GCP fundamentals: Compute Engine, Cloud Run, BigQuery, Pub/Sub
- `advanced_qna.md` — advanced cloud Q&A
- `qna.md` — cloud Q&A

## 18_interview_prep/ — Interview prep example templates
- `google_example.md` — example interview prep for systems/infrastructure role at Google
- `amazon_example.md` — example interview prep for backend/e-commerce role at Amazon
- `stripe_example.md` — example interview prep for payments role at Stripe
- `README.md` — guidance on using these templates

## 19_state_management/ — Client State Management
- `01_redux.js` — Redux comprehensive: actions, reducers, Redux Toolkit (createSlice/createAsyncThunk/configureStore), entity adapters, Reselect, middleware, Redux Persist, React integration
- `02_zustand.js` — Zustand comprehensive: create, async actions, persist/devtools/immer middleware, slices pattern, vanilla store, React integration
- `qna.md` — State management Q&A: Redux vs Zustand vs Context, immutability, selectors, optimistic updates, race conditions, stale closures

## 20_redis_caching/ — Redis & Caching Strategies
- `01_redis_basics.js` — Redis comprehensive (Node.js): Strings, Hashes, Lists, Sets, Sorted Sets; cache-aside, write-through, cache invalidation; session management, Pub/Sub, distributed locks, rate limiting (fixed/sliding window), HyperLogLog; RDB vs AOF persistence
- `qna.md` — Redis Q&A: data structures, caching patterns, rate limiting, pub/sub, distributed locks, persistence, Redis Cluster

## 21_ai_tools_trending/ — Modern AI Tools, CLI, MCP & Trending Tech
- `01_ai_tools_overview.md` — comprehensive guide: GitHub Copilot, Cursor IDE, Claude Code, Windsurf, Lovable.dev, Bolt.new, Replit Agent, v0 by Vercel, Devin AI, Sweep AI, Codeium, Tabnine, Amazon Q Developer; MCP (Model Context Protocol) architecture, building MCP servers; CLI tools (gh, jq, fzf, httpie, bat, ripgrep, zoxide, aider, warp); Git hooks with husky/lint-staged; AI instruction files (.cursorrules, CLAUDE.md); LangChain, LangGraph, Vercel AI SDK; prompt engineering tips; best practices
- `qna.md` — AI tools Q&A: Copilot vs Cursor, MCP, CLI tools, hooks, LangChain, RAG, future trends, security/ethics, career advice

---

> **Tip:** Start each module with `01_*`, follow the numbering, then review with `qna.md` and `advanced_qna.md`. Use `MASTER_QNA.md` for rapid daily review.
