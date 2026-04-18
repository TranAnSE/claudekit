---
name: openapi
description: Use when designing, documenting, or generating REST APIs with OpenAPI 3.1 — including error contracts, pagination, versioning, auth schemes, request/response schemas, webhooks, or code-gen pipelines for FastAPI, Express, or NestJS. Also use when migrating a spec from OpenAPI 3.0 to 3.1.
---

# OpenAPI 3.1 & REST API Design

## Overview

A design-first reference for REST APIs developers want to use. Standardizes on **RFC 9457 Problem Details**, **camelCase JSON**, **cursor pagination**, and **URL-path versioning** — the 2026 consensus across Google, Microsoft, and the OpenAPI 3.1 ecosystem.

## When to Use
- Designing or documenting a new REST API
- Generating clients/servers from a spec (FastAPI, Express, NestJS, etc.)
- Establishing error, pagination, versioning, or auth conventions for a service
- Migrating a spec from OpenAPI 3.0 → 3.1
- Setting up lint/governance in CI

## When NOT to Use
- GraphQL APIs (different spec format)
- Internal scripts or CLI tools with no HTTP surface
- RPC-style services (gRPC, tRPC)

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| Starter spec to copy and adapt | [templates/openapi-3.1-starter.yaml](templates/openapi-3.1-starter.yaml) |
| Which HTTP status code? | [references/http-status-codes.md](references/http-status-codes.md) |
| URL naming & CRUD mapping | [references/rest-naming.md](references/rest-naming.md) |
| Linting, CI, docs, client gen, mock servers | [references/api-governance.md](references/api-governance.md) |
| Idempotency, rate limiting, ETag, webhook signing, async jobs | [references/production-patterns.md](references/production-patterns.md) |
| Error contract (Problem Details) | § Errors below |
| Pagination pattern | § Pagination below |
| Auth scheme | § Authentication below |
| OpenAPI 3.0 → 3.1 gotchas | § Migration Flags below |

---

## Conventions — the defaults this skill teaches

Pick different conventions only with explicit reason, and apply them **consistently across the whole API**. Mixed conventions within one API are the #1 integration pain point.

| Decision | Default | Why |
|----------|---------|-----|
| Error format | `application/problem+json` (**RFC 9457**) | 2023 successor to RFC 7807. Standard fields, machine-readable `type` URI, native support in Spring / .NET / FastAPI. |
| JSON field casing | **camelCase** | Matches the JS/TS ecosystem (the largest API-consumer population) and Google / Microsoft guidelines. |
| URL segment casing | lowercase plural **kebab-case** (`/user-profiles`) | RFC 3986 friendly, cache-friendly, unambiguous. |
| Query parameter casing | **camelCase** (`pageSize`, `createdAfter`) | Mirrors the JSON body — consumers reason about one casing, not two. |
| HTTP header casing | `Kebab-Case` (`X-Request-Id`, `Idempotency-Key`) | HTTP convention. |
| Pagination | **Cursor** for growable lists; offset only for small bounded sets | Cursor is stable under concurrent inserts/deletes and O(1) per page. |
| Versioning (public) | URL path (`/v1`, `/v2`) | Explicit, routable, CDN/cache-friendly. |
| Versioning (internal) | Date header (`X-Api-Version: 2026-06-01`) | Fine-grained evolution without URL churn. |
| ID format in JSON | `string` — UUID or prefixed slug (`usr_abc123`) | Avoids JS number precision loss; prefixed IDs aid debugging. |
| Timestamps | ISO 8601 / RFC 3339 string | Universal, sortable, timezone-aware. |

---

## Spec Structure

Skeleton of a well-organized OpenAPI 3.1 document. Split large specs with `$ref` and bundle with `redocly cli bundle` for tooling.

```yaml
openapi: 3.1.0
info:
  title: Acme API
  version: 2.0.0
  contact: { name: API Support, email: api@acme.dev }
  license: { name: MIT, identifier: MIT }   # 3.1 SPDX identifier
servers:
  - url: https://api.acme.dev/v2
  - url: https://staging-api.acme.dev/v2
tags:
  - { name: Users,  description: User management }
  - { name: Orders, description: Order lifecycle }
paths:
  /users:            { $ref: './paths/users.yaml' }
  /users/{userId}:   { $ref: './paths/users-by-id.yaml' }
components:
  schemas:         { $ref: './components/schemas/_index.yaml' }
  securitySchemes:
    BearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
security:
  - BearerAuth: []
webhooks:
  orderCompleted: { $ref: './webhooks/order-completed.yaml' }
```

Recommended file layout:

```
spec/
├── openapi.yaml
├── paths/            # One file per resource
├── components/
│   └── schemas/      # Shared schemas
└── webhooks/         # Event payloads
```

