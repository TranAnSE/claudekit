# Authentication Flows Quick Reference

## Decision Tree: Which Auth Method?

```
What are you building?
│
├─ Server-rendered web app (Next.js, Django, Rails)?
│  └─> SESSION-BASED AUTH
│      - HttpOnly cookies, server-side session store
│      - Simple, secure, well-understood
│
├─ SPA + API backend (same domain)?
│  └─> SESSION-BASED AUTH (still preferred)
│      - Cookies sent automatically, no JS token handling
│      - Or: JWT in HttpOnly cookie (not localStorage)
│
├─ SPA + API backend (different domain)?
│  └─> JWT with access + refresh tokens
│      - Access token: short-lived, in memory
│      - Refresh token: HttpOnly cookie
│
├─ Mobile app?
│  └─> JWT with access + refresh tokens
│      - Store refresh token in secure storage (Keychain/Keystore)
│      - Access token in memory
│
├─ Third-party API access?
│  └─> OAuth2 + API keys
│      - OAuth2 for user-delegated access
│      - API keys for server-to-server
│
├─ Machine-to-machine (service-to-service)?
│  └─> API KEYS or OAuth2 Client Credentials
│      - API key: simple, rotate regularly
│      - Client Credentials: when you need scoped access
│
└─ CLI tool?
   └─> OAuth2 Device Code Flow or API key
```

---

## JWT Access + Refresh Token Flow

```
┌──────────┐                  ┌──────────┐                  ┌──────────┐
│  Client   │                  │  Auth    │                  │  API     │
│  (SPA/    │                  │  Server  │                  │  Server  │
│  Mobile)  │                  │          │                  │          │
└────┬──────┘                  └────┬─────┘                  └────┬─────┘
     │                              │                              │
     │  1. POST /auth/login         │                              │
     │  { email, password }         │                              │
     │─────────────────────────────>│                              │
     │                              │                              │
     │  2. 200 OK                   │                              │
     │  { access_token (15min) }    │                              │
     │  Set-Cookie: refresh_token   │                              │
     │  (HttpOnly, Secure, 7d)      │                              │
     │<─────────────────────────────│                              │
     │                              │                              │
     │  3. GET /api/data            │                              │
     │  Authorization: Bearer <access_token>                       │
     │─────────────────────────────────────────────────────────────>│
     │                              │                              │
     │  4. 200 OK { data }          │                              │
     │<─────────────────────────────────────────────────────────────│
     │                              │                              │
     │  ── access_token expires ──  │                              │
     │                              │                              │
     │  5. GET /api/data            │                              │
     │  Authorization: Bearer <expired_token>                      │
     │─────────────────────────────────────────────────────────────>│
     │                              │                              │
     │  6. 401 { code: "token_expired" }                           │
     │<─────────────────────────────────────────────────────────────│
     │                              │                              │
     │  7. POST /auth/refresh       │                              │
     │  Cookie: refresh_token       │                              │
     │─────────────────────────────>│                              │
     │                              │                              │
     │  8. 200 { new access_token } │                              │
     │  Set-Cookie: new refresh     │                              │
     │<─────────────────────────────│                              │
     │                              │                              │
     │  9. Retry original request with new access_token            │
     │─────────────────────────────────────────────────────────────>│
```

### JWT Best Practices

| Concern | Recommendation |
|---------|---------------|
| Access token lifetime | 5-15 minutes |
| Refresh token lifetime | 7-30 days |
| Access token storage | Memory only (JS variable) |
| Refresh token storage | HttpOnly Secure cookie (web) or Keychain (mobile) |
| Token rotation | Issue new refresh token on each refresh |
| Revocation | Maintain server-side deny list for refresh tokens |
| Algorithm | RS256 (asymmetric) for distributed systems, HS256 for single server |
| Claims | Minimal: sub, exp, iat, roles/permissions |

---

