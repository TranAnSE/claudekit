---
name: openapi
description: >
  Use this skill when designing, documenting, or generating REST API specifications using OpenAPI/Swagger. Trigger on keywords like OpenAPI, Swagger, API spec, REST documentation, API schema, request body, response schema, and API client generation. Also apply when adopting design-first API development, validating API contracts, or setting up auto-generated API documentation for FastAPI, Express, or NestJS endpoints.
---

# OpenAPI & REST API Design

## When to Use

- Documenting REST APIs
- Generating API clients
- API design-first development
- Defining webhook contracts
- Establishing pagination, versioning, or auth patterns for a new service

## When NOT to Use

- Internal-only scripts or automation that do not expose HTTP endpoints
- CLI tools and command-line utilities without a REST interface
- GraphQL APIs where a different specification format applies

---

## Core Patterns

### 1. OpenAPI 3.1 Specification Structure

A complete spec skeleton showing every top-level section. Use `$ref` to split
large specs into per-resource files.

```yaml
openapi: 3.1.0
info:
  title: Acme API
  version: 2.0.0
  description: Public API for the Acme platform.
  contact:
    name: API Support
    email: api@acme.dev
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.acme.dev/v2
    description: Production
  - url: https://staging-api.acme.dev/v2
    description: Staging

tags:
  - name: Users
    description: User management operations
  - name: Orders
    description: Order lifecycle operations

paths:
  /users:
    $ref: './paths/users.yaml'
  /users/{userId}:
    $ref: './paths/users-by-id.yaml'
  /orders:
    $ref: './paths/orders.yaml'

components:
  schemas:
    $ref: './components/schemas/_index.yaml'
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key

security:
  - BearerAuth: []

webhooks:
  orderCompleted:
    $ref: './webhooks/order-completed.yaml'
```

**Organizing with `$ref`** -- keep one file per resource under `paths/` and
shared schemas under `components/schemas/`. A bundler such as
`@redocly/cli bundle` resolves references into a single file for tooling.

```
spec/
├── openapi.yaml            # Root document
├── paths/
│   ├── users.yaml
│   ├── users-by-id.yaml
│   └── orders.yaml
├── components/
│   └── schemas/
│       ├── _index.yaml
│       ├── User.yaml
│       ├── Order.yaml
│       └── ProblemDetail.yaml
└── webhooks/
    └── order-completed.yaml
```

---

### 2. Path & Operation Patterns

#### RESTful URL Naming Conventions

- Use **plural nouns** for collections: `/users`, `/orders`.
- Use **path parameters** for single-resource access: `/users/{userId}`.
- Nest only one level deep: `/users/{userId}/orders` (not deeper).
- Use **query parameters** for filtering, sorting, and pagination.
- Avoid verbs in paths -- let HTTP methods convey the action.

#### CRUD Operations

```yaml
paths:
  /users:
    get:
      operationId: listUsers
      tags: [Users]
      summary: List users
      parameters:
        - $ref: '#/components/parameters/PageCursor'
        - $ref: '#/components/parameters/PageSize'
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive]
      responses:
        '200':
          description: Paginated list of users
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'

    post:
      operationId: createUser
      tags: [Users]
      summary: Create a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          headers:
            Location:
              schema:
                type: string
              description: URL of the new resource
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '409':
          $ref: '#/components/responses/Conflict'
        '422':
          $ref: '#/components/responses/ValidationError'

  /users/{userId}:
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: string
          format: uuid

    get:
      operationId: getUser
      tags: [Users]
      summary: Get a single user
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'

    patch:
      operationId: updateUser
      tags: [Users]
      summary: Partially update a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUserRequest'
      responses:
        '200':
          description: User updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'
        '422':
          $ref: '#/components/responses/ValidationError'

    delete:
      operationId: deleteUser
      tags: [Users]
      summary: Delete a user
      responses:
        '204':
          description: User deleted
        '404':
          $ref: '#/components/responses/NotFound'
```

