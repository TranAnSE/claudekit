---
name: mongodb
description: >
  Use this skill whenever working with MongoDB, document databases, or NoSQL data modeling. Trigger on keywords like MongoDB, Mongo, document database, aggregation pipeline, collection, embedded documents, or BSON. Also applies when designing document schemas, building aggregation queries, handling unstructured or semi-structured data, or migrating from relational to document-based storage.
---

# MongoDB

## When to Use

- MongoDB database operations
- Document-based data modeling
- Aggregation pipelines
- Semi-structured or polymorphic data that varies per record
- Rapid prototyping where schema flexibility accelerates iteration
- Event logging, IoT telemetry, or content management systems

## When NOT to Use

- Relational-heavy data models with complex joins and foreign key constraints
- SQL-only projects where the entire stack is built around relational databases
- Simple key-value storage where Redis or a lightweight store is more appropriate
- Financial systems requiring multi-table ACID transactions as the norm

---

## Core Patterns

### 1. Schema Design

The central decision in MongoDB modeling is **embed vs. reference**.

**Decision tree:**

```
Does the child data belong to exactly one parent?
  YES --> Is the child array unbounded (could grow to thousands)?
            YES --> Reference (separate collection)
            NO  --> Embed
  NO  --> Is it a many-to-many relationship?
            YES --> Reference (with array of ObjectIds on one or both sides)
            NO  --> Reference
```

**Embedding pattern -- best for data that is read together:**

```javascript
// User with embedded address and preferences
// Good: one read fetches everything the profile page needs
db.users.insertOne({
  email: "user@example.com",
  name: "Alice Chen",
  address: {
    street: "123 Main St",
    city: "Portland",
    state: "OR",
    zip: "97201"
  },
  preferences: {
    theme: "dark",
    language: "en",
    notifications: { email: true, push: false }
  },
  createdAt: new Date()
});
```

**Referencing pattern -- best for independent or unbounded data:**

```javascript
// Orders reference the user by ID
// Good: orders grow unboundedly, accessed independently
db.orders.insertOne({
  userId: ObjectId("6651a..."),
  status: "shipped",
  totalCents: 4999,
  items: [
    { sku: "WIDGET-001", name: "Blue Widget", qty: 2, priceCents: 1999 },
    { sku: "GADGET-010", name: "Mini Gadget", qty: 1, priceCents: 1001 }
  ],
  placedAt: new Date()
});
```

**Denormalization pattern -- duplicate data to avoid frequent lookups:**

```javascript
// Store author name directly on the post (denormalized from users)
// Trade-off: faster reads, but updates to user name require updating all posts
db.posts.insertOne({
  title: "Getting Started with MongoDB",
  body: "...",
  author: {
    _id: ObjectId("6651a..."),
    name: "Alice Chen"    // denormalized -- must be updated if name changes
  },
  tags: ["mongodb", "tutorial"],
  publishedAt: new Date()
});
```

**Polymorphic pattern -- different shapes in one collection:**

```javascript
// Events collection stores different event types
db.events.insertMany([
  {
    type: "page_view",
    userId: ObjectId("6651a..."),
    url: "/products/widget",
    timestamp: new Date()
  },
  {
    type: "purchase",
    userId: ObjectId("6651a..."),
    orderId: ObjectId("6651b..."),
    totalCents: 4999,
    timestamp: new Date()
  }
]);
// Use a discriminator field (type) and query by it
```

**Schema validation -- enforce structure at the database level:**

```javascript
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name", "createdAt"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^.+@.+\\..+$",
          description: "Must be a valid email"
        },
        name: {
          bsonType: "string",
          minLength: 1
        },
        role: {
          enum: ["admin", "editor", "viewer"],
          description: "Must be a valid role"
        },
        createdAt: { bsonType: "date" }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});
```

---

### 2. Aggregation Pipeline

Build complex data transformations as a sequence of stages.

