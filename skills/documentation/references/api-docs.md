# API Documentation Patterns

## Endpoint Documentation Template

```markdown
## POST /api/orders

Create a new order.

### Authentication
Requires Bearer token.

### Request Body
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| items | array | yes | Order items |
| shippingAddress | object | yes | Delivery address |

### Response (201 Created)
```json
{
  "id": "order_456",
  "status": "pending",
  "total": 99.99,
  "createdAt": "2024-01-15T10:00:00Z"
}
```

### Errors
| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_ITEMS | Items array is empty |
| 401 | UNAUTHORIZED | Invalid or missing token |
| 422 | OUT_OF_STOCK | Item not available |
```

## Discovery Process

1. Scan route definitions (`@app.get`, `router.post`, `@Controller`)
2. Identify HTTP methods and paths
3. Note authentication requirements
4. Document request/response schemas
5. List all error responses with codes
6. Add working curl/httpx examples
