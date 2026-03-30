---
name: pytest
description: >
  Trigger this skill whenever writing, debugging, or refactoring Python tests, or when pytest fixtures, parametrization, mocking, or coverage are mentioned. Activate for any .py test file, test_* function, conftest.py, pytest.ini, or pyproject.toml [tool.pytest] reference. Also use when the user asks about Python test patterns, test organization, or test-driven development in a Python context.
---

# pytest

## When to Use

- Writing Python tests
- Test fixtures and setup
- Mocking dependencies

## When NOT to Use

- JavaScript or TypeScript testing -- use the `testing/vitest` skill instead
- Projects that explicitly mandate unittest-only by convention with no pytest dependency
- Non-Python test files or environments

---

## Core Patterns

### 1. Fixtures

Fixtures provide reusable setup and teardown logic. They are requested by name as test function parameters.

#### Function-Scoped Fixtures (default)

A new instance is created for every test that requests it.

```python
import pytest
from myapp.models import User
from myapp.db import Session


@pytest.fixture
def user():
    """Fresh user instance per test."""
    return User(id=1, name="Alice", email="alice@example.com")


def test_user_display_name(user):
    assert user.display_name() == "Alice"


def test_user_email_domain(user):
    assert user.email_domain() == "example.com"
```

#### Class and Module Scope

Use broader scopes for expensive resources that are safe to share.

```python
@pytest.fixture(scope="class")
def api_client():
    """Shared across all tests in a test class."""
    client = APIClient(base_url="http://testserver")
    client.authenticate(token="test-token")
    return client


@pytest.fixture(scope="module")
def database_schema():
    """Created once per test module, shared across all tests in the file."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def redis_connection():
    """Created once for the entire test session."""
    conn = Redis(host="localhost", port=6379, db=15)
    conn.flushdb()
    yield conn
    conn.flushdb()
    conn.close()
```

#### Yield Fixtures for Teardown

`yield` separates setup from teardown. Code after `yield` runs after the test completes, even if the test fails.

```python
@pytest.fixture
def db_session():
    session = Session()
    session.begin()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def temp_config(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("debug: true\nlog_level: INFO\n")
    yield config_file
    # tmp_path is automatically cleaned up by pytest
```

#### Autouse Fixtures

Apply a fixture to every test automatically without requesting it by name.

```python
@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Ensure each test starts with clean environment variables."""
    monkeypatch.delenv("API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)


@pytest.fixture(autouse=True)
def freeze_time():
    """Pin time for deterministic tests."""
    with freeze_time("2025-06-15T12:00:00Z"):
        yield
```

#### Factory Fixtures

Return a factory function when tests need multiple instances with varying parameters.

```python
@pytest.fixture
def make_user():
    """Factory that creates users with sensible defaults."""
    created = []

    def _make_user(name="Test User", role="viewer", active=True):
        user = User(name=name, role=role, active=active)
        created.append(user)
        return user

    yield _make_user

    # Teardown: clean up all created users
    for u in created:
        u.delete()


def test_admin_permissions(make_user):
    admin = make_user(name="Admin", role="admin")
    viewer = make_user(name="Viewer", role="viewer")
    assert admin.can_delete_users() is True
    assert viewer.can_delete_users() is False
```

#### Parametrized Fixtures with request.param

Run the same test against multiple fixture variants.

```python
@pytest.fixture(params=["sqlite", "postgresql"])
def db_engine(request):
    """Test against multiple database backends."""
    if request.param == "sqlite":
        engine = create_engine("sqlite:///:memory:")
    elif request.param == "postgresql":
        engine = create_engine("postgresql://test:test@localhost/testdb")
    yield engine
    engine.dispose()


def test_insert_and_query(db_engine):
    # This test runs twice: once with sqlite, once with postgresql
    with db_engine.connect() as conn:
        conn.execute(text("CREATE TABLE t (id INT)"))
        conn.execute(text("INSERT INTO t VALUES (1)"))
        result = conn.execute(text("SELECT * FROM t")).fetchall()
        assert len(result) == 1
```

---

### 2. Parametrize

#### Single Parameter

