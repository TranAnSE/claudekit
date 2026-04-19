# Backend Frameworks — Express Patterns


# Express

## Overview

Production patterns for building Node.js HTTP servers and REST APIs with Express. Covers routing, middleware, validation, error handling, authentication, database integration, and testing.

## When to Use

- Building REST APIs with Express (without NestJS)
- Adding middleware (auth, logging, rate limiting, CORS)
- Handling file uploads, streaming, or WebSockets on Express
- Migrating Express apps or adding features to existing ones

## When NOT to Use

- **NestJS projects** — use the `nestjs` skill (NestJS wraps Express but has its own patterns)
- **FastAPI / Django** — use the `fastapi` or `django` skill
- **Frontend** — use `react` or `nextjs`
- **Cloudflare Workers / edge** — use `cloudflare-workers`

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| Project structure | SS Architecture below |
| Route patterns | SS Routing below |
| Middleware | SS Middleware below |
| Input validation | SS Validation below |
| Error handling | SS Error Handling below |
| Auth patterns | SS Authentication below |
| Database integration | SS Database below |
| Testing | SS Testing below |

---

## Architecture

### Project structure

```
src/
├── app.ts                    # Express app setup (middleware, routes)
├── server.ts                 # HTTP server bootstrap
├── routes/
│   ├── index.ts              # Route aggregator
│   ├── users.routes.ts       # /api/users
│   └── orders.routes.ts      # /api/orders
├── middleware/
│   ├── auth.ts               # JWT verification
│   ├── validate.ts           # Zod validation middleware
│   ├── error-handler.ts      # Global error handler
│   └── rate-limit.ts         # Rate limiting
├── services/
│   ├── users.service.ts      # Business logic
│   └── orders.service.ts
├── models/                   # Prisma or TypeORM entities
├── utils/
│   └── async-handler.ts      # Async error wrapper
└── tests/
    ├── users.test.ts
    └── orders.test.ts
```

### App setup

```typescript
// src/app.ts
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { json } from 'express';
import { router } from './routes';
import { errorHandler } from './middleware/error-handler';

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));

// Body parsing
app.use(json({ limit: '10kb' }));

// Routes
app.use('/api', router);

// Health check
app.get('/health', (_req, res) => res.json({ status: 'ok' }));

// Global error handler (must be last)
app.use(errorHandler);

export { app };
```

```typescript
// src/server.ts
import { app } from './app';

const PORT = process.env.PORT ?? 3000;
app.listen(PORT, () => console.log(`Listening on :${PORT}`));
```

---

## Routing

### Router pattern

```typescript
// src/routes/users.routes.ts
import { Router } from 'express';
import { UsersService } from '../services/users.service';
import { validate } from '../middleware/validate';
import { createUserSchema, updateUserSchema } from '../schemas/user.schema';
import { asyncHandler } from '../utils/async-handler';

const router = Router();
const service = new UsersService();

router.post('/', validate(createUserSchema), asyncHandler(async (req, res) => {
  const user = await service.create(req.body);
  res.status(201).json(user);
}));

router.get('/:id', asyncHandler(async (req, res) => {
  const user = await service.findOne(req.params.id);
  if (!user) {
    res.status(404).json({ type: 'not-found', title: 'Not Found', status: 404, detail: `User ${req.params.id} not found` });
    return;
  }
  res.json(user);
}));

router.patch('/:id', validate(updateUserSchema), asyncHandler(async (req, res) => {
  const user = await service.update(req.params.id, req.body);
  res.json(user);
}));

router.delete('/:id', asyncHandler(async (req, res) => {
  await service.remove(req.params.id);
  res.status(204).end();
}));

export { router as usersRouter };
```

### Async error wrapper

```typescript
// src/utils/async-handler.ts
import { Request, Response, NextFunction, RequestHandler } from 'express';

export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<void>
): RequestHandler {
  return (req, res, next) => fn(req, res, next).catch(next);
}
```

### Route aggregator

```typescript
// src/routes/index.ts
import { Router } from 'express';
import { usersRouter } from './users.routes';
import { ordersRouter } from './orders.routes';

const router = Router();
router.use('/users', usersRouter);
router.use('/orders', ordersRouter);

export { router };
```

---

## Middleware

### Middleware order matters

```typescript
// Correct order in app.ts:
app.use(helmet());              // 1. Security headers
app.use(cors());                // 2. CORS
app.use(json());                // 3. Body parsing
app.use(requestLogger);         // 4. Logging
app.use(rateLimiter);           // 5. Rate limiting
app.use('/api', router);        // 6. Routes
app.use(errorHandler);          // 7. Error handler (MUST be last)
```

### Request logging

```typescript
import { Request, Response, NextFunction } from 'express';

export function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  res.on('finish', () => {
    console.log(`${req.method} ${req.originalUrl} ${res.statusCode} ${Date.now() - start}ms`);
  });
  next();
}
```

### Rate limiting

```typescript
import rateLimit from 'express-rate-limit';

export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                    // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
  message: { type: 'rate-limit', title: 'Too Many Requests', status: 429 },
});
```

---

## Validation

### Zod validation middleware

