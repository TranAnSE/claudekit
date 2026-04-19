# State Management — Patterns


# State Management Patterns

## When to Use

- Choosing between local, shared, or global state in a React application
- Setting up server state caching with TanStack Query or SWR
- Building forms with validation, arrays, and nested fields
- Syncing application state with URL search parameters
- Designing Python domain models with dataclasses or Pydantic
- Refactoring prop-drilling into a shared store
- Deciding whether to add a state management library or keep things simple

## When NOT to Use

- Static sites with no interactive state (pure content pages, docs)
- Server-only rendering with no client-side interactivity
- Simple CRUD backends where database is the only source of truth and there is no in-process state to manage

---

## Core Patterns

### 1. Local vs Global State Decision Tree

Before reaching for a library, walk through this decision tree.

```
Is the state used by a single component?
├── YES --> useState or useReducer
└── NO
    Is it shared by a parent and 1-2 direct children?
    ├── YES --> Lift state up to the common parent, pass via props
    └── NO
        Is it server data (fetched from an API)?
        ├── YES --> TanStack Query (useQuery / useMutation)
        └── NO
            Is it URL-representable (filters, pagination, tabs)?
            ├── YES --> URL state (useSearchParams / nuqs)
            └── NO
                Is it form data with validation?
                ├── YES --> react-hook-form + zod
                └── NO
                    Zustand store (or Jotai for atomic state)
```

**Rules of thumb:**

- Start with the simplest option. Only add a library when props become painful.
- Server state and client state are different concerns. Never put fetched API data in Zustand; use TanStack Query instead.
- URL state is free persistence. If the user should be able to bookmark or share the current view, put it in the URL.
- Form state belongs to the form library. Do not mirror react-hook-form values in a Zustand store.

---

### 2. React State Patterns

**useState for simple values**

```typescript
function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount((prev) => prev + 1)}>
      Count: {count}
    </button>
  );
}
```

**useReducer for complex state with multiple transitions**

```typescript
interface TimerState {
  status: "idle" | "running" | "paused";
  elapsed: number;
}

type TimerAction =
  | { type: "start" }
  | { type: "pause" }
  | { type: "reset" }
  | { type: "tick" };

function timerReducer(state: TimerState, action: TimerAction): TimerState {
  switch (action.type) {
    case "start":
      return { ...state, status: "running" };
    case "pause":
      return { ...state, status: "paused" };
    case "reset":
      return { status: "idle", elapsed: 0 };
    case "tick":
      return state.status === "running"
        ? { ...state, elapsed: state.elapsed + 1 }
        : state;
  }
}

function Timer() {
  const [state, dispatch] = useReducer(timerReducer, {
    status: "idle",
    elapsed: 0,
  });

  useEffect(() => {
    if (state.status !== "running") return;
    const id = setInterval(() => dispatch({ type: "tick" }), 1000);
    return () => clearInterval(id);
  }, [state.status]);

  return (
    <div>
      <p>{state.elapsed}s</p>
      {state.status !== "running" && (
        <button onClick={() => dispatch({ type: "start" })}>Start</button>
      )}
      {state.status === "running" && (
        <button onClick={() => dispatch({ type: "pause" })}>Pause</button>
      )}
      <button onClick={() => dispatch({ type: "reset" })}>Reset</button>
    </div>
  );
}
```

**When to pick which:**

| Criteria | useState | useReducer |
|----------|----------|------------|
| Single primitive value | Yes | Overkill |
| Multiple related fields | Possible | Preferred |
| Complex transitions | Messy | Clean |
| Needs testing in isolation | Hard | Easy (test the reducer) |

---

### 3. Global State (Zustand)

Zustand is lightweight, TypeScript-friendly, and avoids the boilerplate of Redux.

**Basic store**

```typescript
import { create } from "zustand";

interface AuthStore {
  user: User | null;
  token: string | null;
  login: (user: User, token: string) => void;
  logout: () => void;
}

const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  login: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null }),
}));

// In components - use selectors to avoid unnecessary re-renders
function UserMenu() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  if (!user) return <LoginButton />;
  return (
    <div>
      <span>{user.name}</span>
      <button onClick={logout}>Log out</button>
    </div>
  );
}
```

**Slices pattern for large stores**

