# MongoDB + Mongoose — Advanced Q&A & Patterns

---

## SCHEMA DESIGN

**Q: How do you decide between embedding vs referencing in MongoDB?**

**Embed when:**
- Data is always accessed together (post + its comments)
- Data doesn't change frequently
- Array won't grow unbounded (< 100 items)
- Strong ownership (comment belongs to one post)

**Reference when:**
- Data is shared across documents (user is author of many posts)
- Array could grow very large (user's followers)
- Need to query sub-documents independently
- Need to update sub-data frequently

```js
// EMBEDDING — comments inside post
const postSchema = new Schema({
    title:    String,
    comments: [{ body: String, author: String, date: Date }]  // embedded
});

// REFERENCING — comments as separate documents
const commentSchema = new Schema({
    postId: { type: ObjectId, ref: "Post" },   // reference
    body:   String,
    author: { type: ObjectId, ref: "User" }
});
```

---

**Q: What is the 16MB document size limit and why does it matter?**
A: MongoDB documents have a 16MB limit. If you embed arrays that grow unboundedly (like a chat history or all orders), you'll hit this. Solution: reference instead of embed, or use GridFS for large files.

---

## INDEXING

**Q: What types of indexes does MongoDB support?**

| Index Type | Use Case |
|-----------|----------|
| Single field | Most common — `{email: 1}` |
| Compound | Multiple fields — `{status: 1, createdAt: -1}` |
| Text | Full-text search — `{"$text": {"$search": "legal"}}` |
| 2dsphere | Geospatial queries (near me, within radius) |
| TTL | Auto-delete documents after N seconds (sessions, logs) |
| Unique | Enforce uniqueness (like unique email) |

```js
// Compound index — good for queries that filter by status then sort by date
userSchema.index({ status: 1, createdAt: -1 });

// Text index for full-text search
caseSchema.index({ title: "text", description: "text" });

// TTL index — auto-delete sessions after 24 hours
sessionSchema.index({ createdAt: 1 }, { expireAfterSeconds: 86400 });

// Partial index — only index active users (saves space)
userSchema.index({ email: 1 }, { partialFilterExpression: { active: true } });
```

---

**Q: What is the ESR rule for compound indexes?**
A: Order index fields: **E**quality → **S**ort → **R**ange. Put equality filters first, sort fields second, range queries last. This maximizes index effectiveness.
```js
// Query: active users in India, sorted by created date, aged 25-35
// ESR order: status (equality) → createdAt (sort) → age (range)
userSchema.index({ status: 1, createdAt: -1, age: 1 });
```

---

## AGGREGATION PIPELINE IN DEPTH

**Q: What are all the common aggregation pipeline stages?**
```js
User.aggregate([
    // 1. $match — filter (like WHERE). Put first to reduce data early.
    { $match: { status: "active", age: { $gte: 18 } } },

    // 2. $project — select/transform fields (like SELECT)
    { $project: { name: 1, email: 1, _id: 0, domain: { $split: ["$email", "@"] } } },

    // 3. $group — aggregate (like GROUP BY + aggregate functions)
    { $group: {
        _id: "$department",
        count:      { $sum: 1 },
        avgAge:     { $avg: "$age" },
        names:      { $push: "$name" },        // collect into array
        maxSalary:  { $max: "$salary" }
    }},

    // 4. $sort — order results
    { $sort: { count: -1 } },

    // 5. $limit + $skip — pagination
    { $skip: 0 }, { $limit: 10 },

    // 6. $lookup — join another collection (like SQL JOIN)
    { $lookup: {
        from:         "orders",
        localField:   "_id",
        foreignField: "userId",
        as:           "orders"
    }},

    // 7. $unwind — flatten an array field into separate documents
    { $unwind: "$orders" },

    // 8. $addFields — add computed fields without removing others
    { $addFields: { fullName: { $concat: ["$firstName", " ", "$lastName"] } } },

    // 9. $count — count matching documents
    { $count: "totalUsers" },

    // 10. $facet — run multiple sub-pipelines in one pass (for faceted search)
    { $facet: {
        "byStatus":  [{ $group: { _id: "$status", count: { $sum: 1 } } }],
        "byAge":     [{ $bucket: { groupBy: "$age", boundaries: [18, 25, 35, 50] } }]
    }}
]);
```

---

**Q: How do you write a query for all cases per corporate client grouped by status?**
```js
// In pymongo:
pipeline = [
    { "$match": { "clientId": client_id, "createdAt": { "$gte": thirty_days_ago } } },
    { "$group": {
        "_id": "$status",
        "count": { "$sum": 1 },
        "totalAmount": { "$sum": "$amount" },
        "avgResolutionDays": { "$avg": "$resolutionDays" }
    }},
    { "$sort": { "count": -1 } }
]
result = db.cases.aggregate(pipeline)
```

---

## TRANSACTIONS

**Q: Does MongoDB support ACID transactions?**
A: Yes, since MongoDB 4.0 for replica sets, 4.2 for sharded clusters. Use multi-document transactions when you need atomicity across multiple documents (e.g., debit one account, credit another — both must succeed or neither does).

```js
const session = await mongoose.startSession();
session.startTransaction();
try {
    await Account.findByIdAndUpdate(fromId, { $inc: { balance: -amount } }, { session });
    await Account.findByIdAndUpdate(toId,   { $inc: { balance: +amount } }, { session });
    await session.commitTransaction();
} catch (err) {
    await session.abortTransaction();   // rollback both on error
    throw err;
} finally {
    session.endSession();
}
```
Note: Transactions in MongoDB have overhead. Design schemas to minimize the need for them.

---

## PERFORMANCE

**Q: How do you identify slow queries in MongoDB?**
A:
1. `db.setProfilingLevel(1, { slowms: 100 })` — log slow queries (>100ms)
2. `db.system.profile.find().sort({ts:-1}).limit(10)` — view slow query log
3. Use `.explain("executionStats")` on a query to see if it's doing a COLLSCAN
4. Add indexes on fields you filter/sort by frequently

```js
// Check if a query uses an index
await User.find({ email: "x@y.com" }).explain("executionStats");
// Look for: winningPlan.stage === "IXSCAN" (index scan — good)
// vs        winningPlan.stage === "COLLSCAN" (collection scan — bad, no index)
```

---

## MONGOOSE ADVANCED

**Q: What are Mongoose middleware hooks?**
```js
// pre("save") — runs before .save() — perfect for password hashing
userSchema.pre("save", async function(next) {
    if (!this.isModified("password")) return next();   // only hash if changed!
    this.password = await bcrypt.hash(this.password, 10);
    next();
});

// post("save") — runs after successful save — good for sending welcome email
userSchema.post("save", async function(doc) {
    await sendWelcomeEmail(doc.email);
});

// pre("find") — runs before every find query — e.g., auto-filter deleted docs
userSchema.pre(/^find/, function(next) {
    this.find({ deleted: { $ne: true } });   // never return deleted docs
    next();
});
```

---

**Q: What is `lean()` in Mongoose and when should you use it?**
A: `lean()` returns plain JavaScript objects instead of Mongoose Documents. Much faster and lighter — no virtuals, no methods, no middleware. Use when you're just reading data and don't need to modify it.
```js
// Without lean() — full Mongoose document (~80KB+ memory per doc)
const users = await User.find();

// With lean() — plain JS object (~2KB per doc), 30-40% faster
const users = await User.find().lean();
users[0].save();  // ERROR! plain objects don't have save()
```

---

**Q: MongoDB vs Postgres — when to choose each?**

| Factor | MongoDB | PostgreSQL |
|--------|---------|-----------|
| Schema flexibility | High — add fields anytime | Low — migrations required |
| Query complexity | Good | Excellent (JOINs, CTEs, window fns) |
| ACID transactions | Multi-doc since 4.0 | Full ACID always |
| Horizontal scaling | Native sharding | Harder (Citus extension) |
| JSON storage | Native BSON | JSONB with indexing |
| Full-text search | Built-in text index | Built-in tsvector |
| When to choose | Flexible docs, rapid iteration, hierarchical data | Reporting, complex joins, financial data |