#### Path Parameters vs Query Parameters

| Use case | Mechanism | Example |
|----------|-----------|---------|
| Identify a specific resource | Path parameter | `/orders/{orderId}` |
| Filter a collection | Query parameter | `/orders?status=shipped` |
| Sort a collection | Query parameter | `/orders?sort=-createdAt` |
| Paginate | Query parameter | `/orders?cursor=abc&limit=20` |
| Expand nested data | Query parameter | `/orders?expand=items,customer` |

---

### 3. Request Body Patterns

#### JSON Request Body with Validation

```yaml
components:
  schemas:
    CreateUserRequest:
      type: object
      required:
        - email
        - name
      properties:
        email:
          type: string
          format: email
          maxLength: 254
        name:
          type: string
          minLength: 1
          maxLength: 100
        role:
          type: string
          enum: [admin, member, viewer]
          default: member
      additionalProperties: false
```

Implementation in **FastAPI** (Python):

```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")

    model_config = {"extra": "forbid"}
```

Implementation in **Express** (TypeScript with Zod):

```typescript
import { z } from "zod";

const CreateUserRequest = z.object({
  email: z.string().email().max(254),
  name: z.string().min(1).max(100),
  role: z.enum(["admin", "member", "viewer"]).default("member"),
}).strict();

type CreateUserRequest = z.infer<typeof CreateUserRequest>;
```

#### Multipart Form Data (File Uploads)

```yaml
/users/{userId}/avatar:
  put:
    operationId: uploadAvatar
    tags: [Users]
    summary: Upload user avatar
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: string
          format: uuid
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - file
            properties:
              file:
                type: string
                format: binary
                description: Image file (JPEG or PNG, max 5 MB)
              caption:
                type: string
                maxLength: 200
          encoding:
            file:
              contentType: image/jpeg, image/png
    responses:
      '200':
        description: Avatar updated
        content:
          application/json:
            schema:
              type: object
              properties:
                url:
                  type: string
                  format: uri
      '413':
        $ref: '#/components/responses/PayloadTooLarge'
```

#### Content Negotiation

Support multiple response formats by listing them under `content`:

```yaml
responses:
  '200':
    description: Export data
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ExportData'
      text/csv:
        schema:
          type: string
      application/pdf:
        schema:
          type: string
          format: binary
```

Clients select a format with the `Accept` header. Document which formats your
API actually supports so consumers do not have to guess.

---

### 4. Response Patterns

#### Success Responses

| Code | Meaning | Typical use |
|------|---------|-------------|
| `200` | OK | GET, PATCH, general success |
| `201` | Created | POST that creates a resource |
| `202` | Accepted | Async operation started |
| `204` | No Content | DELETE, or PUT with no body returned |

Always return a `Location` header with `201` pointing to the new resource.

#### Error Responses -- RFC 7807 Problem Details

Define a single reusable error schema based on RFC 7807:

```yaml
components:
  schemas:
    ProblemDetail:
      type: object
      required:
        - type
        - title
        - status
      properties:
        type:
          type: string
          format: uri
          description: URI reference identifying the problem type.
          example: https://api.acme.dev/problems/validation-error
        title:
          type: string
          description: Short human-readable summary.
          example: Validation Error
        status:
          type: integer
          description: HTTP status code.
          example: 422
        detail:
          type: string
          description: Human-readable explanation specific to this occurrence.
          example: "Field 'email' must be a valid email address."
        instance:
          type: string
          format: uri
          description: URI identifying this specific occurrence.
        errors:
          type: array
          description: Field-level validation errors (optional extension).
          items:
            type: object
            properties:
              field:
                type: string
                example: email
              message:
                type: string
                example: Must be a valid email address.
              code:
                type: string
                example: invalid_format

  responses:
    NotFound:
      description: Resource not found
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
          example:
            type: https://api.acme.dev/problems/not-found
            title: Not Found
            status: 404
            detail: User with ID '550e8400' was not found.

    ValidationError:
      description: Request validation failed
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
          example:
            type: https://api.acme.dev/problems/validation-error
            title: Validation Error
            status: 422
            errors:
              - field: email
                message: Must be a valid email address.
                code: invalid_format

    Conflict:
      description: Resource conflict
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'

    PayloadTooLarge:
      description: Request payload exceeds limit
      content:
        application/problem+json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
```

