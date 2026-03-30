---
name: react
description: >
  Use this skill when building React components, using React hooks, or managing component state. Trigger for any mention of React, JSX, TSX, useState, useEffect, useCallback, useMemo, useContext, custom hooks, or React component patterns. Also applies when implementing context providers, handling component lifecycle, optimizing re-renders, or structuring React application architecture.
---

# React

## When to Use

- Building React components
- Using React hooks
- Component state management
- Client-side interactivity in any React-based framework

## When NOT to Use

- Vue, Svelte, or Angular projects — this skill is React-specific
- Backend-only projects without a frontend UI layer
- Static HTML pages that do not require a JavaScript framework

---

## Core Patterns

### 1. Hooks

#### When-to-use guide

| Hook | Use when you need | Do NOT use for |
|------|-------------------|----------------|
| `useState` | Simple local state (toggle, form input, counter) | Derived/computed values |
| `useEffect` | Side effects: subscriptions, DOM mutations, timers | Data transformation (use useMemo) |
| `useRef` | Mutable value that persists across renders without triggering re-render; DOM refs | State that should cause re-render |
| `useMemo` | Expensive computation that should only rerun when deps change | Simple/cheap calculations |
| `useCallback` | Stable function reference to prevent child re-renders | Every function (only when needed) |
| `useReducer` | Complex state with multiple sub-values or state transitions | Simple boolean/string state |
| `useContext` | Reading context values | Frequently changing global state (causes re-renders) |

#### useState

```tsx
// Simple state
const [count, setCount] = useState(0);
const [user, setUser] = useState<User | null>(null);

// Functional updates (when new state depends on previous)
setCount((prev) => prev + 1);

// Lazy initialization (expensive initial value)
const [data, setData] = useState(() => computeExpensiveDefault());
```

#### useEffect

```tsx
// Run on mount + cleanup on unmount
useEffect(() => {
  const controller = new AbortController();
  fetchData(controller.signal).then(setData);
  return () => controller.abort(); // Cleanup
}, []); // Empty deps = run once

// Run when dependency changes
useEffect(() => {
  const handler = () => setWidth(window.innerWidth);
  window.addEventListener("resize", handler);
  return () => window.removeEventListener("resize", handler);
}, []); // No deps needed — handler is stable

// Sync external system with state
useEffect(() => {
  document.title = `${count} items`;
}, [count]);
```

#### useRef

```tsx
// DOM reference
const inputRef = useRef<HTMLInputElement>(null);
const focusInput = () => inputRef.current?.focus();

// Mutable value (no re-render on change)
const renderCount = useRef(0);
useEffect(() => {
  renderCount.current += 1;
});

// Previous value pattern
const prevValueRef = useRef(value);
useEffect(() => {
  prevValueRef.current = value;
}, [value]);
```

#### useReducer

```tsx
interface State {
  items: Item[];
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: "FETCH_START" }
  | { type: "FETCH_SUCCESS"; payload: Item[] }
  | { type: "FETCH_ERROR"; error: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "FETCH_START":
      return { ...state, loading: true, error: null };
    case "FETCH_SUCCESS":
      return { items: action.payload, loading: false, error: null };
    case "FETCH_ERROR":
      return { ...state, loading: false, error: action.error };
  }
}

const [state, dispatch] = useReducer(reducer, {
  items: [],
  loading: false,
  error: null,
});

// Dispatch actions
dispatch({ type: "FETCH_START" });
```

### 2. Custom Hooks

#### Extraction pattern

Extract a custom hook when:
- Two or more components share the same stateful logic
- A component's hook logic is complex enough to deserve its own name and tests
- You want to abstract away an external API (localStorage, WebSocket, etc.)

**Rules:**
- Name must start with `use`
- Can call other hooks (unlike regular functions)
- Each call gets its own independent state

#### Practical examples

```tsx
// useLocalStorage — persist state to localStorage
function useLocalStorage<T>(key: string, initialValue: T) {
  const [stored, setStored] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback(
    (value: T | ((prev: T) => T)) => {
      setStored((prev) => {
        const next = value instanceof Function ? value(prev) : value;
        window.localStorage.setItem(key, JSON.stringify(next));
        return next;
      });
    },
    [key],
  );

  return [stored, setValue] as const;
}

// Usage
const [theme, setTheme] = useLocalStorage("theme", "light");
```