```typescript
import { create, type StateCreator } from "zustand";
import { devtools, persist } from "zustand/middleware";

// Each slice is its own interface + creator
interface CartSlice {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
  clearCart: () => void;
}

interface UISlice {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
}

const createCartSlice: StateCreator<
  CartSlice & UISlice,
  [],
  [],
  CartSlice
> = (set) => ({
  items: [],
  addItem: (item) =>
    set((state) => ({ items: [...state.items, item] })),
  removeItem: (id) =>
    set((state) => ({ items: state.items.filter((i) => i.id !== id) })),
  clearCart: () => set({ items: [] }),
});

const createUISlice: StateCreator<
  CartSlice & UISlice,
  [],
  [],
  UISlice
> = (set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
});

// Combine slices with middleware
const useAppStore = create<CartSlice & UISlice>()(
  devtools(
    persist(
      (...args) => ({
        ...createCartSlice(...args),
        ...createUISlice(...args),
      }),
      {
        name: "app-store",
        partialize: (state) => ({ items: state.items }), // only persist cart
      }
    )
  )
);
```

**Zustand best practices:**

- Always use selectors (`useStore((s) => s.field)`) instead of the whole store.
- Keep stores small and focused. One store per domain, not one mega-store.
- Use `persist` middleware for state that should survive page reloads.
- Use `devtools` middleware in development for Redux DevTools integration.

---

### 4. Server State (TanStack Query)

Server state (data from APIs) has different needs than client state: caching, background refetching, deduplication, pagination.

**Basic query**

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";

// Query key conventions: [entity, ...params]
const userKeys = {
  all: ["users"] as const,
  list: (filters: UserFilters) => ["users", "list", filters] as const,
  detail: (id: string) => ["users", "detail", id] as const,
};

function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => api.users.get(id),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

function UserProfile({ id }: { id: string }) {
  const { data: user, isLoading, error } = useUser(id);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;

  return <div>{user.name}</div>;
}
```

**Mutations with optimistic updates**

```typescript
function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateUserInput) => api.users.update(data.id, data),
    onMutate: async (newData) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({
        queryKey: userKeys.detail(newData.id),
      });

      // Snapshot current value for rollback
      const previous = queryClient.getQueryData(userKeys.detail(newData.id));

      // Optimistically update
      queryClient.setQueryData(userKeys.detail(newData.id), (old: User) => ({
        ...old,
        ...newData,
      }));

      return { previous };
    },
    onError: (_err, newData, context) => {
      // Rollback on failure
      if (context?.previous) {
        queryClient.setQueryData(
          userKeys.detail(newData.id),
          context.previous
        );
      }
    },
    onSettled: (_data, _err, variables) => {
      // Always refetch after mutation to ensure consistency
      queryClient.invalidateQueries({
        queryKey: userKeys.detail(variables.id),
      });
    },
  });
}
```

**Prefetching for instant navigation**

```typescript
function UserListItem({ user }: { user: UserSummary }) {
  const queryClient = useQueryClient();

  const prefetch = () => {
    queryClient.prefetchQuery({
      queryKey: userKeys.detail(user.id),
      queryFn: () => api.users.get(user.id),
      staleTime: 60_000,
    });
  };

  return (
    <Link
      to={`/users/${user.id}`}
      onMouseEnter={prefetch}
      onFocus={prefetch}
    >
      {user.name}
    </Link>
  );
}
```

---

### 5. Form State

Use react-hook-form for performance (uncontrolled inputs) and zod for schema validation.

**Basic form with validation**

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const createUserSchema = z.object({
  name: z.string().min(1, "Name is required").max(100),
  email: z.string().email("Invalid email address"),
  role: z.enum(["admin", "editor", "viewer"]),
  notifications: z.boolean().default(true),
});

type CreateUserForm = z.infer<typeof createUserSchema>;

function CreateUserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateUserForm>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      role: "viewer",
      notifications: true,
    },
  });

  const onSubmit = async (data: CreateUserForm) => {
    await api.users.create(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="name">Name</label>
        <input id="name" {...register("name")} />
        {errors.name && <p className="text-red-500">{errors.name.message}</p>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input id="email" type="email" {...register("email")} />
        {errors.email && <p className="text-red-500">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="role">Role</label>
        <select id="role" {...register("role")}>
          <option value="viewer">Viewer</option>
          <option value="editor">Editor</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create User"}
      </button>
    </form>
  );
}
```

**Dynamic field arrays**

