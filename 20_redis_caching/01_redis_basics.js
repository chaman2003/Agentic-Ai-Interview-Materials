/*
═══════════════════════════════════════════════════════════════════════════════
  REDIS & CACHING — COMPREHENSIVE GUIDE (BASICS TO ADVANCED)
═══════════════════════════════════════════════════════════════════════════════

Redis: Remote Dictionary Server (in-memory data store)
Think: Super fast short-term memory for your app

Why Redis?
✅ Blazing fast (all data in RAM)
✅ Supports complex data structures (strings, lists, sets, hashes, sorted sets)
✅ Pub/sub messaging
✅ Caching layer
✅ Session storage
✅ Rate limiting
✅ Real-time analytics

This file covers:
1. Redis Basics & Data Types
2. Caching Strategies
3. Session Management
4. Rate Limiting
5. Pub/Sub Messaging
6. Redis Patterns
7. Performance & Persistence
8. Redis in Production

*/

const redis = require('redis');
const { promisify } = require('util');

// ─── 1. REDIS BASICS & CONNECTION ──────────────────────────────────────────

// Connect to Redis (default: localhost:6379)
const client = redis.createClient({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  // Retry strategy
  retry_strategy: (options) => {
    if (options.error && options.error.code === 'ECONNREFUSED') {
      return new Error('Redis server refused connection');
    }
    if (options.total_retry_time > 1000 * 60 * 60) {
      return new Error('Redis retry time exhausted');
    }
    if (options.attempt > 10) {
      return undefined; // Stop retrying
    }
    return Math.min(options.attempt * 100, 3000); // Exponential backoff
  }
});

client.on('error', (err) => console.error('Redis Error:', err));
client.on('connect', () => console.log('Connected to Redis'));

// Promisify for async/await
const getAsync = promisify(client.get).bind(client);
const setAsync = promisify(client.set).bind(client);
const delAsync = promisify(client.del).bind(client);

// Modern way: Use ioredis (better TypeScript support, Promise-based)
const Redis = require('ioredis');
const redisClient = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  retryStrategy: (times) => {
    return Math.min(times * 50, 2000);
  }
});

// ─── 2. DATA TYPES & OPERATIONS ────────────────────────────────────────────

/* ──────────────────── STRING ───────────────────── */
// Most basic type: Key-value pair

async function stringExamples() {
  // Set a value
  await redisClient.set('user:1001:name', 'Alice');

  // Get a value
  const name = await redisClient.get('user:1001:name');
  console.log(name); // 'Alice'

  // Set with expiration (TTL - Time To Live)
  await redisClient.setex('session:abc123', 3600, 'user_data'); // Expires in 1 hour

  // Set only if not exists
  await redisClient.setnx('lock:resource', 'locked');

  // Increment (atomic operation!)
  await redisClient.set('page:views', '100');
  await redisClient.incr('page:views'); // 101
  await redisClient.incrby('page:views', 10); // 111

  // Multiple set/get
  await redisClient.mset('key1', 'value1', 'key2', 'value2');
  const values = await redisClient.mget('key1', 'key2'); // ['value1', 'value2']

  // Check if key exists
  const exists = await redisClient.exists('user:1001:name'); // 1 (true)

  // Delete key
  await redisClient.del('user:1001:name');

  // TTL (time remaining)
  const ttl = await redisClient.ttl('session:abc123'); // Seconds remaining
}

/* ──────────────────── HASH ────────────────────── */
// Object-like structure (field-value pairs)

async function hashExamples() {
  // Set hash fields
  await redisClient.hset('user:1002', 'name', 'Bob', 'age', '30', 'city', 'NYC');

  // Get single field
  const name = await redisClient.hget('user:1002', 'name'); // 'Bob'

  // Get all fields
  const user = await redisClient.hgetall('user:1002');
  // { name: 'Bob', age: '30', city: 'NYC' }

  // Increment hash field
  await redisClient.hincrby('user:1002', 'age', 1); // 31

  // Check if field exists
  const hasEmail = await redisClient.hexists('user:1002', 'email'); // 0 (false)

  // Delete field
  await redisClient.hdel('user:1002', 'city');

  // Get all keys
  const keys = await redisClient.hkeys('user:1002'); // ['name', 'age']
}

