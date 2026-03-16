# MONGODB & MONGOOSE Q&A — COMPREHENSIVE

## MONGODB FUNDAMENTALS

**Q: What is MongoDB?**
A: NoSQL document database storing data as BSON (Binary JSON). No fixed schema — documents in same collection can have different fields. Great for flexible, nested, hierarchical data.

**Q: MongoDB vs PostgreSQL — when to use each?**
A: MongoDB: Flexible schema, hierarchical/nested data, horizontal scaling, rapid iteration, document-centric apps.
   PostgreSQL: Complex joins, strict schema enforcement, ACID transactions, analytical queries, relational data.

**Q: What are Collections and Documents?**
A: Hierarchy: Database → Collections → Documents (like SQL: Database → Tables → Rows). Document = JSON object with unique `_id` field.

**Q: What is BSON?**
A: Binary JSON. More data types than JSON (Date, ObjectId, Binary, etc.), smaller size, faster parse.

**Q: What is ObjectId?**
A: Default MongoDB `_id` type. 12-byte hex string: 4-byte timestamp + 5-byte random + 3-byte counter. Globally unique, sortable by creation time.

---

## MONGOOSE

**Q: What is Mongoose?**
A: ODM (Object Data Modeling) library for MongoDB in Node.js. Provides schema validation, middleware (hooks), virtuals, methods, and .populate() for relations.

**Q: Why use Mongoose over native MongoDB driver?**
A: Schema validation, pre/post hooks, virtual fields, instance/static methods, easier populate(), automatic type casting, query builder API.

**Q: Mongoose Schema vs Model?**
A: Schema: Blueprint — defines fields, types, validation rules.
   Model: Compiled schema → provides interface to query/modify the collection.

**Q: Schema types available?**
A: String, Number, Date, Boolean, Buffer, ObjectId, Array, Mixed, Map, Decimal128, UUID.

**Q: Schema validation options?**
A: ```js
   name: { type: String, required: true, trim: true, minlength: 2, maxlength: 50 }
   role: { type: String, enum: ['user', 'admin'], default: 'user' }
   age: { type: Number, min: 0, max: 150 }
   email: { type: String, required: true, unique: true, match: /regex/ }
   ```

**Q: What are virtual fields?**
A: Computed properties not stored in DB, exist only in memory:
   ```js
   userSchema.virtual('fullName').get(function() {
     return `${this.firstName} ${this.lastName}`
   })
   ```

**Q: What are Mongoose middleware hooks?**
A: Functions that run before/after operations:
   ```js
   userSchema.pre('save', async function(next) {
     if (this.isModified('password')) {
       this.password = await bcrypt.hash(this.password, 10)
     }
     next()
   })
   userSchema.post('save', function(doc) {
     console.log('Saved:', doc._id)
   })
   ```
   Hooks available: save, validate, remove, updateOne, deleteOne, findOne, find, aggregate, init

**Q: Instance methods vs static methods?**
A: Instance method: On a document, `this` = document.
   Static method: On the Model class, `this` = Model.
   ```js
   userSchema.methods.comparePassword = async function(pwd) {
     return bcrypt.compare(pwd, this.password)
   }
   userSchema.statics.findByEmail = async function(email) {
     return this.findOne({ email })
   }
   ```

**Q: What is lean()?**
A: Returns plain JS objects instead of full Mongoose documents. Faster, less memory, no methods/virtuals. Use for read-only queries.

**Q: What is populate()?**
A: Replace ObjectId reference with the actual document:
   ```js
   const post = await Post.findById(id)
     .populate('author')                    // Full user doc
     .populate({ path: 'comments', select: 'text', limit: 10 })
   ```

---

## MONGODB CRUD OPERATIONS

**Q: Insert options?**
A: ```js
   new User(data).save()           // Create then save
   await User.create(data)         // Create + save in one
   await User.insertMany([...])    // Bulk insert (faster)
   ```

**Q: Find query modifiers?**
A: ```js
   User.find(filter)
     .select('name email -password')  // Include/exclude fields
     .sort({ createdAt: -1 })
     .skip((page - 1) * limit)
     .limit(20)
     .lean()
   ```

