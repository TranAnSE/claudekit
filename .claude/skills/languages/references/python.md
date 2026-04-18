# Languages — Python Patterns


# Python

## When to Use

- Working with Python files (.py)
- Writing Python scripts or applications
- Using Python frameworks (Django, FastAPI, Flask)
- Data processing and automation

## When NOT to Use

- JavaScript or TypeScript-only projects with no Python components
- Non-Python environments where another language skill is more appropriate

---

## Core Patterns

### 1. Type Hints

Use type hints on all public functions and module-level variables. Python 3.10+ syntax is preferred (use `X | Y` instead of `Union[X, Y]`).

#### Basic Types

```python
from typing import Any

def greet(name: str) -> str:
    return f"Hello, {name}"

def process(count: int, factor: float = 1.0) -> float:
    return count * factor

def is_valid(data: bytes | None) -> bool:
    return data is not None and len(data) > 0
```

#### Optional and Union

```python
# Python 3.10+ syntax (preferred)
def find_user(user_id: int) -> User | None:
    ...

# Pre-3.10 fallback
from typing import Optional, Union

def find_user(user_id: int) -> Optional[User]:
    ...

def parse_input(value: Union[str, int]) -> str:
    return str(value)
```

#### Generic Collections

```python
# Python 3.9+ built-in generics (preferred)
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

def merge_configs(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    return {**base, **overrides}

# Nested generics
def group_by_key(pairs: list[tuple[str, int]]) -> dict[str, list[int]]:
    result: dict[str, list[int]] = {}
    for key, value in pairs:
        result.setdefault(key, []).append(value)
    return result
```

#### Protocol for Structural Subtyping

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Renderable(Protocol):
    def render(self) -> str: ...

class HtmlWidget:
    def render(self) -> str:
        return "<div>widget</div>"

def display(item: Renderable) -> None:
    print(item.render())

# HtmlWidget satisfies Renderable without inheriting from it
display(HtmlWidget())  # works
```

#### TypeVar for Generic Functions

```python
from typing import TypeVar, Sequence

T = TypeVar("T")

def first(items: Sequence[T]) -> T:
    return items[0]

# Bounded TypeVar
Numeric = TypeVar("Numeric", int, float)

def clamp(value: Numeric, low: Numeric, high: Numeric) -> Numeric:
    return max(low, min(high, value))
```

#### @overload for Multiple Signatures

```python
from typing import overload

@overload
def parse(raw: str) -> dict[str, Any]: ...
@overload
def parse(raw: bytes) -> dict[str, Any]: ...
@overload
def parse(raw: str, as_list: bool) -> list[Any]: ...

def parse(raw: str | bytes, as_list: bool = False) -> dict[str, Any] | list[Any]:
    data = raw if isinstance(raw, str) else raw.decode()
    parsed = json.loads(data)
    return list(parsed) if as_list else parsed
```

#### TypeAlias and TypeGuard

```python
from typing import TypeAlias, TypeGuard

# TypeAlias for complex types
JsonValue: TypeAlias = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]
Headers: TypeAlias = dict[str, str]

# TypeGuard for narrowing
def is_string_list(val: list[Any]) -> TypeGuard[list[str]]:
    return all(isinstance(item, str) for item in val)

def process(items: list[Any]) -> None:
    if is_string_list(items):
        # items is now list[str] inside this branch
        print(", ".join(items))
```

---

### 2. Dataclasses & Pydantic

#### @dataclass with Options

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: int
    email: str
    name: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.email = self.email.strip().lower()
```

#### Frozen and Slots

```python
@dataclass(frozen=True, slots=True)
class Coordinate:
    """Immutable, memory-efficient value object."""
    x: float
    y: float

    @property
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
```

#### Pydantic BaseModel

```python
from pydantic import BaseModel, EmailStr, Field, field_validator, computed_field, model_validator

class UserCreate(BaseModel):
    model_config = {"str_strip_whitespace": True, "frozen": False}

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8)
    age: int = Field(ge=0, le=150)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank")
        return v.title()

    @computed_field
    @property
    def display_name(self) -> str:
        return f"{self.name} <{self.email}>"

    @model_validator(mode="after")
    def check_consistency(self) -> "UserCreate":
        if "admin" in self.name.lower() and self.age < 18:
            raise ValueError("Admins must be 18+")
        return self
```

---

### 3. Async Patterns

#### Basic async/await

```python
import asyncio
import aiohttp

async def fetch_json(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()
```

#### asyncio.gather for Parallel Work

```python
async def fetch_all(urls: list[str]) -> list[dict]:
    return await asyncio.gather(*[fetch_json(url) for url in urls])
```

#### asyncio.TaskGroup (Python 3.11+)

