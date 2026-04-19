#!/usr/bin/env node
/**
 * Notification hook: cross-platform desktop notification.
 * Supports macOS (osascript), Linux (notify-send), and Windows (PowerShell).
 * Fails open — notification errors are silently ignored.
 */
"use strict";

const { execSync } = require("child_process");
const os = require("os");

function notify(title, message) {
  const platform = os.platform();

  const commands = {
    darwin: `osascript -e 'display notification "${message}" with title "${title}"'`,
    linux: `notify-send "${title}" "${message}"`,
    win32: `powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('${message}', '${title}', 'OK', 'Information')"`,
  };

  const cmd = commands[platform];
  if (cmd) {
    execSync(cmd, { stdio: "ignore", timeout: 5000 });
  }
}

async function main() {
  try {
    let data = "";
    for await (const chunk of process.stdin) data += chunk;
    const input = JSON.parse(data);

    const message = input?.message ?? "Needs your attention";
    notify("Claude Code", message);
  } catch {
    // Fail open — notification errors should never block work
  }
}

main();
