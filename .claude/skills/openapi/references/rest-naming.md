# REST API Naming Conventions

Guidelines for consistent, predictable REST endpoint design.

---

## Core Rules

1. **Use plural nouns** for resource collections
2. **Use kebab-case** for multi-word URL segments (`/user-profiles`)
3. **Use path parameters** for identity, query parameters for filtering
4. **Never use verbs** in URLs — HTTP methods convey the action
5. **Use lowercase** in URL path segments
6. **Use camelCase** in JSON bodies and query parameter names (`pageSize`, `createdAfter`) — matches the JS/TS ecosystem

---

## Resource Naming

| Pattern | Example | Notes |
|---------|---------|-------|
| Collection | `/users` | Plural noun |
| Single resource | `/users/{id}` | Path parameter |
| Multi-word resource | `/order-items` | Kebab-case |
| Nested resource | `/users/{id}/orders` | Parent-child relationship |
| Deep nesting (avoid) | `/users/{id}/orders/{oid}/items` | Max 2 levels deep |
| Singleton sub-resource | `/users/{id}/profile` | One-to-one relationship |

### Good

```
GET    /users
GET    /users/123
POST   /users
PUT    /users/123
DELETE /users/123
GET    /users/123/orders
GET    /order-items
GET    /user-profiles/123
```

### Bad

```
GET    /getUsers            # verb in URL
GET    /user/123            # singular collection
GET    /Users               # uppercase
POST   /users/create        # redundant verb
GET    /user_profiles       # snake_case (use kebab-case in paths)
GET    /userProfiles        # camelCase (use kebab-case in paths)
DELETE /users/123/delete    # verb in URL
```

---

## CRUD Mapping

| Action | Method | Endpoint | Request Body | Response |
|--------|--------|----------|-------------|----------|
| List | `GET` | `/resources` | None | `200` + array |
| Create | `POST` | `/resources` | Resource data | `201` + created |
| Read | `GET` | `/resources/{id}` | None | `200` + object |
| Update (full) | `PUT` | `/resources/{id}` | Full resource | `200` + updated |
| Update (partial) | `PATCH` | `/resources/{id}` | Partial data | `200` + updated |
| Delete | `DELETE` | `/resources/{id}` | None | `204` |

---

## Nested Resources

Use nesting to express clear parent-child relationships.

```
# User's orders (user owns orders)
GET  /users/{userId}/orders
POST /users/{userId}/orders

# Order's line items
GET  /orders/{orderId}/items
```

**When to nest vs. top-level:**

| Scenario | Approach | Example |
|----------|----------|---------|
| Resource only exists under parent | Nest | `/users/{id}/sessions` |
| Resource is independently accessible | Top-level with filter | `/orders?user_id=123` |
| Shallow relationship | Top-level | `/comments?post_id=456` |

**Rule of thumb:** Never nest more than 2 levels. Use query parameters or top-level endpoints instead.

```
# Too deep -- avoid
GET /users/{id}/orders/{oid}/items/{iid}/reviews

# Better alternatives
GET /order-items/{iid}/reviews
GET /reviews?order_item_id={iid}
```

---

## Query Parameters

### Filtering

```
GET /products?category=electronics&brand=acme
GET /users?status=active&role=admin
GET /orders?createdAfter=2026-01-01&createdBefore=2026-02-01
```

| Convention | Example |
|-----------|---------|
| Exact match | `?status=active` |
| Date range | `?createdAfter=2026-01-01` |
| Multiple values | `?status=active,pending` |
| Search | `?q=search+term` |

### Sorting

```
GET /products?sort=price            # ascending (default)
GET /products?sort=-price           # descending (prefix -)
GET /products?sort=-createdAt,name  # multi-field
```

### Pagination

Prefer **cursor-based** for any list that can grow — it is stable under concurrent inserts/deletes and O(1) per page. Use **offset-based** only for small, bounded collections where users need to jump to a specific page number.

```
# Cursor-based (recommended default)
GET /products?cursor=eyJpZCI6MTAwfQ&limit=25

# Offset-based (only for bounded lists)
GET /products?page=2&limit=25
```

**Response envelope — cursor:**

```json
{
  "data": [ /* ... */ ],
  "pagination": {
    "nextCursor": "eyJpZCI6MTI1fQ",
    "hasMore": true
  }
}
```

**Response envelope — offset:**

```json
{
  "data": [ /* ... */ ],
  "pagination": {
    "page": 2,
    "limit": 25,
    "total": 150,
    "totalPages": 6
  }
}
```

### Field Selection

```
GET /users/123?fields=id,name,email
```

---

## Non-CRUD Actions

Some operations do not map cleanly to CRUD. Use sub-resources with a noun or POST with an action resource.

| Action | Approach | Example |
|--------|----------|---------|
| Send an email | POST to action resource | `POST /users/{id}/verification-email` |
| Archive | PATCH with status | `PATCH /orders/{id} { "status": "archived" }` |
| Bulk delete | POST to action | `POST /users/bulk-delete { "ids": [...] }` |
| Export | GET with format | `GET /reports/sales?format=csv` |
| Search (complex) | POST with body | `POST /products/search { "filters": {...} }` |

---

## Versioning

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URL path | `/api/v1/users` | Simple, explicit | URL pollution |
| Header | `Accept: application/vnd.api.v1+json` | Clean URLs | Hidden |
| Query param | `/users?version=1` | Easy to test | Caching issues |

**Recommended:** URL path versioning (`/api/v1/`) for public APIs due to simplicity.

---

## Summary Checklist

- [ ] Resources are plural nouns (`/users` not `/user`)
- [ ] URL path segments are lowercase kebab-case
- [ ] JSON fields and query params are camelCase
- [ ] No verbs in URLs
- [ ] Nesting limited to 2 levels
- [ ] Filtering uses query parameters
- [ ] Sorting supports `-field` for descending
- [ ] Cursor pagination on any list that can grow; offset only for small bounded lists
- [ ] Max `limit` enforced on every list endpoint
- [ ] API version in URL path for public APIs
- [ ] Error responses use `application/problem+json` (RFC 9457)

*Reference: [Google API Design Guide](https://cloud.google.com/apis/design), [Microsoft REST Guidelines](https://github.com/microsoft/api-guidelines)*