```python
@pytest.mark.parametrize("email", [
    "user@example.com",
    "admin@test.org",
    "name+tag@domain.co.uk",
])
def test_valid_email_accepted(email):
    assert is_valid_email(email) is True
```

#### Multiple Parameters

```python
@pytest.mark.parametrize("input_text, expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
    ("already UPPER", "ALREADY UPPER"),
])
def test_uppercase(input_text, expected):
    assert input_text.upper() == expected
```

#### Custom IDs for Readable Output

```python
@pytest.mark.parametrize("status_code, should_retry", [
    pytest.param(200, False, id="success-no-retry"),
    pytest.param(429, True, id="rate-limited-retry"),
    pytest.param(500, True, id="server-error-retry"),
    pytest.param(404, False, id="not-found-no-retry"),
])
def test_retry_logic(status_code, should_retry):
    response = MockResponse(status_code=status_code)
    assert should_retry_request(response) is should_retry
```

#### Indirect Parametrize

Pass parameters through a fixture rather than directly to the test.

```python
@pytest.fixture
def user_role(request):
    """Create a user with the given role."""
    return User(name="Test", role=request.param)


@pytest.mark.parametrize("user_role", ["admin", "editor", "viewer"], indirect=True)
def test_dashboard_access(user_role):
    if user_role.role == "admin":
        assert user_role.can_access("/admin/dashboard") is True
    else:
        assert user_role.can_access("/admin/dashboard") is False
```

#### Stacking Parametrize Decorators

Creates the cartesian product of all parameter sets.

```python
@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
@pytest.mark.parametrize("auth", ["token", "session", "none"])
def test_endpoint_auth(method, auth):
    # Runs 4 x 3 = 12 test cases
    response = make_request(method=method, auth_type=auth)
    if auth == "none":
        assert response.status_code == 401
    else:
        assert response.status_code in (200, 201, 204)
```

---

### 3. Mocking

#### monkeypatch -- Environment Variables and Attributes

```python
def test_reads_api_key_from_env(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key-12345")
    config = load_config()
    assert config.api_key == "test-key-12345"


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with pytest.raises(ConfigError, match="API_KEY is required"):
        load_config()


def test_override_attribute(monkeypatch):
    monkeypatch.setattr("myapp.settings.MAX_RETRIES", 0)
    assert retry_request(failing_url) is None  # No retries attempted


def test_override_dict_item(monkeypatch):
    monkeypatch.setitem(app_config, "timeout", 1)
    assert app_config["timeout"] == 1
```

#### unittest.mock.patch

```python
from unittest.mock import patch, Mock, AsyncMock


@patch("myapp.services.payment.stripe.Charge.create")
def test_charge_customer(mock_charge):
    mock_charge.return_value = Mock(id="ch_123", status="succeeded")

    result = process_payment(amount=1000, currency="usd", token="tok_visa")

    mock_charge.assert_called_once_with(
        amount=1000, currency="usd", source="tok_visa"
    )
    assert result.charge_id == "ch_123"


@patch("myapp.services.email.send_email")
@patch("myapp.services.user.UserRepository.find_by_id")
def test_send_welcome_email(mock_find, mock_send):
    mock_find.return_value = User(id=1, email="new@example.com")
    mock_send.return_value = True

    send_welcome(user_id=1)

    mock_send.assert_called_once_with(
        to="new@example.com", template="welcome"
    )
```

#### responses Library for HTTP Mocking

```python
import responses
import requests


@responses.activate
def test_fetch_user_from_api():
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        json={"id": 1, "name": "Alice"},
        status=200,
    )

    result = fetch_user(user_id=1)

    assert result["name"] == "Alice"
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "https://api.example.com/users/1"


@responses.activate
def test_api_timeout_handling():
    responses.add(
        responses.GET,
        "https://api.example.com/users/1",
        body=requests.exceptions.ConnectionError("Connection timed out"),
    )

    with pytest.raises(ServiceUnavailableError):
        fetch_user(user_id=1)
```

#### pytest-mock's mocker Fixture

