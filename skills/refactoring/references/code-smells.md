# Code Smells Detection Guide

## Smell → Refactoring Map

| Smell | Signal | Refactoring |
|-------|--------|-------------|
| Long function | >20-30 lines | Extract function |
| Long parameter list | >3-4 params | Introduce parameter object |
| Duplicated logic | Same code in 3+ places | Extract function, DRY |
| Deep nesting | >3 levels of indentation | Early return, extract function |
| Feature envy | Uses another class's data more than its own | Move method to the class with the data |
| Shotgun surgery | One change → edits in many files | Move related code together |
| Primitive obsession | Raw strings/dicts instead of types | Introduce dataclass/interface |
| Dead code | Unreachable or unused | Delete it (git has history) |
| God class | Class does too many things | Extract class by responsibility |
| Comments as deodorant | Comments explaining messy code | Refactor the code to be clear |

## Python-Specific Smells

- `dict` used as a struct → use `@dataclass` or `TypedDict`
- Missing type hints on public functions
- Manual `__init__` boilerplate → `@dataclass`
- String constants → `Enum`
- Getter/setter methods → `@property`

## TypeScript-Specific Smells

- `any` type → `unknown` + narrowing or generics
- Enum → `as const` object (better tree-shaking)
- Class hierarchy for variants → discriminated union
- Interface duplication → utility types (`Pick`, `Omit`, `Partial`)
- Index as key in lists → stable unique ID
