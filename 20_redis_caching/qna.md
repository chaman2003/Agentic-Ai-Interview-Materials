# REDIS & CACHING Q&A — COMPREHENSIVE

## REDIS BASICS

**Q: What is Redis?**
A: Remote Dictionary Server. In-memory data store that's blazingly fast because all data lives in RAM. Supports multiple data structures beyond simple key-value.

**Q: Why is Redis so fast?**
A: 1) Data stored in RAM (not disk)
   2) Single-threaded (no context switching overhead)
   3) Optimized C implementation
   4) Simple protocol

**Q: Redis use cases?**
A: - Caching (reduce DB load)
   - Session storage
   - Rate limiting
   - Pub/sub messaging (real-time features)
   - Leaderboards (sorted sets)
   - Queues (lists)
   - Real-time analytics

**Q: Redis vs Memcached?**
A: Redis: More data structures, persistence, pub/sub, replication, Lua scripting.
   Memcached: Simpler, multi-threaded, only string values.
   Choose Redis for rich features, Memcached for pure simplicity.

**Q: Redis single-threaded or multi-threaded?**
A: Single-threaded for command execution (event loop). Multi-threaded for I/O in Redis 6+. Single-threaded design avoids lock overhead, making it fast.

**Q: What data types does Redis support?**
A: 1) String (key-value)
   2) Hash (object-like, field-value pairs)
   3) List (ordered, can be used as queue/stack)
   4) Set (unique unordered values)
   5) Sorted Set (set with scores, for rankings)
   6) Bitmap, HyperLogLog, Streams, Geospatial

**Q: When NOT to use Redis?**
A: - Data doesn't fit in RAM
   - Need complex queries (use database)
   - Need transactions across multiple keys (limited support)
   - Data must be 100% durable (Redis has some risk)

---

## DATA STRUCTURES

**Q: String use cases?**
A: Simple key-value, counters (INCR), caching JSON, feature flags.

**Q: Hash use cases?**
A: Store objects (user profiles), avoid serialization overhead, partial updates.

**Q: List use cases?**
A: Queues (LPUSH/RPOP), recent items (LPUSH + LTRIM), activity feeds.

**Q: Set use cases?**
A: Unique items, tags, followers, set operations (union, intersection, difference).

**Q: Sorted Set use cases?**
A: Leaderboards, priority queues, time-series data, rate limiting.

**Q: LPUSH vs RPUSH?**
A: LPUSH adds to head (left), RPUSH adds to tail (right).
   Use LPUSH + LTRIM for recent items (newest first).
   Use RPUSH + LPOP for FIFO queue.

**Q: ZADD vs SADD?**
A: ZADD adds to sorted set (with score), maintains order.
   SADD adds to regular set (unordered).

**Q: How to store JSON in Redis?**
A: Serialize to string: `await redis.set('user:1', JSON.stringify(user))`
   Deserialize when reading: `JSON.parse(await redis.get('user:1'))`

**Q: Hash vs serialized JSON?**
A: Hash: Can update individual fields without fetching all.
   JSON: Simpler, but must fetch/parse entire object for updates.

---

## CACHING

**Q: What is caching?**
A: Storing frequently accessed data in fast storage (Redis) to avoid slow operations (database queries, API calls).

**Q: Cache-Aside pattern (Lazy Loading)?**
A: 1) Check cache
   2) If miss, fetch from database
   3) Store in cache for next time
   Most common pattern!

**Q: Write-Through caching?**
A: Update cache whenever writing to database. Keeps cache always in sync.

**Q: Write-Behind caching?**
A: Write to cache first, asynchronously write to database later. Faster writes, but risk of data loss.

**Q: What is cache invalidation?**
A: Removing stale data from cache when underlying data changes.

**Q: How to invalidate cache?**
A: 1) Delete cache key when data changes
   2) Set TTL (time-to-live) for automatic expiration
   3) Use versioned keys (e.g., `user:1:v2`)

**Q: What's a cache stampede?**
A: Many requests hit database simultaneously when cache expires.
   Solution: Lock pattern or probabilistic early expiration.