Use the `application/problem+json` media type for all error responses to signal
RFC 7807 compliance.

---

### 5. Authentication Schemes

#### Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []
```

Override per-operation to allow unauthenticated access:

```yaml
paths:
  /health:
    get:
      security: []    # No auth required
      responses:
        '200':
          description: Healthy
```

#### API Key

```yaml
components:
  securitySchemes:
    ApiKeyHeader:
      type: apiKey
      in: header
      name: X-API-Key
    ApiKeyQuery:
      type: apiKey
      in: query
      name: api_key
```

#### OAuth2 Flows

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.acme.dev/authorize
          tokenUrl: https://auth.acme.dev/token
          refreshUrl: https://auth.acme.dev/token
          scopes:
            users:read: Read user profiles
            users:write: Create and update users
            orders:read: Read orders

paths:
  /users:
    get:
      security:
        - OAuth2: [users:read]
```

---

### 6. Pagination Patterns

#### Cursor-Based Pagination (Recommended)

Best for large, real-time datasets where rows may be inserted or deleted
between pages.

```yaml
components:
  parameters:
    PageCursor:
      name: cursor
      in: query
      description: Opaque cursor returned by a previous response.
      schema:
        type: string
    PageSize:
      name: limit
      in: query
      description: Maximum items per page.
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

  schemas:
    UserListResponse:
      type: object
      required:
        - data
        - pagination
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        pagination:
          type: object
          required:
            - hasMore
          properties:
            nextCursor:
              type: string
              nullable: true
            hasMore:
              type: boolean
```

#### Offset-Based Pagination

Simpler but less efficient for large tables and susceptible to drift when data
changes between requests.

```yaml
components:
  parameters:
    PageOffset:
      name: offset
      in: query
      schema:
        type: integer
        minimum: 0
        default: 0
    PageLimit:
      name: limit
      in: query
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

  schemas:
    PaginatedResponse:
      type: object
      required:
        - data
        - total
        - offset
        - limit
      properties:
        data:
          type: array
          items: {}
        total:
          type: integer
          description: Total number of matching records.
        offset:
          type: integer
        limit:
          type: integer
```

#### Response Envelope Pattern

Wrap every collection in a consistent envelope so clients always know where to
find the data and metadata:

```json
{
  "data": [ ... ],
  "pagination": { "nextCursor": "abc123", "hasMore": true },
  "meta": { "requestId": "req_xyz", "timestamp": "2026-03-29T12:00:00Z" }
}
```

---

### 7. API Versioning

#### URL Versioning

```yaml
servers:
  - url: https://api.acme.dev/v1
    description: Version 1 (deprecated)
  - url: https://api.acme.dev/v2
    description: Version 2 (current)
```

Pros: explicit, easy to route, cache-friendly.
Cons: duplicates paths across versions, harder to share schemas.

#### Header Versioning

```yaml
parameters:
  - name: X-API-Version
    in: header
    required: false
    schema:
      type: string
      enum: ['2024-01-15', '2025-06-01']
      default: '2025-06-01'
    description: Date-based API version. Defaults to latest stable.
```

Pros: clean URLs, fine-grained control.
Cons: less discoverable, harder to test in a browser.

#### Trade-offs Summary

| Approach | Discoverability | URL cleanliness | Caching | Migration effort |
|----------|----------------|-----------------|---------|-----------------|
| URL path | High | Lower | Easy | Higher (path changes) |
| Header | Lower | High | Needs Vary header | Lower |
| Query param | Medium | Medium | Easy | Lower |

Pick one approach and use it consistently. URL versioning is the most common
choice for public APIs; header versioning suits internal services.

