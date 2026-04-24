# DevOps — Docker Patterns


# Docker

## When to Use

- Containerizing applications
- Local development environments
- CI/CD pipelines

## When NOT to Use

- Serverless-only deployments where containers are not part of the architecture (e.g., pure AWS Lambda, Cloudflare Workers)
- Local development without containers where native tooling is preferred
- Simple scripts or utilities that do not need isolation or reproducible environments

---

## Core Patterns

### 1. Multi-Stage Builds

Multi-stage builds separate build-time dependencies from the runtime image, producing
smaller, more secure containers.

#### Python (builder + slim runtime)

```dockerfile
# ---- Build stage ----
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build-only dependencies (gcc, etc.) needed by some wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage ----
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /install /usr/local

# Copy application code
COPY src/ ./src/
COPY main.py .

# Run as non-root
RUN addgroup --system app && adduser --system --ingroup app app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Node.js (build + nginx/alpine)

```dockerfile
# ---- Build stage ----
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first for layer caching
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

# Copy source and build
COPY tsconfig.json ./
COPY src/ ./src/
COPY public/ ./public/
RUN pnpm build

# ---- Runtime stage (static site served by nginx) ----
FROM nginx:1.27-alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Run as non-root
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid
USER nginx

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

#### Node.js (API server with alpine runtime)

```dockerfile
# ---- Build stage ----
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

COPY tsconfig.json ./
COPY src/ ./src/
RUN pnpm build

# Prune dev dependencies for a lighter production node_modules
RUN pnpm prune --prod

# ---- Runtime stage ----
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

RUN addgroup -S app && adduser -S app -G app
USER app

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

CMD ["node", "dist/index.js"]
```

#### Go (build + scratch)

```dockerfile
# ---- Build stage ----
FROM golang:1.22-alpine AS builder

WORKDIR /build

# Download dependencies first for caching
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build a static binary
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/server ./cmd/server

# ---- Runtime stage (scratch = empty image) ----
FROM scratch

# Copy CA certificates for HTTPS calls
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

# Copy the static binary
COPY --from=builder /app/server /server

EXPOSE 8080

ENTRYPOINT ["/server"]
```

---

### 2. Docker Compose for Development

A full-featured Compose file with services, volumes, networks, healthchecks, and
environment variable management.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      target: builder          # Use builder stage for dev with hot-reload
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: development
      DATABASE_URL: postgresql://user:pass@db:5432/app
      REDIS_URL: redis://redis:6379
    env_file:
      - .env.local             # Local overrides (gitignored)
    volumes:
      - .:/app                 # Bind-mount source for hot-reload
      - /app/node_modules      # Anonymous volume to preserve node_modules
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - backend
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    networks:
      - backend

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - backend

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      DATABASE_URL: postgresql://user:pass@db:5432/app
      REDIS_URL: redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  backend:
    driver: bridge
```

---

### 3. Layer Caching

Docker caches each layer. If a layer has not changed, every layer after it is also
cached. Order instructions from least-frequently-changed to most-frequently-changed.

#### Optimal instruction order

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 1. System dependencies (rarely change)
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Dependency manifests (change when adding packages)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Application code (changes most often)
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

#### .dockerignore patterns

Always include a `.dockerignore` to keep the build context small and avoid leaking
secrets into layers.

```
# Version control
.git
.gitignore

# Dependencies (rebuilt inside container)
node_modules
__pycache__
*.pyc
.venv
venv

# Build output
dist
build
*.egg-info

# IDE and editor files
.vscode
.idea
*.swp
*.swo

# Environment and secrets
.env
.env.*
*.pem
*.key

# Docker files (not needed in context)
Dockerfile*
docker-compose*
.dockerignore

# Documentation and misc
README.md
CHANGELOG.md
LICENSE
docs/
```

---

### 4. Health Checks

Health checks let Docker (and orchestrators like Compose/Swarm/K8s) know when a
container is actually ready to serve traffic.

#### HTTP health check with curl

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

#### HTTP health check with wget (alpine images without curl)

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1
```

#### TCP port check (for non-HTTP services)

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD nc -z localhost 5432 || exit 1
```

#### Python-native check (no extra binaries needed)

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

**Parameter reference:**

| Parameter        | Description                                      | Default |
|------------------|--------------------------------------------------|---------|
| `--interval`     | Time between checks                              | 30s     |
| `--timeout`      | Max time for a single check                      | 30s     |
| `--start-period` | Grace period before checks count as failures     | 0s      |
| `--retries`      | Consecutive failures before marking unhealthy    | 3       |

---

### 5. Security Hardening

#### Run as non-root user

```dockerfile
# Debian/Ubuntu based images
RUN addgroup --system app && adduser --system --ingroup app app
USER app

# Alpine based images
RUN addgroup -S app && adduser -S app -G app
USER app
```

#### Use minimal base images

| Base Image         | Size    | Use Case                              |
|--------------------|---------|---------------------------------------|
| `alpine`           | ~5 MB   | General minimal base                  |
| `*-slim`           | ~50 MB  | Debian-based with fewer packages      |
| `distroless`       | ~20 MB  | Google's no-shell, no-package-manager |
| `scratch`          | 0 MB    | Static binaries only (Go, Rust)       |

```dockerfile
# Distroless for Python
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /app /app
CMD ["main.py"]
```

#### Never put secrets in image layers

```dockerfile
# BAD - secret is baked into image history
COPY .env /app/.env
RUN echo "API_KEY=secret123" >> /app/.env

