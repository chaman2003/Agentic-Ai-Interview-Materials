# LLD / HLD — Advanced Q&A (Design Patterns + System Design)

---

## ADVANCED DESIGN PATTERNS

**Q: What is the Command pattern and when do you use it?**
A: Encapsulates a request as an object, allowing you to parameterize clients with different requests, queue or log requests, and support undo/redo.
```python
from abc import ABC, abstractmethod
from typing import List

class Command(ABC):
    @abstractmethod
    def execute(self): ...
    @abstractmethod
    def undo(self): ...

class AddItemCommand(Command):
    def __init__(self, cart, item):
        self.cart = cart
        self.item = item

    def execute(self):
        self.cart.items.append(self.item)

    def undo(self):
        self.cart.items.remove(self.item)

class CommandHistory:
    def __init__(self):
        self._history: List[Command] = []

    def execute(self, cmd: Command):
        cmd.execute()
        self._history.append(cmd)

    def undo(self):
        if self._history:
            self._history.pop().undo()
```
Use when: text editor undo/redo, task queues, transaction logs, macro recording.

**Q: What is the Chain of Responsibility pattern?**
A: Passes a request along a chain of handlers. Each handler decides to process or pass to the next. Decouples sender from receiver.
```python
class Handler(ABC):
    def __init__(self):
        self._next: Handler | None = None

    def set_next(self, handler: 'Handler') -> 'Handler':
        self._next = handler
        return handler   # allows chaining: auth.set_next(rate_limit).set_next(log)

    def handle(self, request):
        if self._next:
            return self._next.handle(request)
        return None

class AuthHandler(Handler):
    def handle(self, request):
        if not request.get('token'):
            return {'error': 'Unauthorized', 'status': 401}
        return super().handle(request)

class RateLimitHandler(Handler):
    def handle(self, request):
        if is_rate_limited(request['user_id']):
            return {'error': 'Too Many Requests', 'status': 429}
        return super().handle(request)

# Build chain
auth = AuthHandler()
auth.set_next(RateLimitHandler()).set_next(LogHandler()).set_next(BusinessHandler())
```
Use when: HTTP middleware pipelines, event processing, approval workflows.

**Q: What is the Mediator pattern?**
A: Defines an object that encapsulates how a set of objects interact. Components communicate through the mediator instead of directly with each other. Reduces coupling from O(n²) to O(n).
```python
class ChatRoom:           # Mediator
    def __init__(self):
        self._users: dict = {}

    def register(self, user):
        self._users[user.name] = user
        user.set_mediator(self)

    def send(self, message: str, sender, recipient_name: str | None = None):
        if recipient_name:
            self._users[recipient_name].receive(message, sender.name)
        else:
            for name, user in self._users.items():
                if name != sender.name:
                    user.receive(message, sender.name)

class User:
    def __init__(self, name):
        self.name = name
        self._mediator = None

    def set_mediator(self, mediator):
        self._mediator = mediator

    def send(self, message, to=None):
        self._mediator.send(message, self, to)

    def receive(self, message, from_name):
        print(f"[{self.name}] from {from_name}: {message}")
```
Use when: chat systems, air traffic control, UI form validation where fields affect each other.

**Q: What is the State Machine pattern?**
A: An object's behavior changes based on its internal state. Eliminates large if/elif chains; each state is its own class.
```python
from enum import Enum, auto

class OrderState(Enum):
    PENDING = auto()
    CONFIRMED = auto()
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

VALID_TRANSITIONS = {
    OrderState.PENDING:    {OrderState.CONFIRMED, OrderState.CANCELLED},
    OrderState.CONFIRMED:  {OrderState.SHIPPED,   OrderState.CANCELLED},
    OrderState.SHIPPED:    {OrderState.DELIVERED},
    OrderState.DELIVERED:  set(),
    OrderState.CANCELLED:  set(),
}

class Order:
    def __init__(self):
        self.state = OrderState.PENDING

    def transition(self, new_state: OrderState):
        if new_state not in VALID_TRANSITIONS[self.state]:
            raise ValueError(f"Cannot go from {self.state} to {new_state}")
        self.state = new_state
```
Use when: order workflows, CI/CD pipeline stages, game character states, connection lifecycle.

