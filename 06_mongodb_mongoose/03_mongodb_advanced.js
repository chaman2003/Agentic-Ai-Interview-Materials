/*
═══════════════════════════════════════════════════════════════════════════════
  MONGODB ADVANCED — COMPREHENSIVE GUIDE (BASICS TO ADVANCED)
═══════════════════════════════════════════════════════════════════════════════

This file covers:
1. Advanced Aggregation Pipelines
2. Indexing Strategies & Performance
3. Transactions & ACID Compliance
4. Schema Design Patterns
5. Replication & Sharding
6. Performance Optimization
7. MongoDB Atlas Features
8. Real-World Patterns

*/

const mongoose = require('mongoose');

// ─── 1. ADVANCED AGGREGATION PIPELINES ─────────────────────────────────────

/*
Aggregation framework is MongoDB's way of processing data and returning computed results
Think of it as SQL GROUP BY on steroids

Pipeline stages: $match → $group → $project → $sort → $limit → $lookup → $unwind
*/

// Example: E-commerce analytics
const Order = mongoose.model('Order', new mongoose.Schema({
  user_id: mongoose.Schema.Types.ObjectId,
  items: [{
    product_id: mongoose.Schema.Types.ObjectId,
    name: String,
    price: Number,
    quantity: Number
  }],
  total: Number,
  status: String,
  created_at: Date
}));

// Complex aggregation: Get top 5 customers by total spending
async function getTopCustomers() {
  return await Order.aggregate([
    // Stage 1: Filter only completed orders
    { $match: { status: 'completed' } },

    // Stage 2: Group by user and calculate total spent
    {
      $group: {
        _id: '$user_id',
        total_spent: { $sum: '$total' },
        order_count: { $sum: 1 },
        avg_order_value: { $avg: '$total' }
      }
    },

    // Stage 3: Sort by total spent (descending)
    { $sort: { total_spent: -1 } },

    // Stage 4: Limit to top 5
    { $limit: 5 },

    // Stage 5: Lookup user details from users collection
    {
      $lookup: {
        from: 'users',
        localField: '_id',
        foreignField: '_id',
        as: 'user_details'
      }
    },

    // Stage 6: Reshape output
    {
      $project: {
        user_id: '$_id',
        name: { $arrayElemAt: ['$user_details.name', 0] },
        email: { $arrayElemAt: ['$user_details.email', 0] },
        total_spent: 1,
        order_count: 1,
        avg_order_value: { $round: ['$avg_order_value', 2] }
      }
    }
  ]);
}

// Advanced: Date-based aggregation (monthly sales report)
async function getMonthlySalesReport(year) {
  return await Order.aggregate([
    {
      $match: {
        created_at: {
          $gte: new Date(`${year}-01-01`),
          $lt: new Date(`${year + 1}-01-01`)
        },
        status: 'completed'
      }
    },
    {
      $group: {
        _id: {
          year: { $year: '$created_at' },
          month: { $month: '$created_at' }
        },
        total_sales: { $sum: '$total' },
        order_count: { $sum: 1 },
        avg_order_value: { $avg: '$total' }
      }
    },
    {
      $sort: { '_id.year': 1, '_id.month': 1 }
    },
    {
      $project: {
        _id: 0,
        month: '$_id.month',
        year: '$_id.year',
        total_sales: { $round: ['$total_sales', 2] },
        order_count: 1,
        avg_order_value: { $round: ['$avg_order_value', 2] }
      }
    }
  ]);
}

// $facet: Multiple aggregations in parallel
async function getOrderAnalytics() {
  return await Order.aggregate([
    {
      $facet: {
        // Pipeline 1: Status distribution
        statusBreakdown: [
          { $group: { _id: '$status', count: { $sum: 1 } } }
        ],

        // Pipeline 2: Sales by day of week
        salesByDayOfWeek: [
          {
            $group: {
              _id: { $dayOfWeek: '$created_at' },
              total_sales: { $sum: '$total' }
            }
          },
          { $sort: { _id: 1 } }
        ],

        // Pipeline 3: Overall statistics
        overallStats: [
          {
            $group: {
              _id: null,
              total_orders: { $sum: 1 },
              total_revenue: { $sum: '$total' },
              avg_order_value: { $avg: '$total' },
              max_order: { $max: '$total' },
              min_order: { $min: '$total' }
            }
          }
        ]
      }
    }
  ]);
}

// ─── 2. INDEXING STRATEGIES & PERFORMANCE ──────────────────────────────────

