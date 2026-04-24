---
name: performance-optimization
argument-hint: "[file or function]"
description: >
  Use when analyzing or optimizing code performance — including profiling, benchmarking, fixing N+1 queries, reducing bundle size, eliminating memory leaks, or improving algorithm complexity. Trigger for keywords like "slow", "performance", "optimize", "profiling", "memory leak", "bundle size", "N+1", "re-render", "benchmark", "latency", "throughput", or any request to make code faster. Also activate when investigating production performance issues or when code review flags performance concerns.
---

# Performance Optimization

## When to Use

- Profiling slow code to find bottlenecks
- Fixing N+1 query problems
- Reducing JavaScript bundle size
- Eliminating memory leaks
- Improving algorithm complexity
- Benchmarking before/after optimization
- Investigating production latency issues

## When NOT to Use

- Premature optimization — profile first, optimize second
- Caching strategy design — use `caching`
- Database schema/index design — use `databases`
- Code structure improvement — use `refactoring`

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| Profiling tools | `references/profiling.md` | Python (cProfile, py-spy, Scalene) and JS/TS (DevTools, Lighthouse, clinic.js) |
| Anti-patterns | `references/anti-patterns.md` | N+1 queries, unnecessary re-renders, event loop blocking, memory leaks |

---

## Optimization Workflow

1. **Measure first** — profile to find the actual bottleneck
2. **Set a target** — "reduce p95 latency from 500ms to 100ms"
3. **Optimize the hot path** — fix the #1 bottleneck, not everything
4. **Benchmark before/after** — prove the improvement with numbers
5. **Check for regressions** — ensure correctness wasn't sacrificed

---

## Profiling Quick Start

### Python

```bash
# CPU profiling
python -m cProfile -o output.prof script.py
# Visualize: pip install snakeviz && snakeviz output.prof

# Live profiling (attach to running process)
py-spy top --pid 12345

# Line-by-line profiling
kernprof -lv script.py  # requires @profile decorator
```

### JavaScript/TypeScript

```bash
# Bundle analysis
npx webpack-bundle-analyzer stats.json
# or: ANALYZE=true next build

# Node.js profiling
node --prof app.js
clinic doctor -- node app.js

# Benchmarking
npx vitest bench
```

---

## Common Anti-Patterns

| Anti-Pattern | Detection | Fix |
|-------------|-----------|-----|
| N+1 queries | `django-debug-toolbar`, `prisma.$on('query')` | `select_related`/`joinedload`/`include` |
| Unnecessary re-renders | React DevTools Profiler | `useMemo`, `useCallback`, `React.memo` |
| Blocking event loop | `clinic doctor`, high event loop lag | `worker_threads`, async variants |
| Memory leaks | Heap snapshots, growing `process.memoryUsage()` | Remove listeners, clear refs, bound caches |
| Unbounded lists | No pagination, full table scans | Cursor pagination, `LIMIT` |
| Heavy imports | Bundle analyzer showing large deps | Tree-shaking, `import { x }`, code splitting |

---

## Best Practices

1. **Profile before optimizing** — intuition about bottlenecks is often wrong.
2. **Optimize the hot path** — 80% of time is spent in 20% of code.
3. **Measure, don't guess** — use benchmarks with statistical significance.
4. **Set clear targets** — "faster" is not measurable; "p95 < 100ms" is.
5. **Avoid premature optimization** — correctness and readability come first.

## Common Pitfalls

1. **Optimizing cold paths** — spending time on code that runs once.
2. **Micro-benchmarking without context** — 10ns vs 20ns doesn't matter if the DB call takes 50ms.
3. **Sacrificing readability** — an unreadable optimization is a future bug.
4. **Caching without invalidation** — stale data is worse than slow data.
5. **Ignoring algorithmic complexity** — no amount of micro-optimization fixes O(n^2) on large inputs.

---

## Related Skills

- `systematic-debugging` — Investigating slow paths with root-cause rigor
- `testing` — Benchmarking and perf regression tests
- `devops` — Deploy-time perf checks