```python
def test_with_mocker(mocker):
    mock_repo = mocker.patch("myapp.services.OrderRepository")
    mock_repo.return_value.get_by_id.return_value = Order(
        id=1, status="pending"
    )

    service = OrderService()
    order = service.get_order(1)

    assert order.status == "pending"
    mock_repo.return_value.get_by_id.assert_called_once_with(1)


def test_spy_on_method(mocker):
    spy = mocker.spy(UserService, "validate_email")

    service = UserService()
    service.register("alice@example.com")

    spy.assert_called_once_with(service, "alice@example.com")
```

---

### 4. Async Testing

#### pytest-asyncio Basics

```python
import pytest
import httpx


@pytest.mark.asyncio
async def test_async_fetch():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/get")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_async_exception():
    with pytest.raises(ValueError, match="invalid"):
        await validate_async_input("")
```

#### Async Fixtures

```python
@pytest.fixture
async def async_db_session():
    session = AsyncSession(bind=async_engine)
    await session.begin()
    yield session
    await session.rollback()
    await session.close()


@pytest.mark.asyncio
async def test_async_query(async_db_session):
    result = await async_db_session.execute(
        select(User).where(User.active == True)
    )
    users = result.scalars().all()
    assert len(users) >= 0
```

#### Configuring asyncio Mode

In `pyproject.toml` or `pytest.ini`, set the default mode to avoid repeating the marker:

```toml
# pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

With `asyncio_mode = "auto"`, any `async def test_*` function is automatically treated as async -- no `@pytest.mark.asyncio` needed.

---

### 5. Test Organization

#### conftest.py Hierarchy

```
tests/
├── conftest.py              # Session/global fixtures (db connection, app client)
├── unit/
│   ├── conftest.py          # Unit-specific fixtures (mocked services)
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── conftest.py          # Integration fixtures (real db session, test server)
│   ├── test_api.py
│   └── test_repositories.py
└── e2e/
    ├── conftest.py          # E2E fixtures (browser, full app)
    └── test_workflows.py
```

Fixtures in a `conftest.py` are available to all tests in the same directory and below. No imports needed.

#### Test Discovery

pytest discovers tests by default based on these rules:
- Files matching `test_*.py` or `*_test.py`
- Classes prefixed with `Test` (no `__init__` method)
- Functions prefixed with `test_`

Configure custom discovery in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

#### Markers

```python
import pytest
import sys

# Built-in markers
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass


@pytest.mark.skipif(
    sys.platform == "win32", reason="Unix-only functionality"
)
def test_unix_permissions():
    pass


@pytest.mark.xfail(reason="Known bug #1234, fix pending")
def test_known_broken():
    result = buggy_function()
    assert result == "expected"
```

#### Custom Markers

Register markers in `pyproject.toml` to avoid warnings:

```toml
[tool.pytest.ini_options]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests requiring external services",
    "smoke: critical path tests for quick validation",
]
```

```python
@pytest.mark.slow
def test_full_data_migration():
    migrate_all_records()  # Takes 30+ seconds
    assert count_records() == EXPECTED_TOTAL


@pytest.mark.smoke
def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
```

Run selectively:

```bash
pytest -m "smoke"                # Only smoke tests
pytest -m "not slow"             # Skip slow tests
pytest -m "integration and not slow"  # Integration but not slow
```

---

### 6. Coverage

#### Basic Usage

```bash
pytest --cov=src --cov-report=term-missing
pytest --cov=src --cov-report=html     # Generates htmlcov/
pytest --cov=src --cov-branch           # Enable branch coverage
```

#### Configuration in pyproject.toml

```toml
[tool.pytest.ini_options]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=80"

[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/__pycache__/*",
    "*/conftest.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@overload",
]
fail_under = 80
show_missing = true
```

#### .coveragerc Alternative

If not using `pyproject.toml`, create `.coveragerc`:

```ini
[run]
source = src
branch = true

[report]
fail_under = 80
show_missing = true
exclude_lines =
    pragma: no cover
    def __repr__
    if TYPE_CHECKING:
```

---

### 7. Assertions

#### pytest.raises for Exceptions

```python
def test_raises_value_error():
    with pytest.raises(ValueError) as exc_info:
        parse_age("not-a-number")
    assert "invalid literal" in str(exc_info.value)


