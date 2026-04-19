# E2E Testing Patterns

Deep-dive patterns for Playwright E2E tests. The main SKILL.md covers the essentials; this reference covers scaling patterns, data management, and anti-flake strategies.

---

## Page Object Model (Scaling Pattern)

Use Page Objects when a suite grows beyond ~20 tests and multiple specs interact with the same pages. Keep them thin — locators and actions only, no assertions.

```typescript
// e2e/pages/login.page.ts
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorAlert: Locator;

  constructor(private readonly page: Page) {
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorAlert = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

```typescript
// e2e/specs/auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

test('valid credentials redirect to dashboard', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin@example.com', 'test-password');
  await expect(page).toHaveURL('/dashboard');
});

test('invalid credentials show error', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('admin@example.com', 'wrong');
  await expect(loginPage.errorAlert).toContainText('Invalid credentials');
});
```

**When to use Page Objects vs inline locators:**
- **< 20 tests:** inline locators in each spec (simpler, less indirection)
- **20-50 tests:** locator helper functions or fixtures
- **50+ tests:** full Page Object Model with fixtures for injection

---

## Test Data Management

### API-based seeding (recommended)

Seed data via API calls in fixtures or `beforeAll`, not through the UI.

```typescript
// e2e/helpers/api.ts
export async function createTestUser(request: APIRequestContext) {
  const response = await request.post('/api/v1/users', {
    data: {
      email: `test-${Date.now()}@example.com`,
      name: 'Test User',
      role: 'member',
    },
    headers: { Authorization: `Bearer ${process.env.TEST_API_TOKEN}` },
  });
  return response.json();
}

export async function deleteTestUser(request: APIRequestContext, userId: string) {
  await request.delete(`/api/v1/users/${userId}`, {
    headers: { Authorization: `Bearer ${process.env.TEST_API_TOKEN}` },
  });
}
```

```typescript
// e2e/specs/user-management.spec.ts
import { test, expect } from '@playwright/test';
import { createTestUser, deleteTestUser } from '../helpers/api';

test.describe('User management', () => {
  let testUser: { id: string; email: string };

  test.beforeAll(async ({ request }) => {
    testUser = await createTestUser(request);
  });

  test.afterAll(async ({ request }) => {
    await deleteTestUser(request, testUser.id);
  });

  test('user appears in list', async ({ page }) => {
    await page.goto('/admin/users');
    await expect(page.getByText(testUser.email)).toBeVisible();
  });
});
```

### Database seeding (alternative)

For complex data, seed directly via a test database. Use `globalSetup` to reset the DB and `beforeAll` per suite for specific records.

```typescript
// e2e/global-setup.ts (addition)
import { execSync } from 'child_process';

async function globalSetup() {
  // Reset test database
  execSync('pnpm db:reset --force', { env: { ...process.env, DATABASE_URL: process.env.TEST_DATABASE_URL } });
  execSync('pnpm db:seed', { env: { ...process.env, DATABASE_URL: process.env.TEST_DATABASE_URL } });

  // ... auth setup ...
}
```

---

## Anti-Flake Strategies

### Disable animations globally

```typescript
// e2e/fixtures.ts
import { test as base } from '@playwright/test';

