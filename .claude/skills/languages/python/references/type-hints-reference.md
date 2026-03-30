# Python Type Hints Quick Reference

> Python 3.10+ syntax preferred. For 3.9, use `from __future__ import annotations`.

## Basic Types

| Type | Example | Notes |
|------|---------|-------|
| `int` | `x: int = 1` | |
| `float` | `x: float = 1.0` | |
| `str` | `x: str = "hi"` | |
| `bool` | `x: bool = True` | |
| `bytes` | `x: bytes = b"hi"` | |
| `None` | `x: None = None` | Use as return type for side-effect functions |
| `object` | `x: object` | Accepts anything, but no attribute access |
| `Any` | `x: Any` | Escapes type checking entirely |

## Collection Types (3.10+)

| Type | Example | Notes |
|------|---------|-------|
| `list[int]` | `x: list[int] = [1, 2]` | Mutable sequence |
| `tuple[int, str]` | `x: tuple[int, str]` | Fixed length |
| `tuple[int, ...]` | `x: tuple[int, ...]` | Variable length |
| `dict[str, int]` | `x: dict[str, int]` | |
| `set[str]` | `x: set[str]` | |
| `frozenset[str]` | `x: frozenset[str]` | |

## Union and Optional

```python
# 3.10+ syntax
def f(x: int | str) -> None: ...
def g(x: int | None = None) -> None: ...

# Pre-3.10
from typing import Union, Optional
def f(x: Union[int, str]) -> None: ...
def g(x: Optional[int] = None) -> None: ...
```

## TypeAlias

```python
from typing import TypeAlias

# Explicit alias (3.10+)
Vector: TypeAlias = list[float]

# 3.12+ syntax
type Vector = list[float]
type Tree[T] = T | list["Tree[T]"]  # recursive
```

## Generics with TypeVar

```python
from typing import TypeVar

T = TypeVar("T")
K = TypeVar("K", bound=str)          # upper bound
N = TypeVar("N", int, float)         # constrained

def first(items: list[T]) -> T:
    return items[0]

# 3.12+ syntax (no TypeVar needed)
def first[T](items: list[T]) -> T:
    return items[0]
```

## ParamSpec and Concatenate

```python
from typing import ParamSpec, Concatenate, Callable

P = ParamSpec("P")
T = TypeVar("T")

# Preserve function signatures through decorators
def logged(fn: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        print(f"Calling {fn.__name__}")
        return fn(*args, **kwargs)
    return wrapper

# Add a parameter to a function signature
def with_user(
    fn: Callable[Concatenate[User, P], T]
) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        return fn(get_current_user(), *args, **kwargs)
    return wrapper
```

## Protocol (Structural Typing)

```python
from typing import Protocol, runtime_checkable

class Renderable(Protocol):
    def render(self) -> str: ...

class Widget(Protocol):
    name: str
    def resize(self, width: int, height: int) -> None: ...

# Any class with matching methods satisfies the protocol
class Button:
    def render(self) -> str:
        return "<button/>"

def draw(item: Renderable) -> None:  # Button works here
    print(item.render())

# Runtime checking
@runtime_checkable
class Sized(Protocol):
    def __len__(self) -> int: ...

assert isinstance([1, 2], Sized)  # True at runtime
```

## @overload

```python
from typing import overload

@overload
def parse(data: str) -> dict[str, Any]: ...
@overload
def parse(data: bytes) -> list[int]: ...
@overload
def parse(data: str, raw: Literal[True]) -> str: ...

def parse(data: str | bytes, raw: bool = False) -> dict | list | str:
    """Implementation handles all overloads."""
    ...
```

## TypeGuard and TypeIs

```python
from typing import TypeGuard, TypeIs  # TypeIs: 3.13+

# TypeGuard: narrows type in True branch only
def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)

# TypeIs: narrows in both True and False branches
def is_int(val: int | str) -> TypeIs[int]:
    return isinstance(val, int)

def f(val: int | str) -> None:
    if is_int(val):
        reveal_type(val)  # int
    else:
        reveal_type(val)  # str (only with TypeIs)
```

## Literal and Final

```python
from typing import Literal, Final

def set_mode(mode: Literal["read", "write", "append"]) -> None: ...

MAX_SIZE: Final = 100          # Cannot be reassigned
PREFIX: Final[str] = "app_"   # With explicit type
```

## Callable

| Signature | Meaning |
|-----------|---------|
| `Callable[[int, str], bool]` | Function taking int and str, returning bool |
| `Callable[..., bool]` | Any args, returning bool |
| `Callable[P, T]` | Generic (use with ParamSpec) |

## TypedDict

```python
from typing import TypedDict, NotRequired, Required

class Config(TypedDict):
    name: str
    debug: NotRequired[bool]         # optional key

class PartialConfig(TypedDict, total=False):
    name: Required[str]              # required even though total=False
    debug: bool                      # optional
```

## Common Patterns

| Pattern | Type Hint |
|---------|-----------|
| JSON value | `dict[str, Any]` or custom TypedDict |
| Decorator preserving sig | `Callable[P, T] -> Callable[P, T]` |
| Context manager | `AbstractContextManager[T]` |
| Async context manager | `AbstractAsyncContextManager[T]` |
| Generator | `Generator[YieldType, SendType, ReturnType]` |
| Async generator | `AsyncGenerator[YieldType, SendType]` |
| Class method returning self | `-> Self` (3.11+, `from typing import Self`) |
| Numeric tower | `int | float` (avoid `numbers.Number`) |

## Type Narrowing Cheat Sheet

| Technique | Example |
|-----------|---------|
| `isinstance` | `if isinstance(x, str):` |
| `is None` / `is not None` | `if x is not None:` |
| `TypeGuard` / `TypeIs` | Custom narrowing functions |
| `assert` | `assert isinstance(x, str)` |
| `Literal` checks | `if x == "read":` |
| `hasattr` | `if hasattr(x, "render"):` (limited) |
