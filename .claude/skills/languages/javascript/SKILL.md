---
name: javascript
description: >
  Trigger this skill whenever working with JavaScript files (.js, .mjs, .cjs), writing Node.js applications without TypeScript, or using ES6+ patterns like destructuring, async/await, optional chaining, and modules. Activate for browser scripting, vanilla JS projects, or when the user asks about JavaScript-specific idioms, ESLint configuration, or modern syntax. Also use when dealing with package.json scripts, CommonJS vs ESM, or JavaScript class patterns.
---

# JavaScript

## When to Use

- Working with JavaScript files (.js, .mjs)
- Browser scripting
- Node.js applications without TypeScript

## When NOT to Use

- TypeScript projects -- use the `languages/typescript` skill instead, which covers typed JavaScript patterns
- Python-only projects with no JavaScript components

---

## Core Patterns

### 1. Modern Syntax

#### Destructuring (Nested, Defaults, Rest)

```javascript
// Object destructuring with defaults and rename
const { name, email, role = "user", address: { city } = {} } = user;

// Nested destructuring
const {
  data: {
    attributes: { title, body },
  },
} = apiResponse;

// Array destructuring with rest
const [first, second, ...remaining] = items;

// Swap variables
let a = 1, b = 2;
[a, b] = [b, a];

// Function parameter destructuring
function createUser({ name, email, role = "user" }) {
  return { name, email, role, createdAt: new Date() };
}
```

#### Optional Chaining (?.)

```javascript
// Property access
const city = user?.address?.city;

// Method call
const uppercased = value?.toString?.();

// Array element
const firstItem = data?.items?.[0];

// Combine with nullish coalescing for defaults
const displayName = user?.profile?.displayName ?? user?.name ?? "Anonymous";
```

#### Nullish Coalescing (??)

```javascript
// Only falls through on null/undefined (not 0, "", false)
const port = config.port ?? 3000;
const name = input ?? "default";

// Contrast with || which falls through on all falsy values
const count = data.count ?? 0; // preserves 0
const count2 = data.count || 0; // replaces 0 with 0 (same here, but misleading)
const label = data.label ?? ""; // preserves ""
const label2 = data.label || "fallback"; // replaces "" with "fallback"
```

#### Logical Assignment (&&=, ||=, ??=)

```javascript
// ??= assigns only if null/undefined
user.name ??= "Anonymous";

// ||= assigns if falsy
config.retries ||= 3;

// &&= assigns only if truthy
user.session &&= refreshSession(user.session);

// Practical: initialize nested objects
const cache = {};
(cache.users ??= []).push(newUser);
```

---

### 2. Async Patterns

#### Promises

```javascript
function fetchJson(url) {
  return fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return response.json();
    });
}

// Chaining
fetchJson("/api/user")
  .then((user) => fetchJson(`/api/posts?userId=${user.id}`))
  .then((posts) => console.log(posts))
  .catch((error) => console.error("Failed:", error.message));
```

#### async/await

```javascript
async function loadUserDashboard(userId) {
  const user = await fetchJson(`/api/users/${userId}`);
  const posts = await fetchJson(`/api/users/${userId}/posts`);
  return { user, posts };
}
```

#### Promise.all / allSettled / race / any

```javascript
// Promise.all -- fail fast on first rejection
const [users, posts, comments] = await Promise.all([
  fetchJson("/api/users"),
  fetchJson("/api/posts"),
  fetchJson("/api/comments"),
]);

// Promise.allSettled -- wait for all, get status of each
const results = await Promise.allSettled([
  fetchJson("/api/fast"),
  fetchJson("/api/slow"),
  fetchJson("/api/flaky"),
]);
const successes = results
  .filter((r) => r.status === "fulfilled")
  .map((r) => r.value);
const failures = results
  .filter((r) => r.status === "rejected")
  .map((r) => r.reason);

// Promise.race -- first to settle wins
const result = await Promise.race([
  fetchJson("/api/primary"),
  new Promise((_, reject) =>
    setTimeout(() => reject(new Error("Timeout")), 5000)
  ),
]);

// Promise.any -- first to fulfill wins (ignores rejections)
const fastest = await Promise.any([
  fetchJson("/api/mirror1"),
  fetchJson("/api/mirror2"),
  fetchJson("/api/mirror3"),
]);
```

