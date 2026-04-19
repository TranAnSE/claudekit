# Profiling Tools Reference

## Python

### cProfile (built-in, function-level)
```bash
python -m cProfile -o output.prof script.py
# Visualize
pip install snakeviz && snakeviz output.prof
```

### py-spy (sampling, production-safe)
```bash
# Top-like view of running process
py-spy top --pid 12345

# Generate flame graph
py-spy record -o profile.svg --pid 12345
```

### line_profiler (line-by-line)
```bash
# Add @profile decorator to target function
kernprof -lv script.py
```

### memory_profiler (memory usage)
```bash
# Add @profile decorator
python -m memory_profiler script.py

# Or use stdlib tracemalloc for snapshot comparison
```

### Scalene (CPU + memory + GPU)
```bash
scalene script.py
# Modern alternative, AI-suggested optimizations
```

## JavaScript / TypeScript

### Chrome DevTools Performance
- Performance tab → Record → interact → Stop
- Flame chart shows main thread activity
- Look for long tasks (>50ms), layout thrashing

### Lighthouse (web vitals)
```bash
npx lighthouse https://localhost:3000 --output=json
# CI integration
npx @lhci/cli autorun
```

### Bundle Analysis
```bash
# Webpack
npx webpack-bundle-analyzer stats.json

# Next.js
ANALYZE=true next build

# Source map explorer
npx source-map-explorer dist/**/*.js
```

### clinic.js (Node.js)
```bash
# Event loop health
clinic doctor -- node app.js

# CPU flame graph
clinic flame -- node app.js

# Async bottlenecks
clinic bubbleprof -- node app.js
```

### Node.js built-in
```bash
node --prof app.js
node --prof-process isolate-*.log > profile.txt
```

## Benchmarking

### Python
```bash
# pytest-benchmark
pytest --benchmark-only

# timeit
python -m timeit -s "setup" "expression"
```

### JavaScript/TypeScript
```typescript
// Vitest bench (built-in)
// my-func.bench.ts
import { bench } from 'vitest';

bench('my function', () => {
  myFunction(testData);
});
```

```bash
npx vitest bench
```
