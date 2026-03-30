# React Patterns Quick Reference

## Hook Rules

1. Only call hooks at the **top level** (not inside loops, conditions, or nested functions)
2. Only call hooks from **React function components** or **custom hooks**
3. Custom hooks **must** start with `use`
4. Hook call order must be **identical** on every render

```typescript
// BAD
if (isLoggedIn) {
  const [user, setUser] = useState(null); // Conditional hook call
}

// GOOD
const [user, setUser] = useState(null);
// Use the state conditionally instead
```

---

## Custom Hook Recipes

### useLocalStorage

```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// Usage
const [theme, setTheme] = useLocalStorage("theme", "dark");
```

### useDebounce

```typescript
function useDebounce<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}

// Usage
const [search, setSearch] = useState("");
const debouncedSearch = useDebounce(search, 300);

useEffect(() => {
  fetchResults(debouncedSearch);
}, [debouncedSearch]);
```

### useMediaQuery

```typescript
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(
    () => window.matchMedia(query).matches
  );

  useEffect(() => {
    const mql = window.matchMedia(query);
    const handler = (e: MediaQueryListEvent) => setMatches(e.matches);
    mql.addEventListener("change", handler);
    return () => mql.removeEventListener("change", handler);
  }, [query]);

  return matches;
}

// Usage
const isMobile = useMediaQuery("(max-width: 768px)");
```

### usePrevious

```typescript
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T | undefined>(undefined);

  useEffect(() => {
    ref.current = value;
  });

  return ref.current;
}

// Usage
const prevCount = usePrevious(count);
```

---

## Compound Component Pattern

```typescript
// Components that work together sharing implicit state
const Accordion = ({ children }: { children: React.ReactNode }) => {
  const [openIndex, setOpenIndex] = useState<number | null>(null);
  return (
    <AccordionContext.Provider value={{ openIndex, setOpenIndex }}>
      <div role="tablist">{children}</div>
    </AccordionContext.Provider>
  );
};

const AccordionItem = ({ index, title, children }: {
  index: number; title: string; children: React.ReactNode;
}) => {
  const { openIndex, setOpenIndex } = useContext(AccordionContext);
  const isOpen = openIndex === index;
  return (
    <div>
      <button onClick={() => setOpenIndex(isOpen ? null : index)}>
        {title}
      </button>
      {isOpen && <div>{children}</div>}
    </div>
  );
};

Accordion.Item = AccordionItem;

// Usage - clean, declarative API
<Accordion>
  <Accordion.Item index={0} title="Section 1">Content 1</Accordion.Item>
  <Accordion.Item index={1} title="Section 2">Content 2</Accordion.Item>
</Accordion>
```

---

## Context Patterns

### Split State and Dispatch

```typescript
// Prevent unnecessary re-renders by splitting contexts
const StateContext = createContext<State | null>(null);
const DispatchContext = createContext<Dispatch | null>(null);

function Provider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <DispatchContext.Provider value={dispatch}>
      <StateContext.Provider value={state}>
        {children}
      </StateContext.Provider>
    </DispatchContext.Provider>
  );
}

// Components that only dispatch won't re-render on state changes
function useAppDispatch() {
  const ctx = useContext(DispatchContext);
  if (!ctx) throw new Error("Must be used within Provider");
  return ctx;
}
```

---

## Performance Checklist

### When to Memoize

| Situation | Solution |
|-----------|----------|
| Expensive computation | `useMemo(() => compute(data), [data])` |
| Stable callback for child | `useCallback(fn, [deps])` |
| Prevent child re-render | `React.memo(Component)` |
| Stable object/array prop | `useMemo(() => ({ ... }), [deps])` |

### When NOT to Memoize

- Simple/cheap calculations
- Primitives (strings, numbers, booleans) -- already stable
- Functions only used in the same component
- Components that are cheap to render

### Key Optimizations

```typescript
// 1. Move state down (colocate state with where it's used)
// BAD: parent re-renders everything
function Parent() {
  const [hover, setHover] = useState(false);
  return <><ExpensiveChild /><HoverTarget onHover={setHover} /></>;
}

// GOOD: isolate the stateful part
function Parent() {
  return <><ExpensiveChild /><HoverSection /></>;
}
function HoverSection() {
  const [hover, setHover] = useState(false);
  return <HoverTarget onHover={setHover} />;
}

// 2. Pass children to avoid re-rendering them
function ScrollTracker({ children }: { children: React.ReactNode }) {
  const [scroll, setScroll] = useState(0);
  // children are created by parent, not re-created on scroll change
  return <div onScroll={e => setScroll(e.currentTarget.scrollTop)}>{children}</div>;
}

// 3. Use key to reset component state
<Form key={selectedId} initialData={data} />

// 4. Lazy load heavy components
const HeavyChart = lazy(() => import("./HeavyChart"));
<Suspense fallback={<Skeleton />}>
  <HeavyChart data={data} />
</Suspense>
```

### React DevTools Profiler Checklist

1. Enable "Highlight updates" to spot unnecessary re-renders
2. Record a profiler session and look for:
   - Components re-rendering without visible changes
   - Long render times (>16ms blocks frames)
   - Cascading re-renders from context changes
3. Fix with: state colocation, memo, context splitting, or external state
