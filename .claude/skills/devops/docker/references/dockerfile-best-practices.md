# Dockerfile Best Practices Reference

Quick reference for writing efficient, secure, and maintainable Dockerfiles.

## Layer Ordering for Cache Optimization

Order instructions from least-frequently-changed to most-frequently-changed:

```dockerfile
# 1. Base image                    (changes: rarely)
FROM node:22-slim

# 2. System dependencies           (changes: rarely)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. App dependency manifest       (changes: sometimes)
COPY package.json pnpm-lock.yaml ./

# 4. Install dependencies          (changes: sometimes, cached if manifests unchanged)
RUN pnpm install --frozen-lockfile

# 5. Copy source code              (changes: frequently)
COPY . .

# 6. Build step                    (changes: frequently)
RUN pnpm build

# 7. Runtime config                (changes: rarely, but placed last for clarity)
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

**Key rule**: If a layer changes, all subsequent layers are rebuilt. Separate dependency installation from source code copying.

## Multi-Stage Builds

Reduce final image size by separating build and runtime stages.

```
+-------------------+      +-------------------+
|   Build Stage     |      |   Runtime Stage   |
|                   |      |                   |
| - Full toolchain  | ---> | - Minimal base    |
| - Dev deps        |      | - Only artifacts  |
| - Source code     |      | - No build tools  |
| - Build output    |      | - No source code  |
+-------------------+      +-------------------+
    ~800 MB                     ~80 MB
```

**Benefits**: Smaller images, faster deploys, reduced attack surface, no build tools in production.

## Base Image Selection

| Image | Size | Use Case | Security | Package Manager |
|-------|------|----------|----------|-----------------|
| **alpine** | ~5 MB | Small images, CLI tools | Good (small surface) | apk |
| **slim** (Debian) | ~80 MB | Most apps (Python, Node) | Good | apt |
| **distroless** | ~20 MB | Production, no shell needed | Excellent (no shell) | None |
| **scratch** | 0 MB | Static Go/Rust binaries | Excellent (nothing) | None |
| **full** (Debian) | ~300 MB | Build stages, debugging | Fair (large surface) | apt |

### Recommendations by Language

| Language | Build Stage | Runtime Stage |
|----------|-------------|---------------|
| **Python** | `python:3.12-slim` | `python:3.12-slim` or `distroless/python3` |
| **Node.js** | `node:22-slim` | `node:22-slim` or `distroless/nodejs22` |
| **Go** | `golang:1.23` | `scratch` or `distroless/static` |
| **Rust** | `rust:1.83` | `scratch` or `distroless/cc` |
| **Java** | `eclipse-temurin:21-jdk` | `eclipse-temurin:21-jre-alpine` |

## Instruction Best Practices

### RUN: Combine and Clean Up

```dockerfile
# BAD: Multiple layers, leftover cache
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git

# GOOD: Single layer, cache cleaned
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
```

### COPY: Be Specific

```dockerfile
# BAD: Copies everything, including .git, node_modules, etc.
COPY . .

# GOOD: Copy only what's needed (use .dockerignore too)
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY src/ ./src/
COPY tsconfig.json ./
```

### .dockerignore Essentials

```
.git
node_modules
__pycache__
.env
*.log
dist
.venv
.pytest_cache
coverage
.DS_Store
```

### USER: Don't Run as Root

```dockerfile
# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/false appuser
USER appuser
```

### HEALTHCHECK

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1
```

### ARG vs ENV

| Directive | Available at | Persists in image | Use for |
|-----------|-------------|-------------------|---------|
| `ARG` | Build time only | No | Build-time toggles, versions |
| `ENV` | Build + runtime | Yes | App configuration |

```dockerfile
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

ENV APP_ENV=production
ENV PORT=8000
```

## Security Checklist

| Practice | Command/Example |
|----------|----------------|
| Pin base image digests | `FROM node:22-slim@sha256:abc123...` |
| Run as non-root | `USER appuser` |
| No secrets in layers | Use `--mount=type=secret` or build args |
| Scan for vulnerabilities | `docker scout cves`, `trivy image` |
| Read-only filesystem | `docker run --read-only` |
| Drop capabilities | `docker run --cap-drop ALL` |
| Use `.dockerignore` | Exclude `.env`, `.git`, credentials |
| Minimal base image | Use slim/distroless/scratch |

### Secrets at Build Time (BuildKit)

```dockerfile
# Mount a secret file without baking it into a layer
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) \
    npm install

# Build command:
# docker build --secret id=npm_token,src=.npmrc .
```

## Image Size Reduction Checklist

1. Use multi-stage builds
2. Choose slim/alpine/distroless base
3. Combine RUN commands
4. Remove package manager caches (`rm -rf /var/lib/apt/lists/*`)
5. Use `.dockerignore`
6. Don't install dev dependencies in runtime stage
7. Remove unnecessary files after build
8. Use `--no-install-recommends` with apt

## Common Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| `COPY . .` before `npm install` | No dependency caching | Copy lockfile first, install, then copy source |
| Using `latest` tag | Non-reproducible builds | Pin specific version tags or digests |
| Secrets in `ENV` or `COPY` | Leaked in image layers | Use BuildKit secrets mount |
| Running as root | Security vulnerability | Add `USER` directive |
| No `.dockerignore` | Bloated context, slow builds | Add and maintain `.dockerignore` |
| Installing build tools in final stage | Bloated image | Use multi-stage; build in first stage |
| Not using `--frozen-lockfile` | Non-deterministic installs | Always use lockfile flags |