**Q: TTL best practices?**
A: - Frequently changing data: Short TTL (minutes)
   - Rarely changing data: Long TTL (hours/days)
   - Always set TTL to free memory eventually

**Q: Cache Hit Ratio?**
A: Percentage of requests served from cache.
   High is good (90%+). Low means cache not effective.

**Q: Cold start problem?**
A: Cache is empty initially, all requests miss. Solved by cache warming (pre-populate) or accepting initial slowness.

---

## SESSION MANAGEMENT

**Q: Why use Redis for sessions?**
A: - Fast access (in-memory)
   - Automatic expiration (TTL)
   - Works across multiple servers (shared state)
   - Better scalability than in-memory sessions

**Q: How to store sessions in Redis?**
A: Use express-session with connect-redis:
   ```js
   app.use(session({
     store: new RedisStore({ client: redisClient }),
     secret: 'secret',
     resave: false,
     saveUninitialized: false
   }))
   ```

**Q: Session vs JWT?**
A: Session: Server stores state in Redis, sends session ID to client.
   JWT: Server doesn't store state, client holds token with claims.

   Session: Can invalidate anytime (logout).
   JWT: Can't invalidate until expiry (unless using blacklist).

---

## RATE LIMITING

**Q: Why rate limit?**
A: Prevent abuse, protect resources, enforce fair usage.

**Q: Fixed window rate limiting?**
A: Count requests in fixed time window (e.g., 100 requests per minute).
   Flaw: Burst at window boundary (99 at :59, 100 at 1:00 = 199 in 1 second).

**Q: Sliding window rate limiting?**
A: Use sorted set with timestamps. Remove old entries, count recent ones.
   More accurate, prevents burst.

**Q: How to implement rate limiting?**
A: Fixed window: Use INCR with EXPIRE.
   Sliding window: Use ZADD with timestamps, ZREMRANGEBYSCORE to remove old.

**Q: Rate limit per user or per IP?**
A: Authenticated users: Per user ID (more accurate).
   Anonymous: Per IP (can be bypassed with VPN, but simple).

---

## PUB/SUB

**Q: What is Pub/Sub?**
A: Messaging pattern. Publishers send messages to channels, subscribers receive from channels they're subscribed to.

**Q: Redis Pub/Sub use cases?**
A: Real-time notifications, chat apps, live updates, event broadcasting.

**Q: Pub/Sub vs message queue?**
A: Pub/Sub: Fire-and-forget, no persistence, subscribers must be online.
   Message Queue: Persistent, guaranteed delivery, workers can be offline.

**Q: How to implement Pub/Sub?**
A: Publisher: `await redis.publish('channel', 'message')`
   Subscriber: `redis.subscribe('channel')` then listen to 'message' event.

**Q: Can Pub/Sub guarantee delivery?**
A: No! If subscriber is offline, message is lost. Use Redis Streams or message queue for guaranteed delivery.

**Q: Pub/Sub vs Streams?**
A: Pub/Sub: Ephemeral, no history.
   Streams: Persistent log, can replay messages, consumer groups.

---

## ADVANCED PATTERNS

**Q: What's a distributed lock?**
A: Prevents multiple processes from accessing same resource simultaneously in distributed system.

**Q: How to implement distributed lock?**
A: Use SETNX (SET if Not eXists) with expiration:
   ```js
   const acquired = await redis.set('lock:resource', 'identifier', 'EX', 10, 'NX')
   ```
   Release with Lua script to ensure you own the lock.

**Q: What's Redlock algorithm?**
A: Distributed lock algorithm for Redis cluster. Acquires lock on majority of nodes. More reliable than single-node lock.

**Q: How to implement leaderboard?**
A: Use sorted set:
   ```js
   await redis.zadd('leaderboard', score, userId)
   const top = await redis.zrevrange('leaderboard', 0, 9) // Top 10
   ```

**Q: How to track unique visitors?**
A: Use HyperLogLog (probabilistic data structure):
   ```js
   await redis.pfadd('visitors:page1', userId)
   const count = await redis.pfcount('visitors:page1')
   ```
   Extremely memory efficient (~12KB for 10^9 elements), ~0.81% error rate.

