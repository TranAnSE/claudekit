# API Governance & Tooling

Linters, docs generators, client generators, mock servers, and contract testing tools for an OpenAPI-based workflow. Focus on what is actually used in 2026.

---

## Why governance matters

Specs drift. A hand-written spec that is not linted in CI will accumulate missing `operationId`s, inline schemas, undocumented errors, and inconsistent naming within weeks. A generated spec (from FastAPI/NestJS) will drift toward whatever the framework emits, which is rarely idiomatic.

**Minimum bar for any new API:**
1. Spec lives in version control
2. A linter runs on every PR
3. Docs regenerate on merge to main
4. At least one generated client (or contract test) catches breaking changes

---

## Linters

All three below consume the same Spectral-compatible rule format.

| Tool | Language | Speed | When to pick |
|------|----------|-------|--------------|
| **Spectral** (Stoplight) | Node | Moderate | Default choice. Largest rule ecosystem, first-party Redocly + Zalando rulesets. |
| **Redocly CLI** | Node | Moderate | Pick if you also want `bundle`, `split`, and `build-docs` in one tool. Ships its own opinionated ruleset. |
| **Vacuum** (daveshanley) | Go | 10–20× faster | Pick for large specs (500+ operations) or monorepo CI where seconds matter. Drop-in Spectral rule compatibility. |

### Minimum Spectral ruleset

Save as `.spectral.yaml` in the spec directory:

```yaml
extends:
  - spectral:oas          # Base OpenAPI rules
  - spectral:asyncapi     # If you mix in AsyncAPI

rules:
  # Every operation must be identified, tagged, and summarized
  operation-operationId:           error
  operation-operationId-unique:    error
  operation-tags:                  error
  operation-summary:               error
  operation-description:           warn

  # Schemas must be referenced, not inlined
  no-inline-schemas:
    description: Request/response bodies must $ref a named schema.
    severity: error
    given: "$.paths.*.*.requestBody.content.*.schema"
    then:
      field: "$ref"
      function: truthy

  # No 3.0-isms in a 3.1 document
  no-nullable:
    description: "Use type: [T, 'null'] instead of nullable: true in 3.1."
    severity: error
    given: "$..nullable"
    then:
      function: falsy

  # Enforce camelCase on JSON properties
  camel-case-properties:
    description: Property names must be camelCase.
    severity: error
    given: "$.components.schemas..properties[*]~"
    then:
      function: pattern
      functionOptions:
        match: "^[a-z][a-zA-Z0-9]*$"

  # Every operation declares at least one 4xx and one 5xx response
  operation-4xx-response:
    severity: error
    given: "$.paths.*.*.responses"
    then:
      function: schema
      functionOptions:
        schema:
          type: object
          patternProperties:
            "^4\\d\\d$": {}
          minProperties: 1

  # Error bodies use application/problem+json
  error-uses-problem-json:
    description: 4xx/5xx responses must use application/problem+json.
    severity: warn
    given: "$.paths.*.*.responses[?(@property.match(/^[45]\\d\\d$/))].content"
    then:
      field: "application/problem+json"
      function: truthy
```

### GitHub Actions CI snippet

```yaml
# .github/workflows/api-spec.yml
name: API spec
on:
  pull_request:
    paths: ['spec/**']
  push:
    branches: [main]
    paths: ['spec/**']

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }

      - name: Bundle spec
        run: npx @redocly/cli@latest bundle spec/openapi.yaml -o spec/openapi.bundled.yaml

      - name: Lint with Spectral
        run: npx @stoplight/spectral-cli@latest lint spec/openapi.bundled.yaml --fail-severity=error

      - name: Detect breaking changes vs main
        if: github.event_name == 'pull_request'
        run: |
          git fetch origin main
          npx @redocly/cli@latest diff origin/main:spec/openapi.yaml spec/openapi.yaml --fail-on=breaking
```

The `diff --fail-on=breaking` step blocks PRs that remove fields, change types, or rename operations — the most common accidental breakages.

---

## Docs Generators

| Tool | Style | When to pick |
|------|-------|--------------|
| **Scalar** | Modern three-column with built-in REST client | Default choice for new projects. Fast, polished, open source. |
| **Redoc** | Classic three-column reference (Stripe-like) | Pick when you want the most battle-tested static docs. Works offline. |
| **Redocly Portal** | Hosted docs with analytics, try-it, versioning | Pick when you need a revenue-class docs portal. Paid. |
| **Swagger UI** | Interactive try-it | Pick only for internal/debug dashboards. Aesthetics lag behind Scalar/Redoc. |

### Scalar (recommended default)

```html
<!-- docs.html -->
<!doctype html>
<html>
<head><title>My API</title></head>
<body>
  <script id="api-reference" data-url="/openapi.yaml"></script>
  <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
</body>
</html>
```

