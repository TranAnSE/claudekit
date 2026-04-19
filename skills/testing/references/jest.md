# Testing — Jest Patterns


# Jest

## Overview

Testing patterns for projects that use Jest as their test runner — primarily NestJS backends and legacy React projects. For new TypeScript/React projects, prefer `vitest` (faster, native ESM, Vite-aligned). This skill focuses on Jest-specific patterns, NestJS integration, and the Jest-to-Vitest migration path.

## When to Use
- NestJS projects (Jest is the default test runner)
- Existing projects that already use Jest
- React component testing with Jest + Testing Library
- Debugging Jest configuration issues (ESM, TypeScript transforms, module resolution)

## When NOT to Use
- **New Vite/React/Next.js projects** — use `vitest` (better ESM support, faster)
- **Python testing** — use `pytest`
- **E2E browser testing** — use `playwright`
- **Cloudflare Workers** — use `vitest` with `@cloudflare/vitest-pool-workers`

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| NestJS testing patterns | § NestJS Testing below |
| Mock patterns | § Mocking below |
| TypeScript config | § Configuration below |
| ESM troubleshooting | § ESM Gotchas below |
| Migration to Vitest | § Jest → Vitest Migration below |

---

## Core Patterns

### Test structure

```typescript
import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';

describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  it('should create a user with default role', () => {
    const user = service.create({ email: 'test@example.com', name: 'Test' });
    expect(user.role).toBe('member');
  });

  it('should throw on duplicate email', () => {
    service.create({ email: 'test@example.com', name: 'A' });
    expect(() => service.create({ email: 'test@example.com', name: 'B' }))
      .toThrow('Email already exists');
  });
});
```

### Assertions

```typescript
// Equality
expect(result).toBe(42);               // strict ===
expect(result).toEqual({ id: '1' });   // deep equality
expect(result).toStrictEqual(obj);      // deep + type equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(count).toBeGreaterThan(0);
expect(price).toBeCloseTo(9.99, 2);

// Strings
expect(message).toMatch(/error/i);
expect(message).toContain('failed');

// Arrays / objects
expect(arr).toContain('item');
expect(arr).toHaveLength(3);
expect(obj).toHaveProperty('email', 'test@example.com');

// Exceptions
expect(() => parse('{bad}')).toThrow(SyntaxError);
expect(() => validate({})).toThrow('Required');

// Async
await expect(fetchUser('missing')).rejects.toThrow('Not found');
await expect(fetchUser('exists')).resolves.toHaveProperty('id');
```

---

## Mocking

### `jest.fn()` — standalone mock function

```typescript
const callback = jest.fn();
callback('arg1');

expect(callback).toHaveBeenCalledTimes(1);
expect(callback).toHaveBeenCalledWith('arg1');
```

### `jest.spyOn()` — spy on existing methods

```typescript
const spy = jest.spyOn(service, 'findOne').mockResolvedValue(mockUser);

await controller.getUser('123');

expect(spy).toHaveBeenCalledWith('123');
spy.mockRestore(); // Restore original
```

### `jest.mock()` — module mocking

```typescript
// Auto-mock entire module
jest.mock('./email.service');

// Manual mock with implementation
jest.mock('./email.service', () => ({
  EmailService: jest.fn().mockImplementation(() => ({
    send: jest.fn().mockResolvedValue({ messageId: 'msg_123' }),
  })),
}));
```

### Mock return values

```typescript
const mock = jest.fn();

mock.mockReturnValue(42);              // Sync
mock.mockReturnValueOnce(1);           // First call only
mock.mockResolvedValue({ ok: true });  // Async
mock.mockRejectedValue(new Error());   // Async throw
mock.mockImplementation((x) => x * 2); // Custom logic
```

### Clear vs Reset vs Restore

| Method | Clears calls | Resets implementation | Restores original |
|--------|-------------|----------------------|-------------------|
| `mockClear()` | yes | no | no |
| `mockReset()` | yes | yes (returns undefined) | no |
| `mockRestore()` | yes | yes | yes (spyOn only) |

Use `jest.restoreAllMocks()` in `afterEach` to avoid mock leaks.

---

## NestJS Testing

### Unit test a service

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from './users.service';
import { PrismaService } from '../prisma/prisma.service';
import { NotFoundException } from '@nestjs/common';

describe('UsersService', () => {
  let service: UsersService;
  let prisma: jest.Mocked<PrismaService>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: PrismaService,
          useValue: {
            user: {
              findUnique: jest.fn(),
              create: jest.fn(),
              update: jest.fn(),
              delete: jest.fn(),
            },
          },
        },
      ],
    }).compile();

    service = module.get(UsersService);
    prisma = module.get(PrismaService);
  });

  it('throws NotFoundException for missing user', async () => {
    prisma.user.findUnique.mockResolvedValue(null);
    await expect(service.findOne('missing')).rejects.toThrow(NotFoundException);
  });

  it('returns user when found', async () => {
    const mockUser = { id: '1', email: 'test@example.com', name: 'Test' };
    prisma.user.findUnique.mockResolvedValue(mockUser);

    const result = await service.findOne('1');
    expect(result).toEqual(mockUser);
    expect(prisma.user.findUnique).toHaveBeenCalledWith({ where: { id: '1' } });
  });
});
```

### E2E test a controller

```typescript
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Users (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = module.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, forbidNonWhitelisted: true }));
    await app.init();
  });

  afterAll(() => app.close());

  it('POST /users creates user', () =>
    request(app.getHttpServer())
      .post('/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(201)
      .expect((res) => expect(res.body).toHaveProperty('id')));

  it('POST /users rejects invalid payload', () =>
    request(app.getHttpServer())
      .post('/users')
      .send({ email: 'bad' })
      .expect(400));
});
```

### Test a guard

```typescript
import { ExecutionContext } from '@nestjs/common';
import { JwtAuthGuard } from './jwt-auth.guard';
import { JwtService } from '@nestjs/jwt';

