---
name: typescript
description: >
  Trigger this skill whenever working with TypeScript files (.ts, .tsx), configuring tsconfig.json, or using TypeScript-specific features like strict typing, generics, utility types, or type guards. Activate for any TypeScript project setup, type definition authoring, Zod schema validation, or discriminated union patterns. Also use when the user asks about avoiding `any`, enabling strict mode, or migrating JavaScript to TypeScript.
---

# TypeScript

## When to Use

- Working with TypeScript files (.ts, .tsx)
- Building typed JavaScript applications
- React/Next.js development
- Node.js backend development

## When NOT to Use

- Pure Python projects with no TypeScript components
- JavaScript projects that have no TypeScript setup and are not being migrated to TypeScript

---

## Core Patterns

### 1. Advanced Types

#### Discriminated Unions

```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rectangle"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case "circle":
      return Math.PI * shape.radius ** 2;
    case "rectangle":
      return shape.width * shape.height;
    case "triangle":
      return (shape.base * shape.height) / 2;
  }
}
```

#### Branded Types

```typescript
type UserId = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };

function createUserId(id: string): UserId {
  if (!id.startsWith("usr_")) throw new Error("Invalid user ID");
  return id as UserId;
}

function getUser(id: UserId): User { ... }

// Prevents mixing IDs:
const userId = createUserId("usr_123");
const orderId = "ord_456" as OrderId;
// getUser(orderId);  // compile error
```

#### Template Literal Types

```typescript
type HttpMethod = "GET" | "POST" | "PUT" | "DELETE";
type ApiRoute = `/api/${string}`;
type EventName = `on${Capitalize<string>}`;

// Combine for precise route definitions
type Endpoint = `${Uppercase<HttpMethod>} ${ApiRoute}`;

// Pattern matching on string types
type ExtractParam<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractParam<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

type Params = ExtractParam<"/users/:userId/posts/:postId">;
// Result: "userId" | "postId"
```

#### Conditional Types with infer

```typescript
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type UnwrapArray<T> = T extends (infer U)[] ? U : T;

// Deeply unwrap nested promises
type DeepAwaited<T> = T extends Promise<infer U> ? DeepAwaited<U> : T;

// Extract function return type conditionally
type AsyncReturnType<T extends (...args: any[]) => any> =
  ReturnType<T> extends Promise<infer U> ? U : ReturnType<T>;
```

#### Mapped Types

```typescript
// Make all properties optional and nullable
type Nullable<T> = { [K in keyof T]: T[K] | null };

// Create a readonly version with getters
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

// Remove specific keys
type RemoveKind<T> = {
  [K in keyof T as Exclude<K, "kind">]: T[K];
};
```

#### Recursive Types

```typescript
type Json =
  | string
  | number
  | boolean
  | null
  | Json[]
  | { [key: string]: Json };

type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object ? DeepPartial<T[K]> : T[K];
};

type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};
```

---

### 2. Utility Types

```typescript
interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "user" | "guest";
  createdAt: Date;
}

// Partial -- all properties optional (useful for update payloads)
type UserUpdate = Partial<User>;

// Required -- all properties required (undo optionality)
type CompleteUser = Required<User>;

// Pick -- select specific properties
type UserPreview = Pick<User, "id" | "name">;

// Omit -- exclude specific properties
type UserCreate = Omit<User, "id" | "createdAt">;

// Record -- dictionary with typed keys and values
type RolePermissions = Record<User["role"], string[]>;

// Exclude -- remove members from a union
type NonGuestRole = Exclude<User["role"], "guest">;
// Result: "admin" | "user"

// Extract -- keep only matching members from a union
type PrivilegedRole = Extract<User["role"], "admin" | "moderator">;
// Result: "admin"

// ReturnType -- extract return type of a function
declare function getUser(): Promise<User>;
type GetUserResult = ReturnType<typeof getUser>;
// Result: Promise<User>

// Parameters -- extract parameter types as a tuple
type GetUserParams = Parameters<typeof getUser>;

// Awaited -- unwrap Promise types
type ResolvedUser = Awaited<ReturnType<typeof getUser>>;
// Result: User

// NonNullable -- remove null and undefined
type DefinitelyString = NonNullable<string | null | undefined>;
// Result: string
```

---

### 3. Generics

#### Generic Functions

```typescript
function first<T>(items: T[]): T | undefined {
  return items[0];
}

function groupBy<T, K extends string | number>(
  items: T[],
  keyFn: (item: T) => K,
): Record<K, T[]> {
  const result = {} as Record<K, T[]>;
  for (const item of items) {
    const key = keyFn(item);
    (result[key] ??= []).push(item);
  }
  return result;
}
```

#### Generic Constraints with extends

```typescript
interface HasId {
  id: string;
}

function findById<T extends HasId>(items: T[], id: string): T | undefined {
  return items.find((item) => item.id === id);
}

// Multiple constraints
function merge<T extends object, U extends object>(a: T, b: U): T & U {
  return { ...a, ...b };
}
```

#### Generic Classes

