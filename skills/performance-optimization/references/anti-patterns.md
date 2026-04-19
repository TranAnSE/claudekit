# Performance Anti-Patterns

## N+1 Queries

**Signal**: Many small queries instead of one batch query.

### SQLAlchemy (Python)
```python
# BAD: N+1 — each user triggers a query for posts
users = session.query(User).all()
for user in users:
    print(user.posts)  # lazy load, 1 query per user

# GOOD: eager loading
from sqlalchemy.orm import joinedload, selectinload
users = session.query(User).options(selectinload(User.posts)).all()
```

### Prisma (TypeScript)
```typescript
// BAD: N+1
const users = await prisma.user.findMany();
for (const user of users) {
  const posts = await prisma.post.findMany({ where: { authorId: user.id } });
}

// GOOD: include
const users = await prisma.user.findMany({ include: { posts: true } });
```

### Django
```python
# BAD
for order in Order.objects.all():
    print(order.customer.name)  # N+1

# GOOD
for order in Order.objects.select_related('customer').all():
    print(order.customer.name)  # 1 query with JOIN
```

## Unnecessary Re-renders (React)

**Signal**: Components re-rendering when their data hasn't changed.

```typescript
// BAD: new object created every render
<Child style={{ color: 'red' }} />

// GOOD: stable reference
const style = useMemo(() => ({ color: 'red' }), []);
<Child style={style} />

// BAD: new function every render
<Button onClick={() => handleClick(id)} />

// GOOD: stable callback
const handleClick = useCallback(() => doSomething(id), [id]);
<Button onClick={handleClick} />
```

Detect with: React DevTools Profiler → "Highlight updates when components render"

## Blocking the Event Loop (Node.js)

**Signal**: High event loop lag, slow response times.

```typescript
// BAD: synchronous file read blocks everything
const data = fs.readFileSync('large-file.json');

// GOOD: async
const data = await fs.promises.readFile('large-file.json');

// BAD: CPU-heavy in main thread
const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512');

// GOOD: async or worker_threads
const hash = await new Promise((resolve, reject) => {
  crypto.pbkdf2(password, salt, 100000, 64, 'sha512', (err, key) => {
    err ? reject(err) : resolve(key);
  });
});
```

## Memory Leaks

### Python
- Circular references with `__del__`
- Unclosed file handles / DB connections
- Growing global caches without TTL
- Detect: `objgraph`, `tracemalloc`

### JavaScript
- Detached DOM nodes
- Forgotten event listeners (`addEventListener` without `removeEventListener`)
- Closures capturing large scopes
- Unbounded `Map`/`Set` growth
- Detect: Chrome Heap Snapshots, `process.memoryUsage()`

## Heavy Imports / Bundle Bloat

```typescript
// BAD: imports entire library
import _ from 'lodash';

// GOOD: tree-shakeable import
import { debounce } from 'lodash-es';

// GOOD: native alternative
const debounce = (fn, ms) => { /* 5 lines */ };
```

Replace heavy deps: moment → dayjs, lodash → lodash-es or native, date-fns (tree-shakeable).
Use `React.lazy()` + `Suspense` for route-based code splitting.