```python
async def fetch_all_safe(urls: list[str]) -> list[dict]:
    results: list[dict] = []
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(fetch_and_append(url, results))
    return results

async def fetch_and_append(url: str, results: list[dict]) -> None:
    data = await fetch_json(url)
    results.append(data)
```

#### Async Generators

```python
async def paginate(url: str) -> AsyncIterator[dict]:
    page = 1
    while True:
        data = await fetch_json(f"{url}?page={page}")
        if not data["items"]:
            break
        for item in data["items"]:
            yield item
        page += 1

# Usage
async for item in paginate("/api/users"):
    process(item)
```

#### Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_transaction(pool):
    conn = await pool.acquire()
    tx = await conn.begin()
    try:
        yield conn
        await tx.commit()
    except Exception:
        await tx.rollback()
        raise
    finally:
        await pool.release(conn)
```

#### Semaphores for Concurrency Limiting

```python
async def fetch_with_limit(urls: list[str], max_concurrent: int = 10) -> list[dict]:
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_fetch(url: str) -> dict:
        async with semaphore:
            return await fetch_json(url)

    return await asyncio.gather(*[limited_fetch(url) for url in urls])
```

---

### 4. Decorators

#### Function Decorator with functools.wraps

```python
import functools
import time

def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timing
def slow_operation():
    time.sleep(1)
```

#### Decorator with Arguments

```python
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay * (2 ** attempt))
            raise last_error
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5)
async def unreliable_call(url: str) -> dict:
    return await fetch_json(url)
```

#### Class Decorator

```python
def singleton(cls):
    instances: dict[type, Any] = {}

    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class AppConfig:
    def __init__(self):
        self.settings = load_settings()
```

#### Caching Decorator

```python
from functools import lru_cache, cache

@lru_cache(maxsize=256)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Python 3.9+ unbounded cache
@cache
def load_config(path: str) -> dict:
    with open(path) as f:
        return json.load(f)
```

---

### 5. Context Managers

#### Basic @contextmanager

```python
from contextlib import contextmanager

@contextmanager
def managed_connection(dsn: str):
    conn = connect(dsn)
    try:
        yield conn
    finally:
        conn.close()

with managed_connection("postgres://...") as conn:
    conn.execute("SELECT 1")
```

#### Temporary File Context Manager

```python
import tempfile
import os

@contextmanager
def temp_directory():
    dirpath = tempfile.mkdtemp()
    try:
        yield dirpath
    finally:
        shutil.rmtree(dirpath)

with temp_directory() as tmpdir:
    filepath = os.path.join(tmpdir, "data.json")
    write_json(filepath, data)
```

#### Lock Context Manager

```python
import threading

@contextmanager
def timed_lock(lock: threading.Lock, timeout: float = 5.0):
    acquired = lock.acquire(timeout=timeout)
    if not acquired:
        raise TimeoutError("Could not acquire lock")
    try:
        yield
    finally:
        lock.release()
```

#### Async Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def http_session():
    session = aiohttp.ClientSession()
    try:
        yield session
    finally:
        await session.close()
```

---

### 6. Pattern Matching

#### Basic match/case

```python
def handle_command(command: str) -> str:
    match command.split():
        case ["quit"]:
            return "Goodbye"
        case ["hello", name]:
            return f"Hello, {name}"
        case ["add", *items]:
            return f"Adding {len(items)} items"
        case _:
            return "Unknown command"
```

#### Structural Patterns

```python
def process_event(event: dict) -> None:
    match event:
        case {"type": "click", "x": int(x), "y": int(y)}:
            handle_click(x, y)
        case {"type": "keypress", "key": str(key)} if len(key) == 1:
            handle_keypress(key)
        case {"type": "resize", "width": w, "height": h}:
            handle_resize(w, h)
```

#### Guard Clauses and OR Patterns

```python
def classify_status(code: int) -> str:
    match code:
        case 200 | 201 | 204:
            return "success"
        case code if 300 <= code < 400:
            return "redirect"
        case 401 | 403:
            return "auth_error"
        case code if 400 <= code < 500:
            return "client_error"
        case code if 500 <= code < 600:
            return "server_error"
        case _:
            return "unknown"
```

---

### 7. Error Handling

#### Custom Exception Hierarchies

```python
class AppError(Exception):
    """Base exception for the application."""
    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.code = code

class NotFoundError(AppError):
    """Resource was not found."""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(f"{resource} {resource_id} not found", code="NOT_FOUND")
        self.resource = resource
        self.resource_id = resource_id

class ValidationError(AppError):
    """Input validation failed."""
    def __init__(self, errors: list[str]):
        super().__init__(f"Validation failed: {'; '.join(errors)}", code="VALIDATION")
        self.errors = errors
```

