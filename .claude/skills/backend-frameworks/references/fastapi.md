# Backend Frameworks — FastAPI Patterns


# FastAPI

## When to Use

- Building REST APIs with Python
- Async web applications
- OpenAPI/Swagger documentation needed
- Python microservices
- WebSocket real-time applications

## When NOT to Use

- Django projects — use the `django` skill instead
- JavaScript/Node.js backends (Express, NestJS) — this skill is Python-only
- Non-API applications such as CLI tools, desktop apps, or batch processing scripts

---

## Core Patterns

### 1. Project Structure

Recommended layout for medium-large FastAPI applications:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app creation, startup/shutdown
│   ├── config.py               # Settings via pydantic-settings
│   ├── dependencies.py         # Shared dependencies
│   ├── exceptions.py           # Custom exception handlers
│   ├── middleware.py            # Custom middleware
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py           # Root router aggregating all sub-routers
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py        # /api/v1/users endpoints
│   │   │   ├── items.py        # /api/v1/items endpoints
│   │   │   └── auth.py         # /api/v1/auth endpoints
│   │   └── v2/                 # Future API version
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # SQLAlchemy / SQLModel ORM models
│   │   └── item.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic request/response schemas
│   │   └── item.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py     # Business logic layer
│   │   └── item_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repo.py        # Data access layer
│   │   └── item_repo.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py         # DB engine, session factory
│   │   └── security.py         # JWT, hashing, auth utils
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py          # Fixtures: test client, test DB
│       ├── test_users.py
│       └── test_items.py
├── alembic/                     # Database migrations
│   ├── env.py
│   └── versions/
├── alembic.ini
├── pyproject.toml
├── Dockerfile
└── .env
```

**Key conventions:**
- Separate `schemas/` (Pydantic) from `models/` (ORM) to keep concerns clean
- Use `services/` for business logic, `repositories/` for data access
- Version API routes under `api/v1/`, `api/v2/` for backward compatibility
- Keep `main.py` thin — it only wires things together

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.router import api_router
from app.config import settings
from app.core.database import engine
from app.middleware import add_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables, warm caches, connect to services
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: close connections, flush buffers
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)
add_middleware(app)
app.include_router(api_router, prefix="/api")
```

### 2. Route Patterns

#### APIRouter with tags, prefixes, and dependencies

```python
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException, status
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserList
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],  # Applied to all routes
    responses={401: {"description": "Not authenticated"}},
)

# Path parameters with validation
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int = Path(..., gt=0, description="The ID of the user to retrieve"),
):
    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Query parameters with defaults and validation
@router.get("/", response_model=UserList)
async def list_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    search: str | None = Query(None, min_length=1, max_length=100),
    sort_by: str = Query("created_at", pattern="^(created_at|name|email)$"),
):
    users = await user_service.list(skip=skip, limit=limit, search=search)
    return users

# Request body with status codes
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a user account and sends a welcome email.",
)
async def create_user(user: UserCreate = Body(...)):
    return await user_service.create(user)

# Multiple response models for different status codes
@router.put("/{user_id}", response_model=UserResponse, responses={
    404: {"description": "User not found"},
    409: {"description": "Email already taken"},
})
async def update_user(user_id: int, user: UserUpdate):
    return await user_service.update(user_id, user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    await user_service.delete(user_id)
```

#### Router aggregation

```python
# app/api/router.py
from fastapi import APIRouter
from app.api.v1 import users, items, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/v1")
api_router.include_router(users.router, prefix="/v1")
api_router.include_router(items.router, prefix="/v1")
```

### 3. Dependency Injection

#### Basic dependency with Depends()

```python
from fastapi import Depends, Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key
```

#### Nested dependencies

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session  # yield dependency — cleanup runs after response

async def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_user_service(
    repo: UserRepository = Depends(get_user_repo),
) -> UserService:
    return UserService(repo)

@router.get("/users")
async def list_users(service: UserService = Depends(get_user_service)):
    return await service.list_all()
```

#### Yield dependencies for cleanup

```python
async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = await aioredis.from_url(settings.REDIS_URL)
    try:
        yield redis
    finally:
        await redis.close()  # Always runs, even on exceptions

async def get_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        yield client
```

#### Request-scoped dependencies with caching

```python
# FastAPI caches dependency results per-request by default.
# The same db session is reused if multiple deps request it.