```typescript
// src/middleware/validate.ts
import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';

export function validate(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (err) {
      if (err instanceof ZodError) {
        res.status(400).json({
          type: 'validation-error',
          title: 'Bad Request',
          status: 400,
          detail: err.errors.map(e => `${e.path.join('.')}: ${e.message}`).join('; '),
        });
        return;
      }
      next(err);
    }
  };
}
```

```typescript
// src/schemas/user.schema.ts
import { z } from 'zod';

export const createUserSchema = z.object({
  email: z.string().email().max(254),
  name: z.string().min(1).max(100),
  role: z.enum(['admin', 'member', 'viewer']).default('member'),
});

export const updateUserSchema = createUserSchema.partial();

export type CreateUserInput = z.infer<typeof createUserSchema>;
```

---

## Error Handling

### Global error handler (RFC 9457 Problem Details)

```typescript
// src/middleware/error-handler.ts
import { Request, Response, NextFunction } from 'express';

export class AppError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
  }
}

export function errorHandler(err: Error, _req: Request, res: Response, _next: NextFunction) {
  const status = err instanceof AppError ? err.statusCode : 500;
  const title = status >= 500 ? 'Internal Server Error' : err.message;

  if (status >= 500) console.error(err);

  res.status(status).json({
    type: `https://api.example.com/problems/${status}`,
    title,
    status,
    detail: status >= 500 ? 'An unexpected error occurred' : err.message,
  });
}
```

---

## Authentication

### JWT middleware

```typescript
// src/middleware/auth.ts
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export interface AuthRequest extends Request {
  user?: { sub: string; role: string };
}

export function authenticate(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    res.status(401).json({ type: 'unauthorized', title: 'Unauthorized', status: 401, detail: 'Missing bearer token' });
    return;
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!) as AuthRequest['user'];
    req.user = payload;
    next();
  } catch {
    res.status(401).json({ type: 'unauthorized', title: 'Unauthorized', status: 401, detail: 'Invalid or expired token' });
  }
}

export function authorize(...roles: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      res.status(403).json({ type: 'forbidden', title: 'Forbidden', status: 403, detail: 'Insufficient permissions' });
      return;
    }
    next();
  };
}
```

---

## Database

### Prisma integration

```typescript
// src/db.ts
import { PrismaClient } from '@prisma/client';

export const prisma = new PrismaClient();

// Graceful shutdown
process.on('SIGTERM', async () => {
  await prisma.$disconnect();
  process.exit(0);
});
```

```typescript
// src/services/users.service.ts
import { prisma } from '../db';
import { CreateUserInput } from '../schemas/user.schema';

export class UsersService {
  async findOne(id: string) {
    return prisma.user.findUnique({ where: { id } });
  }

  async create(data: CreateUserInput) {
    return prisma.user.create({ data });
  }

  async update(id: string, data: Partial<CreateUserInput>) {
    return prisma.user.update({ where: { id }, data });
  }

  async remove(id: string) {
    await prisma.user.delete({ where: { id } });
  }
}
```

---

## Testing

### Integration tests with supertest

```typescript
// src/tests/users.test.ts
import request from 'supertest';
import { app } from '../app';
import { prisma } from '../db';

describe('Users API', () => {
  afterAll(() => prisma.$disconnect());

  it('POST /api/users — creates user', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(201);

    expect(res.body).toHaveProperty('id');
    expect(res.body.email).toBe('test@example.com');
  });

  it('POST /api/users — rejects invalid email', async () => {
    await request(app)
      .post('/api/users')
      .send({ email: 'not-an-email', name: 'Test' })
      .expect(400);
  });

  it('GET /api/users/:id — returns 404 for missing user', async () => {
    await request(app)
      .get('/api/users/nonexistent')
      .expect(404);
  });
});
```

---

## Common Pitfalls

1. **Forgetting `asyncHandler`.** Unhandled promise rejections crash the process. Wrap every async route handler.
2. **Error handler not last.** Express error handlers must have 4 parameters `(err, req, res, next)` and must be registered after all routes.
3. **Not calling `next()`.** Middleware that doesn't call `next()` or send a response will hang the request.
4. **Mutating `req.body` without validation.** Always validate before trusting input. Use Zod or Joi middleware.
5. **Hardcoding CORS origin.** Use environment variables for allowed origins. Never use `cors({ origin: '*' })` in production.
6. **Missing `helmet()`.** Always use helmet for security headers. It's one line and prevents common attacks.
7. **Not limiting body size.** Use `json({ limit: '10kb' })` to prevent denial-of-service via large payloads.
8. **Using `express.static` for uploads.** Serve user uploads from a CDN or S3, not from the Express process.

---

## Related Skills

- `nestjs` — If you need DI, decorators, and modules, use NestJS instead of raw Express
- `openapi` — OpenAPI spec design for Express APIs (use `swagger-jsdoc` + `swagger-ui-express`)
- `typescript` — TypeScript patterns (Express is typed via `@types/express`)
- `docker` — Containerizing Express apps
- `authentication` — JWT / OAuth2 patterns (framework-agnostic)
- `jest` — Testing Express with Jest + supertest
