/// <reference types="vitest/config" />
import { defineConfig } from "vitest/config";
import path from "node:path";

export default defineConfig({
  // -------------------------------------------------------------------------
  // Path aliases -- must match tsconfig.json "paths"
  // -------------------------------------------------------------------------
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@test": path.resolve(__dirname, "test"),
    },
  },

  test: {
    // -----------------------------------------------------------------------
    // Environment
    // -----------------------------------------------------------------------
    // "node"   -- default, for backend / library code
    // "jsdom"  -- for code that accesses DOM APIs (React, etc.)
    // "happy-dom" -- faster jsdom alternative
    environment: "jsdom",

    // -----------------------------------------------------------------------
    // Globals
    // -----------------------------------------------------------------------
    // Set to true to use describe/it/expect without importing from "vitest".
    // Requires adding "vitest/globals" to tsconfig "types".
    globals: true,

    // -----------------------------------------------------------------------
    // Setup files -- run before each test file
    // -----------------------------------------------------------------------
    setupFiles: [
      "./test/setup.ts",
      // "./test/mocks/server.ts",  // MSW server setup
    ],

    // -----------------------------------------------------------------------
    // File patterns
    // -----------------------------------------------------------------------
    include: [
      "src/**/*.{test,spec}.{ts,tsx}",
      "test/**/*.{test,spec}.{ts,tsx}",
    ],
    exclude: [
      "node_modules",
      "dist",
      "e2e/**",
    ],

    // -----------------------------------------------------------------------
    // Coverage
    // -----------------------------------------------------------------------
    coverage: {
      provider: "v8", // or "istanbul"
      reporter: ["text", "text-summary", "lcov", "json"],
      reportsDirectory: "./coverage",

      include: ["src/**/*.{ts,tsx}"],
      exclude: [
        "src/**/*.d.ts",
        "src/**/*.test.{ts,tsx}",
        "src/**/*.spec.{ts,tsx}",
        "src/**/index.ts", // barrel files
        "src/types/**",
      ],

      // Minimum thresholds -- fail if coverage drops below these.
      thresholds: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80,
      },
    },

    // -----------------------------------------------------------------------
    // Timeouts
    // -----------------------------------------------------------------------
    testTimeout: 10_000,     // 10s per test
    hookTimeout: 10_000,     // 10s per beforeEach/afterEach

    // -----------------------------------------------------------------------
    // Reporters
    // -----------------------------------------------------------------------
    reporters: ["default"],
    // For CI, add JUnit output:
    // reporters: ["default", "junit"],
    // outputFile: { junit: "./junit.xml" },

    // -----------------------------------------------------------------------
    // Other options
    // -----------------------------------------------------------------------
    // restoreMocks: true,    // Automatically restore mocks after each test
    // clearMocks: true,      // Clear mock call history after each test
    // mockReset: true,       // Reset mocks (clear + remove implementations)
  },
});