@router.get("/dashboard")
async def dashboard(
    user_service: UserService = Depends(get_user_service),
    item_service: ItemService = Depends(get_item_service),
    # Both services share the same db session from get_db()
):
    users = await user_service.count()
    items = await item_service.count()
    return {"users": users, "items": items}

# To disable caching (get fresh instance each time):
@router.get("/example")
async def example(
    db1: AsyncSession = Depends(get_db),
    db2: AsyncSession = Depends(get_db, use_cache=False),
    # db1 and db2 are different sessions
):
    pass
```

#### Class-based dependencies

```python
class Pagination:
    def __init__(
        self,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
    ):
        self.skip = skip
        self.limit = limit

@router.get("/items")
async def list_items(pagination: Pagination = Depends()):
    # pagination.skip, pagination.limit
    pass
```

### 4. Middleware

#### Custom middleware

```python
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        return response
```

#### Pure ASGI middleware (higher performance)

```python
from starlette.types import ASGIApp, Receive, Scope, Send

class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            request_id = uuid.uuid4().hex
            scope.setdefault("state", {})["request_id"] = request_id

            async def send_with_header(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    headers[b"x-request-id"] = request_id.encode()
                    message["headers"] = list(headers.items())
                await send(message)

            await self.app(scope, receive, send_with_header)
        else:
            await self.app(scope, receive, send)
```

#### Standard middleware configuration

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

def add_middleware(app: FastAPI):
    # Order matters: first added = outermost (runs first on request, last on response)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,  # ["https://example.com"]
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["*"],
    )

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,  # ["example.com", "*.example.com"]
    )

    app.add_middleware(GZipMiddleware, minimum_size=500)  # Compress responses > 500 bytes

    app.add_middleware(TimingMiddleware)
```

### 5. Background Tasks

#### Simple background tasks

```python
from fastapi import BackgroundTasks

async def send_welcome_email(email: str, name: str):
    # This runs after the response is sent
    await email_service.send(
        to=email,
        subject="Welcome!",
        body=f"Hello {name}, welcome to our platform.",
    )

async def log_activity(user_id: int, action: str):
    await activity_repo.create(user_id=user_id, action=action)

@router.post("/users", status_code=201)
async def create_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
):
    new_user = await user_service.create(user)
    # Queue multiple background tasks
    background_tasks.add_task(send_welcome_email, new_user.email, new_user.name)
    background_tasks.add_task(log_activity, new_user.id, "account_created")
    return new_user
```

#### Long-running tasks with task queues

For tasks that take more than a few seconds, use a proper task queue:

```python
from celery import Celery

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL)

@celery_app.task
def generate_report(report_id: int):
    # Long-running: query data, build PDF, upload to S3
    ...

@router.post("/reports", status_code=202)
async def request_report(params: ReportRequest):
    report = await report_service.create(params)
    generate_report.delay(report.id)  # Dispatch to Celery worker
    return {"report_id": report.id, "status": "processing"}

@router.get("/reports/{report_id}/status")
async def report_status(report_id: int):
    report = await report_service.get(report_id)
    return {"status": report.status, "url": report.download_url}
```

### 6. WebSocket

#### WebSocket endpoint with connection management

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        self.active_connections.setdefault(room, []).append(websocket)

    def disconnect(self, websocket: WebSocket, room: str):
        self.active_connections.get(room, []).remove(websocket)

    async def broadcast(self, message: str, room: str):
        for connection in self.active_connections.get(room, []):
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection, room)

manager = ConnectionManager()

@app.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}", room)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
        await manager.broadcast(f"User left the room", room)
```

#### WebSocket with authentication

```python
@app.websocket("/ws/private")
async def private_ws(websocket: WebSocket, token: str = Query(...)):
    try:
        user = verify_token(token)
    except InvalidToken:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            response = await process_message(user, data)
            await websocket.send_json(response)
    except WebSocketDisconnect:
        pass
```

### 7. File Handling

#### Upload files

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
):
    # Validate file type and size
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(400, "Only PNG and JPEG images are allowed")

    if file.size and file.size > 5 * 1024 * 1024:  # 5 MB
        raise HTTPException(400, "File too large (max 5 MB)")

    contents = await file.read()
    path = f"uploads/{uuid.uuid4()}_{file.filename}"
    async with aiofiles.open(path, "wb") as f:
        await f.write(contents)

    return {"filename": file.filename, "path": path, "size": len(contents)}

# Multiple file upload
@router.post("/upload-multiple")
async def upload_multiple(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        results.append({"filename": file.filename, "size": len(contents)})
    return results
```

