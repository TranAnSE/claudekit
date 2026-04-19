---
name: state-management
description: >
  Use when choosing between useState, useReducer, context, Zustand, Jotai, or TanStack Query. Also applies to server state, form state, URL state, and Python application state with dataclasses and Pydantic. Activate whenever someone asks about state architecture, global state, caching API responses, or managing complex form state.
---

# State Management

## When to Use

- Choosing between React state solutions (useState, useReducer, context, Zustand, Jotai)
- Managing server state with TanStack Query or SWR
- Complex form state with react-hook-form + Zod
- URL state for shareable/bookmarkable UI state
- Python domain models with dataclasses or Pydantic
- Global application state architecture decisions

## When NOT to Use

- Simple component state that doesn't leave the component — just use useState
- Backend data storage — use `databases`
- Caching strategies — use `caching`

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| All state patterns | `references/patterns.md` | useState, useReducer, context, Zustand, Jotai, TanStack Query, forms, URL state, Python state |
| Decision tree | `references/state-decision-tree.md` | When to use which state solution |

---

## Best Practices

1. **Start with useState.** Only reach for external state management when state needs to be shared across distant components.
2. **Separate server state from client state.** Use TanStack Query for server data (caching, refetching, optimistic updates). Use Zustand/Jotai for client-only UI state.
3. **Colocate state with its consumers.** State should live in the lowest common ancestor of components that use it.
4. **Derive state, don't sync it.** If a value can be computed from other state, compute it during render with useMemo. Don't useEffect to sync.
5. **Use URL state for shareable UI state.** Filters, sort order, pagination, and selected tabs belong in the URL.
6. **Use Zustand for medium complexity.** When context re-renders too much but Redux is overkill, Zustand's slices pattern scales well.
7. **Keep form state in react-hook-form.** Don't duplicate form state in Zustand/context. Let the form library own it.
8. **Use Pydantic for Python domain state.** Validation, serialization, and type safety in one package.

## Common Pitfalls

1. **Premature global state** — putting everything in a store when useState would suffice.
2. **Context causing unnecessary re-renders** — every consumer re-renders when any context value changes. Split contexts by update frequency.
3. **useEffect for derived state** — causes double renders. Compute inline instead.
4. **Stale closures in Zustand selectors** — use the selector pattern to avoid subscribing to the entire store.
5. **Duplicating server state in client stores** — TanStack Query already caches it. Don't copy to Zustand.
6. **Mutable default arguments in Python dataclasses** — use `field(default_factory=list)`.

---

## Related Skills

- `frontend` — React component patterns and hooks
- `caching` — Cache strategies for API responses
- `languages` — Python dataclass and Pydantic patterns