/*
Indexes are like book indexes - they help find data quickly
Without indexes, MongoDB scans every document (COLLSCAN - BAD!)
With indexes, MongoDB jumps directly to data (IXSCAN - GOOD!)

Types:
1. Single Field Index
2. Compound Index (multiple fields)
3. Text Index (full-text search)
4. Geospatial Index
5. TTL Index (time-to-live, auto-delete)
6. Unique Index
*/

const UserSchema = new mongoose.Schema({
  email: { type: String, required: true },
  username: { type: String, required: true },
  age: Number,
  location: {
    type: { type: String, default: 'Point' },
    coordinates: [Number] // [longitude, latitude]
  },
  created_at: { type: Date, default: Date.now },
  last_login: Date,
  bio: String
});

// 1. Unique index (ensures no duplicates)
UserSchema.index({ email: 1 }, { unique: true });

// 2. Compound index (for queries filtering by username AND age)
UserSchema.index({ username: 1, age: -1 }); // 1 = ascending, -1 = descending

// 3. Text index (for full-text search in bio)
UserSchema.index({ bio: 'text' });

// 4. Geospatial index (for location-based queries)
UserSchema.index({ location: '2dsphere' });

// 5. TTL index (auto-delete documents after 30 days)
const SessionSchema = new mongoose.Schema({
  user_id: mongoose.Schema.Types.ObjectId,
  token: String,
  created_at: { type: Date, default: Date.now }
});
SessionSchema.index({ created_at: 1 }, { expireAfterSeconds: 2592000 }); // 30 days

// How to check if query uses index (explain plan)
async function checkQueryPerformance() {
  const User = mongoose.model('User', UserSchema);

  // Use .explain() to see execution stats
  const explainResult = await User.find({ username: 'john_doe', age: { $gte: 25 } })
    .explain('executionStats');

  console.log('Query Stats:');
  console.log('Execution Time:', explainResult.executionStats.executionTimeMillis, 'ms');
  console.log('Documents Examined:', explainResult.executionStats.totalDocsExamined);
  console.log('Documents Returned:', explainResult.executionStats.nReturned);
  console.log('Index Used:', explainResult.executionStats.executionStages.indexName);

  // Good: totalDocsExamined ≈ nReturned (using index efficiently)
  // Bad: totalDocsExamined >> nReturned (scanning too many docs)
}

// Index best practices
/*
1. Index fields used in queries frequently
2. Put most selective field first in compound indexes
3. Don't over-index (indexes slow down writes)
4. Monitor with db.collection.stats() and db.collection.getIndexes()
5. Use covered queries when possible (query only indexed fields)
*/

// ─── 3. TRANSACTIONS & ACID COMPLIANCE ─────────────────────────────────────

/*
Transactions ensure ACID properties:
- Atomicity: All operations succeed or all fail
- Consistency: Database remains in valid state
- Isolation: Concurrent transactions don't interfere
- Durability: Committed changes persist

MongoDB supports multi-document transactions (since v4.0)
*/

const Account = mongoose.model('Account', new mongoose.Schema({
  user_id: mongoose.Schema.Types.ObjectId,
  balance: { type: Number, default: 0 }
}));

// Example: Transfer money between accounts (must be atomic!)
async function transferMoney(fromAccountId, toAccountId, amount) {
  const session = await mongoose.startSession();
  session.startTransaction();

  try {
    // Step 1: Deduct from sender
    const fromAccount = await Account.findByIdAndUpdate(
      fromAccountId,
      { $inc: { balance: -amount } },
      { session, new: true }
    );

    if (fromAccount.balance < 0) {
      throw new Error('Insufficient funds');
    }

    // Step 2: Add to receiver
    await Account.findByIdAndUpdate(
      toAccountId,
      { $inc: { balance: amount } },
      { session, new: true }
    );

    // Step 3: Commit transaction (both operations succeed)
    await session.commitTransaction();
    console.log('Transfer successful!');

  } catch (error) {
    // Rollback: Neither operation takes effect
    await session.abortTransaction();
    console.error('Transfer failed:', error.message);
    throw error;
  } finally {
    session.endSession();
  }
}

// ─── 4. SCHEMA DESIGN PATTERNS ─────────────────────────────────────────────

/*
MongoDB is schema-less, but good schema design matters!

Key decisions:
1. Embed vs Reference
2. One-to-Many relationships
3. Many-to-Many relationships
*/

// Pattern 1: EMBEDDING (denormalization)
// Use when: Data is accessed together, 1-to-few relationship
const BlogPostEmbedded = new mongoose.Schema({
  title: String,
  content: String,
  author: {
    // Embed author info (duplicated across posts)
    name: String,
    email: String,
    bio: String
  },
  comments: [
    {
      // Embed comments (max ~100 comments per post)
      text: String,
      author: String,
      created_at: Date
    }
  ]
});

