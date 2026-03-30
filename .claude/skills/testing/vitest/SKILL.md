---
name: vitest
description: >
  Trigger this skill whenever writing, debugging, or refactoring JavaScript or TypeScript tests, or when Vitest mocking, coverage, or configuration are mentioned. Activate for any .test.ts, .test.tsx, .test.js, .spec.ts, .spec.js file, vitest.config.ts reference, or React component testing with Testing Library. Also use when the user asks about JS/TS test patterns, test organization, or vi.mock/vi.fn usage.
---

# Vitest

## When to Use

- Testing JavaScript/TypeScript
- React component testing
- Unit and integration tests

## When NOT to Use

- Python testing -- use the `testing/pytest` skill instead
- Projects that explicitly mandate Jest-only by convention with no Vitest dependency
- Non-JavaScript/TypeScript projects

---

## Core Patterns

### 1. Test Structure

#### describe / it / expect

```typescript
import { describe, it, expect } from 'vitest';
import { formatCurrency } from './format';

describe('formatCurrency', () => {
  it('should format whole dollars', () => {
    expect(formatCurrency(100)).toBe('$100.00');
  });

  it('should format cents correctly', () => {
    expect(formatCurrency(9.5)).toBe('$9.50');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('should throw on negative values', () => {
    expect(() => formatCurrency(-5)).toThrow('Amount must be non-negative');
  });
});
```

#### Lifecycle Hooks

```typescript
import { describe, it, expect, beforeEach, afterEach, beforeAll, afterAll } from 'vitest';
import { Database } from './database';

describe('UserRepository', () => {
  let db: Database;

  beforeAll(async () => {
    // Runs once before all tests in this describe block
    db = await Database.connect('test://localhost/testdb');
    await db.migrate();
  });

  afterAll(async () => {
    await db.disconnect();
  });

  beforeEach(async () => {
    // Runs before each test
    await db.seed({ users: [{ id: 1, name: 'Alice' }] });
  });

  afterEach(async () => {
    await db.truncate('users');
  });

  it('should find user by id', async () => {
    const user = await db.users.findById(1);
    expect(user).toEqual({ id: 1, name: 'Alice' });
  });

  it('should return null for missing user', async () => {
    const user = await db.users.findById(999);
    expect(user).toBeNull();
  });
});
```

#### test.each for Parametrized Tests

```typescript
import { describe, it, expect, test } from 'vitest';
import { validateEmail } from './validators';

describe('validateEmail', () => {
  test.each([
    { email: 'user@example.com', expected: true },
    { email: 'admin@test.org', expected: true },
    { email: 'name+tag@domain.co.uk', expected: true },
  ])('should accept valid email: $email', ({ email, expected }) => {
    expect(validateEmail(email)).toBe(expected);
  });

  test.each([
    { email: '', reason: 'empty string' },
    { email: 'no-at-sign', reason: 'missing @' },
    { email: '@no-local.com', reason: 'missing local part' },
    { email: 'spaces in@email.com', reason: 'contains spaces' },
  ])('should reject invalid email ($reason): $email', ({ email }) => {
    expect(validateEmail(email)).toBe(false);
  });
});
```

#### Nested describe Blocks

```typescript
describe('ShoppingCart', () => {
  describe('when empty', () => {
    it('should have zero total', () => {
      const cart = new ShoppingCart();
      expect(cart.total()).toBe(0);
    });

    it('should have zero item count', () => {
      const cart = new ShoppingCart();
      expect(cart.itemCount()).toBe(0);
    });
  });

  describe('with items', () => {
    let cart: ShoppingCart;

    beforeEach(() => {
      cart = new ShoppingCart();
      cart.add({ name: 'Widget', price: 9.99, quantity: 2 });
      cart.add({ name: 'Gadget', price: 24.99, quantity: 1 });
    });

    it('should calculate total', () => {
      expect(cart.total()).toBeCloseTo(44.97);
    });

    it('should count all items', () => {
      expect(cart.itemCount()).toBe(3);
    });
  });
});
```

---

### 2. Mocking

