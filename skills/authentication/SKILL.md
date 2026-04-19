---
name: authentication
description: >
  Use when implementing JWT tokens, OAuth2 flows, session management, role-based access control (RBAC), password hashing, or multi-factor authentication. Also activate whenever code handles login, signup, token refresh, protected routes, permission checks, or user identity verification. Applies to middleware auth guards and API key authentication.
---

# Authentication & Authorization

## When to Use

- Implementing JWT creation, verification, and refresh token flows
- Building OAuth2 authorization code or PKCE flows
- Password hashing with argon2 or bcrypt
- Role-based access control (RBAC) or permission checks
- Session management with Redis or database-backed sessions
- API key authentication for service-to-service communication
- Multi-factor authentication (TOTP, SMS, email)

## When NOT to Use

- Token-free static sites or public APIs with no auth requirements
- Third-party auth services where implementation is fully managed (Auth0, Clerk) — unless customizing
- Simple scripts or CLI tools that do not need user identity

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| All auth patterns | `references/patterns.md` | JWT, OAuth2, password hashing, RBAC, sessions, API keys |
| Auth flow diagrams | `references/auth-flows.md` | Visual flow diagrams for OAuth2, JWT refresh, session lifecycle |

---

## Best Practices

1. **Never store passwords in plain text.** Use argon2id (preferred) or bcrypt with a work factor of 12+.
2. **Keep JWT tokens short-lived.** Access tokens should expire in 15-30 minutes. Use refresh tokens for longer sessions.
3. **Validate tokens on every request.** Never trust a token without verifying signature, expiration, and issuer.
4. **Use HttpOnly, Secure, SameSite cookies** for web session tokens. Never store tokens in localStorage.
5. **Implement token refresh rotation.** Invalidate old refresh tokens when a new one is issued to detect token theft.
6. **Separate authentication from authorization.** Auth verifies identity; authz checks permissions. Keep them in separate middleware/guards.
7. **Rate limit auth endpoints.** Login, registration, and password reset endpoints are prime brute-force targets.
8. **Log auth events.** Record login attempts (success and failure), token refreshes, and permission denials for security auditing.

## Common Pitfalls

1. **Storing JWTs in localStorage** — vulnerable to XSS. Use HttpOnly cookies instead.
2. **Not rotating refresh tokens** — a stolen refresh token gives permanent access.
3. **Hardcoding secrets** — JWT signing keys and API keys must come from environment variables.
4. **Missing token expiration checks** — always verify `exp` claim server-side.
5. **Overly broad RBAC roles** — prefer granular permissions over a few broad roles.
6. **Not hashing API keys** — store hashed API keys in the database, not plain text.

---

## Related Skills

- `owasp` — Security vulnerabilities in auth flows
- `backend-frameworks` — Framework-specific auth middleware
- `databases` — Storing user credentials and sessions