// Pattern 2: REFERENCING (normalization)
// Use when: Data is large, changes frequently, many-to-many
const BlogPostReferenced = new mongoose.Schema({
  title: String,
  content: String,
  author_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User' }, // Reference
  comment_ids: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Comment' }] // Reference array
});

// Populate references (like SQL JOIN)
async function getBlogPostWithDetails(postId) {
  return await BlogPost.findById(postId)
    .populate('author_id') // Fetch author details
    .populate({
      path: 'comment_ids',
      select: 'text author created_at', // Only fetch specific fields
      options: { limit: 10, sort: { created_at: -1 } }
    });
}

// Pattern 3: HYBRID (subset pattern)
// Store frequently accessed data embedded, full data referenced
const ProductSchema = new mongoose.Schema({
  name: String,
  price: Number,
  category_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Category' },
  category_name: String, // Denormalized for fast access
  reviews: [
    {
      // Embed summary, reference full review
      rating: Number,
      summary: String,
      review_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Review' }
    }
  ]
});

// ─── 5. REPLICATION & SHARDING ─────────────────────────────────────────────

/*
REPLICATION (High Availability)
- Primary: Receives all writes
- Secondaries: Replicate data from primary
- If primary fails, secondary becomes primary (automatic failover)

Replica Set: 1 primary + 2+ secondaries (minimum 3 nodes)

Connection string for replica set:
mongodb://host1:27017,host2:27017,host3:27017/mydb?replicaSet=rs0

SHARDING (Horizontal Scaling)
- Split data across multiple servers
- Each shard is a replica set
- Shard key determines data distribution

Shard key strategies:
1. Range-based (e.g., user_id: 1-1000 → shard1, 1001-2000 → shard2)
2. Hash-based (e.g., hash(user_id) → distribute evenly)
3. Zone/Tag-based (e.g., US users → US shard, EU users → EU shard)
*/

// Enable sharding for a collection
/*
sh.enableSharding("mydb")
sh.shardCollection("mydb.users", { user_id: 1 })  // Shard key: user_id
*/

// ─── 6. PERFORMANCE OPTIMIZATION ───────────────────────────────────────────

// 1. Use lean() for read-only queries (skip Mongoose hydration)
async function getUsers() {
  // Without lean: Returns full Mongoose documents (slower, more memory)
  const users1 = await User.find({});

  // With lean: Returns plain JavaScript objects (faster, less memory)
  const users2 = await User.find({}).lean();

  return users2;
}

// 2. Use select() to fetch only needed fields
async function getUserEmails() {
  return await User.find({})
    .select('email username') // Only fetch email and username
    .lean();
}

// 3. Use limit() and skip() for pagination
async function getPaginatedUsers(page = 1, pageSize = 20) {
  const skip = (page - 1) * pageSize;
  return await User.find({})
    .select('username email')
    .skip(skip)
    .limit(pageSize)
    .lean();
}

// 4. Use $in efficiently (but avoid huge arrays)
async function getUsersByIds(userIds) {
  // Good for < 1000 IDs
  return await User.find({ _id: { $in: userIds } });

  // Bad: $in with 100,000 IDs (use batch processing instead)
}

// 5. Avoid N+1 queries with populate
async function getBlogPostsWithAuthors_BAD() {
  const posts = await BlogPost.find({});

  // BAD: N+1 queries (1 for posts + N for each author)
  for (let post of posts) {
    post.author = await User.findById(post.author_id);
  }

  return posts;
}

async function getBlogPostsWithAuthors_GOOD() {
  // GOOD: 1 query for posts + 1 query for all authors
  return await BlogPost.find({}).populate('author_id');
}

// 6. Use bulk operations for mass updates
async function bulkUpdateUsers(updates) {
  const bulkOps = updates.map(update => ({
    updateOne: {
      filter: { _id: update.id },
      update: { $set: update.data }
    }
  }));

  return await User.bulkWrite(bulkOps);
}

// ─── 7. MONGODB ATLAS FEATURES ─────────────────────────────────────────────

/*
MongoDB Atlas is the cloud-hosted MongoDB service

Key features:
1. Atlas Search: Full-text search powered by Apache Lucene
2. Atlas Data Lake: Query data stored in S3
3. Atlas Triggers: Event-driven functions (like AWS Lambda)
4. Atlas Charts: Built-in data visualization
5. Atlas App Services: Backend-as-a-Service (user auth, GraphQL, etc.)

Example: Atlas Search
*/

