# DevOps — GitHub Actions Patterns


# GitHub Actions

## When to Use

- Setting up CI/CD pipelines
- Automating tests and builds
- Deployment automation

## When NOT to Use

- GitLab CI projects using `.gitlab-ci.yml` configuration
- Jenkins pipelines using Jenkinsfile or Groovy-based configuration
- CircleCI, Travis CI, or other non-GitHub CI/CD systems

---

## Core Patterns

### 1. CI Pipeline

Complete CI workflow covering checkout, setup, install, lint, test, and build for
both Python and Node.js projects.

#### Node.js CI Pipeline

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"

      - run: corepack enable

      - run: pnpm install --frozen-lockfile

      - run: pnpm lint

      - run: pnpm typecheck

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"

      - run: corepack enable

      - run: pnpm install --frozen-lockfile

      - run: pnpm test -- --coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
          retention-days: 7

  build:
    name: Build
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"

      - run: corepack enable

      - run: pnpm install --frozen-lockfile

      - run: pnpm build

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/
          retention-days: 5
```

#### Python CI Pipeline

```yaml
name: CI - Python

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - run: pip install -r requirements-dev.txt

      - run: ruff check .

      - run: ruff format --check .

      - run: mypy src/

  test:
    name: Test
    runs-on: ubuntu-latest
    needs: lint
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U test"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/testdb
        run: pytest -v --cov=src --cov-report=xml

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: coverage.xml
          retention-days: 7
```

---

### 2. Matrix Strategy

Matrix builds run the same job across multiple combinations of OS, language
version, or other variables.

#### OS and version matrix

```yaml
jobs:
  test:
    name: Test (${{ matrix.os }}, Node ${{ matrix.node }})
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20, 22]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: "npm"

      - run: npm ci

      - run: npm test
```

#### Include and exclude

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.11", "3.12"]
        exclude:
          # Skip Python 3.11 on Windows
          - os: windows-latest
            python: "3.11"
        include:
          # Add a specific combination with extra env
          - os: ubuntu-latest
            python: "3.13"
            experimental: true
    runs-on: ${{ matrix.os }}
    continue-on-error: ${{ matrix.experimental || false }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}

      - run: pip install -r requirements.txt

      - run: pytest
```

---

### 3. Caching

Caching avoids re-downloading dependencies on every run. Use `hashFiles` to
generate cache keys from lockfiles so the cache invalidates when dependencies
change.

#### npm cache

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      npm-${{ runner.os }}-
```

#### pnpm cache

```yaml
- name: Get pnpm store directory
  id: pnpm-cache
  shell: bash
  run: echo "store=$(pnpm store path)" >> "$GITHUB_OUTPUT"

- uses: actions/cache@v4
  with:
    path: ${{ steps.pnpm-cache.outputs.store }}
    key: pnpm-${{ runner.os }}-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: |
      pnpm-${{ runner.os }}-
```

#### pip cache

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      pip-${{ runner.os }}-
```

#### Docker layer cache

```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build and push
  uses: docker/build-push-action@v6
  with:
    context: .
    push: true
    tags: myapp:latest
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

---

### 4. Reusable Workflows

Reusable workflows let you define a workflow once and call it from other
workflows, reducing duplication across repositories.

#### Defining a reusable workflow (`.github/workflows/reusable-test.yml`)

```yaml
name: Reusable Test Workflow

on:
  workflow_call:
    inputs:
      node-version:
        description: "Node.js version to use"
        required: false
        type: string
        default: "20"
      working-directory:
        description: "Directory to run commands in"
        required: false
        type: string
        default: "."
    secrets:
      NPM_TOKEN:
        required: false

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: "npm"
          registry-url: "https://registry.npmjs.org"

      - run: npm ci
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - run: npm test
```

#### Calling a reusable workflow

```yaml
name: CI

on:
  push:
    branches: [main]

jobs:
  test-app:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: "20"
      working-directory: "packages/app"
    secrets: inherit        # Pass all secrets to the called workflow

  test-lib:
    uses: ./.github/workflows/reusable-test.yml
    with:
      node-version: "20"
      working-directory: "packages/lib"
    secrets: inherit