#### vi.mock for Module Mocking

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { sendWelcomeEmail } from './onboarding';

// Mock the entire email module -- hoisted to the top of the file automatically
vi.mock('./email', () => ({
  sendEmail: vi.fn().mockResolvedValue({ messageId: 'msg-123' }),
}));

// Import AFTER vi.mock declaration
import { sendEmail } from './email';

describe('sendWelcomeEmail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should send email with welcome template', async () => {
    await sendWelcomeEmail('alice@example.com');

    expect(sendEmail).toHaveBeenCalledWith({
      to: 'alice@example.com',
      template: 'welcome',
      subject: 'Welcome to our platform!',
    });
  });

  it('should return the message id', async () => {
    const result = await sendWelcomeEmail('alice@example.com');
    expect(result.messageId).toBe('msg-123');
  });
});
```

#### vi.fn for Function Spies

```typescript
import { describe, it, expect, vi } from 'vitest';

describe('EventEmitter', () => {
  it('should call listener on emit', () => {
    const emitter = new EventEmitter();
    const listener = vi.fn();

    emitter.on('click', listener);
    emitter.emit('click', { x: 10, y: 20 });

    expect(listener).toHaveBeenCalledOnce();
    expect(listener).toHaveBeenCalledWith({ x: 10, y: 20 });
  });

  it('should track multiple calls', () => {
    const callback = vi.fn();

    callback('first');
    callback('second');
    callback('third');

    expect(callback).toHaveBeenCalledTimes(3);
    expect(callback.mock.calls).toEqual([['first'], ['second'], ['third']]);
  });
});
```

#### vi.spyOn

```typescript
import { describe, it, expect, vi, afterEach } from 'vitest';
import * as mathUtils from './math-utils';

describe('calculateTax', () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should use the tax rate function', () => {
    const spy = vi.spyOn(mathUtils, 'getTaxRate').mockReturnValue(0.08);

    const result = calculateTax(100);

    expect(spy).toHaveBeenCalledWith();
    expect(result).toBe(8);
  });

  it('should spy without changing behavior', () => {
    const spy = vi.spyOn(console, 'warn');

    triggerDeprecationWarning();

    expect(spy).toHaveBeenCalledWith(
      expect.stringContaining('deprecated')
    );
  });
});
```

#### mockResolvedValue / mockRejectedValue

```typescript
import { describe, it, expect, vi } from 'vitest';

describe('UserService', () => {
  it('should return user on successful fetch', async () => {
    const fetchUser = vi.fn().mockResolvedValue({ id: 1, name: 'Alice' });

    const user = await fetchUser(1);
    expect(user).toEqual({ id: 1, name: 'Alice' });
  });

  it('should throw on failed fetch', async () => {
    const fetchUser = vi.fn().mockRejectedValue(new Error('User not found'));

    await expect(fetchUser(999)).rejects.toThrow('User not found');
  });

  it('should return different values on successive calls', async () => {
    const getToken = vi.fn()
      .mockResolvedValueOnce('token-1')
      .mockResolvedValueOnce('token-2')
      .mockRejectedValueOnce(new Error('Expired'));

    expect(await getToken()).toBe('token-1');
    expect(await getToken()).toBe('token-2');
    await expect(getToken()).rejects.toThrow('Expired');
  });
});
```

#### MSW (Mock Service Worker) for API Mocking

```typescript
import { describe, it, expect, beforeAll, afterAll, afterEach } from 'vitest';
import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';
import { fetchUsers } from './api-client';

const server = setupServer(
  http.get('https://api.example.com/users', () => {
    return HttpResponse.json([
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
    ]);
  }),

  http.post('https://api.example.com/users', async ({ request }) => {
    const body = await request.json() as { name: string };
    return HttpResponse.json(
      { id: 3, name: body.name },
      { status: 201 }
    );
  })
);

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('API Client', () => {
  it('should fetch users', async () => {
    const users = await fetchUsers();
    expect(users).toHaveLength(2);
    expect(users[0].name).toBe('Alice');
  });

  it('should handle server errors', async () => {
    server.use(
      http.get('https://api.example.com/users', () => {
        return HttpResponse.json(
          { message: 'Internal Server Error' },
          { status: 500 }
        );
      })
    );

    await expect(fetchUsers()).rejects.toThrow('Server error');
  });
});
```

---

### 3. React Testing

#### Render and Query

```tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Greeting } from './Greeting';