```typescript
class Repository<T extends HasId> {
  private items = new Map<string, T>();

  save(item: T): void {
    this.items.set(item.id, item);
  }

  findById(id: string): T | undefined {
    return this.items.get(id);
  }

  findAll(): T[] {
    return [...this.items.values()];
  }
}

const userRepo = new Repository<User>();
```

#### Default Type Parameters

```typescript
type ApiResponse<T, E = Error> = {
  data: T | null;
  error: E | null;
  status: number;
};

// Uses default Error type
const response: ApiResponse<User> = {
  data: user,
  error: null,
  status: 200,
};

// Override with custom error
const response2: ApiResponse<User, ValidationError> = { ... };
```

#### const Type Parameters (TypeScript 5.0+)

```typescript
function createRoute<const T extends readonly string[]>(
  methods: T,
  path: string,
) {
  return { methods, path };
}

// Infers literal tuple type ["GET", "POST"] instead of string[]
const route = createRoute(["GET", "POST"], "/api/users");
```

---

### 4. Async Patterns

#### Promise Typing

```typescript
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch user: ${response.status}`);
  }
  return response.json() as Promise<User>;
}
```

#### Promise.all with Tuple Types

```typescript
async function loadDashboard(userId: string) {
  const [user, posts, notifications] = await Promise.all([
    fetchUser(userId),
    fetchPosts(userId),
    fetchNotifications(userId),
  ] as const);
  // user: User, posts: Post[], notifications: Notification[]
  return { user, posts, notifications };
}
```

#### Result Pattern for Error Handling

```typescript
type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

async function safeAsync<T>(
  fn: () => Promise<T>,
): Promise<Result<T>> {
  try {
    return { ok: true, value: await fn() };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error : new Error(String(error)) };
  }
}

const result = await safeAsync(() => fetchUser("123"));
if (result.ok) {
  console.log(result.value.name);
} else {
  console.error(result.error.message);
}
```

#### AbortController Patterns

```typescript
async function fetchWithTimeout(
  url: string,
  timeoutMs: number = 5000,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}

// Cancellable operation
function createCancellableRequest(url: string) {
  const controller = new AbortController();
  const promise = fetch(url, { signal: controller.signal });
  return {
    promise,
    cancel: () => controller.abort(),
  };
}
```

---

### 5. Zod Integration

#### Schema Definition and Inference

```typescript
import { z } from "zod";

const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  age: z.number().int().min(0).max(150),
  role: z.enum(["admin", "user", "guest"]),
});

type User = z.infer<typeof UserSchema>;
```

#### Refinements and Transforms

```typescript
const PasswordSchema = z
  .string()
  .min(8)
  .refine((val) => /[A-Z]/.test(val), "Must contain uppercase")
  .refine((val) => /[0-9]/.test(val), "Must contain number");

const DateStringSchema = z
  .string()
  .transform((val) => new Date(val))
  .refine((date) => !isNaN(date.getTime()), "Invalid date");

const MoneySchema = z
  .string()
  .transform((val) => parseFloat(val.replace(/[$,]/g, "")))
  .pipe(z.number().positive());
```

#### Discriminated Unions with Zod

```typescript
const ShapeSchema = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("circle"), radius: z.number().positive() }),
  z.object({ kind: z.literal("rectangle"), width: z.number(), height: z.number() }),
]);

type Shape = z.infer<typeof ShapeSchema>;

function validateShape(input: unknown): Shape {
  return ShapeSchema.parse(input);
}
```

#### Zod with API Validation

```typescript
const QueryParamsSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  search: z.string().optional(),
  sort: z.enum(["name", "date", "relevance"]).default("date"),
});

type QueryParams = z.infer<typeof QueryParamsSchema>;

function parseQuery(raw: Record<string, string>): QueryParams {
  return QueryParamsSchema.parse(raw);
}
```

---

### 6. Module Patterns

#### Barrel Exports

```typescript
// src/models/index.ts
export { User, type UserCreate } from "./user.js";
export { Post, type PostCreate } from "./post.js";
export { Comment } from "./comment.js";
```

#### Declaration Merging

```typescript
// Extend an existing interface
interface Window {
  analytics: AnalyticsClient;
}

// Extend Express Request
declare namespace Express {
  interface Request {
    user?: AuthenticatedUser;
  }
}
```

#### Module Augmentation

```typescript
// Augment a third-party module
import "express";

declare module "express" {
  interface Request {
    requestId: string;
    startTime: number;
  }
}
```

#### Ambient Declarations (.d.ts)

```typescript
// global.d.ts
declare global {
  interface ImportMeta {
    env: {
      VITE_API_URL: string;
      VITE_APP_TITLE: string;
    };
  }
}

// Declare untyped modules
declare module "legacy-lib" {
  export function doSomething(input: string): string;
}

export {};
```

---

### 7. Type Guards

#### Built-in Narrowing

```typescript
function process(value: string | number | null) {
  if (typeof value === "string") {
    // value: string
    return value.toUpperCase();
  }
  if (typeof value === "number") {
    // value: number
    return value.toFixed(2);
  }
  // value: null
  return "N/A";
}
```

#### instanceof Guard

```typescript
class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
  ) {
    super(message);
  }
}