```tsx
// useDebounce — debounce a rapidly changing value
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

```tsx
// useFetch — generic data fetching hook
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetch(url, { signal: controller.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((json) => setData(json as T))
      .catch((err) => {
        if (err.name !== "AbortError") setError(err);
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [url]);

  return { data, error, loading };
}

// Usage
const { data: users, loading, error } = useFetch<User[]>("/api/users");
```

### 3. Component Patterns

#### Compound components

```tsx
// Components that work together, sharing implicit state
interface TabsContextType {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}
const TabsContext = createContext<TabsContextType | null>(null);

function Tabs({ defaultTab, children }: { defaultTab: string; children: ReactNode }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div role="tablist">{children}</div>
    </TabsContext.Provider>
  );
}

function TabTrigger({ value, children }: { value: string; children: ReactNode }) {
  const ctx = useContext(TabsContext)!;
  return (
    <button
      role="tab"
      aria-selected={ctx.activeTab === value}
      onClick={() => ctx.setActiveTab(value)}
    >
      {children}
    </button>
  );
}

function TabContent({ value, children }: { value: string; children: ReactNode }) {
  const ctx = useContext(TabsContext)!;
  if (ctx.activeTab !== value) return null;
  return <div role="tabpanel">{children}</div>;
}

// Attach sub-components
Tabs.Trigger = TabTrigger;
Tabs.Content = TabContent;

// Usage
<Tabs defaultTab="settings">
  <Tabs.Trigger value="profile">Profile</Tabs.Trigger>
  <Tabs.Trigger value="settings">Settings</Tabs.Trigger>
  <Tabs.Content value="profile"><ProfileForm /></Tabs.Content>
  <Tabs.Content value="settings"><SettingsForm /></Tabs.Content>
</Tabs>
```

#### Render props

```tsx
interface MousePosition {
  x: number;
  y: number;
}

function MouseTracker({ render }: { render: (pos: MousePosition) => ReactNode }) {
  const [pos, setPos] = useState<MousePosition>({ x: 0, y: 0 });

  useEffect(() => {
    const handler = (e: MouseEvent) => setPos({ x: e.clientX, y: e.clientY });
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }, []);

  return <>{render(pos)}</>;
}

// Usage
<MouseTracker render={({ x, y }) => <span>Mouse: {x}, {y}</span>} />
```

#### Controlled vs uncontrolled

```tsx
// Controlled — parent owns the state
interface ControlledInputProps {
  value: string;
  onChange: (value: string) => void;
}

function ControlledInput({ value, onChange }: ControlledInputProps) {
  return <input value={value} onChange={(e) => onChange(e.target.value)} />;
}

// Uncontrolled — component owns the state, parent reads via ref or callback
function UncontrolledInput({ defaultValue }: { defaultValue?: string }) {
  const ref = useRef<HTMLInputElement>(null);
  return <input ref={ref} defaultValue={defaultValue} />;
}

// Flexible pattern — supports both controlled and uncontrolled
function FlexibleInput({
  value: controlledValue,
  defaultValue = "",
  onChange,
}: {
  value?: string;
  defaultValue?: string;
  onChange?: (value: string) => void;
}) {
  const [internalValue, setInternalValue] = useState(defaultValue);
  const isControlled = controlledValue !== undefined;
  const value = isControlled ? controlledValue : internalValue;

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (!isControlled) setInternalValue(e.target.value);
    onChange?.(e.target.value);
  }

  return <input value={value} onChange={handleChange} />;
}
```

### 4. Context

#### Provider pattern with separate state and dispatch

```tsx
// Split context to prevent unnecessary re-renders
interface AppState {
  user: User | null;
  theme: "light" | "dark";
}

type AppAction =
  | { type: "SET_USER"; user: User | null }
  | { type: "TOGGLE_THEME" };

const AppStateContext = createContext<AppState | null>(null);
const AppDispatchContext = createContext<React.Dispatch<AppAction> | null>(null);

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case "SET_USER":
      return { ...state, user: action.user };
    case "TOGGLE_THEME":
      return { ...state, theme: state.theme === "light" ? "dark" : "light" };
  }
}

