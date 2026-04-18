---
name: languages
description: >
  Use when working with Python, TypeScript, or JavaScript language-specific patterns — including type hints, generics, async/await, dataclasses, Pydantic, PEP 8, strict mode, tsconfig.json, Zod schemas, ESM/CJS, destructuring, optional chaining, or language idioms.
---

# Languages

## When to Use

- Python files (.py) — type hints, async/await, dataclasses, Pydantic, context managers, PEP 8
- TypeScript files (.ts, .tsx) — strict mode, generics, utility types, Zod, discriminated unions
- JavaScript files (.js, .mjs, .cjs) — ES6+ patterns, ESM/CJS, ESLint, modern syntax
- Language-specific idioms, package management (pip, pnpm), or migration between languages

## When NOT to Use

- Framework-specific patterns — use `backend-frameworks` or `frontend`
- Testing — use `testing`
- Database queries — use `databases`

---

## Quick Reference

| Language | Reference | Key features |
|----------|-----------|-------------|
| Python | `references/python.md` | Type hints, dataclasses, Pydantic, asyncio, context managers, PEP 8 |
| TypeScript | `references/typescript.md` | Strict mode, generics, utility types, Zod, discriminated unions, satisfies |
| JavaScript | `references/javascript.md` | ES6+, async/await, ESM/CJS, destructuring, private fields, structuredClone |

---

## Best Practices

1. **Use type hints on all public functions** (Python) / **enable strict mode** (TypeScript).
2. **Prefer dataclasses or Pydantic for structured data** (Python) / **interfaces for object shapes** (TypeScript).
3. **Use context managers for resource management** (Python).
4. **Never use `any`** — use `unknown` instead (TypeScript).
5. **Use `const` by default, `let` when needed, never `var`** (JavaScript).
6. **Validate external data at boundaries** — Zod (TypeScript) or Pydantic (Python).
7. **Handle all promise rejections** (JavaScript/TypeScript).
8. **Follow PEP 8 / ESLint + Prettier** consistently.

## Common Pitfalls

1. **Mutable default arguments** (Python) — use `None` with default in function body.
2. **Blocking calls inside async functions** (Python) — use `asyncio`-compatible libraries.
3. **Overusing type assertions `as`** (TypeScript) — use type guards instead.
4. **Implicit type coercion** (JavaScript) — always use `===` and `!==`.
5. **Forgetting `await`** (all three languages).
6. **Circular imports** (Python) / **circular dependencies** (TypeScript).
7. **`this` binding in callbacks** (JavaScript) — use arrow functions.
8. **Using enums instead of const objects** (TypeScript).

---

## Related Skills

- `backend-frameworks` — Framework-specific patterns
- `testing` — Language-specific test frameworks
- `error-handling` — Exception handling patterns
