# Backend Frameworks — NestJS Patterns


# NestJS

## Overview

Production patterns for building TypeScript backend APIs with NestJS. Covers module architecture, dependency injection, request validation, authentication guards, database integration, testing, and deployment.

## When to Use
- Building REST APIs or GraphQL servers with NestJS
- Configuring modules, providers, and dependency injection
- Creating guards, interceptors, pipes, or middleware
- Integrating Prisma, TypeORM, or MikroORM with NestJS
- Building microservices or WebSocket gateways
- Testing NestJS controllers and services

## When NOT to Use
- **Express without NestJS** — use `express` patterns directly
- **FastAPI / Django** — use the `fastapi` or `django` skill
- **Frontend** — use `react` or `nextjs`
- **Simple scripts** — NestJS is overkill for one-file utilities

---

## Quick Reference

| I need... | Go to |
|-----------|-------|
| Module/DI patterns | § Architecture below |
| Request validation | § Pipes & Validation below |
| Auth guards (JWT/API key) | § Authentication below |
| Database integration | § Database below |
| Testing patterns | § Testing below |
| Error handling | § Exception Filters below |
| OpenAPI generation | § OpenAPI below |

---

## Architecture

### Module structure

Every NestJS app is a tree of modules. Keep modules focused on a single domain.

```
src/
├── app.module.ts              # Root module — imports feature modules
├── main.ts                    # Bootstrap
├── common/                    # Shared utilities
│   ├── decorators/
│   ├── filters/
│   ├── guards/
│   ├── interceptors/
│   └── pipes/
├── config/                    # Configuration module
│   ├── config.module.ts
│   └── config.service.ts
├── users/                     # Feature module
│   ├── users.module.ts
│   ├── users.controller.ts
│   ├── users.service.ts
│   ├── dto/
│   │   ├── create-user.dto.ts
│   │   └── update-user.dto.ts
│   ├── entities/
│   │   └── user.entity.ts
│   └── users.controller.spec.ts
└── orders/                    # Another feature module
    ├── orders.module.ts
    ├── orders.controller.ts
    └── orders.service.ts
```

### Module pattern

```typescript
// users/users.module.ts
import { Module } from '@nestjs/common';
import { UsersController } from './users.controller';
import { UsersService } from './users.service';

@Module({
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],   // Expose to other modules
})
export class UsersModule {}
```

### Controller + Service pattern

```typescript
// users/users.controller.ts
import { Controller, Get, Post, Body, Param, Patch, Delete, HttpCode, HttpStatus } from '@nestjs/common';
import { UsersService } from './users.service';
import { CreateUserDto } from './dto/create-user.dto';
import { UpdateUserDto } from './dto/update-user.dto';

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.usersService.findOne(id);
  }

  @Patch(':id')
  update(@Param('id') id: string, @Body() dto: UpdateUserDto) {
    return this.usersService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string) {
    return this.usersService.remove(id);
  }
}
```

```typescript
// users/users.service.ts
import { Injectable, NotFoundException } from '@nestjs/common';

@Injectable()
export class UsersService {
  async findOne(id: string) {
    const user = await this.prisma.user.findUnique({ where: { id } });
    if (!user) throw new NotFoundException(`User ${id} not found`);
    return user;
  }

  async create(dto: CreateUserDto) {
    return this.prisma.user.create({ data: dto });
  }

  async update(id: string, dto: UpdateUserDto) {
    await this.findOne(id);  // throws if missing
    return this.prisma.user.update({ where: { id }, data: dto });
  }

  async remove(id: string) {
    await this.findOne(id);
    await this.prisma.user.delete({ where: { id } });
  }
}
```

---

## Pipes & Validation

Use `class-validator` + `class-transformer` with the global `ValidationPipe`.

### Bootstrap validation globally

```typescript
// main.ts
import { NestFactory } from '@nestjs/core';
import { ValidationPipe } from '@nestjs/common';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  app.useGlobalPipes(new ValidationPipe({
    whitelist: true,            // Strip unknown properties
    forbidNonWhitelisted: true, // Reject unknown properties with 400
    transform: true,            // Auto-transform payloads to DTO instances
    transformOptions: { enableImplicitConversion: true },
  }));

  await app.listen(3000);
}
bootstrap();
```

### DTO with validation

```typescript
// users/dto/create-user.dto.ts
import { IsEmail, IsString, MinLength, MaxLength, IsOptional, IsEnum } from 'class-validator';

export class CreateUserDto {
  @IsEmail()
  @MaxLength(254)
  email: string;

  @IsString()
  @MinLength(1)
  @MaxLength(100)
  name: string;

  @IsOptional()
  @IsEnum(['admin', 'member', 'viewer'])
  role?: string = 'member';
}
```

