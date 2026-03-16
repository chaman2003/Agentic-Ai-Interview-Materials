# Redis Advanced — Q&A

---

## REDIS STREAMS

**Q: What are Redis Streams?**
A: An append-only log data structure (like Kafka, but in Redis). Entries are added with XADD and consumed with XREAD or XREADGROUP. Supports replay, consumer groups, and acknowledgements. Ideal for event sourcing and messaging.

**Q: What are the core Streams commands?**
A:
```bash
# XADD — append an entry to a stream
# ID format: <milliseconds>-<sequence> or * (auto-generate)
XADD events * type "user.login" userId "123" ip "1.2.3.4"
# Returns auto-generated ID like: "1700000000000-0"

# XLEN — count entries in stream
XLEN events

# XRANGE — read entries in order (forward)
XRANGE events - +             # all entries (- = oldest, + = newest)
XRANGE events 1700000000000-0 + COUNT 10  # from specific ID, limit 10

# XREVRANGE — read entries in reverse
XREVRANGE events + - COUNT 5  # 5 newest

# XREAD — read new entries (blocking or non-blocking)
XREAD COUNT 10 STREAMS events 0          # read from start
XREAD COUNT 10 BLOCK 5000 STREAMS events $  # block 5s for NEW entries
```

**Q: What are Consumer Groups?**
A: Allow multiple consumers to process stream entries in parallel. Each entry is delivered to ONE consumer in the group. Unacknowledged entries can be reclaimed. Multiple groups can read the same stream independently.

```bash
# Create consumer group (start from beginning: 0, or from now: $)
XGROUP CREATE events order-processor 0 MKSTREAM

# Read entries as consumer "worker-1" in group
XREADGROUP GROUP order-processor worker-1 COUNT 10 STREAMS events >
# > = only entries not yet delivered to this group

# Acknowledge processed entries (prevent re-delivery)
XACK events order-processor 1700000000000-0

# Check pending (unacknowledged) entries
XPENDING events order-processor - + 10

# Reclaim stuck entries (pending > 60 seconds, reassign to worker-2)
XCLAIM events order-processor worker-2 60000 1700000000000-0

# Delete processed entries (keep stream size manageable)
XTRIM events MAXLEN ~ 10000  # keep ~10000 most recent (~ = approximate, faster)
```

**Q: Event sourcing with Redis Streams — how does it work?**
A:
```js
// Producer: append events
async function publishEvent(type, payload) {
  const id = await redis.xadd(
    'domain-events',   // stream name
    '*',               // auto-generate ID (timestamp-based)
    'type', type,
    'payload', JSON.stringify(payload),
    'timestamp', Date.now()
  )
  return id
}

// Consumer Group: process events
async function startConsumer(groupName, consumerName) {
  // Create group if not exists
  try {
    await redis.xgroup('CREATE', 'domain-events', groupName, '$', 'MKSTREAM')
  } catch (e) {
    if (!e.message.includes('BUSYGROUP')) throw e
  }

  while (true) {
    // Read new entries
    const entries = await redis.xreadgroup(
      'GROUP', groupName, consumerName,
      'COUNT', 10,
      'BLOCK', 5000,  // block for 5 seconds
      'STREAMS', 'domain-events', '>'
    )

    if (!entries) continue  // timeout, no messages

    for (const [streamName, messages] of entries) {
      for (const [id, fields] of messages) {
        try {
          await processEvent(fields)
          await redis.xack('domain-events', groupName, id)
        } catch (err) {
          console.error('Failed to process:', id, err)
          // Do NOT ack — entry stays in pending, will be reclaimed
        }
      }
    }
  }
}
```

---

## REDIS CLUSTER

**Q: How does Redis Cluster work?**
A: Redis Cluster distributes data across multiple master nodes using hash slots. The keyspace is divided into 16384 hash slots. Each master node owns a range of slots. Data is automatically routed to the correct node.

**Q: How is a key mapped to a hash slot?**
A: `hash_slot = CRC16(key) % 16384`

Example with 3 masters:
- Node A: slots 0–5460
- Node B: slots 5461–10922
- Node C: slots 10923–16383

Key `user:123` → CRC16 → slot 5765 → goes to Node B