#### AbortController

```javascript
async function fetchWithTimeout(url, timeoutMs = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

// Cancellable request pattern
function createRequest(url) {
  const controller = new AbortController();
  return {
    promise: fetch(url, { signal: controller.signal }),
    cancel: () => controller.abort(),
  };
}
```

#### Async Iterators (for await...of)

```javascript
async function* paginateApi(baseUrl) {
  let page = 1;
  while (true) {
    const data = await fetchJson(`${baseUrl}?page=${page}`);
    if (data.items.length === 0) break;
    yield* data.items;
    page++;
  }
}

// Consume the async iterator
for await (const item of paginateApi("/api/records")) {
  processItem(item);
}
```

---

### 3. Closures & Scope

#### Closure Patterns

```javascript
// Counter with private state
function createCounter(initial = 0) {
  let count = initial;
  return {
    increment: () => ++count,
    decrement: () => --count,
    getCount: () => count,
    reset: () => { count = initial; },
  };
}

const counter = createCounter(10);
counter.increment(); // 11
counter.getCount(); // 11
```

#### Module Pattern (Private State via Closures)

```javascript
const rateLimiter = (() => {
  const requests = new Map();

  function isAllowed(clientId, maxPerMinute = 60) {
    const now = Date.now();
    const windowStart = now - 60_000;
    const clientRequests = (requests.get(clientId) ?? []).filter(
      (t) => t > windowStart
    );
    if (clientRequests.length >= maxPerMinute) return false;
    clientRequests.push(now);
    requests.set(clientId, clientRequests);
    return true;
  }

  function reset(clientId) {
    requests.delete(clientId);
  }

  return { isAllowed, reset };
})();
```

#### WeakRef and FinalizationRegistry

```javascript
// Cache that does not prevent garbage collection
const cache = new Map();

function getCached(key, factory) {
  const ref = cache.get(key);
  const cached = ref?.deref();
  if (cached !== undefined) return cached;

  const value = factory();
  cache.set(key, new WeakRef(value));
  return value;
}

// Cleanup when objects are garbage collected
const registry = new FinalizationRegistry((key) => {
  cache.delete(key);
});
```

---

### 4. Iteration Protocols

#### Custom Iterator

```javascript
class Range {
  constructor(start, end, step = 1) {
    this.start = start;
    this.end = end;
    this.step = step;
  }

  [Symbol.iterator]() {
    let current = this.start;
    const { end, step } = this;
    return {
      next() {
        if (current < end) {
          const value = current;
          current += step;
          return { value, done: false };
        }
        return { done: true };
      },
    };
  }
}

for (const n of new Range(0, 10, 2)) {
  console.log(n); // 0, 2, 4, 6, 8
}
```

#### Generators

```javascript
function* fibonacci() {
  let a = 0, b = 1;
  while (true) {
    yield a;
    [a, b] = [b, a + b];
  }
}

// Take first N values
function take(iterable, count) {
  const result = [];
  for (const value of iterable) {
    result.push(value);
    if (result.length >= count) break;
  }
  return result;
}

take(fibonacci(), 8); // [0, 1, 1, 2, 3, 5, 8, 13]
```

#### Lazy Evaluation with Generators

```javascript
function* map(iterable, fn) {
  for (const item of iterable) {
    yield fn(item);
  }
}

function* filter(iterable, predicate) {
  for (const item of iterable) {
    if (predicate(item)) yield item;
  }
}

// Compose lazily -- no intermediate arrays
const data = filter(
  map(readLargeFile(), (line) => line.trim()),
  (line) => line.length > 0
);
```

#### Async Generators

```javascript
async function* readChunks(reader) {
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    yield value;
  }
}

// Stream processing
const response = await fetch("/api/large-data");
for await (const chunk of readChunks(response.body.getReader())) {
  processChunk(chunk);
}
```

---

### 5. Proxy & Reflect

#### Validation Proxy

```javascript
function createValidated(target, validators) {
  return new Proxy(target, {
    set(obj, prop, value) {
      const validate = validators[prop];
      if (validate && !validate(value)) {
        throw new TypeError(`Invalid value for ${String(prop)}: ${value}`);
      }
      return Reflect.set(obj, prop, value);
    },
  });
}

const user = createValidated(
  { name: "", age: 0 },
  {
    name: (v) => typeof v === "string" && v.length > 0,
    age: (v) => typeof v === "number" && v >= 0 && v <= 150,
  }
);

user.name = "Alice"; // works
user.age = -1; // throws TypeError
```