```

---

### 5. Composite Actions

Composite actions package multiple steps into a single reusable action. Unlike
reusable workflows, they run inline within the calling job.

#### Action definition (`.github/actions/setup-project/action.yml`)

```yaml
name: "Setup Project"
description: "Install Node.js, enable corepack, and install dependencies"

inputs:
  node-version:
    description: "Node.js version"
    required: false
    default: "20"
  install-command:
    description: "Command to install dependencies"
    required: false
    default: "pnpm install --frozen-lockfile"

runs:
  using: "composite"
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}

    - name: Enable corepack
      shell: bash
      run: corepack enable

    - name: Get pnpm store directory
      id: pnpm-cache
      shell: bash
      run: echo "store=$(pnpm store path)" >> "$GITHUB_OUTPUT"

    - name: Cache pnpm store
      uses: actions/cache@v4
      with:
        path: ${{ steps.pnpm-cache.outputs.store }}
        key: pnpm-${{ runner.os }}-${{ hashFiles('**/pnpm-lock.yaml') }}
        restore-keys: |
          pnpm-${{ runner.os }}-

    - name: Install dependencies
      shell: bash
      run: ${{ inputs.install-command }}
```

#### Using the composite action

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: ./.github/actions/setup-project
        with:
          node-version: "20"

      - run: pnpm build
```

---

### 6. Deployment

Deployment workflows with environment protection rules, manual approval gates,
and multi-stage promotion.

```yaml
name: Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: "Target environment"
        required: true
        type: choice
        options:
          - staging
          - production

permissions:
  contents: read
  deployments: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: "pnpm"

      - run: corepack enable && pnpm install --frozen-lockfile

      - run: pnpm build

      - uses: actions/upload-artifact@v4
        with:
          name: build-output
          path: dist/

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/

      - name: Deploy to staging
        env:
          DEPLOY_TOKEN: ${{ secrets.STAGING_DEPLOY_TOKEN }}
        run: |
          echo "Deploying to staging..."
          # Replace with your actual deploy command
          # e.g., aws s3 sync, rsync, wrangler publish, etc.

  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production'
    environment:
      name: production
      url: https://example.com
    # Production environment should have required reviewers configured
    # in GitHub Settings > Environments > production > Protection rules
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: build-output
          path: dist/

      - name: Deploy to production
        env:
          DEPLOY_TOKEN: ${{ secrets.PRODUCTION_DEPLOY_TOKEN }}
        run: |
          echo "Deploying to production..."
```

---

### 7. Artifacts

Artifacts let you share data between jobs in the same workflow or persist build
outputs for later download.

#### Upload artifact

```yaml
- name: Upload test results
  uses: actions/upload-artifact@v4
  if: always()    # Upload even if tests fail
  with:
    name: test-results-${{ matrix.os }}-${{ matrix.node }}
    path: |
      test-results/
      coverage/
    retention-days: 14
    if-no-files-found: warn    # warn, error, or ignore
```

#### Download artifact in another job

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  deploy:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - run: ls -la dist/
```

#### Download all artifacts

```yaml
- uses: actions/download-artifact@v4
  with:
    path: all-artifacts/
    # Each artifact is placed in a subdirectory named after the artifact
```

---

### 8. Conditional Execution

Control when jobs and steps run using `if` expressions, job dependencies, and
path filters.

#### Path filters on triggers

```yaml
on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "package.json"
      - "pnpm-lock.yaml"
    paths-ignore:
      - "docs/**"
      - "*.md"