const ArticleSchema = new mongoose.Schema({
  title: String,
  content: String,
  tags: [String]
});

async function searchArticles(query) {
  // Use Atlas Search (requires search index in Atlas UI)
  return await Article.aggregate([
    {
      $search: {
        index: 'article_search_index',
        text: {
          query: query,
          path: ['title', 'content'], // Search in these fields
          fuzzy: {
            maxEdits: 2 // Allow typos
          }
        }
      }
    },
    {
      $project: {
        title: 1,
        content: 1,
        score: { $meta: 'searchScore' } // Relevance score
      }
    },
    { $limit: 10 }
  ]);
}

// ─── 8. REAL-WORLD PATTERNS ────────────────────────────────────────────────

// Pattern 1: Audit logging (track all changes)
const UserAuditSchema = new mongoose.Schema({
  email: String,
  username: String
});

UserAuditSchema.post('save', async function(doc) {
  // Log every user creation/update
  await AuditLog.create({
    action: 'USER_SAVE',
    user_id: doc._id,
    timestamp: new Date(),
    data: doc.toObject()
  });
});

// Pattern 2: Soft delete (don't actually delete, mark as deleted)
const SoftDeleteSchema = new mongoose.Schema({
  name: String,
  deleted_at: { type: Date, default: null }
});

SoftDeleteSchema.methods.softDelete = async function() {
  this.deleted_at = new Date();
  return await this.save();
};

// Override find to exclude soft-deleted docs by default
SoftDeleteSchema.pre(/^find/, function() {
  this.where({ deleted_at: null });
});

// Pattern 3: Versioning (keep history of changes)
const DocumentVersionSchema = new mongoose.Schema({
  document_id: mongoose.Schema.Types.ObjectId,
  version: Number,
  data: mongoose.Schema.Types.Mixed,
  created_at: { type: Date, default: Date.now }
});

async function saveVersion(documentId, data) {
  const lastVersion = await DocumentVersion.findOne({ document_id: documentId })
    .sort({ version: -1 });

  const newVersion = (lastVersion?.version || 0) + 1;

  return await DocumentVersion.create({
    document_id: documentId,
    version: newVersion,
    data: data
  });
}

// Pattern 4: Caching with Redis + MongoDB
const redis = require('ioredis');
const redisClient = new redis();

async function getUserWithCache(userId) {
  // 1. Try cache first
  const cached = await redisClient.get(`user:${userId}`);
  if (cached) {
    return JSON.parse(cached);
  }

  // 2. Cache miss: fetch from MongoDB
  const user = await User.findById(userId).lean();

  // 3. Store in cache for 1 hour
  await redisClient.setex(`user:${userId}`, 3600, JSON.stringify(user));

  return user;
}

// ─── INTERVIEW SUMMARY ─────────────────────────────────────────────────────

/*
KEY CONCEPTS TO MEMORIZE:

1. AGGREGATION:
   - Understand $match, $group, $project, $lookup, $unwind
   - Can you write a multi-stage pipeline?

2. INDEXING:
   - What's the difference between COLLSCAN and IXSCAN?
   - When to use compound indexes?
   - How to check if query uses index? (.explain())

3. TRANSACTIONS:
   - When do you need transactions? (multi-document atomic operations)
   - How to implement? (startSession, startTransaction, commit/abort)

4. SCHEMA DESIGN:
   - Embed vs Reference - when to use each?
   - How to handle one-to-many and many-to-many?

5. PERFORMANCE:
   - Use .lean() for read-only queries
   - Use .select() to fetch only needed fields
   - Avoid N+1 queries with .populate()
   - Use bulk operations for mass updates

6. REPLICATION vs SHARDING:
   - Replication = High availability (failover)
   - Sharding = Horizontal scaling (distribute data)

7. REAL-WORLD:
   - Soft delete pattern
   - Audit logging
   - Versioning
   - Caching with Redis

COMMON INTERVIEW QUESTIONS:
Q: Why is my query slow?
A: Check .explain() - likely missing index or scanning too many docs

Q: How do you handle money transfers atomically?
A: Use transactions with startSession()

Q: Embed or reference comments in a blog post?
A: Embed if < 100 comments, reference if unbounded

Q: How to scale MongoDB horizontally?
A: Sharding with a good shard key (hash or range-based)

Q: How to implement full-text search?
A: Text index or Atlas Search (better)
*/

module.exports = {
  getTopCustomers,
  getMonthlySalesReport,
  getOrderAnalytics,
  transferMoney,
  getBlogPostWithDetails,
  getUserWithCache,
  checkQueryPerformance
};