#### Observable Object

```javascript
function createObservable(target, onChange) {
  return new Proxy(target, {
    set(obj, prop, value) {
      const oldValue = obj[prop];
      const result = Reflect.set(obj, prop, value);
      if (oldValue !== value) {
        onChange(prop, value, oldValue);
      }
      return result;
    },
    deleteProperty(obj, prop) {
      const oldValue = obj[prop];
      const result = Reflect.deleteProperty(obj, prop);
      onChange(prop, undefined, oldValue);
      return result;
    },
  });
}

const state = createObservable({}, (prop, newVal, oldVal) => {
  console.log(`${prop}: ${oldVal} -> ${newVal}`);
});
```

#### Property Access Logging

```javascript
function withLogging(target, label = "access") {
  return new Proxy(target, {
    get(obj, prop) {
      console.log(`[${label}] get .${String(prop)}`);
      return Reflect.get(obj, prop);
    },
    has(obj, prop) {
      console.log(`[${label}] has .${String(prop)}`);
      return Reflect.has(obj, prop);
    },
  });
}
```

---

### 6. Module System

#### ESM (import/export)

```javascript
// Named exports
export function formatDate(date) { ... }
export const MAX_RETRIES = 3;

// Default export
export default class ApiClient { ... }

// Re-exports
export { formatDate } from "./utils.js";
export { default as ApiClient } from "./api-client.js";
```

#### Dynamic import()

```javascript
// Lazy load modules
async function loadChart(type) {
  const module = await import(`./charts/${type}.js`);
  return new module.default();
}

// Conditional loading
const { marked } = await import("marked");

// With error handling
async function tryLoadPlugin(name) {
  try {
    return await import(`./plugins/${name}.js`);
  } catch {
    console.warn(`Plugin ${name} not available`);
    return null;
  }
}
```

#### import.meta

```javascript
// Current module URL
console.log(import.meta.url);

// Resolve relative paths (Node.js)
const configPath = new URL("./config.json", import.meta.url);

// Check if file is the entry point (Node.js)
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

// Vite environment variables
const apiUrl = import.meta.env.VITE_API_URL;
```

#### Top-level await

```javascript
// config.js -- top-level await in ESM modules
const response = await fetch("/api/config");
export const config = await response.json();

// db.js
import { createPool } from "./db-pool.js";
export const pool = await createPool(process.env.DATABASE_URL);
```

---

### 7. Performance

#### structuredClone

```javascript
// Deep clone without library (replaces JSON.parse(JSON.stringify(...)))
const original = { nested: { array: [1, 2, 3], date: new Date() } };
const clone = structuredClone(original);

// Handles Date, Map, Set, ArrayBuffer, RegExp (but not functions)
clone.nested.array.push(4);
console.log(original.nested.array.length); // still 3
```

#### requestAnimationFrame

```javascript
// Smooth animation loop
function animate(timestamp) {
  updatePosition(timestamp);
  render();
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

// Throttle DOM updates to frame rate
let rafId = null;
function scheduleUpdate(data) {
  if (rafId) cancelAnimationFrame(rafId);
  rafId = requestAnimationFrame(() => {
    applyDOMUpdate(data);
    rafId = null;
  });
}
```

#### requestIdleCallback

```javascript
// Run low-priority work when the browser is idle
function processQueue(queue) {
  requestIdleCallback((deadline) => {
    while (deadline.timeRemaining() > 0 && queue.length > 0) {
      const task = queue.shift();
      task();
    }
    if (queue.length > 0) {
      processQueue(queue); // schedule remaining
    }
  });
}
```

#### Web Workers Basics

```javascript
// main.js
const worker = new Worker(new URL("./worker.js", import.meta.url), {
  type: "module",
});

worker.postMessage({ data: largeDataSet, operation: "sort" });
worker.onmessage = (event) => {
  const sorted = event.data;
  renderResults(sorted);
};

// worker.js
self.onmessage = (event) => {
  const { data, operation } = event.data;
  if (operation === "sort") {
    self.postMessage(data.sort((a, b) => a - b));
  }
};
```