For a complete runnable starter — CRUD, auth, cursor pagination, Problem Details, idempotency, rate-limit headers, and ETag concurrency — see [templates/openapi-3.1-starter.yaml](templates/openapi-3.1-starter.yaml).

---

## Path & Operation Patterns

- **Plural collections:** `/users`, `/orders`
- **Path params for identity:** `/users/{userId}`
- **Query params for filter / sort / paginate / expand**
- **Max 2 levels of nesting** — deeper is a smell, flatten it
- **Always set `operationId`** — code generators use it as the method name
- **Always set `tags` and `summary`** — docs UIs and linters require them

Full CRUD mapping table and URL rules: [references/rest-naming.md](references/rest-naming.md).

---

## Request Bodies

Use `additionalProperties: false` on request schemas so typos in payloads fail validation early instead of being silently dropped.

```yaml
CreateUserRequest:
  type: object
  required: [email, name]
  additionalProperties: false
  properties:
    email: { type: string, format: email, maxLength: 254 }
    name:  { type: string, minLength: 1, maxLength: 100 }
    role:  { type: string, enum: [admin, member, viewer], default: member }
```

Framework mirrors:
- **FastAPI:** `pydantic.BaseModel` with `model_config = {"extra": "forbid"}`
- **Express + Zod:** `z.object({...}).strict()`
- **NestJS:** `class-validator` + `ValidationPipe({ whitelist: true, forbidNonWhitelisted: true })`

For uploads, use `multipart/form-data` with `type: string, format: binary` and document the accepted MIME types via `encoding.<field>.contentType`.

---

## Errors (Problem Details)

Return `application/problem+json` per **RFC 9457** for every 4xx / 5xx response. Define one shared `ProblemDetails` schema and reuse it across the spec via `$ref`.

```yaml
components:
  schemas:
    ProblemDetails:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          format: uri
          description: URI reference identifying the problem type.
          example: https://api.acme.dev/problems/validation-error
        title:    { type: string, example: "Validation failed" }
        status:   { type: integer, example: 422 }
        detail:   { type: string, example: "Field 'email' must be a valid email address." }
        instance: { type: string, format: uri }
        errors:
          type: array
          description: Field-level validation errors (extension member).
          items:
            type: object
            required: [field, message]
            properties:
              field:   { type: string, example: email }
              message: { type: string }
              code:    { type: string, example: invalidFormat }

  responses:
    ValidationError:
      description: Request validation failed
      content:
        application/problem+json:
          schema: { $ref: '#/components/schemas/ProblemDetails' }
```

**Make `type` a real documentation URL.** The whole point of RFC 9457 is that `type` uniquely identifies the problem class and links to a human explanation. Using `about:blank` (the spec default) throws away 90% of the value.

**400 vs 422 — the line that matters:**
- `400` → malformed syntax. The request body is not valid JSON, a required field is missing, or a field has the wrong type. Detected by the parser/validator.
- `422` → semantically valid but violates business rules. Email already exists, state transition illegal, quota exceeded. Detected by application logic.

Full status-code catalog and decision flow: [references/http-status-codes.md](references/http-status-codes.md).

---

## Authentication

Pick one scheme, apply globally via top-level `security`, override per operation as needed.

```yaml
components:
  securitySchemes:
    BearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
    ApiKeyAuth: { type: apiKey, in: header, name: X-Api-Key }
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.acme.dev/authorize
          tokenUrl: https://auth.acme.dev/token
          scopes:
            "users:read":  Read user profiles
            "users:write": Create and update users

security:
  - BearerAuth: []

paths:
  /health:
    get:
      security: []          # Public endpoint — override global
      responses: { '200': { description: Healthy } }
  /users:
    get:
      security:
        - OAuth2: ["users:read"]
```

---

## Pagination

**Default to cursor pagination** for any list that can grow. It is stable under concurrent inserts/deletes and O(1) per page regardless of depth.

```yaml
components:
  parameters:
    Cursor:
      name: cursor
      in: query
      description: Opaque cursor from a previous response.
      schema: { type: string }
    Limit:
      name: limit
      in: query
      schema: { type: integer, minimum: 1, maximum: 100, default: 20 }

  schemas:
    UserListResponse:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items: { $ref: '#/components/schemas/User' }
        pagination:
          type: object
          required: [hasMore]
          properties:
            nextCursor: { type: [string, "null"] }   # JSON Schema 2020-12 null union
            hasMore:    { type: boolean }
```

**Use offset pagination only** for small, bounded collections (< ~10k rows) where users need to jump to specific page numbers. Offset drifts when rows are inserted/deleted between requests and scales O(n) in the skipped-row count.