/* ──────────────────── LIST ────────────────────── */
// Ordered collection (like array)

async function listExamples() {
  // Push to list (left/right)
  await redisClient.rpush('queue:emails', 'email1', 'email2', 'email3');
  await redisClient.lpush('queue:emails', 'urgent_email'); // Add to front

  // Pop from list
  const email = await redisClient.lpop('queue:emails'); // 'urgent_email'

  // Get range
  const emails = await redisClient.lrange('queue:emails', 0, -1); // All emails

  // Blocking pop (wait for item if empty)
  const item = await redisClient.blpop('queue:emails', 10); // Wait max 10 seconds

  // List length
  const length = await redisClient.llen('queue:emails');

  // Trim list (keep only range)
  await redisClient.ltrim('recent:posts', 0, 99); // Keep only latest 100
}

/* ──────────────────── SET ─────────────────────── */
// Unordered collection of unique values

async function setExamples() {
  // Add members
  await redisClient.sadd('tags:post:1', 'javascript', 'nodejs', 'redis');

  // Check membership
  const isMember = await redisClient.sismember('tags:post:1', 'nodejs'); // 1 (true)

  // Get all members
  const tags = await redisClient.smembers('tags:post:1');

  // Remove member
  await redisClient.srem('tags:post:1', 'redis');

  // Set operations
  await redisClient.sadd('tags:post:2', 'nodejs', 'mongodb');

  // Union (all tags from both posts)
  const allTags = await redisClient.sunion('tags:post:1', 'tags:post:2');

  // Intersection (common tags)
  const commonTags = await redisClient.sinter('tags:post:1', 'tags:post:2');

  // Difference
  const uniqueTags = await redisClient.sdiff('tags:post:1', 'tags:post:2');

  // Random member
  const randomTag = await redisClient.srandmember('tags:post:1');
}

/* ──────────────────── SORTED SET ──────────────── */
// Set with scores (ordered by score)

async function sortedSetExamples() {
  // Add members with scores
  await redisClient.zadd('leaderboard', 100, 'Alice', 200, 'Bob', 150, 'Charlie');

  // Get rank (0-indexed)
  const rank = await redisClient.zrank('leaderboard', 'Bob'); // 2 (highest score)

  // Get score
  const score = await redisClient.zscore('leaderboard', 'Alice'); // '100'

  // Get top N (highest scores)
  const top3 = await redisClient.zrevrange('leaderboard', 0, 2, 'WITHSCORES');
  // ['Bob', '200', 'Charlie', '150', 'Alice', '100']

  // Get by score range
  const midRange = await redisClient.zrangebyscore('leaderboard', 100, 150);

  // Increment score
  await redisClient.zincrby('leaderboard', 50, 'Alice'); // Alice now has 150

  // Count in range
  const count = await redisClient.zcount('leaderboard', 100, 200);

  // Remove member
  await redisClient.zrem('leaderboard', 'Charlie');
}

// ─── 3. CACHING STRATEGIES ─────────────────────────────────────────────────

/*
Caching: Store frequently accessed data in fast storage (Redis)
to avoid slow operations (database queries, API calls)

Strategies:
1. Cache-Aside (Lazy Loading)
2. Write-Through
3. Write-Behind
4. Cache Invalidation
*/

// Pattern 1: CACHE-ASIDE (LAZY LOADING)
// Most common pattern
async function getUserCacheAside(userId) {
  const cacheKey = `user:${userId}`;

  // 1. Try cache first
  let user = await redisClient.get(cacheKey);

  if (user) {
    console.log('Cache HIT');
    return JSON.parse(user);
  }

  // 2. Cache MISS: Fetch from database
  console.log('Cache MISS');
  user = await User.findById(userId); // MongoDB query

  // 3. Store in cache for next time (1 hour TTL)
  await redisClient.setex(cacheKey, 3600, JSON.stringify(user));

  return user;
}

// Pattern 2: WRITE-THROUGH
// Update cache when writing to database
async function updateUserWriteThrough(userId, updates) {
  const cacheKey = `user:${userId}`;

  // 1. Update database
  const user = await User.findByIdAndUpdate(userId, updates, { new: true });

  // 2. Update cache immediately
  await redisClient.setex(cacheKey, 3600, JSON.stringify(user));

  return user;
}

// Pattern 3: CACHE INVALIDATION
// Delete cache when data changes
async function deleteUserInvalidateCache(userId) {
  const cacheKey = `user:${userId}`;

  // 1. Delete from database
  await User.findByIdAndDelete(userId);

  // 2. Invalidate cache
  await redisClient.del(cacheKey);
}

// Pattern 4: CACHE WITH FALLBACK
async function getDataWithCache(key, fetchFunction, ttl = 3600) {
  // Generic caching helper
  let data = await redisClient.get(key);

  if (data) {
    return JSON.parse(data);
  }

  // Fetch from source
  data = await fetchFunction();

  // Store in cache
  await redisClient.setex(key, ttl, JSON.stringify(data));

  return data;
}

// Usage
const products = await getDataWithCache(
  'products:featured',
  () => Product.find({ featured: true }),
  300 // 5 minutes
);

// ─── 4. SESSION MANAGEMENT ─────────────────────────────────────────────────

/*
Store user sessions in Redis instead of database
Faster access, automatic expiration
*/

const session = require('express-session');
const RedisStore = require('connect-redis')(session);

const app = require('express')();

// Use Redis for session storage
app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production', // HTTPS only in production
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000 // 24 hours
  }
}));

// Store user in session
app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  const user = await User.findOne({ email });
  const isValid = await bcrypt.compare(password, user.password);

  if (isValid) {
    // Store user ID in session (stored in Redis)
    req.session.userId = user._id;
    res.json({ message: 'Logged in' });
  } else {
    res.status(401).json({ error: 'Invalid credentials' });
  }
});

// Access session
app.get('/profile', (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not logged in' });
  }

  res.json({ userId: req.session.userId });
});

// Destroy session
app.post('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    res.json({ message: 'Logged out' });
  });
});

// ─── 5. RATE LIMITING ───────────────────────────────────────────────────────

/*
Prevent abuse by limiting requests per user/IP
*/

// Simple rate limiter (fixed window)
async function rateLimitFixed(userId, limit = 10, window = 60) {
  const key = `rate:${userId}`;

  // Increment request count
  const count = await redisClient.incr(key);

  // Set expiration on first request
  if (count === 1) {
    await redisClient.expire(key, window);
  }

  // Check if exceeded
  if (count > limit) {
    throw new Error('Rate limit exceeded');
  }

  return { remaining: limit - count };
}

// Sliding window rate limiter (more accurate)
async function rateLimitSliding(userId, limit = 10, window = 60) {
  const key = `rate:${userId}`;
  const now = Date.now();
  const windowStart = now - (window * 1000);

  // Remove old requests outside window
  await redisClient.zremrangebyscore(key, 0, windowStart);

  // Count requests in current window
  const count = await redisClient.zcard(key);

  if (count >= limit) {
    throw new Error('Rate limit exceeded');
  }

  // Add current request
  await redisClient.zadd(key, now, `${now}-${Math.random()}`);

  // Set expiration
  await redisClient.expire(key, window);

  return { remaining: limit - count - 1 };
}

// Middleware for Express
function rateLimitMiddleware(limit = 100, window = 60) {
  return async (req, res, next) => {
    const userId = req.user?.id || req.ip;

    try {
      const { remaining } = await rateLimitSliding(userId, limit, window);

      res.setHeader('X-RateLimit-Limit', limit);
      res.setHeader('X-RateLimit-Remaining', remaining);

      next();
    } catch (error) {
      res.status(429).json({
        error: 'Too many requests',
        retryAfter: window
      });
    }
  };
}

// Usage
app.use('/api/', rateLimitMiddleware(100, 60)); // 100 requests per minute

// ─── 6. PUB/SUB MESSAGING ──────────────────────────────────────────────────

/*
Publish-Subscribe pattern: Real-time messaging
Use case: Notifications, chat, real-time updates
*/