describe('JwtAuthGuard', () => {
  let guard: JwtAuthGuard;
  let jwtService: jest.Mocked<JwtService>;

  beforeEach(() => {
    jwtService = { verifyAsync: jest.fn() } as any;
    guard = new JwtAuthGuard(jwtService);
  });

  const mockContext = (authHeader?: string): ExecutionContext => ({
    switchToHttp: () => ({
      getRequest: () => ({
        headers: { authorization: authHeader },
      }),
    }),
  }) as any;

  it('rejects missing token', async () => {
    await expect(guard.canActivate(mockContext())).rejects.toThrow('Missing bearer token');
  });

  it('accepts valid token', async () => {
    jwtService.verifyAsync.mockResolvedValue({ sub: 'user_1', role: 'admin' });
    await expect(guard.canActivate(mockContext('Bearer valid.jwt.token'))).resolves.toBe(true);
  });
});
```

---

## Configuration

### TypeScript with `ts-jest`

```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/*.spec.ts', '**/*.test.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/*.module.ts',
    '!src/main.ts',
    '!src/**/*.dto.ts',
    '!src/**/*.entity.ts',
  ],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
};

export default config;
```

### SWC transform (faster)

Replace `ts-jest` with `@swc/jest` for 5-10x faster transforms:

```typescript
// jest.config.ts
const config: Config = {
  transform: {
    '^.+\\.tsx?$': ['@swc/jest'],
  },
  // ... rest same
};
```

### React + Testing Library

```typescript
// jest.config.ts
const config: Config = {
  testEnvironment: 'jsdom',
  setupFilesAfterSetup: ['<rootDir>/jest.setup.ts'],
  transform: { '^.+\\.tsx?$': ['@swc/jest'] },
  moduleNameMapper: {
    '\\.(css|less|scss)$': 'identity-obj-proxy',
    '\\.(jpg|png|svg)$': '<rootDir>/__mocks__/fileMock.ts',
  },
};

// jest.setup.ts
import '@testing-library/jest-dom';
```

---

## ESM Gotchas

Jest's ESM support is still experimental. Common issues and fixes:

| Problem | Fix |
|---------|-----|
| `SyntaxError: Cannot use import` | Add `transform` with `ts-jest` or `@swc/jest` |
| Module not found for `.js` imports | Set `moduleNameMapper` or use `ts-jest` with `useESM: true` |
| `jest.mock()` doesn't work with ESM | Use `jest.unstable_mockModule()` (experimental) |
| Dynamic `import()` in tests | Set `transform` to handle the syntax |
| `__dirname` undefined | ESM doesn't have `__dirname`; use `import.meta.url` + `fileURLToPath` |

**If fighting ESM issues takes more than 30 minutes, migrate to Vitest.** Vitest handles ESM natively and is a near-drop-in replacement.

---

## Jest → Vitest Migration

For projects outgrowing Jest's ESM limitations or wanting faster transforms:

| Jest | Vitest |
|------|--------|
| `jest.fn()` | `vi.fn()` |
| `jest.mock('./mod')` | `vi.mock('./mod')` |
| `jest.spyOn(obj, 'method')` | `vi.spyOn(obj, 'method')` |
| `jest.useFakeTimers()` | `vi.useFakeTimers()` |
| `jest.config.ts` | `vitest.config.ts` |
| `@jest/globals` | `vitest` |
| `ts-jest` / `@swc/jest` | Not needed (native TS) |
| `jest.setup.ts` → `setupFilesAfterSetup` | `vitest.config.ts` → `setupFiles` |

Most tests migrate with a find-replace of `jest` → `vi` and `@jest/globals` → `vitest`. Run `npx vitest --reporter=verbose` to catch edge cases.

---

## Common Pitfalls

1. **Mock leaks between tests.** Always call `jest.restoreAllMocks()` in `afterEach`. Without it, one test's mock infects the next.
2. **Forgetting `await` on async assertions.** `expect(fn()).rejects.toThrow()` without `await` silently passes even if the promise resolves.
3. **Using `jest.mock()` with ESM.** Module-level `jest.mock()` doesn't work reliably with ESM. Use `jest.unstable_mockModule()` or switch to Vitest.
4. **Testing implementation, not behavior.** Asserting `mock.toHaveBeenCalledTimes(3)` tests internal calls, not outcomes. Assert on the return value or side effect instead.
5. **Slow transforms.** Default `ts-jest` is slow. Switch to `@swc/jest` for 5-10x speedup with zero config change.
6. **Not closing NestJS app in E2E tests.** Missing `afterAll(() => app.close())` leaks connections and causes "open handle" warnings.
7. **Snapshot overuse.** `toMatchSnapshot()` on large objects makes tests pass everything — any change auto-updates. Use targeted assertions instead.
8. **Running Jest where Vitest fits.** For new Vite/React/Next.js projects, Vitest is strictly better (native ESM, faster, same API). Only use Jest when the framework mandates it (NestJS) or the project already depends on it.

---

## Related Skills

- `vitest` — preferred runner for new TypeScript/React projects
- `nestjs` — NestJS framework (Jest is the default runner)
- `react` — React component patterns
- `testing-anti-patterns` — test quality pitfalls (applies to Jest too)
- `test-driven-development` — TDD methodology
