import { defineConfig, devices } from '@playwright/test';

/**
 * Production-grade Playwright config.
 *
 * Includes: multi-browser projects, mobile emulation, auth via storageState,
 * trace-on-first-retry, CI-aware retries, webServer auto-start, and sharding.
 *
 * Copy to your project root and customize baseURL, webServer command, and
 * storageState paths.
 */
export default defineConfig({
  testDir: './e2e/specs',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,

  reporter: process.env.CI
    ? [['html'], ['github'], ['json', { outputFile: 'e2e/results.json' }]]
    : [['html']],

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // --- Auth setup (runs first) ---
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },

    // --- Desktop browsers ---
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState: 'e2e/.auth/user.json',
      },
      dependencies: ['setup'],
    },
    // Uncomment for multi-browser (nightly or pre-release, not every PR):
    // {
    //   name: 'firefox',
    //   use: {
    //     ...devices['Desktop Firefox'],
    //     storageState: 'e2e/.auth/user.json',
    //   },
    //   dependencies: ['setup'],
    // },
    // {
    //   name: 'webkit',
    //   use: {
    //     ...devices['Desktop Safari'],
    //     storageState: 'e2e/.auth/user.json',
    //   },
    //   dependencies: ['setup'],
    // },

    // --- Mobile emulation ---
    // {
    //   name: 'mobile-chrome',
    //   use: {
    //     ...devices['Pixel 7'],
    //     storageState: 'e2e/.auth/user.json',
    //   },
    //   dependencies: ['setup'],
    // },
    // {
    //   name: 'mobile-safari',
    //   use: {
    //     ...devices['iPhone 14'],
    //     storageState: 'e2e/.auth/user.json',
    //   },
    //   dependencies: ['setup'],
    // },

    // --- Guest (unauthenticated) tests ---
    {
      name: 'guest',
      use: {
        ...devices['Desktop Chrome'],
      },
      testMatch: /.*\.guest\.spec\.ts/,
    },
  ],

  // --- Auto-start the dev server ---
  webServer: {
    command: 'pnpm dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },

  // --- Global setup for auth ---
  globalSetup: './e2e/global-setup.ts',
});