## OAuth2 Authorization Code + PKCE Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client   │         │  Auth    │         │  Resource │
│  (Browser)│         │  Provider│         │  Server   │
└────┬──────┘         └────┬─────┘         └────┬──────┘
     │                     │                     │
     │  1. Generate:       │                     │
     │  code_verifier (random 43-128 chars)      │
     │  code_challenge = SHA256(code_verifier)    │
     │                     │                     │
     │  2. Redirect to:    │                     │
     │  /authorize?        │                     │
     │    response_type=code                     │
     │    client_id=xxx    │                     │
     │    redirect_uri=https://app/callback       │
     │    scope=openid profile                   │
     │    state=random_csrf_token                │
     │    code_challenge=xxx                     │
     │    code_challenge_method=S256             │
     │────────────────────>│                     │
     │                     │                     │
     │  3. User logs in    │                     │
     │  and consents       │                     │
     │                     │                     │
     │  4. Redirect to:    │                     │
     │  /callback?code=AUTH_CODE&state=xxx       │
     │<────────────────────│                     │
     │                     │                     │
     │  5. Verify state matches                  │
     │                     │                     │
     │  6. POST /token     │                     │
     │  { grant_type=authorization_code,         │
     │    code=AUTH_CODE,  │                     │
     │    redirect_uri=...,│                     │
     │    code_verifier=ORIGINAL_VERIFIER }      │
     │────────────────────>│                     │
     │                     │                     │
     │  7. { access_token, │                     │
     │       refresh_token,│                     │
     │       id_token }    │                     │
     │<────────────────────│                     │
     │                     │                     │
     │  8. GET /api/resource                     │
     │  Authorization: Bearer <access_token>     │
     │───────────────────────────────────────────>│
```

### PKCE Key Points

| Term | Purpose |
|------|---------|
| `code_verifier` | Random string (43-128 chars), stored client-side |
| `code_challenge` | `BASE64URL(SHA256(code_verifier))` sent in auth request |
| `state` | CSRF protection (random, verify on callback) |
| PKCE purpose | Prevents auth code interception (no client secret needed) |

---

## Session-Based Auth Flow

```
┌──────────┐                  ┌──────────────────┐
│  Browser  │                  │  Server           │
│           │                  │  (session store)  │
└────┬──────┘                  └────┬──────────────┘
     │                              │
     │  1. POST /login              │
     │  { email, password }         │
     │─────────────────────────────>│
     │                              │  2. Verify credentials
     │                              │  3. Create session in store
     │                              │     (Redis/DB/memory)
     │  4. Set-Cookie:              │
     │  session_id=abc123;          │
     │  HttpOnly; Secure;           │
     │  SameSite=Lax; Path=/        │
     │<─────────────────────────────│
     │                              │
     │  5. GET /dashboard           │
     │  Cookie: session_id=abc123   │  (sent automatically)
     │─────────────────────────────>│
     │                              │  6. Lookup session abc123
     │                              │  7. Attach user to request
     │  8. 200 OK                   │
     │<─────────────────────────────│
     │                              │
     │  9. POST /logout             │
     │─────────────────────────────>│
     │                              │  10. Delete session from store
     │  11. Clear cookie            │
     │<─────────────────────────────│
```

### Session Cookie Settings

| Attribute | Value | Purpose |
|-----------|-------|---------|
| `HttpOnly` | Always | Prevent JS access (XSS protection) |
| `Secure` | Always in prod | Only send over HTTPS |
| `SameSite` | `Lax` (default) | CSRF protection (allows top-level navigation) |
| `SameSite` | `Strict` | Stronger CSRF (breaks external link login) |
| `Path` | `/` | Cookie scope |
| `Max-Age` | 86400-2592000 | Session duration (1-30 days) |
| `Domain` | Omit or explicit | Cookie scope to domain |

---

## Comparison: JWT vs Sessions vs API Keys

| Aspect | JWT | Sessions | API Keys |
|--------|-----|----------|----------|
| Stateless | Yes (no server lookup) | No (server-side store) | No (server-side lookup) |
| Revocation | Hard (needs deny list) | Easy (delete session) | Easy (delete key) |
| Scaling | Easy (no shared state) | Needs shared session store | Needs shared key store |
| Security | Token theft = access until expiry | Session theft = access until revoked | Key theft = access until rotated |
| Best for | Distributed APIs, mobile | Web apps, SSR | Service-to-service, CLI |
| CSRF risk | Low (if not in cookie) | Needs CSRF tokens | N/A (header-based) |
| XSS risk | High if in localStorage | Low (HttpOnly cookie) | Low (server-side only) |

### API Key Best Practices

| Practice | Details |
|----------|---------|
| Prefix keys | `sk_live_`, `pk_test_` (identify type/env) |
| Hash before storing | Store `SHA256(key)`, never plaintext |
| Scope keys | Limit permissions per key |
| Set expiry | Auto-expire, require rotation |
| Rate limit per key | Prevent abuse |
| Transmit in header | `Authorization: Bearer <key>` or `X-API-Key: <key>` |
| Never in URL | Query params end up in logs and browser history |