#### performance.mark / measure

```javascript
// Measure operation duration
performance.mark("fetch-start");
const data = await fetchJson("/api/data");
performance.mark("fetch-end");

performance.measure("fetch-duration", "fetch-start", "fetch-end");
const measurement = performance.getEntriesByName("fetch-duration")[0];
console.log(`Fetch took ${measurement.duration.toFixed(2)}ms`);

// Clean up
performance.clearMarks();
performance.clearMeasures();
```

---

## Best Practices

1. **Use `const` by default, `let` only when reassignment is needed** -- never use `var`. Block scoping prevents entire categories of bugs from hoisting and accidental mutation.

2. **Handle all promise rejections** -- unhandled rejections crash Node.js processes. Always use try/catch with await, or attach `.catch()` to promise chains. Add a global handler as a safety net.
   ```javascript
   process.on("unhandledRejection", (reason) => {
     console.error("Unhandled rejection:", reason);
     process.exit(1);
   });
   ```

3. **Use arrow functions for callbacks, regular functions for methods** -- arrow functions capture `this` from the enclosing scope, which is correct for callbacks but breaks object methods that need their own `this`.

4. **Prefer `for...of` over `for...in` for iteration** -- `for...in` iterates over all enumerable properties including inherited ones. Use `for...of` for arrays and iterables, `Object.entries()` for objects.

5. **Use ESLint and Prettier** -- enforce consistent style automatically. Configure in the project root and run on pre-commit hooks.

6. **Avoid mutating function arguments** -- create new objects and arrays with spread syntax instead of modifying inputs in place. This prevents action-at-a-distance bugs.

7. **Use `structuredClone` for deep copies** -- replaces the `JSON.parse(JSON.stringify(x))` hack. Handles Dates, Maps, Sets, and circular references correctly.

8. **Use private class fields (`#field`)** -- the `#` prefix creates truly private fields that cannot be accessed outside the class, unlike the `_` convention which is only a hint.

---

## Common Pitfalls

1. **Implicit type coercion** -- always use `===` and `!==`. The `==` operator performs type coercion with surprising rules (`"" == false`, `0 == null` is false but `0 == undefined` is also false, yet `null == undefined` is true).

2. **Forgetting `await`** -- a missing `await` silently returns a Promise object instead of the resolved value, causing hard-to-debug issues.
   ```javascript
   // BAD -- data is a Promise, not the response
   const data = fetchJson("/api/data");

   // GOOD
   const data = await fetchJson("/api/data");
   ```

3. **`this` binding in callbacks** -- regular functions in callbacks lose their `this` context. Use arrow functions or `.bind()`.
   ```javascript
   // BAD
   class Timer {
     start() { setTimeout(function() { this.tick(); }, 1000); }
   }

   // GOOD
   class Timer {
     start() { setTimeout(() => this.tick(), 1000); }
   }
   ```

4. **Mutating objects passed by reference** -- objects and arrays are passed by reference. Modifying a parameter modifies the original.
   ```javascript
   // BAD
   function addDefaults(config) {
     config.retries = config.retries ?? 3; // mutates caller's object
     return config;
   }

   // GOOD
   function addDefaults(config) {
     return { retries: 3, ...config };
   }
   ```

5. **`for...in` on arrays** -- iterates over indices as strings and includes inherited properties. Use `for...of` or array methods.
   ```javascript
   // BAD
   for (const i in [10, 20, 30]) {
     console.log(typeof i); // "string", not "number"
   }

   // GOOD
   for (const value of [10, 20, 30]) {
     console.log(value); // 10, 20, 30
   }
   ```

6. **Floating point arithmetic** -- `0.1 + 0.2 !== 0.3` in JavaScript. For financial calculations, work in integer cents or use a decimal library.
   ```javascript
   // BAD
   const total = 0.1 + 0.2; // 0.30000000000000004

   // GOOD
   const totalCents = 10 + 20; // 30
   const total = totalCents / 100; // 0.3
   ```

---

## Related Skills

- `languages/typescript` -- TypeScript for typed JavaScript development
- `frameworks/react` -- React component patterns
- `frameworks/nextjs` -- Next.js full-stack framework
- `testing/vitest` -- JavaScript/TypeScript testing with Vitest
