# MongoDB Schema Design Patterns

Quick reference for embedding vs referencing decisions and common schema patterns.

## Embedding vs Referencing Decision Tree

```
What is the relationship cardinality?
|
+-- One-to-Few (< 50 items)?
|   --> EMBED in parent document
|   Example: user.addresses, post.tags
|
+-- One-to-Many (50 - 1000s)?
|   |
|   +-- Child data always accessed with parent?
|   |   --> EMBED (but watch 16 MB doc limit)
|   |
|   +-- Child data accessed independently?
|   |   --> REFERENCE (store child _id in parent array)
|   |
|   +-- Need atomic updates across parent + children?
|       --> EMBED
|
+-- One-to-Millions?
|   --> REFERENCE from child to parent
|   Example: log_entry.host_id (not host.log_entry_ids)
|
+-- Many-to-Many?
    --> REFERENCE with array of _ids on one or both sides
    Example: student.course_ids[], course.student_ids[]
```

## Decision Factors

| Factor | Favor Embedding | Favor Referencing |
|--------|----------------|-------------------|
| **Read pattern** | Always read together | Read independently |
| **Write pattern** | Infrequent child updates | Frequent child updates |
| **Data size** | Small, bounded children | Large or growing children |
| **Atomicity** | Need single-doc transactions | Can tolerate multi-doc txn |
| **Duplication** | OK to denormalize | Must avoid duplication |
| **Cardinality** | Few items | Many/unbounded items |
| **Document size** | Well under 16 MB limit | Approaching 16 MB |

## Pattern Catalog

### 1. Subset Pattern

**Problem**: Document is large but reads only need a few fields from embedded data.

**Solution**: Embed a subset; keep full data in a separate collection.

```javascript
// products collection - fast reads for listing pages
{
  _id: ObjectId("..."),
  name: "Widget",
  price: 29.99,
  // Only the 10 most recent reviews (subset)
  recent_reviews: [
    { user: "alice", rating: 5, text: "Great!", date: ISODate("...") }
  ],
  review_count: 247
}

// reviews collection - full review data
{
  _id: ObjectId("..."),
  product_id: ObjectId("..."),
  user: "alice",
  rating: 5,
  text: "Great!",
  date: ISODate("..."),
  helpful_votes: 12
}
```

**When to use**: Product pages, user profiles, any "preview + detail" pattern.

### 2. Computed Pattern

**Problem**: Expensive aggregation queries run repeatedly on the same data.

**Solution**: Pre-compute and store the result, update on write.

```javascript
// movies collection
{
  _id: ObjectId("..."),
  title: "Example Movie",
  // Pre-computed from screenings collection
  computed: {
    total_revenue: 1250000,
    avg_rating: 4.2,
    rating_count: 843,
    last_computed: ISODate("2025-01-15T00:00:00Z")
  }
}
```

**Update strategy**: On each new rating, increment count and recalculate average. Or use a background job for less time-sensitive data.

**When to use**: Dashboards, leaderboards, summary statistics.

### 3. Bucket Pattern

**Problem**: Many small, time-series documents create overhead (indexes, storage per doc).

**Solution**: Group related data into fixed-size buckets.

```javascript
// sensor_readings collection - one doc per sensor per hour
{
  sensor_id: "sensor-42",
  bucket_start: ISODate("2025-01-15T14:00:00Z"),
  bucket_end: ISODate("2025-01-15T14:59:59Z"),
  count: 60,
  readings: [
    { ts: ISODate("2025-01-15T14:00:00Z"), temp: 22.1, humidity: 45 },
    { ts: ISODate("2025-01-15T14:01:00Z"), temp: 22.3, humidity: 44 }
    // ... up to 60 readings per bucket
  ],
  // Pre-computed aggregates for the bucket
  summary: {
    avg_temp: 22.4,
    min_temp: 21.8,
    max_temp: 23.1
  }
}
```

**Bucket sizing**: Choose a size that balances doc count reduction vs update frequency. Common choices: 1 hour, 1 day, 100 events.

**When to use**: IoT, time-series, event logging, analytics.

### 4. Outlier Pattern

**Problem**: A few documents have vastly more data than the norm (e.g., a viral post with millions of likes).

**Solution**: Flag outliers and overflow into separate documents.

```javascript
// books collection - normal case
{
  _id: ObjectId("..."),
  title: "Normal Book",
  customers_purchased: ["user1", "user2", "user3"],
  has_overflow: false
}

// books collection - outlier (bestseller)
{
  _id: ObjectId("..."),
  title: "Bestseller",
  customers_purchased: ["user1", "user2", /* ... first 1000 */],
  has_overflow: true
}

// book_purchases_overflow collection
{
  book_id: ObjectId("..."),
  page: 2,
  customers_purchased: ["user1001", "user1002", /* ... next 1000 */]
}
```

**When to use**: Social media (viral posts), e-commerce (bestsellers), any data with power-law distribution.

### 5. Extended Reference Pattern

**Problem**: Frequent joins (lookups) to get a few fields from a referenced document.

**Solution**: Copy the most-accessed fields into the referencing document.

```javascript
// orders collection
{
  _id: ObjectId("..."),
  date: ISODate("..."),
  customer_id: ObjectId("..."),
  // Extended reference - copied fields for fast reads
  customer_name: "Alice Smith",
  customer_email: "alice@example.com",
  items: [
    {
      product_id: ObjectId("..."),
      product_name: "Widget",  // copied
      price: 29.99,            // copied (snapshot at time of order)
      quantity: 2
    }
  ]
}
```

**Trade-off**: Stale data is acceptable (order snapshots price at purchase time). For data that must be current, keep only the reference.

**When to use**: Orders (snapshot pricing), notifications (snapshot user name), audit logs.

### 6. Polymorphic Pattern

**Problem**: Objects share some fields but differ in others (e.g., different product types).

**Solution**: Store in a single collection with a type discriminator.

```javascript
// vehicles collection
{ type: "car", make: "Toyota", doors: 4, trunk_size_liters: 450 }
{ type: "truck", make: "Ford", doors: 2, payload_kg: 5000 }
{ type: "motorcycle", make: "Harley", engine_cc: 1200 }
```

**Index strategy**: Index common fields. Use partial indexes for type-specific fields.

```javascript
db.vehicles.createIndex(
  { payload_kg: 1 },
  { partialFilterExpression: { type: "truck" } }
);
```

**When to use**: Product catalogs, content management (articles, videos, images), mixed event streams.

## Anti-Patterns

| Mistake | Problem | Fix |
|---------|---------|-----|
| Unbounded array growth | Document exceeds 16 MB | Use bucket or outlier pattern |
| Deep nesting (> 3 levels) | Hard to query and index | Flatten or reference |
| Normalizing everything | Too many lookups, slow reads | Embed when read together |
| Embedding large blobs | Wastes RAM in working set | Store in GridFS or S3 |
| No schema validation | Inconsistent data over time | Use JSON Schema validation |
| Indexing every field | Slow writes, wasted space | Index based on query patterns |

## Schema Validation

Use `db.createCollection()` with `$jsonSchema` validator to enforce structure. Set `validationLevel: "moderate"` to apply only on inserts and updates (not existing docs).