**Q: What are hash tags?**
A: Force multiple keys to the same slot using `{tag}`. Only the part in `{}` is hashed.
```bash
# Without hash tags — these MAY be on different nodes
# Multi-key commands (MGET, transactions) would fail across nodes
SET user:123:name "Alice"
SET user:123:email "alice@example.com"

# WITH hash tags — same slot guaranteed
SET {user:123}:name "Alice"
SET {user:123}:email "alice@example.com"
# CRC16("user:123") determines slot for both
MGET {user:123}:name {user:123}:email  # works!
```

**Q: What is cluster failover?**
A: When a master node fails:
1. Its replicas detect the master is down (after cluster-node-timeout, default 15s)
2. Replicas start an election (gossip protocol)
3. Majority of masters vote for the new master
4. Winning replica promotes itself to master
5. Cluster state updated, clients reconnect

**Q: Cluster limitations?**
A:
- Multi-key commands only work if all keys are in the same slot (use hash tags)
- No database selection (`SELECT` is not supported)
- Transactions (MULTI/EXEC) only work within a single slot
- Minimum recommended: 3 masters + 3 replicas (6 nodes)

---

## REDIS SENTINEL

**Q: What is Redis Sentinel?**
A: High-availability solution for a single Redis master + replica setup. Sentinel monitors the master, notifies of failures, and auto-promotes a replica to master when needed.

**Q: How does Sentinel failover work?**
A:
1. Sentinels monitor master with regular PING
2. If master doesn't respond → marked `subjectively down (SDOWN)` by one sentinel
3. If quorum of sentinels agree → marked `objectively down (ODOWN)`
4. Sentinels elect a leader (Raft-like)
5. Leader picks best replica (least replication lag)
6. Leader sends `SLAVEOF NO ONE` to promote it
7. Other replicas reconfigure to follow new master
8. Clients get new master address via Sentinel

**Q: Sentinel configuration example:**
```bash
# sentinel.conf
sentinel monitor mymaster 127.0.0.1 6379 2  # need 2 sentinels to agree on failure
sentinel down-after-milliseconds mymaster 5000   # 5s no response = down
sentinel failover-timeout mymaster 60000          # 60s max for failover
sentinel parallel-syncs mymaster 1               # 1 replica resyncs at a time

# Application connects to Sentinel, not master directly
redis.createClient({
  sentinels: [
    { host: 'sentinel-1', port: 26379 },
    { host: 'sentinel-2', port: 26379 },
    { host: 'sentinel-3', port: 26379 },
  ],
  name: 'mymaster',
})
```

**Q: Sentinel vs Cluster?**
A:
| | Sentinel | Cluster |
|--|----------|---------|
| Purpose | HA for single instance | HA + horizontal scaling |
| Sharding | No | Yes (16384 slots) |
| Max data | Limited by single node RAM | Scales with nodes |
| Complexity | Low-medium | High |
| Multi-key ops | Always work | Only within same slot |
| Use case | HA without sharding needs | Large datasets |

---

## REDIS vs MEMCACHED vs HAZELCAST

**Q: Compare Redis, Memcached, and Hazelcast:**
A:

| Feature | Redis | Memcached | Hazelcast |
|---------|-------|-----------|-----------|
| Data structures | String, Hash, List, Set, Sorted Set, Stream, Bitmap, HLL | String only | Map, Queue, Set, List, Ringed Buffer, Topic |
| Persistence | RDB + AOF | None | Yes (hot restart) |
| Clustering | Redis Cluster (sharding) | Client-side sharding | Built-in distributed (partition-aware) |
| Replication | Master-replica | No built-in | Synchronous + backup |
| Pub/Sub | Yes | No | Yes (Topics) |
| Transactions | MULTI/EXEC (single node) | No | Hazelcast transactions |
| Lua scripting | Yes | No | No |
| Java-first | No | No | Yes (JVM-native) |
| Use case | General purpose cache, messaging, sessions | Simple string cache, multi-threaded | Java microservices, distributed computing |

**When to choose:**
- **Redis**: Default choice. Rich data structures, persistence, pub/sub, scripting.
- **Memcached**: Pure string caching, multi-threaded (handles more ops/second for simple GET/SET), existing infrastructure.
- **Hazelcast**: Java ecosystem, need distributed computing (distributed locks, entry processors), near-cache for JVM apps.

---

## CACHE STAMPEDE SOLUTIONS

