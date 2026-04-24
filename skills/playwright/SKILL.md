---
name: playwright
description: Use when writing, debugging, or configuring E2E tests with Playwright. Trigger for any mention of end-to-end testing, browser automation, page objects, visual regression, storageState auth, playwright.config, or cross-browser testing. Also use when setting up E2E in CI, testing critical user flows, or debugging flaky browser tests.
---

# Playwright E2E Testing

## Overview

The definitive E2E testing reference for web apps built with Next.js, FastAPI, Django, NestJS, Express, and React. Covers test structure, locator strategy, authentication reuse, API mocking, visual regression, accessibility, CI sharding, and framework-specific setup.

## When to Use
- Testing critical user flows end-to-end (login, checkout, onboarding)
- Cross-browser testing (Chromium, Firefox, WebKit)
- Visual regression testing with `toHaveScreenshot()`
- Accessibility auditing with `@axe-core/playwright`
- Testing Server Components, SSR pages, or full-stack flows
- Mobile/responsive testing via device emulation

## When NOT to Use
- **Unit testing** isolated functions — use `pytest` or `vitest`
- **Component testing** React components in isolation — use `vitest` + Testing Library (faster feedback loop)
- **API-only testing** with no browser interaction — use `httpx` / `supertest` directly
- **Load/performance testing** — use k6, Artillery, or Locust

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| Production-grade config to copy | [templates/playwright.config.ts](templates/playwright.config.ts) |
| Page Object, auth, mocking patterns | [references/e2e-patterns.md](references/e2e-patterns.md) |
| Locator strategy | § Locators below |
| Auth reuse with storageState | § Authentication below |
| CI setup (GitHub Actions + sharding) | § CI Integration below |
| Framework-specific webServer | § Framework Integration below |

---

## Core Patterns

### Test Structure

```typescript
import { test, expect } from '@playwright/test';

test.describe('Checkout flow', () => {
  test('guest can complete purchase', async ({ page }) => {
    await page.goto('/products/widget-pro');
    await page.getByRole('button', { name: 'Add to cart' }).click();
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();

    await page.getByLabel('Email').fill('guest@example.com');
    await page.getByRole('button', { name: 'Place order' }).click();

    await expect(page.getByText('Order confirmed')).toBeVisible();
  });
});
```

### Locators — the priority order

Always prefer **role-based and user-visible locators**. They survive refactors and match how users interact with the page.

| Priority | Locator | When |
|----------|---------|------|
| 1 | `getByRole('button', { name: '...' })` | Interactive elements with accessible names |
| 2 | `getByLabel('...')` | Form fields with `<label>` |
| 3 | `getByText('...')` | Static visible text |
| 4 | `getByPlaceholder('...')` | Inputs without labels (fix the label instead) |
| 5 | `getByTestId('...')` | Last resort — when no semantic locator works |

**Never use:** `page.locator('.css-class')`, `page.locator('#id')`, XPath. These break on every styling change.

### Assertions

```typescript
// Visibility
await expect(page.getByText('Welcome')).toBeVisible();
await expect(page.getByRole('alert')).not.toBeVisible();

// Content
await expect(page.getByRole('heading')).toHaveText('Dashboard');
await expect(page.getByRole('table')).toContainText('usr_abc123');

// Navigation
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard | Acme');

// Count
await expect(page.getByRole('listitem')).toHaveCount(5);

// Attribute / state
await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
await expect(page.getByRole('checkbox')).toBeChecked();
```

All `expect()` calls **auto-retry** until the timeout (default 5s). No `waitForSelector` needed.

### Fixtures

Extend `test` to share setup logic without inheritance chains.

```typescript
// fixtures.ts
import { test as base, expect } from '@playwright/test';

type Fixtures = {
  adminPage: Page;
};

export const test = base.extend<Fixtures>({
  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'e2e/.auth/admin.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});

export { expect };
```