function handleError(error: unknown): string {
  if (error instanceof ApiError) {
    return `API Error ${error.statusCode}: ${error.message}`;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}
```

#### in Operator Guard

```typescript
interface Dog { bark(): void; breed: string; }
interface Cat { meow(): void; color: string; }

function speak(animal: Dog | Cat): void {
  if ("bark" in animal) {
    animal.bark(); // animal: Dog
  } else {
    animal.meow(); // animal: Cat
  }
}
```

#### Custom Type Predicates (is)

```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "id" in value &&
    "email" in value &&
    typeof (value as User).id === "string"
  );
}

function processInput(data: unknown) {
  if (isUser(data)) {
    // data: User -- fully narrowed
    console.log(data.email);
  }
}
```

#### Assertion Functions (asserts)

```typescript
function assertDefined<T>(
  value: T | null | undefined,
  message?: string,
): asserts value is T {
  if (value === null || value === undefined) {
    throw new Error(message ?? "Value is null or undefined");
  }
}

function processUser(maybeUser: User | null): string {
  assertDefined(maybeUser, "User is required");
  // maybeUser: User after this point
  return maybeUser.name;
}

function assertNever(value: never): never {
  throw new Error(`Unexpected value: ${value}`);
}

// Exhaustiveness checking in switch
function getLabel(role: "admin" | "user" | "guest"): string {
  switch (role) {
    case "admin": return "Administrator";
    case "user": return "Standard User";
    case "guest": return "Guest";
    default: return assertNever(role); // compile error if a case is missed
  }
}
```

---

## Best Practices

1. **Enable strict mode in tsconfig.json** -- set `"strict": true` which enables `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, and other safety checks.

2. **Never use `any` -- use `unknown` instead** -- when the type is truly unknown, use `unknown` and narrow with type guards. Reserve `any` only for exceptional migration scenarios, and flag it with `// eslint-disable-next-line`.

3. **Use interfaces for object shapes, types for unions** -- interfaces support declaration merging and produce clearer error messages. Types are better for unions, intersections, and mapped types.

4. **Prefer discriminated unions for state modeling** -- use a shared literal `kind` or `type` field to enable exhaustive switch statements and precise narrowing.

5. **Use `as const` for literal inference** -- `const assertions` preserve literal types in arrays and objects, avoiding unwanted widening to `string[]` or `number[]`.

6. **Validate external data at boundaries** -- use Zod or a similar runtime validator at API boundaries, config loading, and form inputs. Never trust `as` casts for unknown data.

7. **Prefer type predicates over type assertions** -- custom `is` guards are safer than `as` casts because they include a runtime check.

8. **Use `satisfies` for type checking without widening** -- the `satisfies` operator (TS 5.0+) validates that a value conforms to a type while preserving the narrower inferred type.
   ```typescript
   const config = {
     apiUrl: "https://api.example.com",
     retries: 3,
   } satisfies Record<string, string | number>;
   // config.apiUrl is still string (not string | number)
   ```

---

## Common Pitfalls

1. **Overusing type assertions (`as`)** -- assertions bypass the type checker. Use type guards or schema validation instead.
   ```typescript
   // BAD
   const user = data as User;

   // GOOD
   if (isUser(data)) { ... }
   ```

2. **Ignoring strict null checks** -- `undefined` and `null` cause runtime crashes when not handled. Always enable `strictNullChecks` and handle nullable values explicitly.

3. **Returning `any` from catch blocks** -- `catch (e)` gives `unknown` in strict mode. Always narrow before using the error.
   ```typescript
   catch (error) {
     const message = error instanceof Error ? error.message : String(error);
   }
   ```

4. **Mutation of readonly types at runtime** -- `Readonly<T>` and `readonly` only prevent mutation at compile time. The underlying object can still be mutated at runtime via `Object.assign` or casts.

5. **Forgetting `export {}` in ambient files** -- `.d.ts` files without any import/export are treated as global scripts rather than modules, which can cause unexpected declaration collisions.

6. **Using enums instead of const objects** -- TypeScript enums have quirks (reverse mappings, tree-shaking issues). Prefer `as const` objects or union types.
   ```typescript
   // Prefer this:
   const Role = { Admin: "admin", User: "user" } as const;
   type Role = (typeof Role)[keyof typeof Role];

   // Over this:
   enum Role { Admin = "admin", User = "user" }
   ```

---

## Related Skills

- `languages/javascript` -- JavaScript patterns for JS interop and migration
- `languages/python` -- Python language patterns for polyglot projects
- `frameworks/react` -- React component patterns with TypeScript
- `frameworks/nextjs` -- Next.js framework with TypeScript support
- `testing/vitest` -- TypeScript testing with Vitest
- `patterns/error-handling` -- TypeScript error handling patterns
- `patterns/state-management` -- State management with TypeScript types