```javascript
// Revenue report: total and average spend per user, last 30 days
db.orders.aggregate([
  // Stage 1: filter to recent delivered orders
  { $match: {
    status: "delivered",
    placedAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
  }},

  // Stage 2: group by user
  { $group: {
    _id: "$userId",
    totalSpent: { $sum: "$totalCents" },
    orderCount: { $sum: 1 },
    avgOrderValue: { $avg: "$totalCents" }
  }},

  // Stage 3: sort by spend
  { $sort: { totalSpent: -1 } },

  // Stage 4: limit to top 10
  { $limit: 10 },

  // Stage 5: join user details
  { $lookup: {
    from: "users",
    localField: "_id",
    foreignField: "_id",
    as: "user"
  }},

  // Stage 6: flatten the joined array
  { $unwind: "$user" },

  // Stage 7: reshape output
  { $project: {
    _id: 0,
    userName: "$user.name",
    email: "$user.email",
    totalSpent: 1,
    orderCount: 1,
    avgOrderValue: { $round: ["$avgOrderValue", 0] }
  }}
]);
```

**$unwind -- flatten arrays into individual documents:**

```javascript
// Expand order items to analyze product-level metrics
db.orders.aggregate([
  { $unwind: "$items" },
  { $group: {
    _id: "$items.sku",
    totalQty: { $sum: "$items.qty" },
    totalRevenue: { $sum: { $multiply: ["$items.qty", "$items.priceCents"] } }
  }},
  { $sort: { totalRevenue: -1 } }
]);
```

**$lookup with pipeline -- filtered/correlated joins:**

```javascript
// For each user, get their 3 most recent orders
db.users.aggregate([
  { $lookup: {
    from: "orders",
    let: { uid: "$_id" },
    pipeline: [
      { $match: { $expr: { $eq: ["$userId", "$$uid"] } } },
      { $sort: { placedAt: -1 } },
      { $limit: 3 },
      { $project: { status: 1, totalCents: 1, placedAt: 1 } }
    ],
    as: "recentOrders"
  }}
]);
```

**$facet -- run multiple aggregations in parallel:**

```javascript
// Dashboard: get summary stats and top products in one query
db.orders.aggregate([
  { $match: { status: "delivered" } },
  { $facet: {
    summary: [
      { $group: {
        _id: null,
        totalRevenue: { $sum: "$totalCents" },
        totalOrders: { $sum: 1 }
      }}
    ],
    topProducts: [
      { $unwind: "$items" },
      { $group: { _id: "$items.sku", sold: { $sum: "$items.qty" } } },
      { $sort: { sold: -1 } },
      { $limit: 5 }
    ],
    monthlyTrend: [
      { $group: {
        _id: { $dateToString: { format: "%Y-%m", date: "$placedAt" } },
        revenue: { $sum: "$totalCents" }
      }},
      { $sort: { _id: 1 } }
    ]
  }}
]);
```

---

### 3. Index Strategies

```javascript
// Single field index -- most common
db.users.createIndex({ email: 1 }, { unique: true });

// Compound index -- order matters, follows the ESR rule:
// Equality fields first, Sort fields next, Range fields last
db.orders.createIndex({ status: 1, placedAt: -1 });
// Supports: find({status: "pending"}).sort({placedAt: -1})
// Also supports: find({status: "pending"}) alone (prefix)

// Multikey index -- automatically indexes each array element
db.posts.createIndex({ tags: 1 });
// Supports: find({ tags: "mongodb" })

// Text index -- basic full-text search
db.posts.createIndex(
  { title: "text", body: "text" },
  { weights: { title: 10, body: 1 }, name: "posts_text_search" }
);
// Usage:
db.posts.find(
  { $text: { $search: "mongodb aggregation" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } });

// TTL index -- auto-delete documents after expiry
db.sessions.createIndex(
  { expiresAt: 1 },
  { expireAfterSeconds: 0 }  // delete when expiresAt is in the past
);
// Documents must have a Date field; they are removed by a background task ~every 60s

// Partial index -- only index documents matching a filter
db.orders.createIndex(
  { placedAt: -1 },
  { partialFilterExpression: { status: "pending" } }
);
// Smaller index; only used when the query includes the filter condition

// Wildcard index -- for querying arbitrary keys in a sub-document
db.products.createIndex({ "attributes.$**": 1 });
// Supports: find({ "attributes.color": "red" }) without knowing keys in advance

// Collation -- case-insensitive sorting and matching
db.users.createIndex(
  { name: 1 },
  { collation: { locale: "en", strength: 2 } }
);
```

**The ESR rule for compound indexes:** order fields by **E**quality, **S**ort, **R**ange. This produces the most efficient index scans.