**Q: What is the Template Method pattern?**
A: Defines the skeleton of an algorithm in a base class, deferring specific steps to subclasses. The structure is fixed; implementations vary.
```python
class DataPipeline(ABC):
    # Template method — defines the algorithm
    def run(self):
        raw = self.extract()
        clean = self.transform(raw)
        self.load(clean)
        self.notify_completion()

    @abstractmethod
    def extract(self): ...

    @abstractmethod
    def transform(self, data): ...

    @abstractmethod
    def load(self, data): ...

    def notify_completion(self):   # optional override (hook)
        print("Pipeline done")

class CSVPipeline(DataPipeline):
    def extract(self):   return read_csv('data.csv')
    def transform(self, data): return clean_and_normalize(data)
    def load(self, data):      return write_to_postgres(data)
```
Use when: report generation, data ETL pipelines, multi-step build processes.

**Q: What is the Iterator pattern?**
A: Provides a standard way to traverse a collection without exposing its underlying representation. Python's `__iter__` and `__next__` protocols implement this natively.
```python
class PaginatedIterator:
    """Iterate over API pages transparently"""
    def __init__(self, fetch_fn, page_size=100):
        self.fetch_fn = fetch_fn
        self.page_size = page_size
        self.page = 0
        self.buffer = []

    def __iter__(self):
        return self

    def __next__(self):
        if not self.buffer:
            data = self.fetch_fn(page=self.page, size=self.page_size)
            if not data:
                raise StopIteration
            self.buffer = data
            self.page += 1
        return self.buffer.pop(0)

# Usage — consumer doesn't know about pagination
for user in PaginatedIterator(fetch_users):
    process(user)
```

