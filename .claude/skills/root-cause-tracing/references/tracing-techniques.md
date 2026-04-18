# Tracing Techniques Reference

Backward-tracing techniques for systematic root cause analysis.

## Stack Trace Analysis

### Reading a Stack Trace

1. Start at the **bottom** (most recent call) to find the immediate failure
2. Scan **upward** to find the first frame in **your code** (not library code)
3. That frame is usually the symptom location, not the cause
4. Continue upward to find where bad data or state originated

### Symptom vs Cause

| What You See | Likely Actual Cause |
|---|---|
| `NullPointerException` / `TypeError: cannot read property of undefined` | Value not set upstream, missing null check at origin |
| `IndexOutOfBoundsException` | Off-by-one in loop logic or empty collection not guarded |
| `ConnectionRefusedError` | Service down, wrong port, firewall rule, DNS resolution |
| `TimeoutError` | Deadlock, resource exhaustion, slow query, network partition |
| `ValidationError` | Caller passing wrong shape, schema mismatch, migration gap |

### Tips

- Filter out framework frames to reduce noise
- In async code, the stack may be split; look for `caused by` or `previous` sections
- In Python, read `__cause__` and `__context__` on chained exceptions
- In TypeScript/Node, check `error.cause` (ES2022+)

## Binary Search / Git Bisect

### When to Use

- Bug exists now but worked at some known-good point
- Reproducer is automatable (script, test command)

### Process

```bash
git bisect start
git bisect bad                    # current commit is broken
git bisect good <known-good-sha> # last known working commit
# Git checks out a midpoint; run your test
git bisect good   # or bad, based on result
# Repeat until Git identifies the first bad commit
git bisect reset  # return to original branch
```

### Automated Bisect

```bash
git bisect start HEAD <good-sha>
git bisect run ./test-script.sh
# Exit 0 = good, exit 1 = bad, exit 125 = skip
```

## Log Correlation

### Technique

1. Identify the **exact timestamp** of the error
2. Search all related service logs within a window (e.g., +/- 30 seconds)
3. Filter by **correlation ID**, **request ID**, or **user ID** across services
4. Build a timeline of events across services

### Correlation Fields to Look For

- `request_id` or `trace_id` (distributed tracing)
- `user_id` or `session_id`
- Source IP or client identifier
- Timestamps (normalize to UTC)

### Tools

- `grep` / `rg` with timestamp ranges
- Structured logging with JSON output + `jq`
- Distributed tracing (OpenTelemetry, Jaeger, Zipkin)

## Dependency Analysis (Backward Data Flow)

### Process

1. Start at the error location
2. Identify the **variable or value** that is wrong
3. Trace backward: where was this value set?
4. At each step, ask: is this value correct here? If yes, move forward. If no, keep going back.
5. The root cause is where correct data first becomes incorrect.

### Common Data Flow Points

```
User Input -> Validation -> Transform -> Business Logic -> Persistence -> Query -> Response
```

Trace backward through this chain from wherever the error manifests.

### Dependency Categories

| Dependency | What to Check |
|---|---|
| Function arguments | Caller passing wrong values |
| Config / env vars | Wrong environment, stale config |
| Database state | Missing migration, corrupt data |
| External API | Changed response format, auth expiry |
| Shared state | Race condition, stale cache |

## Instrumentation Points

### Where to Add Temporary Logging

1. **Entry/exit of suspected function** — log arguments and return value
2. **Before/after external calls** — log request and response
3. **Branch points** — log which path was taken and why
4. **Data transformation steps** — log before and after
5. **Error handlers** — log the full error with context

### Guidelines

- Use a distinct prefix (e.g., `[DEBUG-TRACE]`) so logs are easy to find and remove
- Log the **type** as well as the **value** (catches `"null"` vs `null`)
- In production, use feature flags or debug log levels, not code changes
- Remove all temporary logging before committing

### Python Example

```python
import logging
logger = logging.getLogger(__name__)

def process_order(order_id: str) -> Order:
    logger.debug("[DEBUG-TRACE] process_order called with: %s (type: %s)", order_id, type(order_id))
    order = db.get_order(order_id)
    logger.debug("[DEBUG-TRACE] db.get_order returned: %s", order)
    # ... rest of logic
```

### TypeScript Example

```typescript
function processOrder(orderId: string): Order {
  console.debug(`[DEBUG-TRACE] processOrder called with: ${orderId} (type: ${typeof orderId})`);
  const order = db.getOrder(orderId);
  console.debug(`[DEBUG-TRACE] db.getOrder returned:`, order);
  // ... rest of logic
}
```

## Common Root Cause Categories

| Category | Symptoms | Investigation Approach |
|---|---|---|
| **Data issues** | Wrong output, validation errors, corrupt state | Trace the bad value backward through the data flow |
| **Race conditions** | Intermittent failures, works-on-retry, order-dependent | Look for shared mutable state, add timing logs, test with delays |
| **Config drift** | Works locally but not in staging/prod | Diff environment configs, check env vars, verify secrets |
| **Dependency changes** | Broke after deploy with no code changes | Check lock file diffs, dependency changelogs, API version headers |
| **Resource exhaustion** | Timeouts, OOM, connection pool errors | Monitor metrics (memory, CPU, connections, disk), check for leaks |
| **Schema mismatch** | Serialization errors, missing fields | Compare expected vs actual schema, check migration status |

## Quick Decision: Which Technique to Use

| Situation | Start With |
|---|---|
| Have a stack trace | Stack trace analysis |
| "It used to work" | Git bisect |
| Multi-service issue | Log correlation |
| Wrong data in output | Backward data flow |
| No idea where to start | Add instrumentation at boundaries |