```typescript
// users/dto/update-user.dto.ts
import { PartialType } from '@nestjs/mapped-types';
import { CreateUserDto } from './create-user.dto';

export class UpdateUserDto extends PartialType(CreateUserDto) {}
```

`PartialType` makes all fields optional and preserves validators — no manual duplication.

---

## Authentication

### JWT Guard

```typescript
// common/guards/jwt-auth.guard.ts
import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private readonly jwtService: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<Request>();
    const token = this.extractToken(request);
    if (!token) throw new UnauthorizedException('Missing bearer token');

    try {
      const payload = await this.jwtService.verifyAsync(token);
      request['user'] = payload;
    } catch {
      throw new UnauthorizedException('Invalid or expired token');
    }
    return true;
  }

  private extractToken(request: Request): string | undefined {
    const [type, token] = request.headers.authorization?.split(' ') ?? [];
    return type === 'Bearer' ? token : undefined;
  }
}
```

### Apply guard globally with public route bypass

```typescript
// app.module.ts
import { APP_GUARD } from '@nestjs/core';
import { JwtAuthGuard } from './common/guards/jwt-auth.guard';

@Module({
  providers: [{ provide: APP_GUARD, useClass: JwtAuthGuard }],
})
export class AppModule {}
```

```typescript
// common/decorators/public.decorator.ts
import { SetMetadata } from '@nestjs/common';

export const IS_PUBLIC_KEY = 'isPublic';
export const Public = () => SetMetadata(IS_PUBLIC_KEY, true);
```

```typescript
// In JwtAuthGuard.canActivate(), add at the top:
const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
  context.getHandler(),
  context.getClass(),
]);
if (isPublic) return true;
```

```typescript
// Usage — mark public routes
@Public()
@Get('health')
health() { return { status: 'ok' }; }
```

### Role-based access

```typescript
// common/decorators/roles.decorator.ts
import { SetMetadata } from '@nestjs/common';
export const ROLES_KEY = 'roles';
export const Roles = (...roles: string[]) => SetMetadata(ROLES_KEY, roles);

// common/guards/roles.guard.ts
@Injectable()
export class RolesGuard implements CanActivate {
  constructor(private reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    const requiredRoles = this.reflector.getAllAndOverride<string[]>(ROLES_KEY, [
      context.getHandler(), context.getClass(),
    ]);
    if (!requiredRoles) return true;
    const { user } = context.switchToHttp().getRequest();
    return requiredRoles.includes(user.role);
  }
}
```

---

## Exception Filters

### Global Problem Details filter (RFC 9457)

Consistent with the `openapi` skill's convention — all errors as `application/problem+json`.

```typescript
// common/filters/problem-details.filter.ts
import { ExceptionFilter, Catch, ArgumentsHost, HttpException, HttpStatus } from '@nestjs/common';
import { Response } from 'express';

@Catch()
export class ProblemDetailsFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    const exceptionResponse = exception instanceof HttpException
      ? exception.getResponse()
      : {};

    const detail = typeof exceptionResponse === 'string'
      ? exceptionResponse
      : (exceptionResponse as any).message;

    response.status(status).json({
      type: `https://api.example.com/problems/${this.slugify(status)}`,
      title: HttpStatus[status]?.replace(/_/g, ' ').toLowerCase() ?? 'Error',
      status,
      detail: Array.isArray(detail) ? detail.join('; ') : detail,
    });
  }

  private slugify(status: number): string {
    return (HttpStatus[status] ?? 'error').toLowerCase().replace(/_/g, '-');
  }
}
```

Register globally in `main.ts`:

```typescript
app.useGlobalFilters(new ProblemDetailsFilter());
```

---

## Database

### Prisma integration (recommended)

```typescript
// prisma/prisma.service.ts
import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit, OnModuleDestroy {
  async onModuleInit() { await this.$connect(); }
  async onModuleDestroy() { await this.$disconnect(); }
}
```

```typescript
// prisma/prisma.module.ts
import { Global, Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Global()
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {}
```

Then inject `PrismaService` in any service:

```typescript
@Injectable()
export class UsersService {
  constructor(private readonly prisma: PrismaService) {}
  // ...
}
```

### TypeORM alternative

```typescript
// users/entities/user.entity.ts
import { Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, UpdateDateColumn } from 'typeorm';

@Entity()
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  email: string;

  @Column()
  name: string;

  @Column({ default: 'member' })
  role: string;

  @CreateDateColumn()
  createdAt: Date;

  @UpdateDateColumn()
  updatedAt: Date;
}
```

---

## Testing

### Unit testing a service

```typescript
// users/users.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { UsersService } from './users.service';
import { PrismaService } from '../prisma/prisma.service';
import { NotFoundException } from '@nestjs/common';

