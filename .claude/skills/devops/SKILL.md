---
name: devops
description: >
  Use when containerizing applications, configuring CI/CD pipelines, deploying to environments, or deploying to edge — including Docker, Dockerfile, docker-compose, multi-stage builds, GitHub Actions, workflow YAML, matrix builds, workflow_dispatch, Cloudflare Workers, Pages, R2, D1, KV, wrangler, container registries, or deployment workflows (staging, production, health checks, smoke tests).
---

# DevOps

## When to Use

- Containerizing applications with Docker or Docker Compose
- Setting up CI/CD pipelines with GitHub Actions
- Deploying to Cloudflare Workers, Pages, R2, D1, or KV
- Deploying applications to staging or production environments
- Running pre-deploy checks (build, tests, security audit)
- Optimizing container images, build caching, or deployment workflows
- Configuring wrangler.toml, Durable Objects, or Cloudflare Queues

## When NOT to Use

- Application code without infrastructure concerns — use framework-specific skills
- Database schema changes — use `databases`
- Security auditing — use `owasp`

---

## Quick Reference

| Topic | Reference | Key features |
|-------|-----------|-------------|
| Docker | `references/docker.md` | Dockerfiles, multi-stage builds, Compose, .dockerignore, healthchecks |
| GitHub Actions | `references/github-actions.md` | Workflow YAML, matrix builds, caching, secrets, reusable workflows |
| Cloudflare Workers | `references/cloudflare-workers.md` | Workers, Pages, R2, D1, KV, Durable Objects, wrangler |

---

## Best Practices

1. **Use multi-stage builds** to keep production images small (Docker).
2. **Pin image tags and action versions** — use digests or major version tags, never `latest`.
3. **Order instructions for cache efficiency** — copy dependency manifests before application code (Docker).
4. **Run as non-root** in containers (Docker).
5. **Use caching aggressively** in CI — cache package manager stores and Docker layers (GitHub Actions).
6. **Set minimal permissions** — add a top-level `permissions` block (GitHub Actions).
7. **Extract reusable workflows and composite actions** for shared CI logic (GitHub Actions).
8. **Keep secrets out of logs** — never `echo` a secret (GitHub Actions).

## Common Pitfalls

1. **Bloated images** — using full base images instead of slim/alpine variants (Docker).
2. **Cache invalidation by COPY order** — placing `COPY . .` before `RUN pip install` (Docker).
3. **Secrets baked into layers** (Docker).
4. **Unpinned action versions** (GitHub Actions).
5. **Overly broad triggers** — triggering on every push to every branch (GitHub Actions).
6. **Secret exposure in pull requests from forks** (GitHub Actions).
7. **Using Node.js APIs without `nodejs_compat`** (Cloudflare Workers).
8. **Blocking the event loop** — Workers have strict CPU time limits (Cloudflare Workers).
9. **Using KV for frequently updated data** — eventually consistent with ~60s propagation (Cloudflare Workers).

---

## Related Skills

- `backend-frameworks` — Application code that gets containerized
- `databases` — Database services in Docker Compose
- `owasp` — Security hardening for containers and CI