// Publisher (sends messages)
async function publishNotification(channel, message) {
  await redisClient.publish(channel, JSON.stringify(message));
}

// Subscriber (receives messages)
const subscriber = new Redis();

subscriber.subscribe('notifications', (err, count) => {
  if (err) {
    console.error('Failed to subscribe:', err);
  } else {
    console.log(`Subscribed to ${count} channel(s)`);
  }
});

subscriber.on('message', (channel, message) => {
  console.log(`Received message from ${channel}:`, message);

  const data = JSON.parse(message);

  // Process notification (send email, push notification, etc.)
  if (data.type === 'NEW_MESSAGE') {
    sendPushNotification(data.userId, data.message);
  }
});

// Example: Notify all users
await publishNotification('notifications', {
  type: 'NEW_MESSAGE',
  userId: 'user123',
  message: 'You have a new message!'
});

// ─── 7. REDIS PATTERNS ──────────────────────────────────────────────────────

// Pattern 1: DISTRIBUTED LOCK (prevent race conditions)
async function acquireLock(resource, ttl = 10) {
  const lockKey = `lock:${resource}`;
  const identifier = Math.random().toString(36);

  // Try to acquire lock (SETNX = SET if Not eXists)
  const acquired = await redisClient.set(lockKey, identifier, 'EX', ttl, 'NX');

  return acquired ? identifier : null;
}

async function releaseLock(resource, identifier) {
  const lockKey = `lock:${resource}`;

  // Only release if we own the lock (atomic operation using Lua script)
  const script = `
    if redis.call("get", KEYS[1]) == ARGV[1] then
      return redis.call("del", KEYS[1])
    else
      return 0
    end
  `;

  return await redisClient.eval(script, 1, lockKey, identifier);
}

// Usage
const lock = await acquireLock('payment:user123');
if (lock) {
  try {
    // Critical section (only one process can execute this at a time)
    await processPayment('user123');
  } finally {
    await releaseLock('payment:user123', lock);
  }
} else {
  console.log('Could not acquire lock');
}

// Pattern 2: LEADERBOARD (sorted set)
async function updateLeaderboard(userId, score) {
  await redisClient.zadd('game:leaderboard', score, userId);
}

async function getTopPlayers(n = 10) {
  return await redisClient.zrevrange('game:leaderboard', 0, n - 1, 'WITHSCORES');
}

async function getUserRank(userId) {
  // Rank is 0-indexed, so add 1
  const rank = await redisClient.zrevrank('game:leaderboard', userId);
  return rank !== null ? rank + 1 : null;
}

// Pattern 3: RECENT ITEMS (list with trim)
async function addToRecentViews(userId, productId) {
  const key = `recent:${userId}`;

  // Add to front
  await redisClient.lpush(key, productId);

  // Keep only latest 20
  await redisClient.ltrim(key, 0, 19);

  // Set expiration (30 days)
  await redisClient.expire(key, 30 * 24 * 60 * 60);
}

// Pattern 4: COUNTING (HyperLogLog for unique counts)
async function trackUniqueVisitors(pageId, userId) {
  const key = `visitors:${pageId}`;

  // HyperLogLog: Approximate unique count (memory efficient!)
  await redisClient.pfadd(key, userId);
}

async function getUniqueVisitorCount(pageId) {
  const key = `visitors:${pageId}`;
  return await redisClient.pfcount(key);
}

// ─── 8. PERFORMANCE & PERSISTENCE ──────────────────────────────────────────

/*
PERSISTENCE: Redis is in-memory, but can persist to disk

1. RDB (Redis Database): Snapshots at intervals
   - Pros: Fast, compact
   - Cons: Data loss possible (since last snapshot)

2. AOF (Append Only File): Log every write operation
   - Pros: Durable, minimal data loss
   - Cons: Larger file size, slower

3. Hybrid: RDB + AOF (best of both)

Config:
  save 900 1      # Snapshot if 1 key changed in 900 seconds
  save 300 10     # Snapshot if 10 keys changed in 300 seconds
  appendonly yes  # Enable AOF

PERFORMANCE TIPS:
1. Use pipelining for multiple commands
2. Use MGET/MSET for bulk operations
3. Avoid KEYS command in production (use SCAN instead)
4. Use appropriate data structures
5. Set TTLs to free memory
6. Monitor with INFO command
*/