**Q: What is cache stampede and why is it dangerous?**
A: Also called "thundering herd problem." When a popular cache key expires, many requests simultaneously find a cache miss and all hit the database — potentially crashing it.

```
Timeline:
T=0:   Key expires
T=0.1: 100 requests hit the cache, all miss
T=0.2: 100 DB queries fire simultaneously
T=0.5: DB overwhelmed, all 100 requests fail
```

**Q: Solution 1 — Mutex/Lock (single request regenerates cache)**
A:
```js
async function getWithLock(key, fetchFn, ttl) {
  // 1. Try cache
  const cached = await redis.get(key)
  if (cached) return JSON.parse(cached)

  const lockKey = `lock:${key}`
  const lockId  = `${Date.now()}:${Math.random()}`

  // 2. Try to acquire lock (NX = only if not exists)
  const acquired = await redis.set(lockKey, lockId, 'EX', 10, 'NX')

  if (acquired) {
    try {
      // 3. We own the lock: fetch and cache
      const data = await fetchFn()
      await redis.set(key, JSON.stringify(data), 'EX', ttl)
      return data
    } finally {
      // 4. Release lock with Lua (atomic check-and-delete)
      await redis.eval(`
        if redis.call("GET", KEYS[1]) == ARGV[1] then
          return redis.call("DEL", KEYS[1])
        else
          return 0
        end
      `, 1, lockKey, lockId)
    }
  } else {
    // 5. Another process is regenerating — wait and retry
    await new Promise(r => setTimeout(r, 50))
    return getWithLock(key, fetchFn, ttl)
  }
}
```

**Q: Solution 2 — Probabilistic Early Expiration (XFetch)**
A: Re-compute the cache BEFORE it expires, based on a probabilistic formula. Avoids a hard expiration cliff.

```js
// XFetch algorithm (Optimal Probabilistic Cache Stampede Prevention)
async function getWithXFetch(key, fetchFn, ttl, beta = 1.0) {
  const raw = await redis.get(key)

  if (raw) {
    const { value, expiry, delta } = JSON.parse(raw)
    // Probabilistically regenerate before expiry
    // Earlier recomputation more likely as expiry approaches
    const now = Date.now() / 1000
    if (now - beta * delta * Math.log(Math.random()) < expiry) {
      return value  // still fresh enough
    }
  }

  // Cache miss or decided to early-refresh
  const start = Date.now()
  const value = await fetchFn()
  const delta = (Date.now() - start) / 1000  // compute time in seconds
  const expiry = Date.now() / 1000 + ttl

  await redis.set(key, JSON.stringify({ value, expiry, delta }), 'EX', ttl + 1)
  return value
}
```

**Q: Solution 3 — Stale-while-revalidate (serve stale, refresh async)**
A:
```js
async function getStaleWhileRevalidate(key, fetchFn, freshTtl, staleTtl) {
  const cached = await redis.get(key)
  const meta   = await redis.get(`${key}:meta`)

  if (cached && meta) {
    const { refreshAt } = JSON.parse(meta)
    if (Date.now() < refreshAt) return JSON.parse(cached) // still fresh

    // Stale but present: serve stale and refresh in background
    refreshCache(key, fetchFn, freshTtl, staleTtl) // fire and forget
    return JSON.parse(cached)
  }

  // No cache at all: fetch synchronously
  return refreshCache(key, fetchFn, freshTtl, staleTtl)
}

async function refreshCache(key, fetchFn, freshTtl, staleTtl) {
  const data = await fetchFn()
  await redis.set(key, JSON.stringify(data), 'EX', staleTtl)
  await redis.set(`${key}:meta`, JSON.stringify({ refreshAt: Date.now() + freshTtl * 1000 }), 'EX', staleTtl)
  return data
}
```

---

## REDIS MEMORY OPTIMIZATION

**Q: How do you reduce Redis memory usage?**
A:

**1. Use compact data types (Hash instead of many String keys):**
```bash
# Wasteful: 3 separate keys (each has ~90 bytes overhead)
SET user:1:name "Alice"
SET user:1:email "alice@example.com"
SET user:1:age 30

# Compact: 1 hash (hash has lower per-field overhead)
HSET user:1 name Alice email alice@example.com age 30
```