**Always enforce a max `limit`.** "We'll bound it later" never happens before the incident.

---

## Versioning

**Public APIs → URL path** (`/v1`, `/v2`). Simple, explicit, routable by CDN/gateway. This is the current mainstream choice (Google, Stripe, GitHub).

**Internal APIs → Date header** (`X-Api-Version: 2026-06-01`). Fine-grained, no URL churn, easier to deprecate individual fields.

Bump the major version when you break backward compatibility: remove a field, change a type, change an error shape. Everything additive (new fields, new endpoints) stays on the same version.

**Never ship without a version.** Adding one later is painful.

---

## Webhooks

OpenAPI 3.1 introduces top-level `webhooks` for outbound events — a first-class replacement for the old `callbacks` workaround.

```yaml
webhooks:
  orderCompleted:
    post:
      operationId: onOrderCompleted
      summary: Fired when an order reaches "completed" state.
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/OrderCompletedEvent' }
      responses:
        '2XX': { description: Webhook received successfully. }

components:
  schemas:
    WebhookEventBase:
      type: object
      required: [id, type, createdAt]
      properties:
        id:        { type: string, format: uuid }
        type:      { type: string }
        createdAt: { type: string, format: date-time }
    OrderCompletedEvent:
      allOf:
        - $ref: '#/components/schemas/WebhookEventBase'
        - type: object
          properties:
            type: { const: order.completed }
            data:
              type: object
              properties:
                orderId: { type: string, format: uuid }
                total:   { type: number, format: double }
```

Consumers should respond with any 2xx within a few seconds; you retry non-2xx with exponential backoff. **Sign payloads** (HMAC over timestamp + body) so consumers can verify authenticity and reject replays — full pattern with working signing/verification code in [references/production-patterns.md](references/production-patterns.md).

---

## OpenAPI 3.0 → 3.1 Migration Flags

The most common mistakes when moving a spec from 3.0 to 3.1:

| 3.0 (wrong in 3.1) | 3.1 (correct) |
|--------------------|---------------|
| `nullable: true` | `type: [string, "null"]` — `nullable` is **silently ignored** in 3.1 |
| `example: ...` on schema | `examples: [...]` — now an array |
| `exclusiveMinimum: true` + `minimum: 0` | `exclusiveMinimum: 0` — now a numeric value |
| `$ref` cannot have sibling keywords | `$ref` can sit next to `description`, `summary`, etc. |
| `type: integer, format: int64` for long IDs | `type: string` — JS `Number` loses precision above 2^53 |

3.1 is full **JSON Schema 2020-12**: use `oneOf` + `discriminator` for polymorphism, and `if` / `then` / `else` for conditional validation.

---

## Common Pitfalls

1. **Undocumented error responses.** Every operation should list its possible 4xx/5xx codes. At minimum: `400`, `401`, `403`, `404`, `422`, `500`. Consumers cannot handle errors they don't know about.
2. **Inline schemas instead of `$ref`.** Kills SDK quality — generators produce names like `UsersPost200Response`. Put shared shapes under `components/schemas`.
3. **Missing `operationId`.** Generators fall back to `userGet1`, `userGet2`. Every operation needs an `operationId`.
4. **Unbounded list endpoints.** No `limit` cap = OOM or timeout the day traffic doubles.
5. **Mixed casing.** camelCase and snake_case inside the same API confuses every consumer. Enforce with `spectral` or `vacuum`.
6. **`nullable: true` in a 3.1 document.** Silently ignored. Use the JSON Schema null union (`type: [T, "null"]`).
7. **Ambiguous `oneOf` without `discriminator`.** Clients cannot reliably deserialize polymorphic payloads.
8. **Deeply nested URLs.** `/users/{uid}/orders/{oid}/items/{iid}/notes` is fragile and uncacheable. Flatten once the parent relationship is established.
9. **Using `about:blank` for Problem Details `type`.** Wastes the main benefit of RFC 9457 — link to your real docs.
10. **No linter in CI.** Specs drift. Run `redocly lint`, `spectral lint`, or `vacuum` on every PR from day one. For a ready-to-copy Spectral ruleset, GitHub Actions workflow, and a breaking-change diff step, see [references/api-governance.md](references/api-governance.md).
11. **No idempotency on side-effecting POSTs.** A lost response = duplicate charge / duplicate email. Accept an `Idempotency-Key` header and store the *response* keyed by it. Full pattern: [references/production-patterns.md](references/production-patterns.md).

---

## Related Skills

- `api-client` — consuming and generating API clients from specs
- `error-handling` — consistent error handling in consumer code
- `fastapi` — FastAPI's built-in OpenAPI generation