---

### 8. Webhook Specifications

OpenAPI 3.1 supports a top-level `webhooks` key for documenting outbound
event payloads your API will send to consumer-registered URLs.

```yaml
webhooks:
  orderCompleted:
    post:
      operationId: onOrderCompleted
      summary: Fired when an order reaches "completed" status.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/OrderCompletedEvent'
      responses:
        '200':
          description: Webhook received successfully.

components:
  schemas:
    WebhookEventBase:
      type: object
      required:
        - id
        - type
        - createdAt
      properties:
        id:
          type: string
          format: uuid
        type:
          type: string
        createdAt:
          type: string
          format: date-time

    OrderCompletedEvent:
      allOf:
        - $ref: '#/components/schemas/WebhookEventBase'
        - type: object
          required:
            - data
          properties:
            type:
              type: string
              const: order.completed
            data:
              type: object
              properties:
                orderId:
                  type: string
                  format: uuid
                total:
                  type: number
                  format: double
                currency:
                  type: string
                  example: USD
```

Document a shared `WebhookEventBase` so all event payloads have a consistent
envelope with `id`, `type`, and `createdAt`.

---

## Best Practices

1. **Use consistent, plural resource names.** `/users`, `/orders`, `/invoices`
   -- never mix singular and plural within the same API.

2. **Make mutating operations idempotent.** Accept an `Idempotency-Key` header
   on POST endpoints so clients can safely retry without creating duplicates.

3. **Return rate-limit headers on every response.** Include `X-RateLimit-Limit`,
   `X-RateLimit-Remaining`, and `X-RateLimit-Reset` so clients can self-throttle.

4. **Provide `operationId` for every operation.** Code generators use this as
   the method name; without it, generated clients have meaningless names.

5. **Include realistic examples in the spec.** Examples power documentation UIs,
   mock servers, and contract tests. Add them at both the schema and operation
   level.

6. **Use `additionalProperties: false` on request schemas.** This catches typos
   in client payloads early and prevents silently ignored fields.

7. **Document hypermedia links (HATEOAS basics).** Even a minimal `_links`
   object with `self` and `next` URIs helps clients navigate without hardcoding
   paths.

8. **Version your spec file alongside code.** Store the OpenAPI document in the
   same repository as the implementation. Run a CI check (e.g., `redocly lint`)
   to validate the spec on every pull request.

---

## Common Pitfalls

1. **Missing error documentation.** Every operation should list its possible
   `4xx` and `5xx` responses. Consumers cannot handle errors they do not know
   about. At minimum document `400`, `401`, `403`, `404`, and `500`.

2. **Overusing `200 OK` for everything.** Return `201` for resource creation,
   `204` for deletion, and `202` for asynchronous actions. Correct status codes
   let generic HTTP clients behave properly (e.g., following `Location` headers).

3. **Deeply nested resource URLs.** `/users/{uid}/orders/{oid}/items/{iid}/notes`
   is fragile and hard to cache. Flatten to `/order-items/{iid}/notes` once the
   relationship is established.

4. **Inconsistent naming conventions.** Mixing `camelCase` and `snake_case`
   within the same API confuses consumers. Pick one JSON field casing and enforce
   it with a linter rule.

5. **Ignoring `nullable` vs optional.** In OpenAPI 3.1, `nullable` is gone;
   use `type: ["string", "null"]` instead. A field that is not in `required`
   may be absent, but that is different from being explicitly `null`. Be precise
   about which you intend.

6. **No pagination on list endpoints.** Returning unbounded arrays will
   eventually cause timeouts or OOM errors. Every collection endpoint should
   accept `limit` and either `cursor` or `offset` from day one, even if the
   dataset is currently small.

---

## Related Skills

- `patterns/api-client` - Patterns for consuming and generating API clients from specs
- `patterns/error-handling` - Consistent error response structures and handling
- `frameworks/fastapi` - FastAPI framework with built-in OpenAPI generation
