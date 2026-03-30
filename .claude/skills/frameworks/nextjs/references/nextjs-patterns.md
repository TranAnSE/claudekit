# Next.js Patterns Quick Reference

> App Router (Next.js 13.4+). Pages Router patterns not covered.

## App Router File Conventions

| File | Purpose | Renders |
|------|---------|---------|
| `page.tsx` | Route UI (makes route publicly accessible) | Server Component |
| `layout.tsx` | Shared UI wrapping children (preserved on nav) | Server Component |
| `template.tsx` | Like layout but re-mounts on navigation | Server Component |
| `loading.tsx` | Instant loading UI (Suspense boundary) | Server Component |
| `error.tsx` | Error boundary for segment | **Client Component** |
| `not-found.tsx` | UI for `notFound()` calls | Server Component |
| `route.ts` | API endpoint (GET, POST, etc.) | N/A |
| `default.tsx` | Fallback for parallel routes | Server Component |
| `middleware.ts` | Runs before requests (root only) | Edge Runtime |
| `opengraph-image.tsx` | Dynamic OG image generation | Edge Runtime |

### Route Segment Folders

| Pattern | Example | Purpose |
|---------|---------|---------|
| Static | `app/about/page.tsx` | `/about` |
| Dynamic | `app/blog/[slug]/page.tsx` | `/blog/hello-world` |
| Catch-all | `app/docs/[...slug]/page.tsx` | `/docs/a/b/c` |
| Optional catch-all | `app/docs/[[...slug]]/page.tsx` | `/docs` or `/docs/a/b` |
| Route group | `app/(marketing)/about/page.tsx` | Groups without URL segment |
| Parallel route | `app/@modal/login/page.tsx` | Simultaneous route slots |
| Intercepted route | `app/(.)photo/[id]/page.tsx` | Intercept navigation |

---

## Caching Layers Summary

| Layer | What | Where | Duration | Opt-out |
|-------|------|-------|----------|---------|
| Request Memoization | `fetch()` dedup in single render | Server | Per request | `AbortController` |
| Data Cache | `fetch()` results | Server | Persistent | `cache: 'no-store'` or `revalidate: 0` |
| Full Route Cache | Static HTML + RSC payload | Server | Persistent | Dynamic functions or `revalidate` |
| Router Cache | RSC payload | Client | Session (30s dynamic, 5min static) | `router.refresh()` |

### Revalidation Strategies

```typescript
// Time-based
fetch(url, { next: { revalidate: 60 } });           // Revalidate every 60s

// On-demand (from API route or Server Action)
import { revalidatePath, revalidateTag } from "next/cache";
revalidatePath("/blog");                              // Revalidate path
revalidateTag("posts");                               // Revalidate by tag

// Tag a fetch for on-demand revalidation
fetch(url, { next: { tags: ["posts"] } });

// Opt out entirely
fetch(url, { cache: "no-store" });

// Route segment config
export const dynamic = "force-dynamic";               // Always dynamic
export const revalidate = 60;                          // Segment-level ISR
```

---

## Data Fetching Patterns

### Server Component (default, preferred)

```typescript
// Async Server Component - fetch directly
async function BlogPage() {
  const posts = await fetch("https://api.example.com/posts", {
    next: { revalidate: 3600 }
  }).then(r => r.json());

  return <PostList posts={posts} />;
}
```

### Parallel Data Fetching

```typescript
async function Dashboard() {
  // Start all fetches simultaneously
  const [user, orders, stats] = await Promise.all([
    getUser(),
    getOrders(),
    getStats(),
  ]);
  return <DashboardView user={user} orders={orders} stats={stats} />;
}
```

### Streaming with Suspense

```typescript
export default function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      {/* Shows instantly */}
      <StaticContent />

      {/* Streams in when ready */}
      <Suspense fallback={<Skeleton />}>
        <SlowDataComponent />
      </Suspense>

      <Suspense fallback={<TableSkeleton />}>
        <AnotherSlowComponent />
      </Suspense>
    </div>
  );
}
```

### Cached Server Functions

```typescript
import { cache } from "react";

// Deduplicated across components in same request
export const getUser = cache(async (id: string) => {
  const res = await fetch(`/api/users/${id}`);
  return res.json();
});
```

---

## Server Action Patterns

### Basic Form Action

```typescript
// app/actions.ts
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string;
  const body = formData.get("body") as string;

  await db.post.create({ data: { title, body } });
  revalidatePath("/posts");
  redirect("/posts");
}
```

```typescript
// In a Server Component
import { createPost } from "./actions";

export default function NewPost() {
  return (
    <form action={createPost}>
      <input name="title" />
      <textarea name="body" />
      <button type="submit">Create</button>
    </form>
  );
}
```

### Optimistic Updates

```typescript
"use client";
import { useOptimistic } from "react";

function TodoList({ todos, addTodo }) {
  const [optimisticTodos, addOptimistic] = useOptimistic(
    todos,
    (state, newTodo: string) => [...state, { text: newTodo, pending: true }]
  );

  return (
    <form action={async (formData) => {
      const text = formData.get("text") as string;
      addOptimistic(text);
      await addTodo(text);
    }}>
      {optimisticTodos.map(todo => (
        <div style={{ opacity: todo.pending ? 0.5 : 1 }}>{todo.text}</div>
      ))}
      <input name="text" />
    </form>
  );
}
```

---

## Middleware Patterns

```typescript
// middleware.ts (project root)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Auth check
  const token = request.cookies.get("token")?.value;
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Add headers
  const response = NextResponse.next();
  response.headers.set("x-request-id", crypto.randomUUID());

  return response;
}

// Only run on matching paths
export const config = {
  matcher: [
    // Match all except static files and api
    "/((?!_next/static|_next/image|favicon.ico|api/).*)",
  ],
};
```

### Common Middleware Uses

| Use Case | Pattern |
|----------|---------|
| Auth redirect | Check cookie/header, redirect to login |
| i18n routing | Read Accept-Language, redirect to locale |
| A/B testing | Set cookie, rewrite to variant |
| Rate limiting | Check IP/token bucket, return 429 |
| Bot protection | Check User-Agent, block or challenge |
| Feature flags | Read flag, rewrite to feature variant |