```

#### Conditional jobs

```yaml
jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      backend: ${{ steps.filter.outputs.backend }}
      frontend: ${{ steps.filter.outputs.frontend }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            backend:
              - 'src/api/**'
              - 'requirements*.txt'
            frontend:
              - 'src/web/**'
              - 'package.json'

  test-backend:
    needs: changes
    if: needs.changes.outputs.backend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt && pytest

  test-frontend:
    needs: changes
    if: needs.changes.outputs.frontend == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
```

#### Conditional steps with if expressions

```yaml
steps:
  - name: Run only on main branch
    if: github.ref == 'refs/heads/main'
    run: echo "On main"

  - name: Run only on pull requests
    if: github.event_name == 'pull_request'
    run: echo "PR event"

  - name: Run only when previous step failed
    if: failure()
    run: echo "Something failed"

  - name: Always run (cleanup)
    if: always()
    run: echo "Cleanup"

  - name: Run only when a label is present
    if: contains(github.event.pull_request.labels.*.name, 'deploy')
    run: echo "Deploy label found"

  - name: Skip for dependabot
    if: github.actor != 'dependabot[bot]'
    run: npm test
```

#### Job dependencies

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Linting..."

  test:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing..."

  # Runs after both lint and test succeed
  deploy:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - run: echo "Deploying..."

  # Runs even if test fails, but only after it completes
  notify:
    runs-on: ubuntu-latest
    needs: [test]
    if: always()
    steps:
      - run: echo "Test job status: ${{ needs.test.result }}"
```

---

## Best Practices

1. **Pin action versions with SHA** -- Use the full commit SHA instead of a
   mutable tag: `actions/checkout@b4ffde65f...` (or at minimum a major version
   tag like `@v4`). This prevents supply-chain attacks where a tag is moved.

2. **Use caching aggressively** -- Cache package manager stores (`~/.npm`,
   pnpm store, `~/.cache/pip`) and Docker layers. A well-cached pipeline can
   cut run times by 50-80%.

3. **Set minimal permissions** -- Add a top-level `permissions` block and grant
   only what is needed. Default permissions are overly broad and pose a security
   risk, especially for pull requests from forks.

4. **Run jobs in parallel** -- Structure independent jobs (lint, test, typecheck)
   to run concurrently. Use `needs` only when there is a real dependency between
   jobs.

5. **Use `fail-fast: false` in matrix builds** -- By default a failing matrix
   combination cancels all others. Setting `fail-fast: false` lets all
   combinations complete so you get the full picture of what is broken.

6. **Use environment protection rules** -- Configure required reviewers and wait
   timers on production environments in GitHub Settings. This adds a human gate
   before production deploys.

7. **Extract reusable workflows and composite actions** -- If the same steps
   appear in multiple workflows, factor them into a reusable workflow
   (`workflow_call`) or composite action to keep things DRY.

8. **Keep secrets out of logs** -- Never `echo` a secret. GitHub masks known
   secrets, but dynamically constructed values may leak. Use `::add-mask::` for
   runtime values that should be hidden.

---

## Common Pitfalls

1. **Unpinned action versions** -- Using `actions/checkout@main` means your
   workflow pulls whatever is on main today. A bad push to that action
   repository could break or compromise your builds. Pin to a tag (`@v4`) or
   SHA.

2. **Missing caching** -- Running `npm ci` or `pip install` from scratch on
   every run wastes minutes. Always configure caching for your package manager,
   or use the built-in `cache` option in setup actions (e.g.,
   `actions/setup-node` has a `cache` input).

3. **Overly broad triggers** -- Triggering on every push to every branch floods
   the queue. Restrict triggers to `main` and pull requests. Use `paths` or
   `paths-ignore` to skip runs when only docs or unrelated files change.

4. **Secret exposure in pull requests from forks** -- Secrets are NOT available
   in workflows triggered by `pull_request` from forks (by design). If your
   workflow needs secrets for fork PRs, use `pull_request_target` carefully and
   never check out untrusted code in that context.

5. **Large artifacts without retention limits** -- Uploading artifacts without
   setting `retention-days` uses the repository default (90 days), consuming
   storage quota. Set short retention for transient artifacts like test results
   and coverage reports.

6. **Ignoring `if: always()` for cleanup** -- Steps after a failure are skipped
   by default. If you need to upload test results, send notifications, or run
   cleanup regardless of prior step results, use `if: always()` or
   `if: failure()`.

---

## Related Skills

- `docker` - Container patterns for building and deploying Dockerized applications in workflows
- `pytest` - Python test configuration for CI pipeline integration
- `vitest` - TypeScript/JavaScript test configuration for CI pipeline integration
