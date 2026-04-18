---
name: owasp
description: >
  Use when reviewing code for security vulnerabilities, implementing authentication or authorization flows, handling user input validation, or building web endpoints exposed to untrusted data. Trigger on keywords like XSS, SQL injection, CSRF, input sanitization, password hashing, and security headers. Also apply when auditing existing code for OWASP Top 10 compliance or conducting security-focused code reviews.
---

# OWASP Security Patterns

## When to Use

- Reviewing code for OWASP Top 10 vulnerabilities
- Implementing input validation on user-facing endpoints
- Adding security headers (CSP, HSTS, X-Frame-Options)
- Preventing XSS, SQL injection, CSRF, or SSRF
- Auditing authentication or authorization flows
- Building endpoints that handle untrusted data

## When NOT to Use

- Infrastructure security (network, firewall, cloud IAM) — use platform-specific tools
- Cryptographic algorithm selection — consult cryptography experts
- Compliance frameworks (SOC 2, HIPAA) — security patterns help but don't cover audit requirements

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| All security patterns | `references/patterns.md` | Input validation, SQL injection, XSS, CSRF, auth, headers |
| OWASP Top 10 cheatsheet | `references/owasp-top10-cheatsheet.md` | Quick reference for each vulnerability category |
| Security headers | `references/security-headers.md` | CSP, HSTS, X-Frame-Options, Referrer-Policy |
| Security checklist | `references/security-checklist.md` | Pre-deploy security review checklist |
| Security audit script | `references/security-audit.py` | Automated security scanning utility |

---

## Best Practices

1. **Validate all input at the boundary.** Use Pydantic (Python) or Zod (TypeScript) for schema validation. Never trust client-side validation alone.
2. **Use parameterized queries exclusively.** Never concatenate user input into SQL strings. Use ORM query builders or prepared statements.
3. **Encode output based on context.** HTML-encode for HTML, URL-encode for URLs, JSON-encode for JSON. No single encoding fits all contexts.
4. **Set security headers on every response.** CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy.
5. **Use CSRF tokens for state-changing requests.** Every POST/PUT/DELETE from a browser form needs a CSRF token.
6. **Apply rate limiting to all public endpoints.** Especially authentication, registration, and password reset.
7. **Never expose stack traces or internal errors to clients.** Return generic error messages; log details server-side.
8. **Audit dependencies regularly.** Run `npm audit` / `pip-audit` / `safety check` in CI.

## Common Pitfalls

1. **Relying on client-side validation only** — easily bypassed with curl or browser devtools.
2. **Using `dangerouslySetInnerHTML` or `| safe` without sanitization** — XSS vector.
3. **SQL string concatenation** — even "just for this one query" is a SQL injection risk.
4. **Missing CSRF protection on API routes** — if cookies are used for auth, CSRF applies.
5. **Overly permissive CORS** — `Access-Control-Allow-Origin: *` with credentials is a security hole.
6. **Logging sensitive data** — passwords, tokens, and PII in logs persist in storage and backups.

---

## Related Skills

- `authentication` — Secure auth implementation patterns
- `error-handling` — Preventing information leakage through errors
- `backend-frameworks` — Framework-specific security middleware