**Q: How to implement recent items list?**
A: Use list with LPUSH + LTRIM:
   ```js
   await redis.lpush('recent:user1', itemId)
   await redis.ltrim('recent:user1', 0, 19) // Keep only 20
   ```

**Q: What's a pipeline?**
A: Send multiple commands at once, get responses together. Reduces network round trips.
   ```js
   const pipeline = redis.pipeline()
   pipeline.set('key1', 'value1')
   pipeline.get('key2')
   await pipeline.exec()
   ```

**Q: What's a transaction?**
A: Atomic execution of multiple commands (MULTI/EXEC). All succeed or all fail.

**Q: KEYS vs SCAN?**
A: KEYS: Blocks server, returns all matching keys. Never use in production!
   SCAN: Non-blocking, returns keys in batches (cursor-based). Always use SCAN.

---

## PERSISTENCE & DURABILITY

**Q: Is Redis durable?**
A: Not by default (in-memory). But can persist to disk with RDB or AOF.

**Q: What's RDB?**
A: Redis Database file. Snapshots at intervals (e.g., every 5 minutes).
   Pros: Fast, compact.
   Cons: Data loss possible (since last snapshot).

**Q: What's AOF?**
A: Append-Only File. Logs every write operation.
   Pros: Durable, minimal data loss.
   Cons: Larger files, slower.

**Q: RDB vs AOF?**
A: RDB: Fast recovery, but can lose data.
   AOF: Slower recovery, but more durable.
   Recommended: Use both (RDB for fast recovery, AOF for durability).

**Q: AOF rewrite?**
A: Compacts AOF file by removing redundant commands. Reduces file size.

**Q: Redis persistence config?**
A: `save 900 1` = Snapshot if 1 key changed in 900 seconds
   `appendonly yes` = Enable AOF

---

## PERFORMANCE & SCALING

**Q: Redis memory limit?**
A: Set maxmemory in config. When limit reached, eviction policy kicks in.

**Q: Eviction policies?**
A: - noeviction: Return error when memory full
   - allkeys-lru: Evict least recently used keys
   - allkeys-lfu: Evict least frequently used keys
   - volatile-lru: Evict LRU keys with TTL only
   - volatile-ttl: Evict keys with shortest TTL

**Q: How to scale Redis?**
A: - Vertical: More RAM on single instance
   - Horizontal: Redis Cluster (sharding across multiple nodes)
   - Read replicas: Offload reads to replica nodes

**Q: What's Redis Cluster?**
A: Distributed Redis with automatic sharding. Data split across multiple master nodes. Each master has replicas for HA.

**Q: What's Redis Sentinel?**
A: HA solution for single Redis instance. Monitors master, auto-failover to replica if master fails.

**Q: How to monitor Redis?**
A: - INFO command (memory usage, hit rate, connections)
   - SLOWLOG (log slow queries)
   - redis-cli --stat
   - Monitoring tools (RedisInsight, Prometheus + Grafana)

**Q: What's Redis overhead?**
A: Each key has ~90 bytes overhead. Use hashes to group small values and reduce overhead.

**Q: How to debug Redis performance?**
A: 1) Check INFO stats (memory, CPU, hit rate)
   2) Check SLOWLOG for slow commands
   3) Use MONITOR to see all commands (careful in production!)
   4) Check eviction policy and memory usage

---

## INTERVIEW TIPS

**Q: Most common Redis interview question?**
A: "How would you implement a caching layer for your application?"
   Answer: Cache-Aside pattern with TTL. Check cache first, on miss fetch from DB and populate cache.

**Q: Redis anti-patterns?**
A: - Using KEYS in production (use SCAN)
   - Not setting TTLs (memory fills up)
   - Storing large values (> 1MB)
   - Using Redis as primary database
   - Not monitoring memory usage

**Q: Cache invalidation is one of the hardest problems in CS. Why?**
A: Two hard things in computer science: Cache invalidation, naming things, and off-by-one errors. 😄
   Hard because: Timing (when to invalidate?), consistency (cache vs DB), race conditions.