```javascript
// Query: find active orders for a user, sorted by date, in a date range
// Equality: userId, status
// Sort: placedAt
// Range: placedAt (but sort and range on same field -- sort wins)
db.orders.createIndex({ userId: 1, status: 1, placedAt: -1 });
```

---

### 4. Transactions

Multi-document transactions work across collections (requires replica set or sharded cluster).

```javascript
const session = client.startSession();

try {
  session.startTransaction({
    readConcern: { level: "snapshot" },
    writeConcern: { w: "majority" },
    readPreference: "primary"
  });

  const accounts = client.db("bank").collection("accounts");

  // Transfer $50 from account A to account B
  const fromAccount = await accounts.findOne(
    { _id: "account-A" },
    { session }
  );

  if (fromAccount.balanceCents < 5000) {
    await session.abortTransaction();
    throw new Error("Insufficient funds");
  }

  await accounts.updateOne(
    { _id: "account-A" },
    { $inc: { balanceCents: -5000 } },
    { session }
  );

  await accounts.updateOne(
    { _id: "account-B" },
    { $inc: { balanceCents: 5000 } },
    { session }
  );

  // Record the transfer in a separate collection -- still in the same tx
  await client.db("bank").collection("transfers").insertOne({
    from: "account-A",
    to: "account-B",
    amountCents: 5000,
    timestamp: new Date()
  }, { session });

  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  await session.endSession();
}
```

**Guidelines:**
- Keep transactions short -- they hold locks and consume resources
- Design your schema to minimize the need for multi-document transactions
- Transactions have a default 60-second timeout (`maxTimeMS`)
- Retryable writes (`retryWrites=true` in connection string) handle transient errors automatically

---

### 5. Change Streams

Watch for real-time changes to collections, databases, or the entire deployment.

```javascript
// Watch a single collection for inserts and updates
const pipeline = [
  { $match: {
    operationType: { $in: ["insert", "update"] },
    "fullDocument.status": "urgent"
  }}
];

const changeStream = db.collection("tickets").watch(pipeline, {
  fullDocument: "updateLookup"  // include the full document on updates
});

changeStream.on("change", (change) => {
  console.log("Change detected:", change.operationType);
  console.log("Document:", change.fullDocument);
  console.log("Resume token:", change.resumeToken);

  // Process the change (e.g., send notification, update cache)
  notifyTeam(change.fullDocument);
});

// Handle errors and resume from last known position
changeStream.on("error", (error) => {
  console.error("Change stream error:", error);
  // Reconnect using the stored resume token
});
```

**Resumable pattern for production:**

```javascript
let resumeToken = await loadResumeTokenFromStorage();

async function watchWithResume(collection) {
  const options = { fullDocument: "updateLookup" };
  if (resumeToken) {
    options.resumeAfter = resumeToken;
  }

  const stream = collection.watch([], options);

  stream.on("change", async (change) => {
    // Process change
    await handleChange(change);

    // Persist resume token so we can recover after restart
    resumeToken = change._id;
    await saveResumeTokenToStorage(resumeToken);
  });

  stream.on("error", async () => {
    // Wait and reconnect
    await new Promise(r => setTimeout(r, 5000));
    watchWithResume(collection);
  });
}
```

**Use cases:** real-time dashboards, cache invalidation, event-driven architectures, syncing data to search indexes (e.g., Elasticsearch).

---

### 6. Performance

#### Reading explain() output

```javascript
// Run explain to see the query plan
db.orders.find({
  userId: ObjectId("6651a..."),
  status: "pending"
}).sort({ placedAt: -1 }).explain("executionStats");
```

**Key fields in executionStats:**

| Field | What to look for |
|-------|-----------------|
| `winningPlan.stage` | `IXSCAN` good, `COLLSCAN` bad (full collection scan) |
| `totalKeysExamined` | Should be close to `nReturned` (no wasted index scans) |
| `totalDocsExamined` | Should be close to `nReturned` (no wasted document reads) |
| `executionTimeMillis` | Overall query time |
| `rejectedPlans` | Shows alternatives the optimizer considered |

**Covered queries -- answered entirely from the index:**