describe('Greeting', () => {
  it('should display the user name', () => {
    render(<Greeting name="Alice" />);

    // getBy* throws if not found -- use for elements that must exist
    expect(screen.getByText('Hello, Alice!')).toBeInTheDocument();
  });

  it('should not display admin badge for regular users', () => {
    render(<Greeting name="Alice" role="viewer" />);

    // queryBy* returns null if not found -- use for asserting absence
    expect(screen.queryByText('Admin')).not.toBeInTheDocument();
  });

  it('should display admin badge for admins', () => {
    render(<Greeting name="Alice" role="admin" />);
    expect(screen.getByText('Admin')).toBeInTheDocument();
  });
});
```

#### userEvent for Interactions

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  it('should submit credentials', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<LoginForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText('Email'), 'alice@example.com');
    await user.type(screen.getByLabelText('Password'), 'secret123');
    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'alice@example.com',
      password: 'secret123',
    });
  });

  it('should show validation error on empty submit', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(screen.getByText('Email is required')).toBeInTheDocument();
  });

  it('should toggle password visibility', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    const passwordInput = screen.getByLabelText('Password');
    expect(passwordInput).toHaveAttribute('type', 'password');

    await user.click(screen.getByRole('button', { name: 'Show password' }));
    expect(passwordInput).toHaveAttribute('type', 'text');
  });
});
```

#### findBy for Async Rendering and waitFor

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('should load and display user data', async () => {
    render(<UserProfile userId={1} />);

    // findBy* waits for the element to appear (async query)
    const heading = await screen.findByRole('heading', { name: 'Alice' });
    expect(heading).toBeInTheDocument();
  });

  it('should show loading state initially', () => {
    render(<UserProfile userId={1} />);
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('should update after action', async () => {
    const user = userEvent.setup();
    render(<UserProfile userId={1} />);

    await screen.findByRole('heading', { name: 'Alice' });
    await user.click(screen.getByRole('button', { name: 'Deactivate' }));

    await waitFor(() => {
      expect(screen.getByText('Status: Inactive')).toBeInTheDocument();
    });
  });
});
```

#### Testing with Context Providers

```tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from './ThemeContext';
import { ThemedButton } from './ThemedButton';

function renderWithProviders(ui: React.ReactElement, options?: { theme?: 'light' | 'dark' }) {
  const theme = options?.theme ?? 'light';
  return render(
    <ThemeProvider value={theme}>
      {ui}
    </ThemeProvider>
  );
}

describe('ThemedButton', () => {
  it('should apply light theme styles', () => {
    renderWithProviders(<ThemedButton>Click me</ThemedButton>, { theme: 'light' });
    expect(screen.getByRole('button')).toHaveClass('btn-light');
  });

  it('should apply dark theme styles', () => {
    renderWithProviders(<ThemedButton>Click me</ThemedButton>, { theme: 'dark' });
    expect(screen.getByRole('button')).toHaveClass('btn-dark');
  });
});
```

---

### 4. Async Testing

#### Promises and async/await

```typescript
import { describe, it, expect } from 'vitest';
import { fetchUser, processQueue } from './services';