def test_raises_with_match():
    with pytest.raises(PermissionError, match=r"User .+ lacks role 'admin'"):
        authorize(user=viewer, required_role="admin")
```

#### pytest.approx for Floating Point

```python
def test_circle_area():
    assert calculate_area(radius=5) == pytest.approx(78.5398, rel=1e-4)


def test_approx_list():
    result = distribute_evenly(total=100, buckets=3)
    assert result == pytest.approx([33.33, 33.33, 33.34], abs=0.01)
```

#### Custom Assertion Helpers

Build reusable assertion logic for domain-specific validation.

```python
def assert_valid_api_response(response, expected_status=200):
    """Reusable assertion for API responses."""
    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}: "
        f"{response.text}"
    )
    data = response.json()
    assert "error" not in data, f"Unexpected error: {data['error']}"
    return data


def test_create_user(client):
    response = client.post("/users", json={"name": "Alice"})
    data = assert_valid_api_response(response, expected_status=201)
    assert data["name"] == "Alice"
    assert "id" in data
```

---

## Best Practices

1. **Name tests descriptively** -- Use `test_[function]_[scenario]_[expected]` so failures are self-explanatory without reading the test body. `test_parse_date_invalid_format_raises_valueerror` tells you everything.

2. **Keep tests independent** -- Never rely on test execution order. Each test should set up its own state via fixtures and tear it down afterward. Shared mutable state between tests is the top cause of flaky suites.

3. **One assertion focus per test** -- A test can have multiple `assert` statements, but they should all verify the same behavior. If you need to check two independent behaviors, write two tests.

4. **Use fixtures over setup methods** -- Prefer composable fixtures over `setUp`/`tearDown` methods or `setup_function`. Fixtures are explicit about dependencies, reusable across files via `conftest.py`, and support scoping.

5. **Mock at the boundary, not in the middle** -- Mock external services, databases, and network calls. Do not mock internal functions unless they are truly expensive. Over-mocking produces tests that pass but verify nothing.

6. **Use `tmp_path` for file operations** -- pytest's built-in `tmp_path` fixture provides a unique temporary directory per test. Never write to the real filesystem in tests.

7. **Pin randomness and time** -- When testing code that depends on randomness or the current time, use `random.seed()` or a time-freezing library to make tests deterministic.

8. **Run the full suite in CI with branch coverage** -- Local development can use `pytest -x` for fast feedback (stop on first failure), but CI must run the full suite with `--cov-branch` to catch untested branches and regressions.

---

## Common Pitfalls

1. **Shared mutable fixtures** -- A module-scoped fixture returning a mutable object (list, dict, instance) gets modified by one test and breaks another. Return fresh copies or use function scope for mutable data.

2. **Patching the wrong import path** -- `@patch("myapp.services.requests.get")` patches where `requests.get` is looked up, not where it is defined. If `services.py` does `from requests import get`, you must patch `myapp.services.get`, not `requests.get`.

3. **Forgetting to await in async tests** -- Omitting `await` makes the test pass vacuously because it never actually runs the coroutine. Always `await` the function under test and use `@pytest.mark.asyncio`.

4. **Tests that depend on execution order** -- If test B relies on side effects from test A, parallel test execution (pytest-xdist) and `--randomly` will expose the coupling immediately. Fix by making each test self-contained.

5. **Asserting on mock call count without checking arguments** -- `mock.assert_called_once()` confirms the call count but not what was passed. Use `assert_called_once_with(...)` or inspect `mock.call_args` to verify the actual arguments.

6. **Ignoring warnings as errors** -- Configure `filterwarnings = ["error"]` in `pyproject.toml` to catch deprecation warnings early. A passing test suite that emits 50 deprecation warnings is a time bomb.

---

## Related Skills

- `testing/vitest` -- JavaScript/TypeScript testing counterpart
- `languages/python` -- Python language patterns and idioms
- `methodology/test-driven-development` -- TDD workflow for writing tests first
- `devops/github-actions` — Running pytest in CI/CD pipelines
