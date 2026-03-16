# DETAILED INDEX

Comprehensive listing of every file and the topics/sections inside.

---

## Root Files

- **INDEX.md** — Table of contents for all modules, file listing per folder
- **DETAILED_INDEX.md** — This file, detailed section-level index
- **MASTER_QNA.md** — Aggregated Q&A from all major topics for rapid review
- **README.md** — Project overview, study plan, tech stack coverage

---

## 01_python/ — Python Fundamentals to Advanced

- **01_basics.py** — Variables & data types, strings, lists, dicts, sets, tuples, control flow, functions
- **02_intermediate.py** — *args/**kwargs, list/dict comprehensions, lambda, map/filter/zip/enumerate, try/except/finally, custom exceptions
- **03_oop.py** — Classes, `__init__`, instance vs class variables, `__str__`/`__repr__`, inheritance, super(), multiple inheritance, abstract classes, magic methods (`__len__`, `__iter__`, `__eq__`)
- **04_decorators.py** — Decorator basics, `functools.wraps`, parameterized decorators, class decorators, `@property`, `@staticmethod`, `@classmethod`
- **05_generators_context.py** — Generators, `yield`, `yield from`, generator expressions, `__enter__`/`__exit__`, `@contextmanager`
- **06_collections_logging.py** — `Counter`, `defaultdict`, `OrderedDict`, `deque`, `namedtuple`, logging levels/formatters/handlers, file I/O
- **07_patterns_and_variations.py** — Singleton, Factory, Observer, Strategy, Decorator patterns; functional patterns
- **08_async_and_typing.py** — asyncio: `async def`, `await`, `gather`, `wait`, `as_completed`, `Semaphore`, `Queue`, `Task`, `run_in_executor`; type hints: `TypeVar`, `Generic`, `Protocol`, `TypedDict`, `NamedTuple`, `NewType`, `Optional`, `Literal`, `@overload`; `@dataclass` (frozen, post_init, field); metaclasses (`SingletonMeta`, `PluginMeta`); descriptors (`__get__`, `__set__`, `__set_name__`)
- **advanced_qna.md** — Advanced Python deep-dive Q&A
- **qna.md** — Q&A covering: basics (list/tuple/set/dict, `is` vs `==`), functions (*args/**kwargs, lambda), OOP (self, `__str__`/`__repr__`, abstract classes, patterns), decorators, generators, context managers, collections (defaultdict, Counter, deque), exceptions, asyncio (gather, wait, Semaphore, Queue, create_task), type hints (TypeVar, Protocol, TypedDict, Optional, Literal, NewType), dataclasses (frozen, post_init), metaclasses, descriptors, performance (`__slots__`, lru_cache, GIL), tricky questions (mutable defaults, LEGB, `__all__`, `__init__.py`)

---

## 02_flask/ — Flask Web Framework

- **01_basics.py** — Routes, request object, response methods, templates (Jinja2), static files, URL building
- **02_intermediate.py** — Blueprints, app factory pattern, error handlers, config classes, extensions
- **03_jwt_auth.py** — JWT authentication: login/register routes, token generation/verification, protected routes with decorators
- **04_django_basics.py** — Django comparison: models, views, URLs, ORM, admin, manage.py commands
- **advanced_qna.md** — Advanced Flask Q&A: app factory deep-dive, `g` and `current_app`, SQLAlchemy relationships, Celery integration, Flask-SocketIO, testing with `TestClient`, performance tips
- **qna.md** — Q&A: app factory, blueprints, `@login_required`, SQLAlchemy (models/migrations/relationships), JWT, Flask testing, rate limiting, SocketIO, Flask vs Django vs FastAPI

---

## 03_openai_langchain/ — OpenAI API + LangChain

- **01_openai_basics.py** — Chat completions API, `system`/`user`/`assistant` roles, streaming, function calling basics, token counting
- **02_langchain_basics.py** — Chains (LLMChain, SequentialChain), prompt templates (`PromptTemplate`, `ChatPromptTemplate`), memory (`ConversationBufferMemory`, `ConversationSummaryMemory`), output parsers
- **03_langchain_agents.py** — ReAct agents, tools (WebSearch, Calculator, Python REPL), `Agent` vs `AgentExecutor`, structured tool schemas
- **04_advanced_agents.py** — Multi-agent orchestration, LangGraph stateful workflows, `StateGraph` (nodes/edges/conditional edges), Anthropic SDK tool_use patterns, agent memory, parallel tool calls, human-in-the-loop checkpointing
- **advanced_qna.md** — Q&A: function calling internals, RAG in LangChain, custom tools, memory types, agent types (ReAct/OpenAI functions/Plan-and-execute), LangGraph vs LangChain, tracing with LangSmith
- **qna.md** — Q&A: OpenAI API (models, pricing, rate limits), prompt engineering, LangChain core concepts, agents, RAG, streaming

---

## 04_rag_pgvector/ — RAG + pgvector

- **01_rag_pipeline.py** — Text chunking strategies (fixed, recursive, semantic), OpenAI embeddings, pgvector storage, similarity search, query expansion, reranking with cross-encoder
- **02_pgvector.sql** — PostgreSQL setup with `pgvector` extension, embedding column, IVFFlat/HNSW indexes, cosine/L2/dot product operators, hybrid search with `tsvector`
- **advanced_qna.md** — Q&A: chunking strategies (pros/cons), embedding models comparison, HNSW vs IVFFlat, hybrid search (sparse+dense), reranking (cross-encoder, Cohere), RAG evaluation metrics, multi-modal RAG, knowledge graphs
- **qna.md** — Q&A: RAG fundamentals, vector databases, pgvector, embedding, similarity search, hallucination prevention, advanced retrieval

---

## 05_javascript_node/ — JavaScript, Node.js, Express, TypeScript

- **01_js_basics.js** — Variables (const/let/var), data types, functions, array methods (map/filter/reduce), destructuring, spread, template literals, modules
- **02_express_basics.js** — Express setup, routing, `req`/`res` objects, middleware chain, static files, template engines
- **03_jwt_auth_node.js** — JWT strategy, login route, `jsonwebtoken` sign/verify, protected routes middleware, refresh tokens
- **04_typescript_basics.ts** — TypeScript types, interfaces, type aliases, generics, enums, `strictNullChecks`, utility types (Partial/Required/Pick/Omit/Record)
- **05_js_patterns.js** — Design patterns (Module, Singleton, Observer, Factory, Strategy), closures, IIFE, currying, memoization, debounce/throttle
- **06_express_advanced.js** — `asyncHandler` wrapper, custom error classes (`AppError`, `ValidationError`, `NotFoundError`), RBAC (`requireRole`), request ID middleware, rate limiting, `express-validator`, streaming file downloads, SSE (Server-Sent Events), Socket.io authentication (JWT), security middleware (helmet, CORS, mongoSanitize, xss-clean), graceful shutdown, health check endpoint
- **07_nodejs_fundamentals.js** — Event loop phases (timers → I/O → poll → check), `process.nextTick` vs `setImmediate` vs `setTimeout`, streams (Readable/Writable/Transform), Buffer, `fs` (sync/async/stream), clustering (multi-CPU), worker threads vs child processes, EventEmitter (on/emit/once/removeListener), Singleton/Factory/Observer/Middleware Node patterns
- **advanced_qna.md** — Advanced JS/Node Q&A: prototype chain, event delegation, generators, WeakMap, Symbol, Node.js internals, stream backpressure, memory leaks
- **qna.md** — Q&A: const/let/var, hoisting, closures, `this`, arrow functions, prototype chain, Promises (all/allSettled/race/any), async/await, event loop, generators, WeakMap, Symbol, Node.js architecture, process.nextTick, module system, npm, streams, Buffer, clustering, worker threads, EventEmitter, Express middleware, routing, TypeScript utility types, decorators

---

## 06_mongodb_mongoose/ — MongoDB + Mongoose

- **01_mongoose_basics.js** — Schema definition, models, CRUD (save/find/findById/updateOne/deleteOne), populate (references), virtual fields, Mongoose middleware (pre/post hooks), statics vs methods
- **02_pymongo.py** — PyMongo connection, CRUD operations, aggregation pipeline in Python, indexes, bulk operations
- **03_mongodb_advanced.js** — Aggregation: `$match`, `$group`, `$project`, `$lookup`, `$unwind`, `$facet`, `$bucket`, `$bucketAuto`, `$sortByCount`; Indexes: compound (ESR rule), TTL, sparse, text, geospatial (2dsphere); ACID transactions with `startSession()`, `commitTransaction()`, `abortTransaction()`; Schema patterns: embed vs reference, bucket, polymorphic, computed, extended reference, outlier, subset; Replication (oplog, replica set, read preferences); Sharding (range/hash, shard key selection); Performance: `explain()`, covered queries, projection, aggregation optimization; Change streams; Atlas Search; audit logging, soft delete, versioning with `__v`
- **advanced_qna.md** — Advanced Q&A: aggregation pipeline internals, index strategies, transaction limitations, sharding trade-offs, Atlas features
- **qna.md** — Q&A: Mongoose basics, CRUDs, populate, aggregation ($lookup, $facet), N+1 problem, compound index ESR rule, TTL indexes, transactions (4 ACID properties), schema design (embed when to/when not to), change streams, sharding vs replication, MongoDB Atlas

---

## 07_react/ — React & Modern Frontend

- **01_hooks.jsx** — `useState`, `useEffect` (deps array, cleanup), `useRef`, `useCallback`, `useMemo`, `useContext`
- **02_intermediate_hooks.jsx** — `useReducer`, custom hooks (`useDebounce`, `useFetch`, `useLocalStorage`), context + reducer pattern, `useImperativeHandle`
- **03_typescript_react.tsx** — Typed props/state, `React.FC`, `React.ReactNode` vs `React.ReactElement`, event types, generic components, typed context, `forwardRef` with TypeScript
- **04_patterns.jsx** — Higher-Order Components (HOC), Render Props, Compound Components, Controlled vs Uncontrolled, component composition with `children`
- **05_react_router_suspense.jsx** — React Router v6 (`createBrowserRouter`, `<Outlet>`, nested routes, loaders/actions, `useNavigate`, `useParams`, `useLoaderData`), `React.lazy()`, `<Suspense>`, code splitting, error boundaries, React Query (useQuery/useMutation/prefetching/cache invalidation)
- **06_react_testing.jsx** — React Testing Library (`render`, `screen`, `userEvent`, `waitFor`, `within`), Jest setup, mocking (`vi.fn`, `vi.mock`, MSW for API mocks), testing hooks, async tests, snapshot testing, coverage
- **advanced_qna.md** — Advanced React Q&A: reconciliation, React Fiber, concurrent features, Server Components vs Client Components
- **qna.md** — Q&A: hooks rules, `useEffect` dependencies, memoization (useMemo/useCallback/memo), rendering optimizations, React Query vs Redux, testing philosophy, Suspense and error boundaries

---

## 08_sql/ — SQL Query Patterns

- **01_basics.sql** — SELECT with filtering/sorting, GROUP BY/HAVING, all JOIN types (INNER/LEFT/RIGHT/FULL/CROSS/SELF), subqueries (scalar/correlated), INSERT/UPDATE/DELETE, CREATE TABLE/INDEX/VIEW
- **02_window_ctes.sql** — Window functions (ROW_NUMBER, RANK, DENSE_RANK, NTILE, LAG, LEAD, FIRST_VALUE, LAST_VALUE, running totals), CTEs (simple, multiple, chained), recursive CTEs (org chart, date series)
- **03_sql_advanced.sql** — Conditional aggregation (CASE/FILTER), multi-table CTEs with segmentation, PIVOT patterns, string manipulation (SUBSTRING, REGEXP_REPLACE, similarity), date/time ops (EXTRACT, DATE_TRUNC, INTERVAL), JSONB operators (`->`, `->>`, `@>`, `@?`, `jsonb_set`, GIN indexes), full-text search (tsvector/tsquery/ts_rank), table partitioning (range/list/hash), EXPLAIN ANALYZE (seq scan vs index scan, 60x speedup example)
- **advanced_qna.md** — Advanced Q&A: query execution internals, optimizer hints, index-only scans, partial indexes, expression indexes
- **qna.md** — Q&A: JOIN types, window functions vs GROUP BY, CTE vs subquery, ACID (atomicity/consistency/isolation/durability), isolation levels (dirty read/phantom read), B-tree vs Hash vs GIN indexes, normalization (1NF-BCNF), stored procedures vs functions, views vs materialized views, EXPLAIN ANALYZE, SQL vs NoSQL decision matrix

---

## 09_rest_security/ — REST API Design + Security

- **01_rest_design.md** — REST constraints (stateless, uniform interface, layered), HTTP verbs, status codes (2xx/3xx/4xx/5xx), API versioning (URL/header/query param), HATEOAS, REST vs GraphQL vs gRPC, pagination strategies
- **02_security.js** — JWT strategies (HS256/RS256), refresh token rotation, RBAC with permission bits, rate limiting (fixed/sliding window with Redis), bcrypt hashing, input validation, SQL injection prevention, XSS sanitization, CORS configuration, HTTPS/HSTS
- **advanced_qna.md** — Advanced Q&A: OAuth2 flows (authorization code, PKCE, client credentials), OpenID Connect, mTLS, API key management, SSRF prevention, security headers checklist, OWASP Top 10 for APIs
- **qna.md** — Q&A: stateless vs stateful, idempotency, REST best practices, JWT structure/validation, OAuth2 vs JWT, CSRF, XSS, SQL injection, rate limiting, API security checklist

---

## 10_dsa/ — Data Structures & Algorithms

- **01_basics.py** — Arrays, linked lists (singly/doubly), stacks, queues, heaps (min/max, heapq), hash maps, tries, binary trees, BST operations, graphs (adjacency list/matrix), BFS/DFS
- **02_problems.py** — 30+ problems: two sum, longest substring without repeating chars, sliding window maximum, merge intervals, product of array except self, binary search variants, linked list cycle, merge K sorted lists, LRU cache, word break (DP), coin change, longest palindrome, matrix spiral, number of islands, course schedule (topological sort), word ladder, implement trie, Dijkstra's shortest path, and more
- **03_js_problems.js** — DSA problems in JavaScript: closures-based LRU, prototype-based linked list, async producer-consumer
- **advanced_qna.md** — Advanced Q&A: Big-O mastery, DP patterns (knapsack/LCS/matrix-chain), graph algorithms (Bellman-Ford/Floyd-Warshall/Kruskal/Prim), amortized analysis, probabilistic data structures (Bloom filter, Count-Min Sketch)
- **qna.md** — Q&A: complexity (time/space), sorting algorithms, tree traversals, graph BFS/DFS, DP vs greedy, sliding window, two pointers, binary search templates

---

## 11_docker_cicd/ — Docker & CI/CD

- **Dockerfile** — Multi-stage build (builder + runtime stages), non-root user, health check, `.dockerignore`, ENV best practices
- **docker-compose.yml** — Multi-service: app + postgres + redis + nginx, named volumes, health checks, env files, restart policies
- **github_actions.yml** — CI workflow: checkout, setup, lint, test with services (Postgres/Redis), coverage upload, Docker build on merge to main
- **02_kubernetes_basics.md** — Kubernetes architecture (control plane/nodes), core resources (Pod/Deployment/ReplicaSet/Service/Ingress/HPA/ConfigMap/Secret/PersistentVolume), `kubectl` command reference, Helm package manager, resource requests/limits, rolling updates, namespace isolation, RBAC
- **advanced_qna.md** — Advanced Q&A: Docker layer caching, BuildKit, multi-arch builds, container security (non-root, read-only FS), Kubernetes operators, service mesh (Istio), GitOps with ArgoCD
- **qna.md** — Q&A: VM vs container, image vs container, Docker networking modes, volumes, compose vs swarm, GitHub Actions vs Jenkins vs GitLab CI, CD strategies (blue/green, canary), Kubernetes vs Docker Swarm

---

## 12_fastapi/ — FastAPI Framework

- **01_fastapi_basics.py** — ASGI setup, path/query/body params, Pydantic request/response models, path operations, status codes, automatic OpenAPI docs
- **02_fastapi_advanced.py** — Dependency injection (Depends), OAuth2 with JWT, Background Tasks, middleware, CORS, lifespan events (startup/shutdown), response models, custom exceptions
- **03_fastapi_websockets.py** — Basic echo WebSocket, `ConnectionManager` (broadcast/rooms/DMs), multi-room chat server with JSON protocol, live metrics dashboard, JWT-authenticated WebSocket (query param token), binary data handler, HTML test client, Redis pub/sub pattern for horizontal scaling
- **advanced_qna.md** — Q&A: WebSocket auth (why query params not headers), file uploads (`UploadFile`, validation, size limits), Background Tasks vs Celery (comparison table), Alembic migrations (workflow, what autogenerate misses), testing (TestClient, `dependency_overrides`, AsyncClient with pytest-asyncio), sync-in-async blocking pitfall (`run_in_threadpool`), connection pooling, ORJSONResponse, Pydantic v1 vs v2 breaking changes, 7 interview traps, FastAPI vs Flask vs Django comparison table
- **qna.md** — Q&A: FastAPI vs Flask, Pydantic models, path/query/body params, DI patterns, async vs sync handlers, authentication, testing strategies

---

## 13_nltk_pandas/ — NLP + Data Analysis

- **01_nltk_basics.py** — Tokenization, stop words, stemming/lemmatization, POS tagging, named entity recognition, TF-IDF, bag of words, text classification basics
- **02_pandas_basics.py** — DataFrame/Series creation, selection (loc/iloc), filtering, groupby, merge/join, pivot, apply, value_counts, missing data handling
- **advanced_qna.md** — Q&A: HuggingFace `pipeline()` for sentiment/NER/summarization/QA, embeddings (CLS vs mean pooling), TF-IDF with `ngram_range`, sklearn Pipeline, `cross_val_score`, VADER for social media, Pandas MultiIndex (creation/selection/stack/unstack), pivot_table vs groupby vs crosstab, time series (resample/shift/diff/pct_change/rolling/ewm), performance (vectorized vs apply, chunked CSV, dtype optimization with `category`/downcast), Polars comparison, 6 interview traps (SettingWithCopyWarning, iterrows slowness, inplace=True misconception, merge vs join vs concat, mutable defaults, Pandas 2.x observed=False)
- **qna.md** — Q&A: NLP pipeline, regex, TF-IDF, word embeddings, DataFrame operations, groupby, merge types, time series, pandas optimization

---

## 14_llm_guards_eval/ — LLM Safety & Evaluation

- **01_llm_guards.py** — Input/output guardrails, PII detection, toxicity filtering, topic restriction, prompt injection detection, NeMo Guardrails Colang rules
- **02_llm_evaluation.py** — RAGAS metrics (faithfulness, answer relevancy, context precision/recall), human evaluation frameworks, automated scoring
- **03_mcp_server.py** — MCP server implementation: tool definitions, resource handlers, prompt templates, `SecureMCPWrapper` with rate limiting and audit logging
- **advanced_qna.md** — Q&A: RAGAS all four metrics (how faithfulness scoring works step-by-step), Langfuse (`@observe`, manual trace/span/generation, session tracing), LangSmith (`@traceable`, `evaluate()`, datasets), LLM-as-Judge (structured output with Pydantic, pairwise A/B evaluation, 4 judge biases), prompt injection (direct/indirect RAG, 6 prevention strategies), jailbreaking vs prompt injection comparison, jailbreaking techniques (DAN, many-shot, crescendo, token smuggling, multi-language), LLM safety taxonomy (8 categories), hallucination prevention (5 strategies), output validation (Instructor with `max_retries`, Guardrails AI validators), agentic evaluation (trajectory/outcome/efficiency/tool validity), MCP security (tool poisoning, HMAC verification, security checklist)
- **qna.md** — Q&A: evaluation metrics, RLHF, Constitutional AI, guardrails types, red-teaming, alignment techniques

---

## 15_lld_hld/ — Low-Level & High-Level Design

- **01_lld_design_patterns.py** — GoF patterns with Python: Singleton (thread-safe), Factory (shape/transport/logger factories), Observer (event emitter), Strategy (sort/payment strategies), Command (undo/redo queue), Decorator (caching/logging), Builder, Abstract Factory
- **02_hld_system_design.md** — System design framework (requirements → estimates → API → data model → high-level → deep dive → scale), URL shortener (Base62 vs MD5, read-heavy optimization), Twitter feed (fan-out-on-write vs fan-out-on-read), rate limiter (token bucket algorithm), CDN and load balancer patterns
- **03_solid_principles.py** — S: Single Responsibility, O: Open/Closed, L: Liskov Substitution, I: Interface Segregation, D: Dependency Inversion — each with violates-then-fixes examples
- **advanced_qna.md** — Q&A: Command/Chain of Responsibility/Mediator/State Machine/Template Method/Iterator/Proxy patterns with full examples; Twitter timeline (fan-out-on-write vs read, celebrity problem, hybrid model); Notification system (Kafka per channel, idempotency keys, retry backoff); Rate limiter (token bucket vs sliding window, Redis Lua atomic script); Distributed cache (consistent hashing, virtual nodes, thundering herd with Redis NX); URL Shortener (301 vs 302 analytics tradeoff, zookeeper for IDs); Chat app (WebSocket + Redis Pub/Sub, Cassandra TIMEUUID, delivery receipts); CAP theorem with PACELC extension; Saga pattern (choreography vs orchestration); Event Sourcing; CQRS; service mesh with Istio YAML; API Gateway with BFF pattern
- **qna.md** — Q&A: all 23 GoF patterns summary, SOLID principles, DRY/KISS/YAGNI, CAP theorem, microservices vs monolith, CQRS, event sourcing, system design interview template

---

## 16_python_tooling/ — Python Development Tools

- **01_pytest_guide.py** — pytest basics, fixtures (function/class/session scope), parametrize with `pytest.param`, marks (skip/xfail/slow), monkeypatch, `tmp_path`, async tests with `pytest-asyncio`, coverage with `pytest-cov`
- **02_venv_poetry.md** — venv, virtualenv, pipenv, Poetry (pyproject.toml, lock file, scripts, publish), uv (fastest), comparison table (pip vs pipenv vs poetry vs uv)
- **advanced_qna.md** — Q&A: Black configuration (pyproject.toml settings), Ruff (rule selection E/W/F/I/N/UP/B/S/C90), isort with Black profile, flake8 config; mypy strict mode, Generics with TypeVar/Generic[T], Protocols with @runtime_checkable, TypedDict with NotRequired; pre-commit config with Ruff/mypy hooks + CI integration; Makefile with auto-documentation (help target); tox matrix (Python 3.9-3.12 + lint + type environments); profiling (cProfile + snakeviz, line_profiler @profile, memory_profiler + tracemalloc); pytest advanced (stacked @parametrize, factory fixtures, snapshot testing with syrupy); pdb/ipdb commands; structlog structured logging; Docker multi-stage (builder + runtime, .dockerignore, ENV vars); complete GitHub Actions workflow with services/matrix/Codecov
- **qna.md** — Q&A: pytest fundamentals, black/flake8/mypy comparison, virtual environments, packaging (wheel/sdist), pre-commit hooks, CI/CD integration

---

## 17_aws_gcp/ — Cloud Platforms

- **01_aws_basics.md** — EC2 (instance types, AMIs, security groups), S3 (presigned URLs, lifecycle, Storage Classes), Lambda (cold starts, layers, SAM), RDS vs Aurora vs DynamoDB, SQS/SNS (message queue patterns), API Gateway, IAM (roles/policies/least privilege), VPC, CloudWatch, Elastic Beanstalk vs ECS vs EKS
- **02_gcp_basics.md** — Compute Engine, Cloud Run (serverless containers), GKE, BigQuery (partitioning/clustering, cost optimization), Cloud Storage, Pub/Sub, Cloud SQL, Firestore, Cloud Functions, IAM, gcloud CLI
- **advanced_qna.md** — Q&A: AWS vs GCP comparison, serverless trade-offs, multi-region architecture, disaster recovery (RTO/RPO), cost optimization (Spot/Preemptible), S3 + CloudFront CDN, Lambda cold start mitigation, DynamoDB single-table design
- **qna.md** — Q&A: IaaS/PaaS/SaaS, core services, when to use each service, cloud security, cost management basics

---

## 18_interview_prep/ — Interview Preparation Templates

- **google_example.md** — Prep for Google SWE/infrastructure: behavioral (STAR format), system design (distributed systems focus), coding (LeetCode patterns), culture (ownership, innovation)
- **amazon_example.md** — Prep for Amazon SDE: Leadership Principles with STAR stories, behavioral scenarios, system design (high availability, event-driven), coding (arrays/graphs/DP)
- **stripe_example.md** — Prep for Stripe backend: payments domain knowledge, API design principles, distributed systems (idempotency, consistency), security-first mindset
- **README.md** — How to use these templates: customize company facts, practice STAR stories, mock interview schedule

---

## 19_state_management/ — Client State Management

- **01_redux.js** — Redux basics (actions, action creators, reducers, createStore, dispatch, subscribe); React-Redux (Provider, useSelector, useDispatch); Redux Toolkit: `createSlice` (Immer-backed mutation), `createAsyncThunk` (pending/fulfilled/rejected), `configureStore`, `createEntityAdapter` (normalized state, selectAll/selectById/selectIds); Reselect `createSelector` (memoized, composed selectors, TodoStats example); Redux middleware (loggerMiddleware, analyticsMiddleware); Redux Persist (persistConfig, whitelist/blacklist, PersistGate); Redux DevTools
- **02_zustand.js** — `create` with `set`/`get`, async actions (fetchUser), subscribeWithSelector, `useStore(selector)` for selective subscriptions; Middleware: `persist` (localStorage), `devtools` (Redux DevTools), `immer` (mutable-style), `combine`; Slices pattern (createUserSlice, createTodoSlice, merge); Vanilla store (`createStore`); React integration (Counter, TodoList), comparison with Redux/Context
- **qna.md** — Q&A: Redux core principles, reducer (pure function), actions, action creators, createSlice, createAsyncThunk, useSelector/useDispatch, selector vs Reselect, middleware signature, Redux Persist, DevTools; Zustand createStore, async, persist, devtools, immer middleware, slices pattern, vanilla store, bundle size; General: state management philosophy, prop drilling, Observer pattern, immutability, Context API pitfalls, optimistic/pessimistic updates, client state vs server state (React Query/SWR), race conditions, stale closures, memory leaks, testing (mock store)

---

## 20_redis_caching/ — Redis & Caching

- **01_redis_basics.js** — Node.js ioredis client; **5 Data Types**: Strings (SET/GET/INCR/EXPIRE/SETNX/GETSET), Hashes (HSET/HGET/HGETALL/HINCRBY), Lists (LPUSH/RPUSH/LPOP/LRANGE/BLPOP), Sets (SADD/SMEMBERS/SRANDMEMBER/SINTERSTORE), Sorted Sets (ZADD/ZRANK/ZRANGEBYSCORE/ZRANGEBYLEX); **Caching Patterns**: cache-aside (read: cache miss → DB → cache fill), write-through (write: cache then DB), cache invalidation (tag-based, key-based); **Session Management**: JSON serialization, sliding expiry, atomic operations; **Pub/Sub**: publisher/subscriber with message routing; **Distributed Locks**: SET NX PX with auto-expiry, lock retry with jitter; **Rate Limiting**: fixed window (INCR + EXPIRE), sliding window (sorted set + ZREMRANGEBYSCORE + ZCARD); **HyperLogLog**: approximate cardinality (PFADD/PFCOUNT); **Persistence**: RDB (point-in-time snapshots) vs AOF (append-log); **Redis Cluster**: horizontal sharding, hash slots (16384), masters + replicas
- **qna.md** — Q&A: Redis vs Memcached (persistence/data structures), 5 data types with use cases, cache-aside vs write-through vs write-behind, TTL strategies, cache stampede (dog-piling) prevention (mutex lock/probabilistic early expiry/stale-while-revalidate), session storage (vs cookie/JWT), pub/sub vs message queues (Kafka/RabbitMQ), distributed lock (Redlock algorithm), rate limiting implementations, HyperLogLog precision (0.81% std error), persistence comparison (RDB: lower overhead/data loss risk, AOF: durable/larger files), Redis Cluster (hash slots, CROSSSLOT error), when NOT to use Redis

---

## 21_ai_tools_trending/ — AI Tools, MCP, CLI & Trending Tech

- **01_ai_tools_overview.md** — **AI Code Assistants**: GitHub Copilot (inline autocomplete, pricing), Cursor IDE (Cmd+K chat, Cmd+L edit, codebase search), Claude Code (terminal agent, CLAUDE.md instructions, autonomous multi-step tasks), Windsurf (Cascade multi-file agent, supercomplete), Lovable.dev (React + Supabase full-stack generation, GitHub sync), Bolt.new (browser-run full-stack, WebContainers), Replit Agent (autonomous full-stack builder), v0 by Vercel (UI component generator), Devin AI (autonomous software engineer), Zed Editor (Rust-native, real-time collab), JetBrains AI (IDE-native assistant), Amazon Q Developer (AWS deep integration, security scanning), Codeium (free forever), Tabnine (local/enterprise); **Comprehensive comparison table** (price/category/best-for); **MCP Architecture**: client/server/JSON-RPC protocol, building MCP server in Python (database query tool), `mcpServers` config, Tools/Resources/Prompts concepts, MCP use cases; **CLI Tools**: `gh` (GitHub CLI), `jq` (JSON processor), `fzf` (fuzzy finder), `httpie` (HTTP client), `tldr`, `bat`, `ripgrep`, `zoxide`, `aider` (AI terminal coding), `warp` (AI terminal), GitHub Copilot CLI; **Hooks/Skills/Instructions**: Git hooks (pre-commit, pre-push), `husky` + `lint-staged`, `.cursorrules` (Cursor project instructions), `.github/copilot-instructions.md`, CLAUDE.md; **Trending Frameworks**: LangChain (chains/memory/tools), LangGraph (StateGraph nodes/edges/conditional), Vercel AI SDK (streamText, useChat hook); **More tools**: v0, Bolt.new, Replit Agent, Devin AI, Sweep AI; **Prompt Engineering**: specificity, context, format, few-shot examples, task decomposition; **Best Practices**: always review AI code, iterate, keep context focused
- **qna.md** — Q&A: GitHub Copilot, Cursor, Claude Code (vs Cursor), Windsurf, Lovable.dev vs Bolt.new, v0, Devin AI, Amazon Q Developer, Zed Editor, Replit Agent, aider, MCP (what/why/components/use cases/Tools vs Resources/how to build), CLI tools (why CLI, essential tools, jq, fzf, AI-powered CLI), Git hooks (pre-commit/pre-push/commit-msg, husky, lint-staged), AI instructions (.cursorrules/CLAUDE.md), LangChain, LangGraph, Vercel AI SDK, RAG, function calling, prompt engineering, productivity tips, AI ethics (privacy/copyright/jobs), future trends (autonomous agents, voice coding), career advice (skills that matter more/less)

---

> **How to use:** Start each module at `01_*.py/js/md`, progress numerically, then reinforce with `qna.md`. For advanced preparation, work through `advanced_qna.md`. The `MASTER_QNA.md` aggregates the highest-value questions for quick daily revision.
