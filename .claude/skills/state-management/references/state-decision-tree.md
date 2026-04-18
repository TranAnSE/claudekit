# State Management Decision Tree

## Primary Decision Tree

```
What kind of state is it?
│
├─ SERVER DATA (fetched from API/DB)
│  │
│  ├─ React/Next.js project?
│  │  ├─ YES ──> TanStack Query (React Query)
│  │  │         - Auto caching, dedup, background refresh
│  │  │         - Stale-while-revalidate out of the box
│  │  │         - DevTools for debugging
│  │  │
│  │  └─ Next.js App Router with Server Components?
│  │     └─ Consider: fetch() in Server Components + revalidation
│  │        - No client-side state library needed
│  │        - Use TanStack Query only for client-interactive data
│  │
│  └─ Need real-time sync?
│     ├─ WebSocket data ──> TanStack Query + custom subscription
│     └─ Collaborative ──> Liveblocks, Yjs, or Partykit
│
├─ URL STATE (filters, pagination, search, tabs)
│  │
│  ├─ Next.js App Router ──> useSearchParams() + useRouter()
│  ├─ React Router ──> useSearchParams()
│  └─ Plain React ──> nuqs or custom URL sync hook
│
│  Why URL state? Shareable links, back/forward navigation,
│  bookmarkable, SSR-friendly.
│
├─ FORM STATE (input values, validation, dirty/touched)
│  │
│  ├─ Complex forms (multi-step, dynamic fields, arrays)
│  │  └─ react-hook-form + zod
│  │     - Uncontrolled by default (performant)
│  │     - Schema validation with zod resolver
│  │
│  ├─ Simple forms (login, search, contact)
│  │  └─ Server Actions (Next.js) or native form + useState
│  │
│  └─ Form + server state (edit existing record)
│     └─ TanStack Query (fetch) + react-hook-form (edit)
│        - Populate form with query data
│        - Submit with mutation
│
├─ GLOBAL CLIENT STATE (shared across many components)
│  │
│  ├─ Simple (theme, sidebar open, user preferences)
│  │  │
│  │  ├─ Changes rarely ──> React Context
│  │  │  (Wrap app, useContext to consume)
│  │  │
│  │  └─ Changes often or many consumers ──> Zustand
│  │     - Avoids Context re-render problem
│  │     - Selector-based subscriptions
│  │     - Tiny bundle, minimal boilerplate
│  │
│  ├─ Complex (shopping cart, multi-step wizard, editor)
│  │  └─ Zustand (or Jotai for atomic state)
│  │
│  └─ Need devtools and time-travel debugging?
│     └─ Zustand with devtools middleware
│
├─ LOCAL COMPONENT STATE (only used in one component)
│  │
│  ├─ Single value ──> useState
│  │  const [count, setCount] = useState(0);
│  │
│  ├─ Related values or complex transitions ──> useReducer
│  │  const [state, dispatch] = useReducer(reducer, initial);
│  │
│  └─ Derived value (computed from other state) ──> useMemo
│     const total = useMemo(() => items.reduce(...), [items]);
│
└─ TRANSIENT UI STATE (animations, hover, drag position)
   │
   ├─ CSS can handle it? ──> Use CSS (transitions, :hover)
   ├─ Ref-based (no re-render needed) ──> useRef
   └─ Needs re-render ──> useState (local)
```

## Quick Lookup Table

| State Type | Recommended Tool | When NOT to Use |
|-----------|-----------------|-----------------|
| Server data | TanStack Query | Data never changes, or SSR-only |
| URL params | useSearchParams | Ephemeral UI state (hover, etc.) |
| Form inputs | react-hook-form | Single `<input>` |
| Global UI | Zustand | Only 1-2 consumers (use Context) |
| Global UI (simple) | React Context | Frequent updates with many consumers |
| Local state | useState | Complex state transitions |
| Complex local | useReducer | Single boolean toggle |
| Derived data | useMemo | Cheap computations |
| No re-render needed | useRef | Value that should trigger re-render |

## Library Comparison

| Library | Bundle Size | Boilerplate | Learning Curve | Best For |
|---------|------------|-------------|----------------|----------|
| useState/useReducer | 0 KB | Minimal | Low | Local state |
| React Context | 0 KB | Low | Low | Rarely-changing global state |
| Zustand | ~1 KB | Minimal | Low | Global client state |
| Jotai | ~3 KB | Minimal | Medium | Atomic/derived state |
| TanStack Query | ~12 KB | Medium | Medium | Server state |
| Redux Toolkit | ~30 KB | High | High | Large teams needing strict patterns |

## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Storing server data in Zustand/Redux | Manual cache invalidation, stale data | Use TanStack Query |
| Storing URL state in useState | Not shareable, lost on refresh | Use URL search params |
| Putting everything in global state | Unnecessary re-renders, complexity | Colocate state where used |
| Context for frequently changing data | Re-renders all consumers | Use Zustand with selectors |
| Duplicating derived state | Out-of-sync bugs | Compute with useMemo |
| useState for complex transitions | Inconsistent intermediate states | Use useReducer |

## Zustand Quick Setup

```typescript
import { create } from "zustand";

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  total: () => number;
}

const useCartStore = create<CartStore>((set, get) => ({
  items: [],
  addItem: (item) => set((s) => ({ items: [...s.items, item] })),
  removeItem: (id) => set((s) => ({ items: s.items.filter(i => i.id !== id) })),
  total: () => get().items.reduce((sum, i) => sum + i.price, 0),
}));

// Usage with selector (only re-renders when items change)
const items = useCartStore((s) => s.items);
const addItem = useCartStore((s) => s.addItem);
```
