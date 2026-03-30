# TypeScript Advanced Types Quick Reference

## Discriminated Unions

```typescript
// Tag each variant with a literal type field
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number }
  | { kind: "triangle"; base: number; height: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle":    return Math.PI * s.radius ** 2;
    case "rect":      return s.width * s.height;
    case "triangle":  return (s.base * s.height) / 2;
  }
}

// Exhaustiveness check helper
function assertNever(x: never): never {
  throw new Error(`Unexpected value: ${x}`);
}
```

## Branded Types

```typescript
// Prevent mixing structurally identical types
type Brand<T, B extends string> = T & { readonly __brand: B };

type UserId = Brand<string, "UserId">;
type OrderId = Brand<string, "OrderId">;

function getUser(id: UserId) { /* ... */ }

const userId = "abc" as UserId;
const orderId = "abc" as OrderId;

getUser(userId);    // OK
getUser(orderId);   // Error: OrderId not assignable to UserId

// Validation-based branding
type Email = Brand<string, "Email">;
function parseEmail(input: string): Email {
  if (!input.includes("@")) throw new Error("Invalid email");
  return input as Email;
}
```

## Template Literal Types

```typescript
// Build string types from unions
type Method = "get" | "post" | "put" | "delete";
type Route = "/users" | "/orders";
type Endpoint = `${Uppercase<Method>} ${Route}`;
// "GET /users" | "GET /orders" | "POST /users" | ...

// Event handler pattern
type EventName = "click" | "focus" | "blur";
type Handler = `on${Capitalize<EventName>}`;
// "onClick" | "onFocus" | "onBlur"

// Extract parts from string types
type ExtractParam<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractParam<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

type Params = ExtractParam<"/users/:id/posts/:postId">;
// "id" | "postId"
```

## Conditional Types

```typescript
// Basic conditional
type IsString<T> = T extends string ? true : false;

// Distributive over unions (when T is naked type parameter)
type ToArray<T> = T extends unknown ? T[] : never;
type Result = ToArray<string | number>; // string[] | number[]

// Prevent distribution with tuple wrapping
type ToArrayNonDist<T> = [T] extends [unknown] ? T[] : never;
type Result2 = ToArrayNonDist<string | number>; // (string | number)[]

// infer keyword
type ReturnOf<T> = T extends (...args: any[]) => infer R ? R : never;
type Unpacked<T> = T extends Promise<infer U> ? U :
                   T extends Array<infer U> ? U : T;

// infer with constraints (TS 4.7+)
type FirstString<T> =
  T extends [infer S extends string, ...unknown[]] ? S : never;
```

## Mapped Types

```typescript
// Transform all properties
type Readonly<T> = { readonly [K in keyof T]: T[K] };
type Optional<T> = { [K in keyof T]?: T[K] };
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
type Required<T> = { [K in keyof T]-?: T[K] };

// Map to new value types
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

interface Person { name: string; age: number }
type PersonGetters = Getters<Person>;
// { getName: () => string; getAge: () => number }
```

## Key Remapping (via `as`)

```typescript
// Filter keys
type OnlyStrings<T> = {
  [K in keyof T as T[K] extends string ? K : never]: T[K];
};

// Rename keys
type Prefixed<T, P extends string> = {
  [K in keyof T as `${P}${Capitalize<string & K>}`]: T[K];
};

// Remove specific keys
type RemoveKind<T> = {
  [K in keyof T as Exclude<K, "kind">]: T[K];
};

// Build from union
type EventMap<T extends string> = {
  [K in T as `on${Capitalize<K>}`]: (event: K) => void;
};
type Handlers = EventMap<"click" | "scroll">;
// { onClick: (event: "click") => void; onScroll: (event: "scroll") => void }
```

## Recursive Types

```typescript
// JSON type
type Json =
  | string
  | number
  | boolean
  | null
  | Json[]
  | { [key: string]: Json };

// Deep readonly
type DeepReadonly<T> = T extends Function
  ? T
  : T extends object
    ? { readonly [K in keyof T]: DeepReadonly<T[K]> }
    : T;

// Deep partial
type DeepPartial<T> = T extends object
  ? { [K in keyof T]?: DeepPartial<T[K]> }
  : T;

// Flatten nested object paths
type Paths<T, Prefix extends string = ""> = T extends object
  ? {
      [K in keyof T & string]: T[K] extends object
        ? Paths<T[K], `${Prefix}${K}.`>
        : `${Prefix}${K}`;
    }[keyof T & string]
  : never;

type P = Paths<{ a: { b: number; c: { d: string } } }>;
// "a.b" | "a.c.d"
```

## Utility Types Cheat Sheet

| Utility | Effect |
|---------|--------|
| `Partial<T>` | All properties optional |
| `Required<T>` | All properties required |
| `Readonly<T>` | All properties readonly |
| `Record<K, V>` | Object with keys K and values V |
| `Pick<T, K>` | Subset of properties |
| `Omit<T, K>` | All except listed properties |
| `Exclude<U, E>` | Remove members from union |
| `Extract<U, E>` | Keep matching members from union |
| `NonNullable<T>` | Remove null and undefined |
| `ReturnType<F>` | Return type of function |
| `Parameters<F>` | Tuple of parameter types |
| `ConstructorParameters<C>` | Constructor parameter types |
| `InstanceType<C>` | Instance type of constructor |
| `Awaited<T>` | Unwrap Promise (deeply) |
| `NoInfer<T>` | Prevent inference from this position (5.4+) |

## Satisfies Operator (4.9+)

```typescript
// Validate type without widening
const palette = {
  red: "#ff0000",
  green: [0, 255, 0],
} satisfies Record<string, string | number[]>;

palette.red.toUpperCase();     // OK - knows it's string
palette.green.map(x => x);    // OK - knows it's number[]
```

## const Type Parameters (5.0+)

```typescript
// Infer narrow literal types from arguments
function routes<const T extends readonly string[]>(paths: T): T {
  return paths;
}

const r = routes(["/home", "/about"]);
// Type: readonly ["/home", "/about"]  (not string[])
```

## Pattern: Type-Safe Event Emitter

```typescript
type EventMap = {
  login: { userId: string };
  logout: undefined;
  error: { code: number; message: string };
};

class Emitter<E extends Record<string, unknown>> {
  on<K extends keyof E>(
    event: K,
    handler: E[K] extends undefined
      ? () => void
      : (payload: E[K]) => void
  ): void { /* ... */ }

  emit<K extends keyof E>(
    ...args: E[K] extends undefined ? [K] : [K, E[K]]
  ): void { /* ... */ }
}
```
