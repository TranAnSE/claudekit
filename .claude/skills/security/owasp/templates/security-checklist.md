# Security Code Review Checklist

**Project**: _______________
**Reviewer**: _______________
**Date**: _______________
**Scope**: _______________

---

## Authentication and Session Management

- [ ] Passwords hashed with bcrypt/argon2 (not MD5/SHA1)
- [ ] Session tokens are cryptographically random
- [ ] Session cookies use `Secure`, `HttpOnly`, `SameSite` flags
- [ ] Session timeout is enforced (idle and absolute)
- [ ] Failed login attempts are rate-limited
- [ ] MFA is available for sensitive accounts
- [ ] Password reset tokens expire and are single-use

## Authorization and Access Control

- [ ] Access denied by default (allowlist approach)
- [ ] Server-side authorization on every request
- [ ] Resource ownership verified before access
- [ ] Role/permission checks cannot be bypassed via direct URL
- [ ] Admin endpoints have separate authentication
- [ ] CORS policy restricts allowed origins

## Input Validation

- [ ] All user input validated server-side
- [ ] Parameterized queries used for all database access
- [ ] No string concatenation in SQL/commands
- [ ] File uploads validated (type, size, content)
- [ ] Path traversal prevented on file operations
- [ ] JSON/XML parsers configured against XXE

## Output Encoding

- [ ] HTML output properly escaped (XSS prevention)
- [ ] Content-Type headers set correctly on all responses
- [ ] API responses do not leak stack traces in production
- [ ] Error messages do not reveal system internals
- [ ] Sensitive data excluded from logs

## Cryptography

- [ ] TLS 1.2+ enforced for all connections
- [ ] Sensitive data encrypted at rest
- [ ] No hardcoded secrets, keys, or passwords in source
- [ ] Secrets loaded from environment variables or vault
- [ ] Strong algorithms used (AES-256, RSA-2048+, SHA-256+)
- [ ] No custom cryptographic implementations

## Security Headers

- [ ] Content-Security-Policy configured
- [ ] Strict-Transport-Security enabled
- [ ] X-Frame-Options set to DENY
- [ ] X-Content-Type-Options set to nosniff
- [ ] Referrer-Policy configured
- [ ] Permissions-Policy restricts unused features

## Dependencies

- [ ] No known vulnerabilities (`npm audit` / `pip audit` clean)
- [ ] Unused dependencies removed
- [ ] Dependencies pinned to specific versions
- [ ] Lock file committed and up to date

## Logging and Monitoring

- [ ] Authentication events logged (success and failure)
- [ ] Authorization failures logged
- [ ] Sensitive data not written to logs
- [ ] Log injection prevented (user input sanitized in logs)
- [ ] Alerts configured for suspicious patterns

## API Security

- [ ] Rate limiting on all public endpoints
- [ ] Request size limits configured
- [ ] API keys/tokens not exposed in URLs
- [ ] Pagination enforced on list endpoints
- [ ] HTTPS required (HTTP redirects or blocks)

## Infrastructure

- [ ] Debug mode disabled in production
- [ ] Default credentials changed
- [ ] Unnecessary ports/services disabled
- [ ] Container runs as non-root user
- [ ] Environment variables not logged at startup

---

## Summary

| Category | Pass | Fail | N/A |
|----------|------|------|-----|
| Authentication | | | |
| Authorization | | | |
| Input Validation | | | |
| Output Encoding | | | |
| Cryptography | | | |
| Security Headers | | | |
| Dependencies | | | |
| Logging | | | |
| API Security | | | |
| Infrastructure | | | |

**Overall Assessment**: [ ] Pass / [ ] Conditional Pass / [ ] Fail

**Notes**:



**Follow-up Actions**:


