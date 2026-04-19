---
name: frontend
description: >
  Use when building React components, Next.js applications, or shadcn/ui interfaces — including hooks, useState, useEffect, useCallback, useMemo, Server Components, App Router, Server Actions, SSR, SSG, ISR, Radix primitives, cn() utility, next/navigation, or component architecture.
---

# Frontend

## When to Use

- Building React components, custom hooks, or managing component state
- Next.js App Router, Server Components, Server Actions, route handlers
- shadcn/ui components with Radix primitives and react-hook-form
- Client-side interactivity, context providers, or component composition
- SEO-critical sites needing SSR/SSG/ISR

## When NOT to Use

- Styling and accessibility — use `frontend-styling`
- Backend API development — use `backend-frameworks`
- State management architecture decisions — use `state-management`

---

## Quick Reference

| Topic | Reference | Key features |
|-------|-----------|-------------|
| React | `references/react.md` | Hooks, memo, context, composition, effect cleanup, custom hooks |
| Next.js | `references/nextjs.md` | App Router, Server Components, Server Actions, loading.tsx, middleware |
| shadcn/ui | `references/shadcn-ui.md` | Radix primitives, cn(), asChild, CSS variables, Zod forms |

---

## Best Practices

1. **Keep components small and single-purpose** (~100 lines max).
2. **Use TypeScript interfaces for all props.** Avoid `any`.
3. **Clean up all effects.** Return cleanup from every `useEffect` that subscribes to events or starts timers.
4. **Derive state instead of syncing it.** Compute from props/state during render or with `useMemo`.
5. **Default to Server Components** — only add `"use client"` when you need interactivity (Next.js).
6. **Colocate data fetching with the component that uses it** (Next.js).
7. **Use `loading.tsx` for instant loading states** (Next.js).
8. **Validate Server Action inputs** — Server Actions are public HTTP endpoints (Next.js).
9. **Install shadcn/ui components individually** — only add what you need.
10. **Use `cn()` for all conditional styling** (shadcn/ui).
11. **Keep forms type-safe end to end** — Zod schema + inferred type + `useForm<T>` (shadcn/ui).

## Common Pitfalls

1. **Missing or wrong dependency arrays** in hooks.
2. **Setting state during render** — causes infinite loops.
3. **Using `useEffect` for derived state** — causes double renders; compute inline instead.
4. **Using hooks in Server Components** (Next.js).
5. **Large client bundles from misplaced `"use client"`** (Next.js).
6. **Stale data from aggressive caching** (Next.js).
7. **Forgetting `"use client"` for shadcn/ui components in Next.js App Router.**
8. **Hardcoded colors instead of CSS variables** (shadcn/ui).

---

## Related Skills

- `frontend-styling` — Tailwind CSS and accessibility
- `state-management` — State architecture decisions
- `error-handling` — Error boundaries in React
