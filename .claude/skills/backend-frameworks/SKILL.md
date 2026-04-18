---
name: backend-frameworks
description: >
  Use when building REST APIs or web servers with FastAPI, Django, NestJS, or Express — including routing, middleware, dependency injection, Pydantic models, serializers, controllers, services, guards, pipes, app.get, app.post, APIRouter, class-based views, or framework-specific patterns.
---

# Backend Frameworks

## When to Use

- Building REST APIs with FastAPI, Django REST Framework, NestJS, or Express
- Configuring middleware, routing, authentication, or request validation
- Setting up dependency injection, services, or module structure
- Integrating with databases via ORMs (SQLAlchemy, Django ORM, TypeORM, Prisma)
- WebSocket servers, microservices, or GraphQL resolvers

## When NOT to Use

- Frontend development — use `frontend`
- Database-specific queries without framework context — use `databases`
- API design/documentation — use `openapi`

---

## Quick Reference

| Framework | Reference | Language | Key features |
|-----------|-----------|----------|-------------|
| FastAPI | `references/fastapi.md` | Python | Pydantic, async, APIRouter, Depends(), OpenAPI auto-docs |
| Django | `references/django.md` | Python | ORM, admin, DRF serializers, class-based views, migrations |
| NestJS | `references/nestjs.md` | TypeScript | Modules, DI, guards, pipes, interceptors, Prisma/TypeORM |
| Express | `references/express.md` | TypeScript | Middleware, Router, error handling, helmet, rate limiting |

---

## Best Practices

1. **Use validation models for all request/response data.** Pydantic (FastAPI), class-validator DTOs (NestJS), Zod (Express), serializers (Django).
2. **Separate business logic from routes/controllers.** Route handlers handle HTTP; services handle domain logic.
3. **Organize routes by resource and version.** APIRouter (FastAPI), module structure (NestJS), Router (Express), URL conf (Django).
4. **Return proper HTTP status codes.** 201 for creation, 204 for deletion, 202 for accepted-but-not-done, 409 for conflicts.
5. **Use async all the way down.** Never mix sync blocking calls in async routes (especially FastAPI).
6. **Configure settings from environment variables.** pydantic-settings (FastAPI), django-environ (Django), dotenv (Express/NestJS).
7. **Use `select_related`/`prefetch_related` for every query touching relations** (Django).
8. **Use `transaction.atomic()` for multi-step writes** (Django).

## Common Pitfalls

1. **Blocking I/O in async routes.** `requests.get()`, `time.sleep()` in `async def` routes starves the event loop (FastAPI).
2. **Missing response_model / leaking internal fields** (FastAPI).
3. **N+1 queries from missing eager loading** (Django `select_related`, NestJS relations).
4. **Circular imports/dependencies.** Use `forwardRef()` (NestJS), restructure modules (Django/FastAPI).
5. **Forgetting `asyncHandler`** — unhandled promise rejections crash the process (Express).
6. **Error handler not registered last** (Express).
7. **Putting business logic in controllers** (NestJS).
8. **Not using `whitelist: true` on ValidationPipe** (NestJS).

---

## Related Skills

- `databases` — Database queries, schema design, migrations
- `openapi` — API specification and documentation
- `error-handling` — Exception handling and API error responses
- `authentication` — Auth flows for web applications