#### ExceptionGroup (Python 3.11+)

```python
async def process_batch(items: list[dict]) -> list[dict]:
    results = []
    errors = []
    for item in items:
        try:
            results.append(await process(item))
        except Exception as e:
            errors.append(e)
    if errors:
        raise ExceptionGroup("Batch processing errors", errors)
    return results

# Handling with except*
try:
    await process_batch(items)
except* ValueError as eg:
    print(f"Validation errors: {len(eg.exceptions)}")
except* ConnectionError as eg:
    print(f"Connection errors: {len(eg.exceptions)}")
```

#### Exception Chaining

```python
def load_config(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise AppError(f"Config file missing: {path}") from e
    except json.JSONDecodeError as e:
        raise AppError(f"Invalid JSON in {path}") from e
```

#### contextlib.suppress

```python
from contextlib import suppress

# Instead of try/except/pass
with suppress(FileNotFoundError):
    os.remove("temp_file.txt")

# Instead of:
# try:
#     os.remove("temp_file.txt")
# except FileNotFoundError:
#     pass
```

---

## Best Practices

1. **Use type hints on all public functions** -- they serve as documentation, enable IDE autocompletion, and allow static analysis with mypy or pyright.

2. **Prefer dataclasses or Pydantic for structured data** -- avoid passing raw dicts around. Use `@dataclass` for internal data, Pydantic `BaseModel` for external boundaries (API input/output, config files).

3. **Use context managers for resource management** -- database connections, file handles, locks, and temporary resources should always be wrapped in `with` statements to guarantee cleanup.

4. **Prefer `asyncio.TaskGroup` over bare `gather`** -- TaskGroup (3.11+) provides proper error handling by cancelling sibling tasks when one fails, avoiding orphaned coroutines.

5. **Follow PEP 8 and use a formatter** -- use `ruff format` or `black` for consistent formatting, and `ruff check` for linting. Configure in `pyproject.toml`.

6. **Write small, composable functions** -- each function should do one thing. Prefer returning values over mutating state. Limit functions to ~20 lines when practical.

7. **Use `__all__` in public modules** -- explicitly declare the public API of a module to prevent accidental imports of internal helpers.

8. **Use `pathlib.Path` over `os.path`** -- pathlib provides a cleaner, object-oriented API for file system operations and works cross-platform.

---

## Common Pitfalls

1. **Mutable default arguments** -- default values are shared across calls. Use `None` and initialize inside the function body.
   ```python
   # BAD
   def add_item(item: str, items: list[str] = []) -> list[str]: ...

   # GOOD
   def add_item(item: str, items: list[str] | None = None) -> list[str]:
       if items is None:
           items = []
       items.append(item)
       return items
   ```

2. **Blocking calls inside async functions** -- calling `time.sleep()`, `requests.get()`, or CPU-heavy code in an async function blocks the entire event loop. Use `asyncio.to_thread()` or `asyncio.sleep()`.
   ```python
   # BAD
   async def fetch():
       return requests.get(url)  # blocks event loop

   # GOOD
   async def fetch():
       return await asyncio.to_thread(requests.get, url)
   ```

3. **Catching bare `Exception`** -- always be specific about which exceptions you catch. Bare `except:` or `except Exception:` hides bugs.
   ```python
   # BAD
   try:
       result = compute()
   except Exception:
       pass

   # GOOD
   try:
       result = compute()
   except (ValueError, TypeError) as e:
       logger.warning("Computation failed: %s", e)
       result = default_value
   ```

4. **Using `is` for value comparison** -- `is` checks identity, not equality. Only use `is` for `None`, `True`, `False`, and sentinel objects.
   ```python
   # BAD
   if x is 42: ...

   # GOOD
   if x == 42: ...
   if x is None: ...
   ```

5. **Forgetting to close resources** -- file handles, database connections, and HTTP sessions leak if not closed. Always use context managers.
   ```python
   # BAD
   f = open("data.txt")
   data = f.read()

   # GOOD
   with open("data.txt") as f:
       data = f.read()
   ```

6. **Circular imports** -- restructure code to avoid circular dependencies. Move shared types into a separate module, use `TYPE_CHECKING` for type-only imports, or use lazy imports.
   ```python
   from __future__ import annotations
   from typing import TYPE_CHECKING

   if TYPE_CHECKING:
       from myapp.models import User  # only imported during type checking
   ```

---

## Related Skills

- `typescript` -- TypeScript language patterns for polyglot projects
- `fastapi` -- FastAPI web framework built on Python
- `django` -- Django web framework for Python
- `pytest` -- Python testing with pytest
- `error-handling` -- Python error handling and exception hierarchies
