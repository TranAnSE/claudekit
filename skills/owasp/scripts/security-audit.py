#!/usr/bin/env python3
"""Security audit scanner for common vulnerabilities.

Scans source files for hardcoded secrets, eval() usage, SQL string
concatenation, and sensitive data in console output. Outputs JSON.

Usage:
    python security-audit.py ./src
    python security-audit.py ./src --severity high --format pretty
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go",
    ".rb", ".php", ".env", ".yaml", ".yml", ".toml", ".json",
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "vendor",
}


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    severity: str
    message: str
    snippet: str


@dataclass
class AuditReport:
    scanned_files: int = 0
    findings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)


# --- Detection Rules ---

SECRET_PATTERNS = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][A-Za-z0-9_\-]{16,}["\']', "Possible API key"),
    (r'(?i)(secret|password|passwd|pwd)\s*[=:]\s*["\'][^"\']{8,}["\']', "Possible hardcoded secret"),
    (r'(?i)(aws_access_key_id|aws_secret_access_key)\s*[=:]\s*["\'][^"\']+["\']', "AWS credential"),
    (r'(?i)bearer\s+[A-Za-z0-9_\-\.]{20,}', "Possible bearer token"),
    (r'(?i)(ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}', "GitHub token"),
    (r'(?i)(sk-|pk_live_|pk_test_|sk_live_|sk_test_)[A-Za-z0-9]{20,}', "API secret key"),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key in source"),
]

EVAL_PATTERNS = [
    (r'\beval\s*\(', "eval() usage detected"),
    (r'\bexec\s*\(', "exec() usage detected (Python)"),
    (r'new\s+Function\s*\(', "new Function() usage (dynamic code)"),
    (r'\bchild_process\.exec\s*\(', "child_process.exec (command injection risk)"),
    (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', "subprocess with shell=True"),
    (r'os\.system\s*\(', "os.system() usage (command injection risk)"),
]

SQL_PATTERNS = [
    (r'(?i)(SELECT|INSERT|UPDATE|DELETE|DROP)\s+.*([\+]|\.format\(|f["\']|%\s)', "SQL string concatenation"),
    (r'(?i)execute\s*\(\s*f["\']', "SQL f-string in execute()"),
    (r'(?i)\.query\s*\(\s*`[^`]*\$\{', "SQL template literal injection"),
    (r'(?i)\.raw\s*\(\s*f["\']', "Raw SQL with f-string"),
]

SENSITIVE_LOG_PATTERNS = [
    (r'console\.log\s*\(.*(?i)(password|secret|token|key|credential)', "Sensitive data in console.log"),
    (r'print\s*\(.*(?i)(password|secret|token|key|credential)', "Sensitive data in print()"),
    (r'logger?\.(info|debug|warn)\s*\(.*(?i)(password|secret|token)', "Sensitive data in logger"),
]

RULES = [
    ("hardcoded-secret", "high", SECRET_PATTERNS),
    ("dangerous-eval", "high", EVAL_PATTERNS),
    ("sql-injection", "high", SQL_PATTERNS),
    ("sensitive-logging", "medium", SENSITIVE_LOG_PATTERNS),
]


def should_scan(path: Path) -> bool:
    if path.suffix not in SCAN_EXTENSIONS:
        return False
    for part in path.parts:
        if part in SKIP_DIRS:
            return False
    return True


def scan_file(filepath: Path) -> list[Finding]:
    findings = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except (OSError, PermissionError):
        return findings

    lines = content.splitlines()
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "/*")):
            continue
        for rule_name, severity, patterns in RULES:
            for pattern, message in patterns:
                if re.search(pattern, line):
                    findings.append(Finding(
                        file=str(filepath),
                        line=line_num,
                        rule=rule_name,
                        severity=severity,
                        message=message,
                        snippet=line.strip()[:120],
                    ))
    return findings


def scan_directory(target: Path, severity_filter: str | None = None) -> AuditReport:
    report = AuditReport()
    severity_order = {"high": 3, "medium": 2, "low": 1}
    min_severity = severity_order.get(severity_filter, 0) if severity_filter else 0

    for root, dirs, files in os.walk(target):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            fpath = Path(root) / fname
            if not should_scan(fpath):
                continue
            report.scanned_files += 1
            for finding in scan_file(fpath):
                if severity_order.get(finding.severity, 0) >= min_severity:
                    report.findings.append(finding)

    report.summary = {
        "total": len(report.findings),
        "high": sum(1 for f in report.findings if f.severity == "high"),
        "medium": sum(1 for f in report.findings if f.severity == "medium"),
        "low": sum(1 for f in report.findings if f.severity == "low"),
        "by_rule": {},
    }
    for f in report.findings:
        report.summary["by_rule"][f.rule] = report.summary["by_rule"].get(f.rule, 0) + 1

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Scan source files for common security issues.",
        epilog="Example: python security-audit.py ./src --severity high",
    )
    parser.add_argument("target", help="Directory or file to scan")
    parser.add_argument(
        "--severity", choices=["low", "medium", "high"],
        help="Minimum severity to report (default: all)",
    )
    parser.add_argument(
        "--format", choices=["json", "pretty"], default="json",
        help="Output format (default: json)",
    )
    args = parser.parse_args()

    target = Path(args.target)
    if not target.exists():
        print(f"Error: {target} does not exist", file=sys.stderr)
        sys.exit(1)

    report = scan_directory(target, args.severity)
    output = {
        "scanned_files": report.scanned_files,
        "summary": report.summary,
        "findings": [asdict(f) for f in report.findings],
    }

    if args.format == "pretty":
        print(f"\nScanned {report.scanned_files} files\n")
        print(f"Findings: {report.summary['total']} total "
              f"({report.summary['high']} high, {report.summary['medium']} medium)")
        print("-" * 60)
        for f in report.findings:
            print(f"[{f.severity.upper()}] {f.file}:{f.line}")
            print(f"  Rule: {f.rule}")
            print(f"  {f.message}")
            print(f"  > {f.snippet}")
            print()
    else:
        print(json.dumps(output, indent=2))

    sys.exit(1 if report.summary.get("high", 0) > 0 else 0)


if __name__ == "__main__":
    main()
