# pytest Fixture Patterns

Catalog of reusable fixture patterns for common testing scenarios.

## 1. Factory Fixture

Create multiple instances with customizable defaults.

```python
import pytest
from dataclasses import dataclass

@pytest.fixture
def make_user():
    """Factory fixture: creates User instances with sensible defaults."""
    created = []

    def _make_user(
        name: str = "Test User",
        email: str | None = None,
        is_active: bool = True,
    ):
        if email is None:
            email = f"user-{len(created)}@test.com"
        user = User(name=name, email=email, is_active=is_active)
        created.append(user)
        return user

    yield _make_user

    # Cleanup: delete all created users
    for user in created:
        user.delete()
```

Usage:

```python
def test_deactivate_user(make_user):
    user = make_user(name="Alice", is_active=True)
    user.deactivate()
    assert not user.is_active
```

## 2. Database Session (SQLAlchemy)

Transaction-isolated database session that rolls back after each test.

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def engine():
    """Create a test database engine (once per test session)."""
    engine = create_engine("postgresql://test:test@localhost:5432/test_db")
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def tables(engine):
    """Create all tables once, drop after all tests."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    """Provide a transactional database session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

## 3. Temporary Files and Directories

```python
@pytest.fixture
def sample_config(tmp_path: Path) -> Path:
    """Create a temporary config file with test content."""
    config = tmp_path / "config.yaml"
    config.write_text(
        """\
        database:
          host: localhost
          port: 5432
        debug: true
        """
    )
    return config

@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """Create a temporary directory structure for testing."""
    (tmp_path / "input").mkdir()
    (tmp_path / "output").mkdir()
    (tmp_path / "input" / "data.csv").write_text("id,name\n1,Alice\n2,Bob\n")
    return tmp_path
```

## 4. Mock External Service

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def mock_http_client():
    """Mock an HTTP client with pre-configured responses."""
    client = MagicMock()
    client.get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"status": "ok"},
    )
    client.post.return_value = MagicMock(
        status_code=201,
        json=lambda: {"id": "new-123"},
    )
    return client

@pytest.fixture
def mock_payment_gateway():
    """Mock a payment gateway service."""
    with patch("app.services.payment.PaymentGateway") as mock_cls:
        instance = mock_cls.return_value
        instance.charge.return_value = {
            "transaction_id": "txn-test-123",
            "status": "succeeded",
        }
        instance.refund.return_value = {
            "refund_id": "ref-test-456",
            "status": "refunded",
        }
        yield instance

# Async version
@pytest.fixture
def mock_email_service():
    """Mock an async email service."""
    with patch("app.services.email.EmailService") as mock_cls:
        instance = mock_cls.return_value
        instance.send = AsyncMock(return_value={"message_id": "msg-test-789"})
        yield instance
```

## 5. Authenticated Test Client (FastAPI)

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth import create_access_token

@pytest.fixture
def auth_token():
    """Generate a valid JWT token for testing."""
    return create_access_token(
        data={"sub": "test-user-id", "role": "admin"},
        expires_minutes=60,
    )

@pytest.fixture
def auth_headers(auth_token: str) -> dict[str, str]:
    """HTTP headers with Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
async def client():
    """Unauthenticated async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

@pytest.fixture
async def auth_client(auth_headers):
    """Authenticated async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=auth_headers,
    ) as c:
        yield c
```

## 6. Environment Variables

```python
@pytest.fixture
def env_vars(monkeypatch):
    """Set environment variables for the test, automatically restored after."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.delenv("PRODUCTION_API_KEY", raising=False)
```

## 7. Freezing Time

```python
@pytest.fixture
def frozen_time():
    """Freeze time to a specific moment."""
    fixed = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    with patch("app.services.datetime") as mock_dt:
        mock_dt.now.return_value = fixed
        mock_dt.utcnow.return_value = fixed
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        yield fixed
```

Alternative: use `freezegun` library with `@freeze_time("2025-01-15 12:00:00")`.

## 8. Parametrized Fixture

```python
@pytest.fixture(params=["sqlite", "postgresql"])
def db_url(request):
    """Run tests against multiple database backends."""
    urls = {
        "sqlite": "sqlite:///test.db",
        "postgresql": "postgresql://test:test@localhost/test",
    }
    return urls[request.param]
```

## Fixture Scope Reference

| Scope | Lifetime | Use For |
|-------|----------|---------|
| `function` (default) | Each test | Most fixtures, mutable state |
| `class` | Each test class | Shared setup for a class |
| `module` | Each test file | Expensive setup shared across file |
| `session` | Entire test run | Database engine, heavy resources |

## Tips

- Use `yield` (not `return`) when cleanup is needed after the test.
- Use `autouse=True` sparingly -- only for things every test needs.
- Keep fixtures small and composable -- combine them in tests, not in other fixtures.
- Use `monkeypatch` instead of `unittest.mock.patch` for env vars and attributes when possible.
- Name fixtures after what they provide, not what they do: `db_session` not `setup_database`.