# GOOD - pass secrets at runtime
CMD ["python", "main.py"]
# docker run -e API_KEY=secret123 myapp
# or docker run --env-file .env myapp
```

#### Multi-stage to exclude build tools

Build tools (compilers, package managers, source code) stay in the builder stage
and never reach the runtime image. This reduces attack surface and image size.

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build && pnpm prune --prod

FROM node:20-alpine
WORKDIR /app
# Only the built output and production deps are copied
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

---

### 6. Environment Configuration

#### ARG vs ENV

| Directive | Available at | Persists in image | Use for                     |
|-----------|-------------|-------------------|-----------------------------|
| `ARG`     | Build time  | No                | Build-time variables        |
| `ENV`     | Build + run | Yes               | Runtime configuration       |

```dockerfile
# ARG - only available during build
ARG NODE_ENV=production
ARG BUILD_VERSION=unknown

# ENV - available at build and runtime
ENV NODE_ENV=${NODE_ENV}
ENV APP_VERSION=${BUILD_VERSION}

# Build with: docker build --build-arg BUILD_VERSION=1.2.3 .
```

#### .env files with Compose

```yaml
services:
  app:
    build: .
    # Single .env file
    env_file:
      - .env

    # Multiple files (later files override earlier ones)
    env_file:
      - .env.defaults
      - .env.local

    # Inline environment variables (override env_file)
    environment:
      LOG_LEVEL: debug
      DEBUG: "true"
```

#### Secrets management with Docker Compose

```yaml
services:
  app:
    build: .
    secrets:
      - db_password
      - api_key
    environment:
      DB_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
  api_key:
    environment: API_KEY    # Read from host environment
```

Inside the container, secrets are mounted at `/run/secrets/<name>` as files.

---

### 7. Networking

#### Bridge networks for service isolation

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    networks:
      - frontend-net
      - backend-net     # Can reach the API

  api:
    build: ./api
    ports:
      - "8000:8000"
    networks:
      - backend-net     # Reachable by frontend and workers

  db:
    image: postgres:16-alpine
    networks:
      - backend-net     # Only reachable by api and workers
    # No ports exposed to host

  worker:
    build: ./worker
    networks:
      - backend-net

networks:
  frontend-net:
    driver: bridge
  backend-net:
    driver: bridge
```

#### Service discovery

Within a Docker Compose network, services reach each other by **service name**
as the hostname.

```python
# In the api service, connect to db using its service name
DATABASE_URL = "postgresql://user:pass@db:5432/app"

# In the frontend service, call the api by service name
API_URL = "http://api:8000"
```

#### Exposing ports

```yaml
services:
  app:
    ports:
      - "3000:3000"             # host:container, binds to 0.0.0.0
      - "127.0.0.1:3000:3000"  # bind to localhost only (more secure)
    expose:
      - "3000"                  # expose to other containers only, not host
```

---

## Best Practices

1. **Use multi-stage builds** -- Separate build dependencies from the runtime
   image. The final image should contain only what is needed to run the
   application.

2. **Pin image tags** -- Use `node:20.11-alpine` or a digest instead of
   `node:latest` or `node:20`. Floating tags lead to unpredictable builds.

3. **Order instructions for cache efficiency** -- Copy dependency manifests and
   install dependencies before copying application code. This ensures that code
   changes do not invalidate the dependency layer cache.

4. **Use .dockerignore** -- Exclude `.git`, `node_modules`, `__pycache__`, `.env`
   files, and anything not needed inside the container to keep the build context
   small and avoid leaking secrets.

5. **Run as non-root** -- Add a `USER` instruction to run the process as an
   unprivileged user. Never run production containers as root.

6. **Combine RUN commands** -- Merge related `RUN` instructions with `&&` to
   reduce layers and always clean up apt/apk caches in the same layer that
   installs packages.

7. **Use COPY instead of ADD** -- `COPY` is explicit and predictable. `ADD` has
   implicit behaviors (tar extraction, URL fetching) that can surprise you.

8. **Set explicit HEALTHCHECK** -- Define health checks in the Dockerfile so
   orchestrators know when the container is ready. This prevents routing traffic
   to containers that are still starting up.

---

## Common Pitfalls

1. **Bloated images** -- Using full base images like `python:3.12` instead of
   `python:3.12-slim` adds hundreds of megabytes. Always prefer slim or alpine
   variants. Use multi-stage builds to exclude build tools.

2. **Cache invalidation by COPY order** -- Placing `COPY . .` before
   `RUN pip install` means every code change reinstalls all dependencies. Always
   copy the dependency manifest first, install, then copy the rest of the code.

3. **Running as root** -- Forgetting the `USER` instruction means the container
   process runs as root. If the application is compromised, the attacker has full
   control of the container filesystem.

4. **Secrets baked into layers** -- Using `COPY .env .` or `ARG` for secrets
   embeds them in the image layer history. Anyone with access to the image can
   extract them with `docker history`. Pass secrets at runtime via environment
   variables or Docker secrets.

5. **Missing .dockerignore** -- Without a `.dockerignore`, the entire directory
   (including `.git`, `node_modules`, `.env` files) is sent as build context.
   This slows builds, increases image size, and risks leaking credentials.

6. **Ignoring healthchecks in Compose** -- Using `depends_on` without
   `condition: service_healthy` means the dependent service starts as soon as
   the database container starts, not when the database is actually ready to
   accept connections. Always pair `depends_on` with healthchecks.

---

## Related Skills

- `github-actions` - CI/CD workflows for building and deploying Docker containers
- `owasp` - Security best practices for container hardening and vulnerability scanning
