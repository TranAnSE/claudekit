# OWASP Top 10 (2021) Cheat Sheet

Quick reference for the OWASP Top 10 web application security risks.

---

## A01: Broken Access Control

**Risk**: Users act outside intended permissions (view other users' data, modify access).

**Prevention**: Deny by default. Enforce ownership. Disable directory listing. Log failures.

```python
# Enforce ownership check
def get_order(order_id, current_user):
    order = db.query(Order).get(order_id)
    if order.user_id != current_user.id:
        raise PermissionError("Access denied")
    return order
```

## A02: Cryptographic Failures

**Risk**: Exposure of sensitive data due to weak or missing encryption.

**Prevention**: Encrypt data at rest and in transit. Use strong algorithms (AES-256, bcrypt). Never store plaintext passwords.

```python
from passlib.hash import bcrypt
hashed = bcrypt.hash(password)
assert bcrypt.verify(password, hashed)
```

## A03: Injection

**Risk**: Untrusted data sent to an interpreter as part of a command or query.

**Prevention**: Use parameterized queries. Validate and sanitize all input. Use ORMs.

```python
# WRONG: cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
# RIGHT:
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

```typescript
// WRONG: db.query(`SELECT * FROM users WHERE id = ${id}`)
// RIGHT:
db.query("SELECT * FROM users WHERE id = $1", [id]);
```

## A04: Insecure Design

**Risk**: Missing or ineffective security controls due to flawed architecture.

**Prevention**: Use threat modeling. Apply secure design patterns. Establish reference architectures. Write abuse-case tests.

```python
# Rate-limit sensitive operations
from functools import lru_cache
from datetime import datetime, timedelta

LOGIN_ATTEMPTS = {}  # Use Redis in production

def check_rate_limit(ip: str, max_attempts=5, window=300):
    now = datetime.now().timestamp()
    attempts = [t for t in LOGIN_ATTEMPTS.get(ip, []) if now - t < window]
    if len(attempts) >= max_attempts:
        raise RateLimitExceeded()
    attempts.append(now)
    LOGIN_ATTEMPTS[ip] = attempts
```

## A05: Security Misconfiguration

**Risk**: Default configs, incomplete setups, open cloud storage, verbose errors.

**Prevention**: Repeatable hardening process. Minimal platform. Remove unused features. Review cloud permissions.

```yaml
# Docker: don't run as root
FROM python:3.12-slim
RUN useradd -m appuser
USER appuser
```

## A06: Vulnerable and Outdated Components

**Risk**: Using components with known vulnerabilities.

**Prevention**: Remove unused dependencies. Monitor CVEs. Use `pip audit`, `npm audit`. Pin versions.

```bash
pip audit                    # Python
npm audit                    # Node.js
npx depcheck                 # Find unused deps
```

## A07: Identification and Authentication Failures

**Risk**: Weak authentication, credential stuffing, session fixation.

**Prevention**: MFA. Strong password policies. Secure session management. Throttle failed logins.

```python
# Secure session config (Flask)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),
)
```

## A08: Software and Data Integrity Failures

**Risk**: Code and infrastructure that does not protect against integrity violations (CI/CD, unsigned updates).

**Prevention**: Verify signatures. Use lock files. Review CI/CD pipelines. Use Subresource Integrity.

```html
<!-- Subresource Integrity -->
<script src="https://cdn.example.com/lib.js"
  integrity="sha384-abc123..."
  crossorigin="anonymous"></script>
```

## A09: Security Logging and Monitoring Failures

**Risk**: Insufficient logging makes breaches undetectable.

**Prevention**: Log auth events, access control failures, input validation failures. Set up alerts.

```python
import logging

logger = logging.getLogger("security")

def login(username, password):
    user = authenticate(username, password)
    if not user:
        logger.warning("Failed login attempt", extra={
            "username": username,
            "ip": request.remote_addr,
            "timestamp": datetime.utcnow().isoformat(),
        })
        raise AuthenticationError()
    logger.info("Successful login", extra={"user_id": user.id})
```

## A10: Server-Side Request Forgery (SSRF)

**Risk**: Application fetches remote resources without validating user-supplied URLs.

**Prevention**: Allowlist URLs/domains. Block private IP ranges. Disable redirects.

```python
from urllib.parse import urlparse
import ipaddress

ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.hostname not in ALLOWED_HOSTS:
        return False
    try:
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback:
            return False
    except ValueError:
        pass  # hostname, not IP — already checked against allowlist
    return True
```

---

## Quick Reference Table

| ID  | Name                          | Key Control                    |
|-----|-------------------------------|--------------------------------|
| A01 | Broken Access Control         | Deny by default, enforce ownership |
| A02 | Cryptographic Failures        | Encrypt in transit + at rest   |
| A03 | Injection                     | Parameterized queries          |
| A04 | Insecure Design               | Threat modeling, abuse cases   |
| A05 | Security Misconfiguration     | Hardened defaults, minimal surface |
| A06 | Vulnerable Components         | Audit deps, pin versions       |
| A07 | Auth Failures                 | MFA, session security          |
| A08 | Integrity Failures            | Verify signatures, lock files  |
| A09 | Logging Failures              | Log security events, alert     |
| A10 | SSRF                          | Allowlist URLs, block private IPs |

*Source: [OWASP Top 10 (2021)](https://owasp.org/Top10/)*