**Q: Common query operators?**
A: Comparison: `$eq, $ne, $gt, $gte, $lt, $lte`
   Array: `$in, $nin, $all, $elemMatch`
   Element: `$exists, $type`
   Logical: `$and, $or, $not, $nor`

**Q: Difference between findOneAndUpdate and updateOne?**
A: `findOneAndUpdate`: Returns the document (before or after based on `{ new: true }`).
   `updateOne`: Returns operation result `{ matchedCount, modifiedCount }`, not the doc.

**Q: Common update operators?**
A: ```js
   $set: { name: 'Alice' }        // Set field
   $unset: { temp: '' }           // Remove field
   $inc: { views: 1 }             // Increment
   $push: { tags: 'nodejs' }      // Add to array
   $pull: { tags: 'old' }         // Remove from array
   $addToSet: { tags: 'unique' }  // Add if not exists
   $pop: { items: 1 }             // Remove last/first element
   ```

**Q: What is upsert?**
A: Update if exists, insert if not: `User.findOneAndUpdate(filter, update, { upsert: true })`

---

## AGGREGATION PIPELINE

**Q: What is the aggregation pipeline?**
A: Series of stages that transform documents. More powerful than .find(). Stages execute in sequence, each stage's output is next stage's input.

**Q: Most important pipeline stages?**
A: - `$match`: Filter (like WHERE)
   - `$group`: Group + aggregate ($sum, $avg, $max, $min, $count)
   - `$project`: Shape output (include, exclude, rename, compute)
   - `$sort`: Sort
   - `$limit` / `$skip`: Pagination
   - `$lookup`: JOIN another collection
   - `$unwind`: Flatten arrays
   - `$facet`: Multiple parallel pipelines
   - `$addFields`: Add computed fields

**Q: $group example?**
A: ```js
   { $group: {
     _id: '$category',
     total: { $sum: '$price' },
     count: { $sum: 1 },
     avg: { $avg: '$price' },
     distinctUsers: { $addToSet: '$userId' }
   }}
   ```

**Q: $lookup (JOIN) example?**
A: ```js
   { $lookup: {
     from: 'users',
     localField: 'userId',
     foreignField: '_id',
     as: 'user'
   }}
   // After lookup: { ...post, user: [{ ...userDoc }] }
   // Use $unwind to unwrap single-element array if needed
   ```

**Q: $facet for pagination with count?**
A: ```js
   { $facet: {
     data: [{ $skip: 0 }, { $limit: 20 }],
     total: [{ $count: 'count' }]
   }}
   ```

**Q: Date-based group (monthly report)?**
A: ```js
   { $group: {
     _id: { year: { $year: '$createdAt' }, month: { $month: '$createdAt' } },
     total: { $sum: '$amount' }
   }}
   ```

---

## INDEXING

**Q: What is an index and why use it?**
A: B-tree structure for fast lookups. Without: COLLSCAN (scan every doc). With: IXSCAN (jump directly). Critical for performance at scale.

**Q: Types of indexes?**
A: - Single field: `{ email: 1 }`
   - Compound: `{ username: 1, age: -1 }`
   - Text: `{ bio: 'text' }` (full-text search)
   - Geospatial: `{ location: '2dsphere' }`
   - TTL: `{ expiredAt: 1 }, { expireAfterSeconds: 0 }` (auto-delete)
   - Unique: `{ email: 1 }, { unique: true }`

**Q: How to check if query uses index?**
A: ```js
   const explain = await User.find({ email: 'test@test.com' }).explain('executionStats')
   // Look for: winningPlan.stage === 'IXSCAN' (good), 'COLLSCAN' (bad)
   // totalDocsExamined should ≈ nReturned
   ```

**Q: ESR rule for compound indexes?**
A: Order: Equality → Sort → Range for optimal index usage.
   `{ status: 1, createdAt: -1, age: 1 }` if query: `status === 'active'` (equality), sort by `createdAt` (sort), filter `age > 18` (range).