**Q: What is the Proxy pattern and its variants?**
A: A proxy controls access to another object. Common variants:
- **Virtual proxy** — lazy initialization (don't create heavy object until needed)
- **Protection proxy** — access control
- **Caching proxy** — memoize expensive calls
- **Remote proxy** — local facade for a remote service

```python
class CachingProxy:
    def __init__(self, real_service):
        self._service = real_service
        self._cache = {}

    def get_user(self, user_id):
        if user_id not in self._cache:
            self._cache[user_id] = self._service.get_user(user_id)
        return self._cache[user_id]

# Python's functools.lru_cache is a caching proxy decorator
```

---

## SYSTEM DESIGN EXERCISES

**Q: Design Twitter/X Timeline feed (at scale: 500M users, 500M tweets/day).**
A:

**Functional requirements:**
- Post tweets (text, images, video)
- Follow/unfollow users
- See home timeline (tweets from followed users, ranked by recency/relevance)
- See user profile timeline

**Approach 1 — Fan-out on write (push model):**
When a user tweets, immediately write to each follower's timeline cache (Redis sorted set by timestamp).
- Timeline read = O(1) Redis read. Fast for most users.
- Problem: celebrity with 100M followers → 100M Redis writes per tweet (write amplification).

**Approach 2 — Fan-out on read (pull model):**
When a user opens timeline, fetch tweets from everyone they follow and merge.
- Problem: following 2,000 people → 2,000 queries on read.

**Hybrid (Twitter's actual approach):**
- Regular users: fan-out on write → pre-populate timeline in Redis.
- Celebrities (>1M followers): fan-out on read, merged in at timeline request time.
- Threshold is dynamic based on follower count.

**Key components:**
```
Client → CDN (media) → API Gateway → Tweet Service
                                    ↓
                              Message Queue (Kafka)
                                    ↓
                         Fanout Service → Redis (timelines)
                                    ↓
                            Timeline Service ← Redis
                         Tweet DB (Cassandra, by user_id)
                         User DB (MySQL, followers graph)
                         Media Storage (S3 + CDN)
```

**Data model (Cassandra):**
```
tweets: (tweet_id UUID, user_id, content, media_urls, created_at, likes_count)
timelines: (user_id, tweet_id, score DOUBLE)  // Redis sorted set
followers: (user_id → set of follower_ids)    // Redis set or graph DB
```

---

**Q: Design a Notification System (email, SMS, push — multi-channel, at scale).**
A:

**Requirements:** Support email, SMS, push, in-app. Reliable delivery, deduplication, rate limiting per user, template rendering, analytics.

**Architecture:**
```
Service A (Order) ──┐
Service B (Auth)  ──┤→ Notification API → Queue (Kafka)
Service C (Pay)   ──┘                         ↓
                               ┌──────────────┴───────────────┐
                               ↓              ↓               ↓
                          Email Worker   SMS Worker    Push Worker
                          (AWS SES)      (Twilio)      (FCM/APNs)
                               ↓
                         Delivery DB (Postgres)  ← Status webhooks
```

**Key design decisions:**
1. **Kafka topics per channel** — `notifications.email`, `notifications.sms`, `notifications.push`. Each has independent consumers and dead-letter queues.
2. **Idempotency key** — each notification request carries a unique key; workers deduplicate before sending.
3. **Template Service** — renders HTML/text templates with user data, stored in S3.
4. **Rate Limiter** — Redis sliding window: max N notifications per user per hour per channel.
5. **Retry with backoff** — transient failures (provider down) retry with exponential backoff; permanent failures (invalid number) go to DLQ.
6. **Delivery tracking** — webhooks from providers (SES bounce, Twilio delivery receipt) update Postgres `notification_logs` table.
7. **User preferences** — per-channel opt-out stored in Redis; checked before enqueuing.

---

**Q: Design a Rate Limiter (distributed, at scale).**
A:

**Algorithms:**

1. **Token Bucket** — bucket holds up to N tokens; refilled at rate R/sec. Allows bursts. Flexible.
2. **Fixed Window Counter** — count requests in 1-minute windows. Simple, but spike at window boundary allows 2x rate.
3. **Sliding Window Log** — store exact timestamps of each request. Accurate, memory intensive.
4. **Sliding Window Counter** — hybrid: weighted sum of current and previous window count. Accurate + efficient.

**Redis implementation (sliding window counter):**
```python
import redis
import time

r = redis.Redis()

def is_allowed(user_id: str, limit: int = 100, window_sec: int = 60) -> bool:
    now = time.time()
    window_start = now - window_sec
    key = f"rate:{user_id}"

    pipe = r.pipeline()
    # Remove old entries outside window
    pipe.zremrangebyscore(key, 0, window_start)
    # Count remaining
    pipe.zcard(key)
    # Add current request with timestamp as score
    pipe.zadd(key, {str(now): now})
    # Expire key to save memory
    pipe.expire(key, window_sec * 2)
    results = pipe.execute()

    current_count = results[1]
    return current_count < limit

# With Lua script for atomicity (production pattern):
LUA_SCRIPT = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
local count = redis.call('ZCARD', key)
if count < limit then
    redis.call('ZADD', key, now, now)
    redis.call('EXPIRE', key, window * 2)
    return 1
end
return 0
"""
```

**Distributed considerations:** Use Redis Cluster with consistent hashing for sharding rate limit keys. Return `Retry-After` header on 429. Implement different limits per tier (free/pro/enterprise).

---

**Q: Design a Distributed Cache (like Redis or Memcached at scale).**
A:

**Core requirements:** Sub-millisecond reads, high availability, eviction policies, distributed across nodes.

**Architecture decisions:**

1. **Consistent hashing** — map cache keys to nodes using a hash ring. Adding/removing a node only remaps ~1/N keys (vs modulo hashing which remaps nearly all).

2. **Replication** — each shard has 1 primary + 1-2 replicas. Reads can go to replicas. Leader election via Raft or Redis Sentinel.

3. **Eviction policies** — LRU (Least Recently Used) most common. Also: LFU (Least Frequently Used), TTL-based, random, no-eviction.

4. **Cache patterns:**
   - **Cache-aside** (lazy loading): app checks cache → miss → query DB → write to cache
   - **Write-through**: write to cache AND DB synchronously. Always consistent, slower writes.
   - **Write-behind** (write-back): write to cache immediately, DB async. Fast writes, risk of data loss.
   - **Read-through**: cache populates itself on miss, transparent to app.

5. **Cache stampede prevention (thundering herd):**
```python
import asyncio
import redis

async def get_with_lock(r, key, fetch_fn, ttl=3600):
    val = r.get(key)
    if val:
        return val
    # Set a lock to prevent multiple DB calls
    lock_key = f"{key}:lock"
    got_lock = r.set(lock_key, "1", nx=True, ex=10)   # NX = only if not exists
    if got_lock:
        val = await fetch_fn()
        r.setex(key, ttl, val)
        r.delete(lock_key)
    else:
        await asyncio.sleep(0.05)    # wait and retry
        return await get_with_lock(r, key, fetch_fn, ttl)
    return val
```

---

**Q: Design a URL Shortener (with collision handling, analytics, scale).**
A:

**Functional requirements:** Shorten URL, redirect, custom aliases, expiry, click analytics.
**Scale:** 100M URLs, 10B redirects/day (~115K RPS on redirects).

**Key generation strategies:**

Option A — Counter-based + Base62 encode:
```python
import string
BASE62 = string.ascii_letters + string.digits  # 62 chars

def encode(n: int) -> str:
    result = []
    while n:
        result.append(BASE62[n % 62])
        n //= 62
    return ''.join(reversed(result)).zfill(6)   # e.g., counter 1000000 → 'hSBy'
```
Problem: predictable, sequential. Requires a distributed counter (Redis INCR or DB sequence).

Option B — MD5/SHA256 + take first 7 chars:
```python
import hashlib
def shorten(long_url: str) -> str:
    return hashlib.md5(long_url.encode()).hexdigest()[:7]
```
Problem: **collision handling needed** — two different URLs could produce same 7-char prefix.

```python
def shorten_with_collision_handling(long_url: str, attempt: int = 0) -> str:
    key = hashlib.md5((long_url + str(attempt)).encode()).hexdigest()[:7]
    if exists_in_db(key) and get_url(key) != long_url:
        return shorten_with_collision_handling(long_url, attempt + 1)
    return key
```

**Data model:**
```sql
CREATE TABLE urls (
    short_code  CHAR(7) PRIMARY KEY,
    long_url    TEXT NOT NULL,
    user_id     INT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    expires_at  TIMESTAMPTZ,
    click_count BIGINT DEFAULT 0
);
-- Analytics: async writes to Kafka → ClickHouse for aggregations
```

**Redirect flow:** Client → CDN (cache popular codes) → API → Redis (hot URLs) → Postgres → 301/302 redirect. Write click event to Kafka async (never block the redirect).

**301 vs 302:** 302 (temporary) is preferred for analytics — browsers don't cache it, every click hits your servers. 301 (permanent) reduces server load but breaks analytics.

---

**Q: Design a Chat Application (real-time, group chat, at scale).**
A:

**Requirements:** 1-on-1 and group chat, message history, online presence, typing indicators, message delivery receipts.

**Connection layer — WebSockets:**
```
Client ←──WebSocket──→ Chat Server (stateful, per connection)
                              ↓
                        Redis Pub/Sub  (broadcast to other servers)
                              ↓
                     Message Queue (Kafka) → Message Store (Cassandra)
```

**Why Redis Pub/Sub for inter-server broadcast:**
- Users A and B may be connected to different Chat Server instances
- When A sends to B: Chat Server 1 publishes to Redis channel `user:{B.id}`
- Chat Server 2 (where B is connected) subscribes and pushes to B's WebSocket

**Message storage (Cassandra schema):**
```
CREATE TABLE messages (
    conversation_id UUID,
    message_id      TIMEUUID,  -- TimeUUID: encodes timestamp + unique
    sender_id       UUID,
    content         TEXT,
    status          TEXT,      -- 'sent', 'delivered', 'read'
    PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```
Cassandra: write-optimized, time-series queries by conversation_id, horizontal scale.

**Delivery guarantees:**
- Client sends message → server ACKs with message_id → client marks as "sent"
- Recipient's server delivers → sends delivery receipt back through the same pipeline
- Recipient opens chat → sends "read" receipt

**Online presence:** Redis hash `presence:{user_id} → {server_id, last_seen}`. TTL of 30s refreshed via heartbeat ping. Absence of key means offline.

---

## CAP THEOREM DEEP DIVE

**Q: Explain CAP theorem. What does it mean in practice?**
A: In a distributed system that must handle network partitions (P is not optional in practice), you choose between:
- **CP (Consistency + Partition Tolerance):** All nodes return the same data OR return an error. No stale reads. Examples: HBase, Zookeeper, etcd, MongoDB (strong consistency mode).
- **AP (Availability + Partition Tolerance):** System always returns a response, but it might be stale. Examples: Cassandra, DynamoDB, CouchDB.

**PACELC extension:** Even without a partition, there's a latency vs consistency tradeoff. Low latency needs fewer replica acknowledgments (risk of inconsistency). Full consistency requires waiting for all replicas (higher latency).

| System      | During Partition | Normal Operation |
|-------------|-----------------|-----------------|
| Cassandra   | AP              | Low latency     |
| DynamoDB    | AP              | Low latency     |
| MongoDB     | CP (configurable)| Low latency    |
| PostgreSQL  | CP              | Low latency     |
| Zookeeper   | CP              | Higher latency  |

---

## CONSISTENT HASHING

**Q: What is consistent hashing and why is it important?**
A: A technique for distributing data across nodes where adding or removing a node only remaps ~1/N of the keys (vs modulo hashing which remaps nearly everything).

**How it works:**
1. Map both nodes and keys onto a ring (0 to 2³²)
2. Each key belongs to the next clockwise node on the ring
3. When a node is added: only keys between it and its predecessor are remapped
4. When a node is removed: only its keys move to the next node

**Virtual nodes (vnodes):** Each physical node gets multiple positions on the ring. Ensures better load distribution and smoother rebalancing when nodes have different capacities.

**Used in:** Cassandra, Amazon DynamoDB, distributed caches, load balancers.

---

## SAGA PATTERN

**Q: What is the Saga pattern and why is it needed in microservices?**
A: In a microservices architecture, a single business transaction spans multiple services. Since each service has its own DB, you can't use a single ACID transaction. The Saga pattern splits a distributed transaction into a sequence of local transactions with compensating transactions for rollback.

**Two approaches:**

**Choreography:** Services emit events; each listens and reacts. No central coordinator. Simple, but hard to track and debug.
```
Order Service  → emit "OrderCreated"
Payment Service → consume → process payment → emit "PaymentCompleted"
Inventory Service → consume → reserve stock → emit "StockReserved"
Shipping Service → consume → create shipment
```

**Orchestration:** A central Saga Orchestrator sends commands and reacts to replies. Easier to visualize and debug; single point of failure concern.
```
Saga Orchestrator:
  1. → cmd: ProcessPayment   → Payment Service
  2. ← reply: PaymentOK
  3. → cmd: ReserveInventory → Inventory Service
  4. ← reply: OutOfStock      ← FAILURE
  5. → cmd: RefundPayment    → Payment Service (compensate)
```

---

## EVENT SOURCING AND CQRS

**Q: What is Event Sourcing?**
A: Instead of storing the CURRENT state of an entity, store the SEQUENCE OF EVENTS that led to that state. The current state is derived by replaying events.

```python
# Traditional: store current balance
account = {"id": 1, "balance": 850}  # opaque — how did we get here?

# Event sourcing: store events
events = [
    {"type": "AccountOpened",  "amount": 1000, "ts": "..."},
    {"type": "Withdrawal",     "amount": 200,  "ts": "..."},
    {"type": "Deposit",        "amount": 50,   "ts": "..."},
    # Current balance = 1000 - 200 + 50 = 850
]
```

Benefits: Full audit trail, time travel (replay to any point), event replay for new projections, easier debugging.
Challenges: Query complexity, eventual consistency, event schema evolution, storage grows unboundedly (mitigate with snapshots).

**Q: What is CQRS (Command Query Responsibility Segregation)?**
A: Separate the write model (commands that change state) from the read model (queries that return data). Often combined with Event Sourcing.

```
Write Side: OrderService.place_order(cmd) → validates → appends to event store → emits OrderPlaced event
                                                                                          ↓
Read Side: Event Handler updates read-optimized projections (denormalized SQL views, Elasticsearch, Redis)
         → OrderQueryService.get_order(id) reads from projection (fast, no joins)
```

Benefits: Optimize reads and writes independently, scale read replicas, polyglot persistence (different DBs for reads vs writes).

---

## SERVICE MESH

**Q: What is a service mesh and what does Istio do?**
A: A service mesh is an infrastructure layer for managing service-to-service communication, offloading cross-cutting concerns from application code.

**Istio architecture:**
- **Data plane:** Envoy sidecar proxies injected alongside each service container. Intercept all inbound/outbound traffic.
- **Control plane (Istiod):** Configures the Envoy proxies via xDS APIs.

**What Istio handles:**
1. **mTLS everywhere** — automatic mutual TLS between services (zero-trust networking)
2. **Traffic management** — canary deployments (route 5% traffic to new version), A/B testing, circuit breaking
3. **Observability** — distributed tracing (Jaeger), metrics (Prometheus), access logs — all without code changes
4. **Fault injection** — inject artificial delays/errors to test resilience
5. **Rate limiting** — Envoy-level rate limiting without application code

```yaml
# Istio VirtualService: canary deployment (10% to v2)
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
spec:
  hosts: ["product-service"]
  http:
  - route:
    - destination:
        host: product-service
        subset: v1
      weight: 90
    - destination:
        host: product-service
        subset: v2
      weight: 10
```

---

## API GATEWAY PATTERNS

**Q: What does an API Gateway do and when do you need one?**
A: An API Gateway is the single entry point for all clients. It handles cross-cutting concerns at the edge.

**Core responsibilities:**
1. **Routing** — forward requests to the right microservice based on path/host
2. **Authentication & Authorization** — verify JWT/API keys before reaching services (Kong, AWS API Gateway)
3. **Rate limiting** — protect backend services from abuse
4. **Request/Response transformation** — aggregate multiple service calls into one response (BFF pattern)
5. **SSL termination** — offload TLS from backend services
6. **Load balancing** — distribute traffic across service instances
7. **Circuit breaking** — detect failing services, return cached/fallback responses
8. **Logging & Tracing** — inject trace IDs, log all requests centrally
9. **Canary routing** — route specific users/regions to new versions

**Backend for Frontend (BFF) pattern:**
Instead of one gateway for all clients, create dedicated gateways per client type:
- Mobile BFF — returns compressed, minimal payloads optimized for mobile bandwidth
- Web BFF — returns richer data for desktop
- Partner API Gateway — strict rate limiting, different auth scheme

**Popular options:** Kong, AWS API Gateway, Nginx, Traefik, Envoy, APISIX.