function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, {
    user: null,
    theme: "light",
  });

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
}

// Typed hooks for consumers
function useAppState() {
  const ctx = useContext(AppStateContext);
  if (!ctx) throw new Error("useAppState must be used within AppProvider");
  return ctx;
}

function useAppDispatch() {
  const ctx = useContext(AppDispatchContext);
  if (!ctx) throw new Error("useAppDispatch must be used within AppProvider");
  return ctx;
}
```

**Why split?** Components that only dispatch actions (buttons) do not re-render when state changes. Only components that read state re-render.

#### Context splitting for performance

```tsx
// Instead of one giant context with everything:
const UserContext = createContext<User | null>(null);
const ThemeContext = createContext<"light" | "dark">("light");
const NotificationContext = createContext<Notification[]>([]);

// Components subscribe only to the context they need
function Avatar() {
  const user = useContext(UserContext); // Only re-renders when user changes
  return <img src={user?.avatar} />;
}
```

### 5. Error Boundaries

#### Class-based error boundary

```tsx
class ErrorBoundary extends React.Component<
  { children: ReactNode; fallback: ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: ReactNode; fallback: ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("Error boundary caught:", error, info.componentStack);
    // Send to error tracking service
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}
```

#### react-error-boundary library (recommended)

```tsx
import { ErrorBoundary, useErrorBoundary } from "react-error-boundary";

function ErrorFallback({
  error,
  resetErrorBoundary,
}: {
  error: Error;
  resetErrorBoundary: () => void;
}) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

// Usage
<ErrorBoundary
  FallbackComponent={ErrorFallback}
  onReset={() => {
    // Reset app state if needed
  }}
  resetKeys={[userId]} // Auto-reset when these values change
>
  <Dashboard />
</ErrorBoundary>

// Programmatic error throwing from child
function SaveButton() {
  const { showBoundary } = useErrorBoundary();

  async function handleSave() {
    try {
      await saveData();
    } catch (error) {
      showBoundary(error); // Propagate to nearest ErrorBoundary
    }
  }

  return <button onClick={handleSave}>Save</button>;
}
```

### 6. Suspense

#### Suspense boundaries with lazy loading

```tsx
import { Suspense, lazy } from "react";

// Code-split heavy components
const HeavyChart = lazy(() => import("./heavy-chart"));
const AdminPanel = lazy(() => import("./admin-panel"));

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <Suspense fallback={<ChartSkeleton />}>
        <HeavyChart />
      </Suspense>
      <Suspense fallback={<div>Loading admin panel...</div>}>
        <AdminPanel />
      </Suspense>
    </div>
  );
}
```

#### Suspense with data fetching (React 19+ / framework integration)

```tsx
// With a Suspense-compatible data source (React Query, Next.js, Relay)
function ProjectList() {
  return (
    <Suspense fallback={<ProjectListSkeleton />}>
      <ProjectListContent />
    </Suspense>
  );
}

