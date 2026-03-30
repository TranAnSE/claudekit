# FastAPI Project Structure Reference

## Small Project (1-5 endpoints, single module)

```
project/
├── main.py              # App factory, routes, startup
├── models.py            # Pydantic schemas + SQLAlchemy models
├── database.py          # DB connection, session factory
├── config.py            # Settings via pydantic-settings
├── requirements.txt
├── .env
└── tests/
    ├── conftest.py      # Fixtures (test client, test DB)
    └── test_main.py
```

**When to use**: Prototypes, microservices, internal tools, single-domain APIs.

**`main.py` structure**:
```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    yield
    # shutdown

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health(): return {"status": "ok"}
```

---

## Medium Project (5-20 endpoints, feature-grouped)

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # App factory, include routers
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Engine, SessionLocal, Base
│   ├── dependencies.py      # Shared deps (get_db, get_current_user)
│   ├── exceptions.py        # Custom exception handlers
│   ├── middleware.py         # CORS, logging, timing middleware
│   │
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py        # POST /login, POST /register
│   │   ├── schemas.py       # LoginRequest, TokenResponse
│   │   ├── models.py        # User SQLAlchemy model
│   │   ├── service.py       # Business logic (hash, verify, tokens)
│   │   └── dependencies.py  # get_current_user, require_role
│   │
│   ├── items/
│   │   ├── __init__.py
│   │   ├── router.py        # CRUD endpoints
│   │   ├── schemas.py       # ItemCreate, ItemRead, ItemUpdate
│   │   ├── models.py        # Item SQLAlchemy model
│   │   └── service.py       # Business logic
│   │
│   └── shared/
│       ├── __init__.py
│       ├── pagination.py    # Pagination params + response schema
│       └── filters.py       # Common query filter patterns
│
├── alembic/                 # DB migrations
│   ├── env.py
│   └── versions/
├── alembic.ini
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── tests/
    ├── conftest.py
    ├── auth/
    │   └── test_router.py
    └── items/
        ├── test_router.py
        └── test_service.py
```

**When to use**: Multi-feature APIs, team projects, typical SaaS backends.

**Key patterns**:
- Each feature gets its own directory with router, schemas, models, service
- `router.py` uses `APIRouter(prefix="/items", tags=["items"])`
- `main.py` includes routers: `app.include_router(items.router)`
- Shared deps in root `dependencies.py`, feature-specific in feature dir

---

## Large Project (20+ endpoints, domain-driven)

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py                  # App factory only
│   ├── config.py                # Layered settings
│   │
│   ├── core/                    # Framework-level concerns
│   │   ├── __init__.py
│   │   ├── database.py          # Engine, session management
│   │   ├── security.py          # JWT, hashing, RBAC
│   │   ├── exceptions.py        # Base exceptions + handlers
│   │   ├── middleware.py        # All middleware stack
│   │   ├── dependencies.py      # Cross-cutting deps
│   │   ├── events.py            # Domain event bus
│   │   └── pagination.py        # Cursor + offset pagination
│   │
│   ├── domain/                  # Business logic (framework-agnostic)
│   │   ├── users/
│   │   │   ├── __init__.py
│   │   │   ├── entity.py        # Domain entity (plain dataclass)
│   │   │   ├── repository.py    # Abstract repository interface
│   │   │   ├── service.py       # Business rules
│   │   │   └── events.py        # Domain events
│   │   ├── orders/
│   │   │   └── ...
│   │   └── payments/
│   │       └── ...
│   │
│   ├── infrastructure/          # External system adapters
│   │   ├── database/
│   │   │   ├── models.py        # All SQLAlchemy models
│   │   │   ├── repositories/    # Concrete repo implementations
│   │   │   │   ├── user_repo.py
│   │   │   │   └── order_repo.py
│   │   │   └── migrations/      # Alembic
│   │   ├── cache/
│   │   │   └── redis_client.py
│   │   ├── email/
│   │   │   └── smtp_service.py
│   │   └── external/
│   │       └── stripe_client.py
│   │
│   └── api/                     # HTTP layer only
│       ├── __init__.py
│       ├── v1/
│       │   ├── __init__.py      # v1 router aggregator
│       │   ├── users.py         # Thin: parse request -> call service -> format response
│       │   ├── orders.py
│       │   └── payments.py
│       ├── v2/
│       │   └── ...
│       ├── schemas/             # Request/response schemas
│       │   ├── user_schemas.py
│       │   ├── order_schemas.py
│       │   └── common.py
│       ├── dependencies.py      # API-layer deps
│       └── websockets/
│           └── notifications.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── domain/
│   │   │   └── test_user_service.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_user_api.py
│   │   └── test_order_flow.py
│   └── e2e/
│       └── test_checkout.py
│
├── scripts/                     # Dev/ops scripts
│   ├── seed_db.py
│   └── migrate.py
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── Makefile
```

**When to use**: Complex domains, multiple teams, long-lived products.

**Key patterns**:
- **Domain layer** has zero framework imports (testable in isolation)
- **Infrastructure** implements domain interfaces (repository pattern)
- **API layer** is thin: validation, auth, call service, return schema
- API versioning via `/api/v1/`, `/api/v2/`
- Separate unit, integration, and e2e test directories

---

## File Responsibilities

| File | Responsibility | Dependencies |
|------|---------------|-------------|
| `router.py` | HTTP handling, request parsing, response formatting | schemas, service, dependencies |
| `schemas.py` | Pydantic models for request/response validation | None (or shared schemas) |
| `models.py` | SQLAlchemy/ODM models (DB table mapping) | database |
| `service.py` | Business logic, orchestration | repository/models, external services |
| `dependencies.py` | FastAPI `Depends()` callables | database, config, auth |
| `exceptions.py` | Custom exceptions + handlers | None |
| `config.py` | `BaseSettings` with env loading | None |

## Router Registration Pattern

```python
# app/main.py
from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.items.router import router as items_router

def create_app() -> FastAPI:
    app = FastAPI(title="My API")
    app.include_router(auth_router)
    app.include_router(items_router)
    return app

app = create_app()
```

```python
# app/items/router.py
from fastapi import APIRouter, Depends
router = APIRouter(prefix="/items", tags=["items"])

@router.get("/")
async def list_items(db=Depends(get_db)): ...
```