describe('UsersService', () => {
  let service: UsersService;
  let prisma: PrismaService;

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

  it('throws NotFoundException when user does not exist', async () => {
    jest.spyOn(prisma.user, 'findUnique').mockResolvedValue(null);
    await expect(service.findOne('missing')).rejects.toThrow(NotFoundException);
  });
});
```

### E2E testing a controller

```typescript
// test/users.e2e-spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('UsersController (e2e)', () => {
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

  it('POST /users — creates user', () =>
    request(app.getHttpServer())
      .post('/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(201)
      .expect((res) => {
        expect(res.body).toHaveProperty('id');
        expect(res.body.email).toBe('test@example.com');
      }));

  it('POST /users — rejects invalid email', () =>
    request(app.getHttpServer())
      .post('/users')
      .send({ email: 'not-an-email', name: 'Test' })
      .expect(400));
});
```

---

## OpenAPI

NestJS has first-class OpenAPI generation via `@nestjs/swagger`.

```typescript
// main.ts
import { SwaggerModule, DocumentBuilder } from '@nestjs/swagger';

const config = new DocumentBuilder()
  .setTitle('Acme API')
  .setVersion('1.0')
  .addBearerAuth()
  .build();
const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup('docs', app, document);
```

Annotate DTOs for richer specs:

```typescript
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateUserDto {
  @ApiProperty({ example: 'jane@example.com', maxLength: 254 })
  @IsEmail()
  email: string;

  @ApiPropertyOptional({ enum: ['admin', 'member', 'viewer'], default: 'member' })
  @IsOptional()
  @IsEnum(['admin', 'member', 'viewer'])
  role?: string = 'member';
}
```

Use the `@nestjs/swagger` CLI plugin to auto-generate `@ApiProperty` decorators from TypeScript types — saves boilerplate.

---

## Configuration

Use `@nestjs/config` with Zod validation for type-safe env vars.

```typescript
// config/env.validation.ts
import { z } from 'zod';

export const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
});

export type Env = z.infer<typeof envSchema>;
```

```typescript
// config/config.module.ts
import { ConfigModule } from '@nestjs/config';
import { envSchema } from './env.validation';

export const AppConfigModule = ConfigModule.forRoot({
  validate: (config) => envSchema.parse(config),
  isGlobal: true,
});
```

---

## Interceptors

### Request logging

```typescript
// common/interceptors/logging.interceptor.ts
import { Injectable, NestInterceptor, ExecutionContext, CallHandler, Logger } from '@nestjs/common';
import { Observable, tap } from 'rxjs';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
  private readonly logger = new Logger('HTTP');

  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const req = context.switchToHttp().getRequest();
    const { method, url } = req;
    const start = Date.now();

    return next.handle().pipe(
      tap(() => {
        const res = context.switchToHttp().getResponse();
        this.logger.log(`${method} ${url} ${res.statusCode} ${Date.now() - start}ms`);
      }),
    );
  }
}
```

### Response transform (envelope)

```typescript
// common/interceptors/transform.interceptor.ts
import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable, map } from 'rxjs';

@Injectable()
export class TransformInterceptor<T> implements NestInterceptor<T, { data: T }> {
  intercept(_context: ExecutionContext, next: CallHandler<T>): Observable<{ data: T }> {
    return next.handle().pipe(map((data) => ({ data })));
  }
}
```

---

## Common Pitfalls

1. **Circular dependencies.** Module A imports Module B which imports Module A. Use `forwardRef()` or restructure to break the cycle. If you need `forwardRef`, the architecture likely needs rethinking.
2. **Not using `whitelist: true` on ValidationPipe.** Without it, extra properties pass through silently — a security risk and a debugging nightmare.
3. **Overusing `@Global()` modules.** Only truly cross-cutting concerns (config, database, logging) should be global. Feature modules should explicitly import what they need.
4. **Testing with real database in unit tests.** Unit tests should mock the database layer. Use NestJS E2E tests (with `supertest`) for integration testing against a real DB.
5. **Forgetting to `await app.init()` in E2E tests.** Without it, providers aren't initialized and tests fail with cryptic DI errors.
6. **Putting business logic in controllers.** Controllers should only parse requests and return responses. All logic goes in services.
7. **Not using `PartialType` / `PickType` / `OmitType` for DTOs.** Duplicating validation rules across create/update DTOs leads to drift. Use mapped types.
8. **Ignoring graceful shutdown.** Call `app.enableShutdownHooks()` so `onModuleDestroy` lifecycle hooks fire on SIGTERM (critical for database connections in containers).

---

## Related Skills

- `openapi` — OpenAPI spec design (NestJS auto-generates from decorators)
- `typescript` — TypeScript patterns (NestJS is TypeScript-first)
- `postgresql` — Database design and query optimization
- `docker` — Containerizing NestJS apps
- `playwright` — E2E testing NestJS APIs through the browser
- `authentication` — JWT / OAuth2 patterns (framework-agnostic)
- `github-actions` — CI/CD for NestJS projects
