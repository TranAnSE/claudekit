# Validation Layers Reference

Multi-layer validation strategy ensuring no single point of failure.

## Overview

```
Request -> [Layer 1: Input] -> [Layer 2: Business] -> [Layer 3: Persistence] -> [Layer 4: Output] -> Response
```

Each layer validates independently. A failure at any layer should produce a clear, actionable error. Never rely on a single layer.

## Layer 1: Input Boundary

**Purpose**: Reject malformed, oversized, or obviously invalid data at the edge.

### What to Validate

- Data types and shapes (string, number, object structure)
- Required vs optional fields
- String length, numeric ranges, allowed values
- Format patterns (email, URL, UUID, date)
- Content-Type headers, encoding
- File upload size and MIME type
- Request rate and authentication tokens

### Python (FastAPI + Pydantic)

```python
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI, Query

class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    age: int = Field(ge=0, le=150)
    role: Literal["admin", "user", "viewer"]

@app.post("/users")
async def create_user(req: CreateUserRequest):
    # req is already validated by Pydantic
    ...
```

### TypeScript (Zod + Express)

```typescript
import { z } from "zod";

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(200),
  age: z.number().int().min(0).max(150),
  role: z.enum(["admin", "user", "viewer"]),
});

app.post("/users", (req, res) => {
  const result = CreateUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.issues });
  }
  // result.data is typed and validated
});
```

### Tools

| Language | Library | Purpose |
|---|---|---|
| Python | Pydantic, marshmallow, cerberus | Schema validation |
| TypeScript | Zod, Yup, io-ts, Ajv | Schema validation |
| Any | JSON Schema | Language-agnostic schema |

## Layer 2: Business Logic

**Purpose**: Enforce domain rules, state transitions, and authorization.

### What to Validate

- Business rules (e.g., "cannot cancel a shipped order")
- State machine transitions (e.g., draft -> published, not draft -> archived)
- Cross-field dependencies (e.g., "end_date must be after start_date")
- Authorization (e.g., "only the owner can modify this resource")
- Resource existence (e.g., "referenced entity must exist")
- Idempotency and duplicate detection

### Python

```python
class OrderService:
    def cancel_order(self, order_id: str, user_id: str) -> Order:
        order = self.repo.get(order_id)
        if order is None:
            raise NotFoundError(f"Order {order_id} not found")
        if order.owner_id != user_id:
            raise ForbiddenError("Only the order owner can cancel")
        if order.status not in ("pending", "confirmed"):
            raise BusinessRuleError(
                f"Cannot cancel order in '{order.status}' status"
            )
        order.status = "cancelled"
        return self.repo.save(order)
```

### TypeScript

```typescript
class OrderService {
  cancelOrder(orderId: string, userId: string): Order {
    const order = this.repo.get(orderId);
    if (!order) throw new NotFoundError(`Order ${orderId} not found`);
    if (order.ownerId !== userId) throw new ForbiddenError("Only the order owner can cancel");

    const cancellableStatuses = ["pending", "confirmed"] as const;
    if (!cancellableStatuses.includes(order.status)) {
      throw new BusinessRuleError(`Cannot cancel order in '${order.status}' status`);
    }
    order.status = "cancelled";
    return this.repo.save(order);
  }
}
```

### Guidelines

- Keep validation logic in the service/domain layer, not in controllers
- Use custom exception types that map to HTTP status codes
- Business rules should be testable independently of HTTP/DB

## Layer 3: Data Persistence

**Purpose**: Enforce data integrity at the database level as the last line of defense.

### What to Validate

- NOT NULL constraints
- UNIQUE constraints (email, username)
- FOREIGN KEY constraints (referential integrity)
- CHECK constraints (value ranges, enums)
- Data types and precision
- Default values

### PostgreSQL Examples

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL CHECK (char_length(name) > 0),
    age INTEGER CHECK (age >= 0 AND age <= 150),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'user', 'viewer')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'confirmed', 'shipped', 'cancelled')),
    total_cents INTEGER NOT NULL CHECK (total_cents >= 0)
);
```

### Guidelines

- Mirror constraints in your ORM (SQLAlchemy `CheckConstraint`, Prisma `@unique`, etc.)
- Database constraints are the safety net; they catch bugs in application code
- Always handle constraint violation errors gracefully (unique violation -> 409 Conflict)
- Use migrations to manage schema changes

## Layer 4: Output Boundary

**Purpose**: Ensure responses are safe, well-formed, and contain only intended data.

### What to Validate

- Strip sensitive fields (passwords, internal IDs, tokens)
- HTML-encode user-generated content to prevent XSS
- Validate response schema (catch accidental data leaks)
- Set security headers (Content-Type, X-Content-Type-Options)
- Limit response size

### Techniques

- **Python**: Use Pydantic `response_model` to exclude fields not in the response schema
- **TypeScript**: Create explicit mapper functions (`toUserResponse()`) that pick only safe fields
- **Headers**: Set `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`
- **Encoding**: HTML-encode user-generated content before rendering

## Layer Interaction Summary

| Layer | Catches | If Missing |
|---|---|---|
| Input | Malformed data, injection attempts | Bad data flows into business logic |
| Business | Invalid operations, auth bypass | Violated business rules, data corruption |
| Persistence | Constraint violations, duplicates | Inconsistent data in database |
| Output | Data leaks, XSS | Sensitive data exposed to clients |