```javascript
// Create an index that covers the query
db.orders.createIndex({ userId: 1, status: 1, totalCents: 1 });

// This query only needs fields in the index -- no document fetch
db.orders.find(
  { userId: ObjectId("6651a..."), status: "delivered" },
  { _id: 0, totalCents: 1 }  // projection must exclude _id and only include indexed fields
);
// explain() will show: "totalDocsExamined": 0
```

**Projection optimization -- fetch only what you need:**

```javascript
// BAD: fetches entire document including large body field
const posts = await db.posts.find({ author: userId }).toArray();

// GOOD: only fetch fields needed for the list view
const posts = await db.posts.find(
  { author: userId },
  { projection: { title: 1, publishedAt: 1, tags: 1 } }
).toArray();
```

**Bulk operations for write-heavy workloads:**

```javascript
const bulk = db.products.initializeUnorderedBulkOp();

for (const update of priceUpdates) {
  bulk.find({ sku: update.sku })
      .updateOne({ $set: { priceCents: update.newPrice, updatedAt: new Date() } });
}

const result = await bulk.execute();
console.log(`Modified: ${result.nModified}, Errors: ${result.getWriteErrorCount()}`);
```

---

## Best Practices

1. **Design schema around query patterns, not data relationships.** Ask "how will I read this data?" before "how does this data relate?" Embed data that is always fetched together; reference data accessed independently.

2. **Use the ESR rule for compound indexes.** Order index fields by Equality, Sort, Range. This maximizes the index's usefulness and minimizes keys examined.

3. **Set read/write concerns appropriately.** Use `w: "majority"` and `readConcern: "majority"` for data that must survive failovers. Use `w: 1` for non-critical writes where speed matters more than durability.

4. **Use projection to limit returned fields.** Transferring large documents over the network when you only need two fields wastes bandwidth and memory. Always project.

5. **Avoid unbounded array growth.** An embedded array that can grow to thousands of elements bloats the document (16 MB max) and degrades performance. Move to a separate collection with a reference when the array exceeds ~100 elements.

6. **Use bulk operations for batch writes.** Individual `insertOne` or `updateOne` calls in a loop are slow. Batch them with `bulkWrite` or `initializeUnorderedBulkOp` for 10-50x throughput improvement.

7. **Enable retryable writes.** Add `retryWrites=true` to your connection string. This handles transient network errors and primary elections automatically without application-level retry logic.

8. **Monitor with database profiler and serverStatus.** Use `db.setProfilingLevel(1, { slowms: 100 })` to log slow queries. Check `db.serverStatus().opcounters` and `db.serverStatus().connections` for overall health.

## Common Pitfalls

1. **Treating MongoDB like a relational database.** Normalizing everything into separate collections and using `$lookup` for every query defeats the purpose. If you need heavy joins, PostgreSQL is likely a better fit. Design for embedding first.

2. **Missing indexes on query fields.** Every `find()`, `$match`, and `sort()` should be backed by an index. Use `db.collection.getIndexes()` and `explain()` to verify. A `COLLSCAN` on a large collection is almost always a bug.

3. **Ignoring the 16 MB document size limit.** Embedding unbounded arrays (comments, logs, events) will eventually hit this wall, crashing writes. Use the bucket pattern (fixed-size sub-documents) or reference a separate collection.

4. **Not using readPreference for read-heavy workloads.** By default all reads go to the primary. For analytics or non-critical reads, use `readPreference: "secondaryPreferred"` to distribute load across replicas.

5. **Forgetting that updates replace matched array elements, not all of them.** Using `$set` on a matched array element with positional `$` only updates the first match. Use `$[]` for all elements or `$[<identifier>]` with `arrayFilters` for conditional updates:

```javascript
// Update price for a specific item in all orders
db.orders.updateMany(
  { "items.sku": "WIDGET-001" },
  { $set: { "items.$[item].priceCents": 2499 } },
  { arrayFilters: [{ "item.sku": "WIDGET-001" }] }
);
```

6. **Running aggregation pipelines without early $match.** Always filter as early as possible in the pipeline. A `$group` or `$unwind` before `$match` processes the entire collection unnecessarily. Put `$match` first to leverage indexes and reduce documents flowing through subsequent stages.

## Related Skills

- `databases/postgresql` - Relational database patterns for structured data with complex relationships
- `patterns/caching` - Caching strategies to reduce database load
- `patterns/logging` - Logging patterns for query debugging and monitoring