// Pipelining (send multiple commands at once)
async function pipelineExample() {
  const pipeline = redisClient.pipeline();

  pipeline.set('key1', 'value1');
  pipeline.set('key2', 'value2');
  pipeline.get('key1');
  pipeline.incr('counter');

  const results = await pipeline.exec();
  console.log(results);
}

// Transactions (atomic operations)
async function transactionExample() {
  const multi = redisClient.multi();

  multi.set('user:1:coins', 100);
  multi.decrby('user:1:coins', 50);
  multi.incrby('user:2:coins', 50);

  const results = await multi.exec(); // All or nothing
}

// SCAN (safe alternative to KEYS)
async function getAllKeysPattern(pattern) {
  const keys = [];
  let cursor = '0';

  do {
    const [newCursor, scannedKeys] = await redisClient.scan(
      cursor,
      'MATCH',
      pattern,
      'COUNT',
      100
    );

    cursor = newCursor;
    keys.push(...scannedKeys);
  } while (cursor !== '0');

  return keys;
}

// ─── INTERVIEW SUMMARY ─────────────────────────────────────────────────────

/*
KEY CONCEPTS TO MEMORIZE:

1. WHAT IS REDIS:
   - In-memory data store (super fast!)
   - Supports multiple data structures
   - Use cases: Cache, session store, pub/sub, rate limiting

2. DATA TYPES:
   - String: Simple key-value
   - Hash: Object-like (field-value pairs)
   - List: Ordered collection (queue)
   - Set: Unique values
   - Sorted Set: Set with scores (leaderboard)

3. CACHING STRATEGIES:
   - Cache-Aside: Check cache, then DB, then populate cache
   - Write-Through: Update cache when writing to DB
   - Invalidation: Delete cache when data changes

4. COMMON PATTERNS:
   - Session storage
   - Rate limiting (fixed/sliding window)
   - Distributed locks
   - Leaderboards (sorted sets)
   - Recently viewed (lists with trim)

5. PUB/SUB:
   - Publisher sends messages to channels
   - Subscribers receive messages from channels
   - Real-time notifications, chat

6. PERSISTENCE:
   - RDB: Snapshots (fast, but data loss possible)
   - AOF: Append-only log (durable, but slower)
   - Hybrid: Both (recommended)

7. PERFORMANCE:
   - Always set TTLs to free memory
   - Use pipelines for bulk operations
   - Use SCAN instead of KEYS in production
   - Monitor with INFO command

COMMON INTERVIEW QUESTIONS:

Q: What is Redis?
A: In-memory data store. Super fast because all data lives in RAM.

Q: Redis vs Memcached?
A: Redis has more data structures, persistence, pub/sub. Memcached is simpler, only key-value.

Q: How to handle cache invalidation?
A: Delete cache when data changes, or use TTL for automatic expiration.

Q: What's cache-aside pattern?
A: Check cache first, if miss, fetch from DB and populate cache.

Q: How to implement rate limiting?
A: Use sorted sets (sliding window) or counters with expiration (fixed window).

Q: Redis for session storage?
A: Yes! Fast access, automatic expiration, works across multiple servers.

Q: What's pub/sub?
A: Messaging pattern. Publishers send to channels, subscribers receive from channels.

Q: How does Redis persist data?
A: RDB (snapshots) or AOF (append-only log), or both.

Q: What's a distributed lock?
A: Prevent multiple processes from accessing same resource. Use SETNX with TTL.

Q: Redis single-threaded?
A: Yes (for commands), but handles concurrency with event loop. Fast because no lock overhead.

Q: When NOT to use Redis?
A: When data must be durable (use database), or data doesn't fit in RAM.
*/

module.exports = {
  redisClient,
  getUserCacheAside,
  updateUserWriteThrough,
  getDataWithCache,
  rateLimitSliding,
  acquireLock,
  releaseLock,
  updateLeaderboard,
  getTopPlayers
};