#### Streaming responses

```python
from fastapi.responses import StreamingResponse
import csv
import io

@router.get("/export/users")
async def export_users():
    async def generate_csv():
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "name", "email"])
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

        async for user in user_service.stream_all():
            writer.writerow([user.id, user.name, user.email])
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"},
    )
```

#### Static files

```python
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 8. Testing

#### TestClient for synchronous tests

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/api/v1/users", json={
        "email": "test@example.com",
        "name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

def test_get_user_not_found():
    response = client.get("/api/v1/users/99999")
    assert response.status_code == 404
```

#### Async testing with httpx

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.mark.anyio
async def test_list_users(async_client: AsyncClient):
    response = await async_client.get("/api/v1/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

#### Overriding dependencies for tests

```python
from app.dependencies import get_db, get_current_user
from app.models.user import User

# Mock database session
async def override_get_db():
    async with test_session_maker() as session:
        yield session

# Mock authenticated user
async def override_get_current_user():
    return User(id=1, email="test@example.com", name="Test")

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

# In conftest.py — clean up after tests
@pytest.fixture(autouse=True)
def clear_overrides():
    yield
    app.dependency_overrides.clear()
```

#### Testing WebSocket endpoints

```python
def test_websocket():
    with client.websocket_connect("/ws/test-room") as ws:
        ws.send_text("hello")
        data = ws.receive_text()
        assert "hello" in data
```

---

## Best Practices

1. **Use Pydantic models for all request/response validation** — never pass raw dicts through your API boundary. Define separate `Create`, `Update`, and `Response` schemas for each resource.

2. **Organize routes with APIRouter** — group related endpoints by resource and version. Apply shared dependencies at the router level, not on each individual route.

3. **Separate business logic from routes** — route functions should only handle HTTP concerns (parsing request, returning response). Delegate logic to service classes injected via `Depends()`.

4. **Use the lifespan context manager** — replace deprecated `on_event("startup")` and `on_event("shutdown")` with the `lifespan` async context manager for resource setup and teardown.

5. **Return proper HTTP status codes** — 201 for creation, 204 for deletion, 202 for accepted-but-not-done, 409 for conflicts. Use `status_code` parameter on route decorators.

6. **Add OpenAPI metadata** — provide `summary`, `description`, `tags`, and `responses` on routes. Set `title`, `version`, and `description` on the FastAPI app. This generates high-quality auto-docs.

7. **Use async all the way down** — if your route is `async def`, every I/O call inside it must also be async. Mixing sync blocking calls (e.g., `requests.get()`) in an async route will block the event loop.

8. **Configure settings with pydantic-settings** — load config from environment variables with validation and type coercion. Never hardcode secrets or connection strings.

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    DEBUG: bool = False

    model_config = {"env_file": ".env"}

settings = Settings()
```

---

## Common Pitfalls

1. **Blocking I/O in async routes** — calling `requests.get()`, `time.sleep()`, or synchronous DB drivers inside `async def` routes starves the event loop. Use `httpx`, `asyncio.sleep()`, and async database drivers instead. If you must call sync code, use `run_in_executor`.

2. **Missing response_model** — without `response_model`, FastAPI returns whatever you return, potentially leaking internal fields (passwords, internal IDs). Always define a Pydantic response schema.

3. **Forgetting to await coroutines** — calling `await db.execute(query)` vs `db.execute(query)` is easy to miss. The latter returns a coroutine object instead of results. Enable linting rules that catch unawaited coroutines.

4. **Circular imports between models and schemas** — when schemas reference ORM models and vice versa, you get import cycles. Fix by using `TYPE_CHECKING` imports or by keeping schemas and models in separate modules that do not import each other.

5. **Not handling Pydantic validation errors** — FastAPI returns 422 by default, but the error format may confuse API consumers. Add a custom exception handler to reshape validation error responses to match your API's error format.

6. **Sharing mutable state across requests without locks** — global mutable variables (lists, dicts) accessed from async routes can cause race conditions. Use async-safe structures or dependency-injected per-request state.

---

## Related Skills

- `python` — Python language patterns and best practices
- `openapi` — OpenAPI specification and documentation standards
- `postgresql` — Database integration with async SQLAlchemy
- `pytest` — Testing FastAPI applications with pytest and httpx
- `authentication` — JWT, OAuth2, and session patterns for FastAPI endpoints
- `logging` — Structured logging for FastAPI applications