**2. Redis uses compact encoding automatically for small hashes/lists:**
- Hash with <= 128 fields AND all values <= 64 bytes → stored as ziplist (compact)
- Configure: `hash-max-listpack-entries 128`, `hash-max-listpack-value 64`

**3. Lazy freeing (non-blocking deletion):**
```bash
# Synchronous (blocks server for large keys)
DEL massive-sorted-set

# Async (non-blocking — frees in background thread)
UNLINK massive-sorted-set

# Enable lazy freeing for expiration and eviction
# redis.conf:
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
```

**4. Enable compression for RDB:**
```bash
# redis.conf
rdbcompression yes  # LZF compression for RDB snapshots
```

**5. Key naming strategy — shorter keys reduce overhead:**
```bash
# Long (more memory)
SET user:profile:data:12345 "..."

# Short (less memory, but less readable — tradeoff)
SET up:12345 "..."
```

**Q: How do you find memory-hungry keys?**
A:
```bash
# Get memory usage for specific key
MEMORY USAGE user:12345

# Find top memory consumers
redis-cli --bigkeys        # find largest keys by type

# MEMORY DOCTOR — diagnostics
MEMORY DOCTOR

# Check overall memory
INFO memory
# used_memory_human, mem_fragmentation_ratio (>1.5 = high fragmentation)
```

---

## REDIS SECURITY

**Q: How do you secure Redis?**
A:

**1. Authentication (AUTH):**
```bash
# redis.conf
requirepass "your-strong-password"

# Connect with password
redis-cli -a "your-strong-password"
redis.createClient({ password: 'your-strong-password' })
```

**2. ACL (Access Control Lists) — Redis 6+:**
```bash
# Create read-only user
ACL SETUSER readonly-user on >password ~* &* +@read
# ~ = key pattern (* = all), & = channel pattern, +@read = allow read commands

# Create user for specific commands and keys
ACL SETUSER app-user on >apppass ~app:* +GET +SET +DEL

# List users
ACL LIST
ACL WHOAMI

# redis.conf (ACL file approach)
aclfile /etc/redis/users.acl
```

**3. TLS/SSL:**
```bash
# redis.conf
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
tls-auth-clients yes  # require client certificates
```

**4. Network isolation:**
```bash
# Bind to specific interface (NOT 0.0.0.0 in production)
bind 127.0.0.1 10.0.0.5

# Disable dangerous commands
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""
```

**5. Disable protected mode (only in trusted networks):**
```bash
protected-mode yes  # default, good
```

---

## LUA SCRIPTING IN REDIS

**Q: Why use Lua scripts in Redis?**
A: Lua scripts run atomically on the Redis server — no other commands execute in between. Eliminates race conditions for multi-step operations without using MULTI/EXEC.

**Q: How do you run Lua scripts?**
A:
```bash
# EVAL script numkeys [key [key ...]] [arg [arg ...]]
EVAL "return 1" 0

# Access keys and args
EVAL "return redis.call('SET', KEYS[1], ARGV[1])" 1 mykey myvalue

# Conditional check-and-set (atomic compare-and-swap)
EVAL "
  local current = redis.call('GET', KEYS[1])
  if current == ARGV[1] then
    redis.call('SET', KEYS[1], ARGV[2])
    return 1
  end
  return 0
" 1 mykey oldvalue newvalue
```

**Practical Lua scripts in Node.js:**
```js
// Rate limiter with sliding window (atomic)
const rateLimitScript = `
  local key = KEYS[1]
  local now = tonumber(ARGV[1])
  local window = tonumber(ARGV[2])
  local limit = tonumber(ARGV[3])

  -- Remove old entries
  redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

  -- Count current requests
  local count = redis.call('ZCARD', key)

  if count < limit then
    -- Add this request
    redis.call('ZADD', key, now, now .. math.random())
    redis.call('EXPIRE', key, window / 1000)
    return 1  -- allowed
  end
  return 0  -- blocked
`

async function rateLimit(userId, windowMs = 60000, limit = 100) {
  const key = `ratelimit:${userId}`
  const now = Date.now()
  const allowed = await redis.eval(rateLimitScript, 1, key, now, windowMs, limit)
  return allowed === 1
}

// Distributed lock release (atomic check-and-delete)
const releaseLockScript = `
  if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
  else
    return 0
  end