describe('async operations', () => {
  it('should resolve with user data', async () => {
    const user = await fetchUser(1);
    expect(user).toEqual({ id: 1, name: 'Alice' });
  });

  it('should reject with descriptive error', async () => {
    await expect(fetchUser(-1)).rejects.toThrow('Invalid user ID');
  });

  it('should process all items in queue', async () => {
    const results = await processQueue(['a', 'b', 'c']);
    expect(results).toHaveLength(3);
    expect(results.every((r) => r.status === 'done')).toBe(true);
  });
});
```

#### Fake Timers

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { debounce } from './debounce';

describe('debounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should not call function before delay', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 300);

    debounced();
    vi.advanceTimersByTime(200);

    expect(fn).not.toHaveBeenCalled();
  });

  it('should call function after delay', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 300);

    debounced();
    vi.advanceTimersByTime(300);

    expect(fn).toHaveBeenCalledOnce();
  });

  it('should reset timer on subsequent calls', () => {
    const fn = vi.fn();
    const debounced = debounce(fn, 300);

    debounced();
    vi.advanceTimersByTime(200);
    debounced(); // reset
    vi.advanceTimersByTime(200);

    expect(fn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledOnce();
  });
});
```

#### Fake Timers with Date

```typescript
import { describe, it, expect, vi } from 'vitest';
import { isExpired } from './token';

describe('isExpired', () => {
  it('should detect expired tokens', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-06-15T12:00:00Z'));

    const token = { expiresAt: '2025-06-15T11:00:00Z' };
    expect(isExpired(token)).toBe(true);

    vi.useRealTimers();
  });
});
```

---

### 5. Snapshot Testing

#### toMatchSnapshot

```typescript
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Badge } from './Badge';

describe('Badge', () => {
  it('should match snapshot for success variant', () => {
    const { container } = render(<Badge variant="success">Active</Badge>);
    expect(container.firstChild).toMatchSnapshot();
  });
});
```

#### toMatchInlineSnapshot

Inline snapshots embed the expected value directly in the test file. Vitest updates them automatically on first run.

```typescript
import { describe, it, expect } from 'vitest';
import { formatError } from './errors';

describe('formatError', () => {
  it('should format validation error', () => {
    const error = formatError({ field: 'email', rule: 'required' });

    expect(error).toMatchInlineSnapshot(`
      {
        "code": "VALIDATION_ERROR",
        "field": "email",
        "message": "email is required",
      }
    `);
  });
});
```

#### When to Use Snapshots (and When Not To)

**Use snapshots for:**
- Serialized output that is tedious to write by hand (large objects, rendered markup)
- Catching unintended changes in generated output
- Error message formatting

**Do not use snapshots for:**
- Business logic assertions -- write explicit `expect(value).toBe(expected)` instead
- Frequently changing output -- snapshot churn leads to mindless updates
- Large component trees -- a small change deep in the tree makes the diff unreadable; test specific elements instead

---

### 6. Coverage

#### vitest.config.ts Coverage Settings

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8', // or 'istanbul'
      reporter: ['text', 'html', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/**/*.{ts,tsx}'],
      exclude: [
        'src/**/*.test.{ts,tsx}',
        'src/**/*.d.ts',
        'src/**/index.ts', // barrel files
        'src/test-utils/**',
      ],
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },
  },
});
```

#### Running Coverage

```bash
vitest run --coverage                # Run once with coverage
vitest --coverage                    # Watch mode with coverage
vitest run --coverage.provider=v8    # Override provider via CLI
```

#### Per-File Thresholds

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      thresholds: {
        // Global thresholds
        statements: 80,
        // Per-glob overrides for critical paths
        'src/auth/**': {
          statements: 95,
          branches: 95,
        },
      },
    },
  },
});
```

---

### 7. Setup and Configuration

#### vitest.config.ts Basics

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,          // Use describe/it/expect without imports
    environment: 'jsdom',   // DOM environment for React (or 'happy-dom')
    setupFiles: ['./src/test-setup.ts'],
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'e2e'],
    testTimeout: 10_000,
    hookTimeout: 30_000,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
```

#### Setup File

```typescript
// src/test-setup.ts
import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Automatic cleanup after each test
afterEach(() => {
  cleanup();
});
```

#### Workspace Configuration

For monorepos with multiple packages:

```typescript
// vitest.workspace.ts
import { defineWorkspace } from 'vitest/config';