export const test = base.extend({
  page: async ({ page }, use) => {
    await page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `,
    });
    await use(page);
  },
});
```

### Wait for network idle after navigation

```typescript
test('dashboard loads fully', async ({ page }) => {
  await page.goto('/dashboard');
  // Wait for the specific content, not generic network idle
  await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  await expect(page.getByRole('table')).toBeVisible();
});
```

**Never use `page.waitForLoadState('networkidle')`** for SPAs — it fires prematurely when the initial HTML loads but React hasn't rendered yet. Wait for the specific element you care about.

### Retry flaky assertions with custom timeout

```typescript
// For a known-slow operation
await expect(page.getByText('Report generated')).toBeVisible({ timeout: 30_000 });
```

### Isolate test state with fresh contexts

```typescript
test.describe('shopping cart', () => {
  test.use({ storageState: undefined }); // Fresh guest for each test

  test('add item to cart', async ({ page }) => {
    // This test starts with an empty cart every time
  });
});
```

---

## Multi-Role Testing

Test different user roles in separate projects or fixtures.

```typescript
// playwright.config.ts
projects: [
  { name: 'setup', testMatch: /.*\.setup\.ts/ },
  {
    name: 'admin',
    use: { storageState: 'e2e/.auth/admin.json' },
    dependencies: ['setup'],
    testMatch: /.*\.admin\.spec\.ts/,
  },
  {
    name: 'member',
    use: { storageState: 'e2e/.auth/member.json' },
    dependencies: ['setup'],
    testMatch: /.*\.member\.spec\.ts/,
  },
  {
    name: 'guest',
    testMatch: /.*\.guest\.spec\.ts/,
  },
],
```

Or use fixtures for per-test role selection:

```typescript
// e2e/fixtures.ts
type Accounts = {
  adminPage: Page;
  memberPage: Page;
};

export const test = base.extend<Accounts>({
  adminPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'e2e/.auth/admin.json' });
    await use(await ctx.newPage());
    await ctx.close();
  },
  memberPage: async ({ browser }, use) => {
    const ctx = await browser.newContext({ storageState: 'e2e/.auth/member.json' });
    await use(await ctx.newPage());
    await ctx.close();
  },
});
```

---

## Network Interception Patterns

### Wait for a specific API response before asserting

```typescript
test('submitting form shows success', async ({ page }) => {
  await page.goto('/settings');

  const responsePromise = page.waitForResponse(
    (resp) => resp.url().includes('/api/v1/settings') && resp.status() === 200,
  );

  await page.getByRole('button', { name: 'Save' }).click();
  await responsePromise;

  await expect(page.getByText('Settings saved')).toBeVisible();
});
```

### Mock a third-party service

```typescript
test('shows map with mocked geocoding', async ({ page }) => {
  await page.route('**/maps.googleapis.com/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: [{ geometry: { location: { lat: 37.7749, lng: -122.4194 } } }],
      }),
    }),
  );

  await page.goto('/locations/new');
  await page.getByLabel('Address').fill('123 Main St');
  await page.getByRole('button', { name: 'Lookup' }).click();
  await expect(page.getByTestId('map-marker')).toBeVisible();
});
```

### Simulate slow network

```typescript
test('shows loading state on slow network', async ({ page, context }) => {
  await context.route('**/api/**', async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 3000));
    await route.continue();
  });

  await page.goto('/dashboard');
  await expect(page.getByRole('progressbar')).toBeVisible();
});
```

---

## Accessibility Patterns

### Scan all critical pages in a single test file

```typescript
// e2e/specs/a11y.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const pages = ['/', '/login', '/dashboard', '/settings', '/users'];

for (const path of pages) {
  test(`${path} has no critical a11y violations`, async ({ page }) => {
    await page.goto(path);

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .exclude('.third-party-widget')
      .analyze();

    expect(results.violations.filter((v) => v.impact === 'critical')).toEqual([]);
  });
}
```

### Assert specific a11y rules

```typescript
test('form has proper labels', async ({ page }) => {
  await page.goto('/signup');

  const results = await new AxeBuilder({ page })
    .include('form')
    .withRules(['label', 'input-button-name'])
    .analyze();

  expect(results.violations).toEqual([]);
});
```

---

## Debugging Checklist

When a test fails in CI:

1. **Download the trace artifact** from GitHub Actions
2. **Open with:** `npx playwright show-trace trace.zip`
3. **Check the timeline:** click through each action to see DOM snapshots
4. **Check the console tab:** look for JS errors or failed requests
5. **Check the network tab:** did an API call fail or return unexpected data?
6. **If flaky:** run locally with `npx playwright test path/to/test --repeat-each=20`
7. **If environment-specific:** compare screenshots from CI vs local
8. **If timing-related:** replace `waitForTimeout` with `expect().toBeVisible()` or `waitForResponse()`

---

## Related

- [templates/playwright.config.ts](../templates/playwright.config.ts) — starter config
- [Playwright official docs](https://playwright.dev/docs/intro)
- [Playwright best practices](https://playwright.dev/docs/best-practices)