### Redoc (static build)

```bash
npx @redocly/cli build-docs spec/openapi.yaml -o dist/api.html
```

Deploy the single HTML file to any static host (Cloudflare Pages, S3, GitHub Pages).

---

## Client Generation

| Tool | Targets | When to pick |
|------|---------|--------------|
| **Kubb** | TypeScript (Zod, TanStack Query, SWR, MSW, Axios, Fetch) | Default for 2026 frontend. Plugin-based, generates exactly what you want, no framework bloat. |
| **Orval** | TypeScript (React Query, SWR, Zod, MSW, Axios) | Close alternative to Kubb. Pick if you prefer a single-config approach. |
| **openapi-generator** | 30+ languages (Python, Go, Java, Kotlin, Ruby, Rust, etc.) | Default for non-TypeScript languages. The workhorse, but generated code is heavier. |
| **openapi-ts** (hey-api) | TypeScript only, lightweight | Pick when you want a minimal fetch wrapper with full types and zero framework coupling. |

### Kubb starter (TypeScript + TanStack Query + Zod)

```ts
// kubb.config.ts
import { defineConfig } from '@kubb/core'
import { pluginOas } from '@kubb/plugin-oas'
import { pluginTs } from '@kubb/plugin-ts'
import { pluginZod } from '@kubb/plugin-zod'
import { pluginClient } from '@kubb/plugin-client'
import { pluginReactQuery } from '@kubb/plugin-react-query'

export default defineConfig({
  input:  { path: './spec/openapi.yaml' },
  output: { path: './src/api/generated', clean: true },
  plugins: [
    pluginOas(),
    pluginTs(),
    pluginZod(),
    pluginClient({ importPath: '../client.ts' }),
    pluginReactQuery(),
  ],
})
```

### openapi-generator (Python / Go / Java / etc.)

```bash
npx @openapitools/openapi-generator-cli generate \
  -i spec/openapi.yaml \
  -g python \
  -o clients/python \
  --additional-properties=packageName=acme_client,library=asyncio
```

---

## Mock Servers

| Tool | When to pick |
|------|--------------|
| **Prism** (Stoplight) | Run a mock server directly from your spec. Validates requests against the schema and returns examples. Best for frontend dev against an unfinished backend. |
| **MSW** (Mock Service Worker) | Runs in the browser/Node for testing client code. Pair with Kubb's `@kubb/plugin-msw` to generate handlers from the spec. |

### Prism starter

```bash
npx @stoplight/prism-cli mock spec/openapi.yaml --port 4010
# Server at http://127.0.0.1:4010 responds based on the spec examples
```

Add `--errors` to make Prism return the declared error responses when the request is invalid, useful for exercising error paths.

---

## Contract Testing

Tools that verify the running implementation still matches the spec.

| Tool | Approach | When to pick |
|------|----------|--------------|
| **Schemathesis** | Property-based fuzzing driven by the spec | Best signal per line of setup. Catches unhandled edge cases the developer never thought to test. |
| **Dredd** | Replays documented examples against the server | Simple smoke-test. Good for regression on happy paths. |
| **Pact** | Consumer-driven contracts (not spec-first) | Pick when consumers write the contracts rather than deriving from the server's OpenAPI. |

### Schemathesis in CI

```bash
pipx install schemathesis
schemathesis run spec/openapi.yaml \
  --base-url=http://localhost:3000/v1 \
  --checks=all \
  --hypothesis-max-examples=50
```

Runs ~50 generated requests per operation and checks: status code validity, response schema conformance, `Content-Type` match, and absence of server errors (5xx).

---

## Governance checklist

Before calling an API "production-ready":

- [ ] Spec is in version control alongside the code
- [ ] Spec is bundled (`redocly bundle`) and the bundled artifact is linted
- [ ] Spectral (or equivalent) runs on every PR and blocks on errors
- [ ] A breaking-change check runs on every PR (`redocly diff` or `oasdiff`)
- [ ] Every operation has `operationId`, `tags`, `summary`, at least one `4xx` and at least one `5xx` response
- [ ] Docs are regenerated on merge to main (Scalar, Redoc, or portal)
- [ ] At least one generated client is compiled in CI — proves the spec is consumable
- [ ] Contract tests run against a deployed preview before merge
- [ ] A mock server (Prism) is available for consumer development

---

## Related

- [rest-naming.md](rest-naming.md) — URL and naming conventions
- [http-status-codes.md](http-status-codes.md) — status code selection
- [production-patterns.md](production-patterns.md) — idempotency, rate limiting, ETags, webhook signing
- [openapi.tools](https://openapi.tools/) — community catalog of all OpenAPI tools
