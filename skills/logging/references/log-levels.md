# Log Levels Quick Reference

## Level Summary

| Level | When to Use | Audience | Production Default |
|-------|------------|----------|-------------------|
| **DEBUG** | Detailed diagnostic info | Developers debugging | Off |
| **INFO** | Routine operational events | Ops team monitoring | On |
| **WARNING** | Something unexpected but handled | Ops + Devs | On |
| **ERROR** | Operation failed, needs attention | On-call engineers | On |
| **CRITICAL** | System is unusable or data at risk | On-call + management | On + alert |

---

## DEBUG

**Purpose**: Fine-grained information useful only when diagnosing problems.

**Turn on**: During local development or when investigating a specific issue.

| Good | Bad |
|------|-----|
| `Parsing config file: /etc/app/config.yaml` | `Entering function parse_config` |
| `Cache miss for key user:123, fetching from DB` | `x = 5` |
| `SQL: SELECT * FROM users WHERE id=$1 [params: 123]` | `Here we go!` |
| `Retry attempt 2/3 for payment gateway` | `Debug debug debug` |
| `JWT token expires at 2025-01-29T10:00:00Z` | `token = eyJhbG...` (secret!) |

**Rule**: Never log secrets, tokens, passwords, or PII at any level.

---

## INFO

**Purpose**: Confirm the system is working as expected. Key business events.

| Good | Bad |
|------|-----|
| `Server started on port 8080` | `Server is running` (which port? which version?) |
| `User user:456 created account via OAuth (Google)` | `New user` |
| `Order ord:789 placed, total=$45.00, items=3` | `Order created` |
| `Migration v42 applied successfully (12 tables)` | `Migration done` |
| `Scheduled job "daily-report" completed in 4.2s` | `Job finished` |
| `Payment processed: txn:abc, amount=$99, method=card` | `Payment OK` |

**Rule**: Include enough context to answer "what happened, to what, and relevant numbers."

---

## WARNING

**Purpose**: Something unexpected happened, but the system handled it. May indicate a future problem.

| Good | Bad |
|------|-----|
| `Connection pool at 85% capacity (17/20)` | `Pool getting full` |
| `Deprecated API v1 called by client app:legacy (use v2)` | `Old API used` |
| `Disk space below 10% on /data (2.1 GB remaining)` | `Low disk` |
| `Request took 4.8s (threshold: 5s) for GET /api/search` | `Slow request` |
| `Config REDIS_URL missing, falling back to in-memory cache` | `No Redis` |
| `Rate limit approaching for IP 10.0.0.5: 90/100 requests` | `Almost rate limited` |

**Rule**: Warnings should be actionable. If nobody would investigate, it's DEBUG or INFO.

---

## ERROR

**Purpose**: An operation failed. The system can continue, but something broke.

| Good | Bad |
|------|-----|
| `Failed to send email to user:123: SMTP timeout after 30s` | `Email error` |
| `Payment declined for order:789: card_expired (Stripe)` | `Payment failed` |
| `Database query timeout after 10s: SELECT FROM orders WHERE...` | `DB error` |
| `File upload failed: S3 returned 503, bucket=media, key=img/456.jpg` | `Upload error` |
| `Unhandled exception in POST /api/orders: ValueError("...")` | (stack trace only, no context) |

**Rule**: Include the operation, the target/ID, the error detail, and what was attempted.

---

## CRITICAL

**Purpose**: System is unusable or data integrity is at risk. Requires immediate human intervention.

| Good | Bad |
|------|-----|
| `Database connection lost, all pools exhausted, 0/20 available` | `DB down` |
| `Disk full on /data, writes failing, data loss possible` | `No disk space` |
| `Security: 500 failed login attempts from IP 10.0.0.5 in 60s` | `Too many logins` |
| `Data corruption detected: order:789 total=-$50.00` | `Bad data` |
| `TLS certificate expires in 24h, auto-renewal failed` | `Cert expiring` |

**Rule**: Every CRITICAL log should trigger an alert (PagerDuty, Slack, etc.).

---

## Structured Logging Format

### Python (structlog)

```python
import structlog

log = structlog.get_logger()

log.info("order.placed", order_id="ord:789", total=45.00, items=3)
log.error("email.send_failed", user_id="user:123", error="SMTP timeout", retry=2)
```

### TypeScript (pino)

```typescript
import pino from "pino";

const log = pino({ level: "info" });

log.info({ orderId: "ord:789", total: 45.0, items: 3 }, "order.placed");
log.error({ userId: "user:123", err, retry: 2 }, "email.send_failed");
```

### Key-Value Best Practices

| Field | Purpose | Example |
|-------|---------|---------|
| `event` / message | What happened | `"order.placed"` |
| `request_id` | Trace across services | `"req_abc123"` |
| `user_id` | Who triggered it | `"user:456"` |
| `duration_ms` | How long it took | `142` |
| `error` | Error message (not stack in prod) | `"connection refused"` |
| `component` | Which module/service | `"payment-gateway"` |

---

## Configuration by Environment

| Environment | Minimum Level | Structured? | Destination |
|-------------|--------------|-------------|-------------|
| Local dev | DEBUG | No (human-readable) | stdout |
| CI/Test | WARNING | No | stdout |
| Staging | DEBUG | Yes (JSON) | Log aggregator |
| Production | INFO | Yes (JSON) | Log aggregator |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Logging PII/secrets | Security/compliance violation | Redact or mask sensitive fields |
| `log.error()` in a loop | Log flooding, storage cost | Log once with count |
| `log.error("Error: " + err)` | Missing context, hard to search | Use structured fields |
| Logging at wrong level | Alert fatigue or missed issues | Follow the guide above |
| Catch-log-rethrow | Duplicate log entries | Log at the handling site only |
| No request_id | Cannot correlate logs | Add correlation ID middleware |
| Logging full request bodies | Performance, storage, PII risk | Log summary fields only |