```typescript
import { useFieldArray } from "react-hook-form";

const orderSchema = z.object({
  customer: z.string().min(1),
  items: z
    .array(
      z.object({
        productId: z.string().min(1),
        quantity: z.number().int().min(1).max(999),
      })
    )
    .min(1, "At least one item is required"),
});

type OrderForm = z.infer<typeof orderSchema>;

function OrderForm() {
  const { register, control, handleSubmit } = useForm<OrderForm>({
    resolver: zodResolver(orderSchema),
    defaultValues: { items: [{ productId: "", quantity: 1 }] },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: "items",
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {fields.map((field, index) => (
        <div key={field.id} className="flex gap-2">
          <input
            {...register(`items.${index}.productId`)}
            placeholder="Product ID"
          />
          <input
            {...register(`items.${index}.quantity`, { valueAsNumber: true })}
            type="number"
            min={1}
          />
          <button type="button" onClick={() => remove(index)}>
            Remove
          </button>
        </div>
      ))}
      <button
        type="button"
        onClick={() => append({ productId: "", quantity: 1 })}
      >
        Add item
      </button>
      <button type="submit">Place order</button>
    </form>
  );
}
```

---

### 6. URL State

Encode filters, pagination, and view settings in the URL so users can bookmark and share.

**Using nuqs (type-safe URL search params)**

```typescript
import { useQueryState, parseAsInteger, parseAsStringEnum } from "nuqs";

const sortOptions = ["name", "date", "price"] as const;

function ProductList() {
  const [search, setSearch] = useQueryState("q", { defaultValue: "" });
  const [page, setPage] = useQueryState("page", parseAsInteger.withDefault(1));
  const [sort, setSort] = useQueryState(
    "sort",
    parseAsStringEnum(sortOptions).withDefault("name")
  );

  // URL looks like: /products?q=shoes&page=2&sort=price
  const { data } = useQuery({
    queryKey: ["products", { search, page, sort }],
    queryFn: () => api.products.list({ search, page, sort }),
  });

  return (
    <div>
      <input
        value={search}
        onChange={(e) => setSearch(e.target.value || null)}
        placeholder="Search products..."
      />
      <select
        value={sort}
        onChange={(e) => setSort(e.target.value as typeof sort)}
      >
        {sortOptions.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>

      <ProductGrid products={data?.items ?? []} />

      <Pagination
        page={page}
        total={data?.totalPages ?? 1}
        onChange={setPage}
      />
    </div>
  );
}
```

**Using React Router useSearchParams**

```typescript
import { useSearchParams } from "react-router-dom";

function FilteredList() {
  const [searchParams, setSearchParams] = useSearchParams();

  const status = searchParams.get("status") ?? "all";
  const page = Number(searchParams.get("page") ?? "1");

  const updateFilter = (key: string, value: string | null) => {
    setSearchParams((prev) => {
      const next = new URLSearchParams(prev);
      if (value === null) {
        next.delete(key);
      } else {
        next.set(key, value);
      }
      // Reset page when filter changes
      if (key !== "page") next.set("page", "1");
      return next;
    });
  };

  return (
    <div>
      <select
        value={status}
        onChange={(e) => updateFilter("status", e.target.value)}
      >
        <option value="all">All</option>
        <option value="active">Active</option>
        <option value="archived">Archived</option>
      </select>
    </div>
  );
}
```

---

### 7. Python State

Use dataclasses for lightweight domain objects and Pydantic for validated external data. Combine with the repository pattern for persistence.

**Dataclasses for domain objects**

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price


@dataclass
class Order:
    customer_id: str
    items: list[OrderItem] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)
    status: OrderStatus = OrderStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)

    def confirm(self) -> None:
        if self.status != OrderStatus.DRAFT:
            raise ValueError(f"Cannot confirm order in '{self.status}' state")
        if not self.items:
            raise ValueError("Cannot confirm an empty order")
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status in (OrderStatus.DELIVERED, OrderStatus.CANCELLED):
            raise ValueError(f"Cannot cancel order in '{self.status}' state")
        self.status = OrderStatus.CANCELLED
