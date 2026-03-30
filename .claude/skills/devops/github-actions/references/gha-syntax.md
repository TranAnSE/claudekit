# GitHub Actions Syntax Quick Reference
## Workflow File Structure

```yaml
name: CI                          # Workflow name (shown in GitHub UI)

on:                               # Triggers
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:                      # Workflow-level permissions
  contents: read

env:                              # Workflow-level environment variables
  NODE_ENV: test

jobs:
  build:                          # Job ID
    runs-on: ubuntu-latest        # Runner
    steps:
      - uses: actions/checkout@v4 # Action step
      - run: echo "Hello"         # Shell step
```

## Triggers (on:)

### Common Events

```yaml
on:
  push:
    branches: [main, "release/**"]
    paths: ["src/**", "!src/**/*.test.ts"]   # Path filtering
    tags: ["v*"]
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
  workflow_dispatch:                           # Manual trigger
    inputs:
      environment:
        type: choice
        options: [staging, production]
  schedule:
    - cron: "0 6 * * 1"                      # Every Monday at 6am UTC
  release:
    types: [published]
  workflow_call:                               # Reusable workflow
    inputs:
      node-version: { type: string, default: "22" }
    secrets:
      NPM_TOKEN: { required: true }
```

## Jobs

```yaml
jobs:
  test:
    name: Run Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - run: npm test
  deploy:
    needs: [lint, test]           # Runs after lint AND test succeed
    runs-on: ubuntu-latest
    steps: [...]
```

### Matrix Strategy

```yaml
jobs:
  test:
    strategy:
      fail-fast: false            # Don't cancel other jobs on failure
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [20, 22]
        exclude:
          - os: macos-latest
            node: 20
        include:
          - os: ubuntu-latest
            node: 22
            coverage: true
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

## Steps

### Action Step

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0                # Full history (needed for some tools)

- uses: actions/setup-node@v4
  with:
    node-version-file: ".nvmrc"
    cache: "pnpm"
```

### Shell Step

```yaml
- name: Run tests
  run: npm test
  working-directory: ./packages/api
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  shell: bash
  continue-on-error: true         # Don't fail the job
  timeout-minutes: 10
```

### Multi-line Commands

```yaml
- run: |
    echo "Line 1"
    echo "Line 2"
    npm run build
```

## Conditionals (if:)

```yaml
# Run only on main branch
- if: github.ref == 'refs/heads/main'

# Run only on pull requests
- if: github.event_name == 'pull_request'

# Run only when previous step failed
- if: failure()

# Always run (even if previous steps failed)
- if: always()

# Run only when a matrix variable is set
- if: matrix.coverage == true

# Run based on changed files (requires dorny/paths-filter or similar)
- if: steps.filter.outputs.backend == 'true'

# Run on specific actor
- if: github.actor != 'dependabot[bot]'
```

## Environment and Secrets

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://example.com
    env:
      APP_VERSION: ${{ github.sha }}
    steps:
      - run: deploy.sh
        env:
          API_KEY: ${{ secrets.API_KEY }}             # Repository secret
          DEPLOY_TOKEN: ${{ vars.DEPLOY_TOKEN }}      # Repository variable
```

## Caching

### Built-in Cache (setup actions)

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: 22
    cache: "pnpm"                  # Automatic pnpm cache
```

### Manual Cache

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .mypy_cache
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

## Artifacts

### Upload

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: coverage-report
    path: coverage/
    retention-days: 7
```

### Download (in another job)

```yaml
- uses: actions/download-artifact@v4
  with:
    name: coverage-report
    path: ./coverage
```

## Services (Containers)

Define `services:` under a job with `image`, `env`, `ports`, and `options` (for health checks). Common: postgres, redis, mysql.

## Outputs (Passing Data Between Steps/Jobs)

```yaml
# Step output: echo "key=value" >> "$GITHUB_OUTPUT"
# Read in later step: ${{ steps.<step-id>.outputs.key }}
# Job output: declare under jobs.<job>.outputs, read via needs.<job>.outputs.key
```

## Permissions

Common values: `contents: read`, `pull-requests: write`, `issues: write`, `packages: write`, `id-token: write` (OIDC).

## Reusable Workflows

Caller uses `uses: ./.github/workflows/reusable.yaml` with `with:` and `secrets: inherit`. Callee triggers on `workflow_call:` with `inputs:` and `secrets:` definitions.

## Useful Expressions

| Expression | Result |
|-----------|--------|
| `${{ github.sha }}` | Full commit SHA |
| `${{ github.ref_name }}` | Branch or tag name |
| `${{ github.event.pull_request.number }}` | PR number |
| `${{ runner.os }}` | `Linux`, `macOS`, `Windows` |
| `${{ hashFiles('**/lockfile') }}` | SHA256 of files |
| `${{ contains(github.event.head_commit.message, '[skip ci]') }}` | Check commit message |
