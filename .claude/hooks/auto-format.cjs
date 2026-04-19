#!/usr/bin/env node
/**
 * PostToolUse hook: auto-formats files after Write or Edit.
 * Detects file extension and runs the appropriate formatter.
 * Fails open — formatting errors are silently ignored.
 */
"use strict";

const { execSync } = require("child_process");
const path = require("path");

const FORMATTERS = {
  ".py": (f) => `ruff check --fix "${f}"`,
  ".ts": (f) => `npx eslint --fix "${f}"`,
  ".tsx": (f) => `npx eslint --fix "${f}"`,
  ".js": (f) => `npx eslint --fix "${f}"`,
  ".jsx": (f) => `npx eslint --fix "${f}"`,
};

async function main() {
  try {
    let data = "";
    for await (const chunk of process.stdin) data += chunk;
    const input = JSON.parse(data);

    const filePath = input?.tool_input?.file_path ?? "";
    if (!filePath) return;

    const ext = path.extname(filePath).toLowerCase();
    const formatter = FORMATTERS[ext];
    if (!formatter) return;

    execSync(formatter(filePath), {
      stdio: "ignore",
      timeout: 10000,
    });
  } catch {
    // Fail open — formatting errors should never block work
  }
}

main();