`

// EVALSHA — cache script by SHA1 (avoid sending script every time)
const sha = await redis.script('LOAD', rateLimitScript)
await redis.evalsha(sha, 1, key, now, windowMs, limit)
```

---

## REDIS PERFORMANCE BENCHMARKING

**Q: How do you benchmark Redis performance?**
A:
```bash
# redis-benchmark — built-in benchmarking tool
redis-benchmark -h 127.0.0.1 -p 6379 -n 100000 -c 50

# Options:
# -n 100000  = total 100k requests
# -c 50      = 50 parallel connections
# -d 1024    = data size 1KB
# -q         = quiet mode (only ops/sec)
# -t         = specific commands to test

# Benchmark specific commands
redis-benchmark -t set,get -n 1000000 -q
redis-benchmark -t lpush,lpop -c 100 -n 500000

# Pipeline benchmark (multiple commands per round trip)
redis-benchmark -t set -n 100000 --pipeline 16

# Key distribution patterns
redis-benchmark -r 1000000  # use 1M random keys (realistic)
```

**Interpreting results:**
```
====== SET ======
  1000000 requests completed in 8.40 seconds
  50 parallel clients
  3 bytes payload
  keep alive: 1

  119047.62 requests per second  ← throughput

====== GET ======
  128205.13 requests per second
```

**Q: What are typical Redis performance numbers?**
A:
- Single instance: ~100,000–200,000 ops/second for GET/SET
- With pipeline: ~500,000–1,000,000 ops/second
- With cluster: scales linearly with nodes

**Q: What slows down Redis?**
A:
- `KEYS *` command (O(N), blocks server)
- Large values (>1MB per key)
- Slow Lua scripts
- AOF fsync (every write) — use `appendfsync everysec` instead
- High memory fragmentation
- Network latency (use pipelining to batch commands)

---

## REDIS IN PRODUCTION

**Q: What eviction policies should you use in production?**
A:
```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # evict least recently used when full

# Policy choices:
# noeviction           — return error when full (bad for caches)
# allkeys-lru          — evict any LRU key (best for pure cache)
# volatile-lru         — evict LRU keys WITH expiry (mixed workloads)
# allkeys-lfu          — evict least frequently used (better than LRU for skewed access)
# volatile-ttl         — evict key with shortest TTL
# allkeys-random       — random eviction (avoid this)
```

**Q: Connection pooling for Redis:**
A:
```js
// ioredis with connection pool
const Redis = require('ioredis')

const redis = new Redis({
  host: 'redis.example.com',
  port: 6379,
  password: 'secret',
  maxRetriesPerRequest: 3,
  lazyConnect: true,
  keepAlive: 30000,
  connectTimeout: 5000,
})

// Cluster with connection pool
const cluster = new Redis.Cluster([
  { host: 'redis-node-1', port: 6379 },
  { host: 'redis-node-2', port: 6379 },
  { host: 'redis-node-3', port: 6379 },
], {
  scaleReads: 'slave',    // read from replicas
  maxRedirections: 16,
})
```

**Q: What to monitor in Redis production?**
A:
```bash
# Key INFO metrics
INFO all

# Memory
used_memory_human              # current memory usage
maxmemory_human                # configured limit
mem_fragmentation_ratio        # >1.5 = high fragmentation, restart may help
evicted_keys                   # how many keys were evicted

# Performance
instantaneous_ops_per_sec      # current throughput
hit_rate = keyspace_hits / (keyspace_hits + keyspace_misses)

# Connections
connected_clients
blocked_clients

# Replication
role                           # master or slave
master_repl_offset
repl_backlog_size

# SLOWLOG — find slow commands
SLOWLOG GET 25                 # last 25 slow commands
SLOWLOG RESET
# Default: log commands > 10000 microseconds (10ms)
# config set slowlog-log-slower-than 5000  # 5ms threshold
```

---

## INTERVIEW SCENARIOS