```typescript
// admin.spec.ts
import { test, expect } from './fixtures';

test('admin can view users', async ({ adminPage }) => {
  await adminPage.goto('/admin/users');
  await expect(adminPage.getByRole('table')).toBeVisible();
});
```

---

## Authentication

Use **`storageState`** to log in once in `globalSetup` and reuse across all tests. Eliminates login page interaction from every test.

```typescript
// e2e/global-setup.ts
import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  await page.goto('http://localhost:3000/login');
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill('test-password');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('/dashboard');

  await page.context().storageState({ path: 'e2e/.auth/admin.json' });
  await browser.close();
}

export default globalSetup;
```

```typescript
// playwright.config.ts
export default defineConfig({
  globalSetup: './e2e/global-setup.ts',
  projects: [
    { name: 'authenticated', use: { storageState: 'e2e/.auth/admin.json' } },
    { name: 'guest', use: { storageState: undefined } },
  ],
});
```

**Multiple roles:** create separate storage state files per role (`admin.json`, `member.json`, `guest`) and use Playwright projects or fixtures to select which role each test suite uses.

---

## API Mocking

Use `page.route()` to intercept network requests. Prefer this over MSW for E2E — it runs at the browser level and doesn't require service worker setup.

```typescript
test('shows error on API failure', async ({ page }) => {
  await page.route('**/api/v1/users', (route) =>
    route.fulfill({
      status: 500,
      contentType: 'application/problem+json',
      body: JSON.stringify({
        type: 'https://api.example.com/problems/internal-error',
        title: 'Internal server error',
        status: 500,
      }),
    }),
  );

  await page.goto('/users');
  await expect(page.getByRole('alert')).toContainText('Something went wrong');
});
```

**When to mock vs use real backend:**
- **Mock:** error paths, edge cases, third-party integrations, rate-limit scenarios
- **Real backend:** happy-path smoke tests, data integrity flows, auth flows

---

## Framework Integration

### Next.js

```typescript
// playwright.config.ts
export default defineConfig({
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  use: { baseURL: 'http://localhost:3000' },
});
```

For App Router with Server Components — test the rendered output, not the server component directly. Playwright sees the final HTML the browser receives.

### FastAPI / Django (Python backends)

```typescript
// playwright.config.ts
export default defineConfig({
  webServer: [
    {
      command: 'uvicorn app.main:app --port 8000',
      url: 'http://localhost:8000/health',
      reuseExistingServer: !process.env.CI,
      timeout: 30_000,
    },
    {
      command: 'pnpm dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
    },
  ],
  use: { baseURL: 'http://localhost:3000' },
});
```

`webServer` accepts an array — spin up both backend and frontend in one config.

### NestJS / Express

Same pattern as FastAPI — use `webServer` with the backend's start command (`nest start --watch` or `node dist/main.js`). Point the health check URL at the backend's `/health` endpoint.

---

## CI Integration (GitHub Actions)

```yaml
# .github/workflows/e2e.yml
name: E2E Tests
on:
  pull_request:
  push:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1/4, 2/4, 3/4, 4/4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: pnpm install
      - run: pnpm exec playwright install --with-deps chromium

      - run: pnpm exec playwright test --shard=${{ matrix.shard }}

      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report-${{ strategy.job-index }}
          path: playwright-report/
          retention-days: 7

      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-traces-${{ strategy.job-index }}
          path: test-results/
          retention-days: 3
```

**Sharding** splits tests across `N` parallel runners. Use `fail-fast: false` so one shard failure doesn't kill the others.

**Artifacts:** always upload `playwright-report/` (HTML report) and `test-results/` on failure (traces for debugging).

---

## Accessibility Testing

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage has no a11y violations', async ({ page }) => {
  await page.goto('/');

  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

Run accessibility audits on every critical page. Integrate into the main E2E suite — don't create a separate "a11y suite" that gets ignored. Use `.withTags()` to target specific WCAG levels.

---

## Visual Regression