export default defineWorkspace([
  {
    extends: './vitest.config.ts',
    test: {
      name: 'ui',
      include: ['packages/ui/**/*.test.{ts,tsx}'],
      environment: 'jsdom',
    },
  },
  {
    extends: './vitest.config.ts',
    test: {
      name: 'api',
      include: ['packages/api/**/*.test.ts'],
      environment: 'node',
    },
  },
]);
```

#### Environment Per File

Use a magic comment at the top of a test file to override the environment:

```typescript
// @vitest-environment happy-dom

import { describe, it, expect } from 'vitest';

describe('DOM-heavy tests', () => {
  it('should create elements', () => {
    const div = document.createElement('div');
    div.textContent = 'Hello';
    expect(div.textContent).toBe('Hello');
  });
});
```

#### Globals Mode

When `globals: true` is set in config, you do not need to import `describe`, `it`, `expect`, `vi`, etc. Add the types to `tsconfig.json`:

```json
{
  "compilerOptions": {
    "types": ["vitest/globals"]
  }
}
```

---

## Best Practices

1. **Use `userEvent` over `fireEvent`** -- `userEvent` simulates real user behavior (focus, keystrokes, blur) while `fireEvent` dispatches raw DOM events. `userEvent` catches bugs that `fireEvent` misses, such as disabled buttons still receiving clicks.

2. **Query by role and label, not test IDs** -- Prefer `getByRole('button', { name: 'Submit' })` and `getByLabelText('Email')` over `getByTestId('submit-btn')`. Accessible queries validate your markup and are resilient to refactors.

3. **Clear mocks between tests** -- Call `vi.clearAllMocks()` in `beforeEach` or `vi.restoreAllMocks()` in `afterEach`. Leaked mock state between tests causes order-dependent failures that are painful to debug.

4. **Keep tests focused on one behavior** -- Each `it` block should test a single user-observable behavior. If your test description contains "and", split it into two tests.

5. **Avoid testing implementation details** -- Do not assert on component state, internal method calls, or private variables. Test what the user sees and what the component outputs. Implementation tests break on every refactor without catching real bugs.

6. **Use MSW for network mocking over vi.mock on fetch** -- MSW intercepts at the network level, so your tests exercise the actual fetch/axios code paths. Mocking `fetch` directly skips serialization, headers, and error handling logic.

7. **Colocate tests with source files** -- Place `Button.test.tsx` next to `Button.tsx`. This makes it obvious which files have tests and simplifies imports. Reserve a top-level `e2e/` folder only for end-to-end tests.

8. **Run tests in watch mode during development** -- `vitest` (no flags) starts in watch mode and re-runs only affected tests on file change. Use `vitest run` in CI for a single full run with exit code.

---

## Common Pitfalls

1. **Forgetting to await userEvent calls** -- Every `userEvent` method is async. Omitting `await` causes the assertion to run before the interaction completes, leading to false passes or intermittent failures.

2. **vi.mock hoisting confusion** -- `vi.mock()` calls are hoisted to the top of the file. If you define a mock implementation that references a variable declared below the `vi.mock` call, it will be `undefined`. Use `vi.mock` with a factory function or move the variable above.

3. **Not cleaning up after fake timers** -- Forgetting `vi.useRealTimers()` in `afterEach` causes subsequent tests to silently use fake timers, producing mysterious timeouts and passing tests that should fail.

4. **Using `getBy` queries for elements that may not exist** -- `getByText('Error')` throws immediately if the element is absent. When asserting that something is NOT rendered, use `queryByText('Error')` which returns `null`.

5. **Snapshot overuse** -- Developers update snapshots without reviewing the diff. Over time, snapshots become rubber stamps. Limit snapshots to serialized output and error formatting; use explicit assertions for behavior.

6. **Testing third-party library internals** -- Do not test that React Router navigates correctly or that Zustand updates state. Test that your component renders the right thing after navigation or state change. Trust library authors; test your code.

---

## Related Skills

- `testing/pytest` -- Python testing counterpart
- `languages/typescript` -- TypeScript language patterns and strict typing
- `frameworks/react` -- React component patterns for component testing
- `methodology/test-driven-development` -- TDD workflow for writing tests first
- `devops/github-actions` — Running vitest in CI/CD pipelines