**Q: Design a distributed cache for a high-traffic e-commerce site.**
A:
```
Architecture:
1. Redis Cluster (3 masters + 3 replicas) for horizontal scaling
2. L1 cache: in-process (node-lru-cache, ~100ms TTL) to avoid Redis round-trips
3. L2 cache: Redis (~5-60 minute TTL based on data type)
4. L3: Database

Cache strategy by data type:
- Product catalog: Write-through, 1-hour TTL (changes infrequently)
- User sessions: Write-through, 30-minute TTL with sliding expiration
- Shopping cart: Write-through, persist to DB on checkout
- Inventory count: No cache! Use Redis DECR for atomic decrement
- Price: 5-minute TTL (can be slightly stale)
- Search results: 2-minute TTL

Stampede prevention:
- Popular product pages: XFetch probabilistic early expiration
- New product launch: Cache warming before launch
- Flash sales: Pre-populate cache, use Redis DECR for stock

Monitoring:
- Alert if hit rate drops below 90%
- Alert if evicted_keys increasing (need more memory)
- Alert if latency > 1ms (90th percentile)
```

**Q: Implement an LRU cache with Redis.**
A:
```js
class RedisLRUCache {
  constructor(redis, name, maxSize) {
    this.redis = redis
    this.name = name
    this.maxSize = maxSize
    this.hashKey  = `lru:${name}:data`   // stores values
    this.zsetKey  = `lru:${name}:access` // sorted by last access time
  }

  async get(key) {
    const script = `
      local value = redis.call('HGET', KEYS[1], ARGV[1])
      if value then
        redis.call('ZADD', KEYS[2], ARGV[2], ARGV[1])  -- update access time
      end
      return value
    `
    const value = await this.redis.eval(
      script, 2,
      this.hashKey, this.zsetKey,
      key, Date.now()
    )
    return value ? JSON.parse(value) : null
  }

  async set(key, value) {
    const script = `
      redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])
      redis.call('ZADD', KEYS[2], ARGV[3], ARGV[1])   -- score = timestamp

      -- Evict oldest if over capacity
      local size = redis.call('ZCARD', KEYS[2])
      if size > tonumber(ARGV[4]) then
        local oldest = redis.call('ZRANGE', KEYS[2], 0, 0)  -- get least recently used
        redis.call('HDEL', KEYS[1], oldest[1])
        redis.call('ZREM', KEYS[2], oldest[1])
      end
      return 1
    `
    await this.redis.eval(
      script, 2,
      this.hashKey, this.zsetKey,
      key, JSON.stringify(value), Date.now(), this.maxSize
    )
  }

  async delete(key) {
    await this.redis.pipeline()
      .hdel(this.hashKey, key)
      .zrem(this.zsetKey, key)
      .exec()
  }

  async size() {
    return this.redis.zcard(this.zsetKey)
  }
}

// Usage
const cache = new RedisLRUCache(redis, 'product-cache', 10000)
await cache.set('product:123', { name: 'Widget', price: 9.99 })
const product = await cache.get('product:123')
```

**Q: How would you handle a Redis outage in production without losing all traffic?**
A:
1. **Circuit breaker**: Detect Redis failures, stop calling Redis, fall through to DB
2. **Graceful degradation**: App continues without cache (slower but functional)
3. **Multiple Redis instances**: Sentinel or Cluster for HA
4. **Local fallback cache**: In-process LRU cache as emergency L1
5. **Read replicas**: If master fails, temporarily read from replica

```js
class ResilientCache {
  constructor(redis) {
    this.redis = redis
    this.localCache = new Map()  // in-process fallback
    this.isRedisDown = false
    this.failureCount = 0
    this.threshold = 5
  }

  async get(key) {
    if (this.isRedisDown) return this.localCache.get(key) ?? null

    try {
      const value = await Promise.race([
        this.redis.get(key),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 100))
      ])
      this.failureCount = 0
      return value ? JSON.parse(value) : null
    } catch {
      this.failureCount++
      if (this.failureCount >= this.threshold) {
        this.isRedisDown = true
        setTimeout(() => { this.isRedisDown = false; this.failureCount = 0 }, 30000)
      }
      return this.localCache.get(key) ?? null
    }
  }
}
```

**Q: "Redis is using 8GB but you only have 4GB. What do you do?"**
A:
1. Check `redis-cli --bigkeys` to find large keys
2. Check `INFO keyspace` for key counts and TTL coverage
3. Short term: set `maxmemory 3.5gb` + `maxmemory-policy allkeys-lru`
4. Fix TTL: find keys without TTL using `OBJECT ENCODING` scan, add TTLs
5. Use compact encoding: check if hashes/lists use compact encoding
6. Consider data compression: compress values > 1KB before storing
7. Long term: Redis Cluster to distribute across machines