// The data-fetching component suspends while loading
function ProjectListContent() {
  const { data } = useSuspenseQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });

  return (
    <ul>
      {data.map((p) => (
        <li key={p.id}>{p.title}</li>
      ))}
    </ul>
  );
}
```

#### Named exports with lazy

```tsx
// For named exports, wrap in a default export adapter
const UserSettings = lazy(() =>
  import("./user-settings").then((mod) => ({ default: mod.UserSettings })),
);
```

### 7. Performance

#### React.memo

```tsx
// Only re-renders when props change (shallow comparison)
const ExpensiveList = React.memo(function ExpensiveList({
  items,
  onSelect,
}: {
  items: Item[];
  onSelect: (item: Item) => void;
}) {
  return (
    <ul>
      {items.map((item) => (
        <li key={item.id} onClick={() => onSelect(item)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
});

// Custom comparison
const Chart = React.memo(ChartComponent, (prev, next) => {
  return prev.data.length === next.data.length && prev.title === next.title;
});
```

#### useMemo and useCallback together

```tsx
function ParentComponent({ items }: { items: Item[] }) {
  // Memoize expensive derived data
  const sortedItems = useMemo(
    () => [...items].sort((a, b) => a.name.localeCompare(b.name)),
    [items],
  );

  // Stable function reference for memoized child
  const handleSelect = useCallback((item: Item) => {
    console.log("Selected:", item.id);
  }, []);

  // ExpensiveList only re-renders when sortedItems or handleSelect change
  return <ExpensiveList items={sortedItems} onSelect={handleSelect} />;
}
```

#### Key prop optimization

```tsx
// BAD: using index as key — breaks state when list order changes
{items.map((item, index) => <Item key={index} data={item} />)}

// GOOD: stable unique key
{items.map((item) => <Item key={item.id} data={item} />)}

// Force remount: change key to reset component state
<ProfileForm key={userId} userId={userId} />
// When userId changes, the form unmounts and remounts with fresh state
```

#### Virtualization for large lists

```tsx
import { useVirtualizer } from "@tanstack/react-virtual";

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Estimated row height in px
    overscan: 5,            // Extra rows rendered above/below viewport
  });

  return (
    <div ref={parentRef} style={{ height: "400px", overflow: "auto" }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: "relative" }}>
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: "absolute",
              top: 0,
              transform: `translateY(${virtualRow.start}px)`,
              height: `${virtualRow.size}px`,
              width: "100%",
            }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Best Practices

1. **Keep components small and single-purpose** — if a component exceeds ~100 lines or handles multiple concerns, extract sub-components or custom hooks. Name components after what they render, not what they do.

2. **Use TypeScript interfaces for all props** — define explicit prop types. Avoid `any`. Use discriminated unions for props that change based on a variant. Export prop types for reuse.

3. **Clean up all effects** — return a cleanup function from every `useEffect` that subscribes to events, starts timers, or creates abort controllers. Missing cleanups cause memory leaks and stale state bugs.

4. **Derive state instead of syncing it** — if a value can be computed from props or other state, compute it during render (or with `useMemo`). Never `useEffect` to sync derived state — it causes an extra render.

5. **Lift state to the lowest common ancestor** — not higher. State should live in the closest parent that needs it. If siblings need shared state, lift to their parent. If distant components need it, use context.

6. **Use `useCallback` and `React.memo` together, not alone** — `useCallback` only helps when the function is passed to a memoized child. `React.memo` only helps when the parent actually passes stable props. Using one without the other is wasted effort.

7. **Prefer composition over prop drilling** — instead of passing props through 5 levels, restructure so the parent renders the child directly (component composition) or use context for truly global state.

8. **Handle all async states** — every data-fetching component should handle loading, error, and empty states. Use Suspense and Error Boundaries for declarative handling. Never leave a component that shows nothing while loading.

---

## Common Pitfalls

1. **Missing or wrong dependency arrays** — forgetting to add a dependency to `useEffect`/`useMemo`/`useCallback` causes stale closures. Adding too many causes unnecessary re-runs. Use the `react-hooks/exhaustive-deps` ESLint rule.

2. **Setting state during render** — calling `setState` unconditionally in the render body causes infinite re-render loops. State updates should be in event handlers, effects, or callbacks — never at the top level of the component function.

3. **Prop drilling through many layers** — passing a prop through 4+ intermediate components that do not use it. Fix with composition (restructuring the component tree), context (for shared state), or a state management library.

4. **Creating objects/arrays in JSX props** — `<Child style={{ color: "red" }} />` creates a new object every render, defeating `React.memo`. Hoist constants outside the component or use `useMemo`.

5. **Using `useEffect` for derived state** — syncing state with `useEffect(() => setFullName(first + last), [first, last])` causes double renders. Just compute it: `const fullName = first + last`. Use `useMemo` if the computation is expensive.

6. **Not handling race conditions in effects** — when a component fetches data based on a prop, fast prop changes can cause older responses to arrive after newer ones, displaying stale data. Use `AbortController` or a boolean flag to ignore stale responses.

---

## Related Skills

- `frameworks/nextjs` — Next.js App Router, SSR, and full-stack React patterns
- `languages/typescript` — TypeScript strict mode and type patterns
- `frontend/tailwind` — Styling with Tailwind CSS
- `frontend/shadcn-ui` — UI component library built on Radix and Tailwind
- `testing/vitest` — Testing React components with vitest and testing-library
- `patterns/state-management` — State management patterns for React