**Q: Index over-optimization problems?**
A: - Each index slows down writes (must be updated)
   - Consumes RAM
   - Rule: Only index frequently queried fields. Monitor with `db.collection.stats()`.

---

## SCHEMA DESIGN

**Q: When to embed vs reference?**
A: Embed: Data always accessed together, 1-to-few (<100 items), rarely changes independently.
   Reference: Data changes independently, large size, 1-to-many or many-to-many, shared across entities.

**Q: Example: Blog post + comments?**
A: Embed: If max ~50 comments. One query, fast reads.
   Reference: If unbounded comments, avoid BSON 16MB limit.

**Q: What is unbounded array anti-pattern?**
A: Array in document that grows forever. Hits 16MB BSON doc limit. Solution: Reference collection instead.

**Q: Many-to-many in MongoDB?**
A: Pattern 1: Array of references on both sides.
   Pattern 2: Junction collection with two ObjectId references + metadata.

---

## TRANSACTIONS

**Q: When do you need MongoDB transactions?**
A: Multiple documents must update atomically. Example: Bank transfer (debit + credit = both succeed or both fail).

**Q: Transaction code pattern?**
A: ```js
   const session = await mongoose.startSession()
   session.startTransaction()
   try {
     await AccountA.debit(amount, { session })
     await AccountB.credit(amount, { session })
     await session.commitTransaction()
   } catch (err) {
     await session.abortTransaction()
     throw err
   } finally {
     session.endSession()
   }
   ```

**Q: Transaction performance?**
A: Slower than non-transactional ops. Only use when atomicity across docs is required.

---

## PERFORMANCE

**Q: N+1 query problem?**
A: Making N queries for N related documents instead of 1 batched query:
   ```js
   // ❌ N+1
   for (const post of posts) { post.author = await User.findById(post.authorId) }

   // ✅ 1+1 with populate
   const posts = await Post.find({}).populate('authorId')
   ```

**Q: How to optimize MongoDB queries?**
A: 1) Add indexes on queried fields
   2) Use .lean() for read-only
   3) Use .select() for needed fields only
   4) Use .populate() not manual loops
   5) Use bulkWrite for mass operations
   6) Use aggregation pipelines for complex computations
   7) Use cursor for large datasets

**Q: What is bulkWrite?**
A: Multiple operations in one network call (much faster):
   ```js
   await User.bulkWrite([
     { updateOne: { filter: { _id: id1 }, update: { $set: { active: true } } } },
     { deleteMany: { filter: { createdAt: { $lt: oldDate } } } },
   ])
   ```

**Q: Connection pooling in Mongoose?**
A: `maxPoolSize: 10` - keep 10 connections open. Don't create new connection per request. Mongoose handles this automatically.

---

## ADVANCED TOPICS

**Q: What are change streams?**
A: Listen to real-time data changes (requires replica set):
   ```js
   const stream = User.watch([{ $match: { 'fullDocument.active': true } }])
   stream.on('change', (change) => {
     // change.operationType: 'insert', 'update', 'delete'
   })
   ```

**Q: MongoDB sharding vs replication?**
A: Replication: Multiple copies for high availability & read scaling. Failover if primary dies.
   Sharding: Partitioning data horizontally across multiple servers for write scaling and huge datasets.

**Q: Capped collection?**
A: Fixed-size, FIFO collection. Old docs auto-deleted when full. Good for logs, activity streams.

**Q: Text search vs Atlas Search?**
A: Text index: Built-in, limited (single field query, no fuzzy), one language.
   Atlas Search: Apache Lucene-powered, fuzzy matching, facets, multi-language, relevance scoring. Preferred!

**Q: HyperLogLog equivalent in MongoDB?**
A: `$approxCountDistinct` in aggregation (available from MongoDB 5.0+). Estimated unique count, memory efficient.

**Q: GridFS?**
A: For files > 16MB. Splits into chunks, stored in `fs.chunks` + `fs.files` collections. For smaller files, use S3 + store URL.