```

**Pydantic for validated external input**

```python
from pydantic import BaseModel, Field, field_validator


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=50)
    items: list["OrderItemInput"] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def no_duplicate_products(cls, items: list["OrderItemInput"]) -> list["OrderItemInput"]:
        product_ids = [item.product_id for item in items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Duplicate product IDs are not allowed")
        return items


class OrderItemInput(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(ge=1, le=999)
```

**Repository pattern for persistence**

```python
from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None: ...

    @abstractmethod
    async def get(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    async def list_by_customer(self, customer_id: str) -> list[Order]: ...


class PostgresOrderRepository(OrderRepository):
    def __init__(self, pool) -> None:
        self.pool = pool

    async def save(self, order: Order) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO orders (id, customer_id, status, created_at)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (id) DO UPDATE SET status = $3
                """,
                order.id,
                order.customer_id,
                order.status.value,
                order.created_at,
            )
            # Upsert items...

    async def get(self, order_id: UUID) -> Order | None:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM orders WHERE id = $1", order_id
            )
            if row is None:
                return None
            items = await conn.fetch(
                "SELECT * FROM order_items WHERE order_id = $1", order_id
            )
            return self._row_to_order(row, items)

    async def list_by_customer(self, customer_id: str) -> list[Order]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM orders WHERE customer_id = $1 ORDER BY created_at DESC",
                customer_id,
            )
            # Fetch items for each order...
            return [self._row_to_order(row, items) for row, items in results]

    def _row_to_order(self, row, item_rows) -> Order:
        return Order(
            id=row["id"],
            customer_id=row["customer_id"],
            status=OrderStatus(row["status"]),
            created_at=row["created_at"],
            items=[
                OrderItem(
                    product_id=r["product_id"],
                    quantity=r["quantity"],
                    unit_price=float(r["unit_price"]),
                )
                for r in item_rows
            ],
        )
```

---

## Best Practices

1. **Start local, promote when needed.** Begin with `useState`. Only move state up or into a store when two or more unrelated components need the same data. Premature globalization makes refactoring painful.

2. **Separate server state from client state.** Use TanStack Query (or SWR) for anything fetched from an API. These libraries handle caching, deduplication, background refetching, and stale-while-revalidate. Do not duplicate fetched data in Zustand.

3. **Use selectors to prevent re-renders.** In Zustand, always select the specific field you need: `useStore((s) => s.count)`, not `useStore()`. The latter re-renders on every store change.

4. **Co-locate state with the component that owns it.** If only `<Sidebar>` uses `isOpen`, keep that state inside `<Sidebar>`. Moving it to a global store just because "it might be needed later" creates unnecessary coupling.

5. **Derive, do not duplicate.** If `fullName` can be computed from `firstName` and `lastName`, compute it on the fly or with `useMemo`. Storing derived values introduces synchronization bugs.

6. **Validate at the boundary, trust internally.** Use Pydantic or Zod to validate data when it enters the system (API requests, form submissions, external events). Once validated, pass typed objects without re-checking.

7. **Keep URL state minimal.** Only encode values the user would want to bookmark or share: active tab, search query, page number, sort column. Do not put ephemeral UI state (hover, open dropdown) in the URL.

8. **Treat form state as its own domain.** Let react-hook-form manage form values, dirty tracking, and validation. Submit the validated result to your mutation or API call. Do not synchronize form fields with external stores.

---

## Common Pitfalls

1. **Putting everything in global state.** Not all state needs to be global. A modal's open/closed state, an input's current text, or a component's loading spinner should stay local. Global stores should hold state that genuinely needs to be shared across distant parts of the tree.

2. **Storing server data in Zustand.** Zustand has no built-in cache invalidation, stale detection, or background refetch. Using it for API data means you are rebuilding TanStack Query poorly. Use the right tool for the job.

3. **Forgetting to invalidate queries after mutations.** After a `useMutation` succeeds, call `queryClient.invalidateQueries` with the affected keys. Without this, the UI shows stale data until the next refetch interval.

4. **Over-using React Context for frequently changing state.** Every Context value change re-renders every consumer. Context is good for low-frequency values (theme, locale, auth). For high-frequency updates (cursor position, scroll offset), use Zustand or a ref.

5. **Duplicating form state.** Calling `useForm()` and then also storing the same values in `useState` or Zustand means two sources of truth that can drift apart. Let the form library be the single owner.

6. **Ignoring URL state for filterable lists.** If a user applies filters and then hits the back button or refreshes, losing the filters is a bad experience. Encode filters in the URL so they survive navigation.

---

## Related Skills

- `react` - React component patterns and hooks
- `nextjs` - Next.js server components and data fetching
- `typescript` - TypeScript types and generics
- `caching` - Cache strategies and invalidation patterns