```typescript
test('dashboard matches screenshot', async ({ page }) => {
  await page.goto('/dashboard');

  // Wait for dynamic content to settle
  await expect(page.getByRole('table')).toBeVisible();

  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixelRatio: 0.01,
    animations: 'disabled',
    mask: [page.getByTestId('timestamp')],
  });
});
```

- **`animations: 'disabled'`** — prevents CSS/JS animation flicker from causing false diffs
- **`mask`** — hides dynamic content (timestamps, avatars, random IDs) that changes between runs
- **`maxDiffPixelRatio`** — allows minor anti-aliasing differences across environments

Update baselines: `pnpm exec playwright test --update-snapshots`

For team-scale visual regression with review UIs, pair with **Argos**, **Percy**, or **Chromatic**.

---

## Debugging

| Situation | Tool |
|-----------|------|
| Writing tests | `npx playwright test --ui` (interactive test explorer) |
| Test just failed in CI | Download `test-results/` artifact → `npx playwright show-trace trace.zip` |
| Flaky test | `npx playwright test --repeat-each=10` to reproduce |
| Step-by-step inspection | `await page.pause()` in code → debugger opens |
| Generate test from actions | `npx playwright codegen http://localhost:3000` |

**Trace-on-first-retry** — the most cost-effective trace strategy for CI:

```typescript
// playwright.config.ts
use: {
  trace: 'on-first-retry',
}
```

Records a trace only when a test fails and retries. You get debugging info without the storage cost of tracing every test.

---

## File Organization

```
e2e/
├── playwright.config.ts
├── global-setup.ts
├── fixtures.ts            # Shared custom fixtures
├── .auth/                 # storageState files (gitignored)
│   ├── admin.json
│   └── member.json
├── pages/                 # Page objects (if used)
│   ├── login.page.ts
│   └── dashboard.page.ts
├── specs/                 # Test files
│   ├── auth.spec.ts
│   ├── checkout.spec.ts
│   └── dashboard.spec.ts
└── helpers/               # Shared utilities
    └── api.ts             # API helpers for seeding data
```

Keep E2E tests in a top-level `e2e/` directory, separate from unit/integration tests. This keeps `vitest` and `playwright` from interfering with each other's config/discovery.

---

## Common Pitfalls

1. **`page.waitForTimeout()`** — never use hard waits. Use `expect()` auto-retry or `page.waitForResponse()` instead. Hard waits are the #1 source of flaky tests.
2. **CSS/XPath selectors** — break on every refactor. Use role/label/text locators. If you can't find a semantic locator, add a `data-testid` attribute (and fix the accessibility).
3. **Test interdependence** — tests that share state or must run in order. Every test should work in isolation. Use `storageState` + API calls to seed data, not prior tests.
4. **Testing implementation details** — checking CSS classes, DOM structure, or internal state. Test what the user sees and does.
5. **Running all browsers in CI** — run Chromium-only in CI by default (covers ~95% of bugs). Run multi-browser on a nightly schedule, not on every PR.
6. **Forgetting `--with-deps` in CI** — `playwright install` without `--with-deps` skips system dependencies (fonts, libs) and causes cryptic failures.
7. **No trace on failure** — without `trace: 'on-first-retry'` and artifact upload, CI failures are impossible to debug remotely.
8. **Giant spec files** — split by feature, not by page. `checkout.spec.ts`, `auth.spec.ts`, `search.spec.ts` — each focused on one flow.
9. **Mocking everything** — E2E tests that mock the entire backend aren't E2E tests. Mock only third-party services and error scenarios; let happy paths hit the real stack.
10. **No visual regression baseline management** — screenshots checked into git without review. Use `--update-snapshots` deliberately, review diffs in PRs.

---

## Related Skills

- `vitest` — unit/integration testing for TypeScript/JavaScript (complement to E2E)
- `pytest` — unit/integration testing for Python
- `testing-anti-patterns` — patterns that make tests unreliable (applies to E2E too)
- `test-driven-development` — TDD methodology (use Playwright for the "integration test" step)
- `github-actions` — CI/CD pipeline configuration for running E2E
