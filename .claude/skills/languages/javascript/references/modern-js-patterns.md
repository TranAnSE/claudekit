# Modern JavaScript Patterns Quick Reference

> ES2020+ patterns. All examples work in current Node.js (18+) and modern browsers.

## Destructuring Tricks

```javascript
// Nested destructuring with rename and default
const { data: { users: members = [] } = {} } = response;

// Array destructuring: skip elements
const [first, , third] = [1, 2, 3];

// Swap variables
[a, b] = [b, a];

// Rest in both arrays and objects
const { id, ...rest } = user;
const [head, ...tail] = items;

// Destructure function parameters
function draw({ x = 0, y = 0, color = "black" } = {}) { /* ... */ }

// Dynamic property destructuring
const key = "name";
const { [key]: value } = { name: "Alice" }; // value = "Alice"

// Destructure from iterables
const [a, b] = new Map([["a", 1], ["b", 2]]);
```

## Optional Chaining (?.)

```javascript
// Property access
const city = user?.address?.city;

// Method call (only calls if method exists)
const result = api?.getData?.();

// Bracket notation
const val = obj?.["dynamic-key"];

// Array index
const first = arr?.[0];

// Combine with nullish coalescing
const name = user?.profile?.name ?? "Anonymous";

// Short-circuit: stops evaluating after first nullish
const len = response?.data?.items?.length; // undefined if any is nullish
```

## Nullish Coalescing (??) vs OR (||)

```javascript
// ?? only triggers on null/undefined (NOT 0, "", false)
0  ?? "fallback"    // 0
"" ?? "fallback"    // ""
null ?? "fallback"  // "fallback"

// || triggers on any falsy value
0  || "fallback"    // "fallback"
"" || "fallback"    // "fallback"
null || "fallback"  // "fallback"

// Use ?? for values where 0/empty string are valid
const port = config.port ?? 3000;
const title = config.title ?? "Untitled";
```

## Logical Assignment Operators

```javascript
// ??= assigns only if current value is null/undefined
user.name ??= "Anonymous";
// Equivalent: user.name = user.name ?? "Anonymous"

// ||= assigns if current value is falsy
opts.verbose ||= false;
// Equivalent: opts.verbose = opts.verbose || false

// &&= assigns only if current value is truthy
user.token &&= encrypt(user.token);
// Equivalent: user.token = user.token && encrypt(user.token)
```

## structuredClone (Deep Copy)

```javascript
// Deep clone objects, arrays, Maps, Sets, Dates, RegExp, etc.
const original = { date: new Date(), nested: { arr: [1, 2] } };
const clone = structuredClone(original);
clone.nested.arr.push(3); // original not affected

// Works with circular references
const obj = { self: null };
obj.self = obj;
const copy = structuredClone(obj); // OK

// Does NOT clone: functions, DOM nodes, symbols, prototype chain
// Throws on: functions, Error objects (in some engines)
```

## Proxy

```javascript
// Validation proxy
const validated = new Proxy({}, {
  set(target, prop, value) {
    if (prop === "age" && (typeof value !== "number" || value < 0)) {
      throw new TypeError("Age must be a non-negative number");
    }
    target[prop] = value;
    return true;
  }
});

// Read-only proxy
function readonly(target) {
  return new Proxy(target, {
    set() { throw new Error("Read-only object"); },
    deleteProperty() { throw new Error("Read-only object"); }
  });
}

// Default values proxy
function withDefaults(target, defaults) {
  return new Proxy(target, {
    get(obj, prop) {
      return prop in obj ? obj[prop] : defaults[prop];
    }
  });
}
const config = withDefaults({}, { theme: "dark", lang: "en" });
config.theme; // "dark"

// Logging / observation proxy
function observable(target, onChange) {
  return new Proxy(target, {
    set(obj, prop, value) {
      const old = obj[prop];
      obj[prop] = value;
      onChange(prop, old, value);
      return true;
    }
  });
}
```

## Generators

```javascript
// Basic generator
function* range(start, end, step = 1) {
  for (let i = start; i < end; i += step) {
    yield i;
  }
}
for (const n of range(0, 10, 2)) { /* 0, 2, 4, 6, 8 */ }

// Infinite sequence
function* ids() {
  let id = 0;
  while (true) yield id++;
}
const gen = ids();
gen.next().value; // 0
gen.next().value; // 1

// Delegate to another generator
function* concat(...iterables) {
  for (const it of iterables) {
    yield* it;
  }
}

// Two-way communication
function* stateMachine() {
  let input;
  while (true) {
    input = yield `received: ${input}`;
  }
}
const sm = stateMachine();
sm.next();            // { value: "received: undefined" }
sm.next("hello");     // { value: "received: hello" }
```

## Async Iterators

```javascript
// for-await-of
async function processStream(stream) {
  for await (const chunk of stream) {
    console.log(chunk);
  }
}

// Async generator
async function* fetchPages(url) {
  let page = 1;
  while (true) {
    const res = await fetch(`${url}?page=${page}`);
    const data = await res.json();
    if (data.items.length === 0) return;
    yield data.items;
    page++;
  }
}

for await (const items of fetchPages("/api/users")) {
  console.log(items);
}

```

## Other Modern Patterns

```javascript
// Object.groupBy (ES2024)
const grouped = Object.groupBy(users, u => u.role);

// at() - negative indexing
[1, 2, 3].at(-1); // 3

// Object.hasOwn (replaces hasOwnProperty)
Object.hasOwn(obj, "key"); // true/false

// Error cause chaining
throw new Error("DB failed", { cause: originalError });

// AbortSignal.timeout (built-in timeout)
fetch(url, { signal: AbortSignal.timeout(5000) });

// using keyword (explicit resource management, ES2024+)
{ using handle = openFile("data.txt"); } // auto-disposed at block exit
```

## Promise Combinators

| Method | Settles when | Returns |
|--------|-------------|---------|
| `Promise.all(ps)` | All fulfill or one rejects | Array of values |
| `Promise.allSettled(ps)` | All settle | Array of `{status, value/reason}` |
| `Promise.race(ps)` | First settles | First value or rejection |
| `Promise.any(ps)` | First fulfills | First value (AggregateError if all reject) |
