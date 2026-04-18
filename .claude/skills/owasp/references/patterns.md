# Owasp — Patterns


# OWASP Web Application Security

## When to Use

- Security code reviews
- Implementing authentication or authorization
- Handling user input from untrusted sources
- Building or auditing web API endpoints
- Configuring CORS, CSP, or other security headers
- Managing secrets, tokens, or credentials in code
- Setting up rate limiting or brute force protection

## When NOT to Use

- General code style or formatting reviews with no security implications
- Non-web applications such as CLI tools, batch scripts, or desktop utilities
- Performance optimization tasks where security is not the concern
- Infrastructure-level security (firewall rules, network segmentation)

---

## Core Patterns

### 1. Input Validation & Sanitization

Always validate input at the boundary. Use allowlists over denylists.

**Python (Pydantic)**

```python
# BAD - no validation, accepts anything
@app.post("/users")
async def create_user(request: Request):
    data = await request.json()
    name = data["name"]          # no length check, no type check
    email = data["email"]        # no format validation
    role = data["role"]          # user controls their own role
    db.execute(f"INSERT INTO users VALUES ('{name}', '{email}', '{role}')")

# GOOD - strict schema validation with Pydantic
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    viewer = "viewer"
    editor = "editor"

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z\s\-]+$")
    email: EmailStr
    role: UserRole = UserRole.viewer  # default to least privilege

@app.post("/users")
async def create_user(payload: CreateUserRequest):
    # Pydantic rejects invalid data before this code runs
    db.add(User(name=payload.name, email=payload.email, role=payload.role))
```

**TypeScript (Zod)**

```typescript
// BAD - trusting req.body directly
app.post("/users", (req, res) => {
  const { name, email, role } = req.body; // no validation
  db.query(`INSERT INTO users VALUES ('${name}', '${email}', '${role}')`);
});

// GOOD - validate with Zod at the boundary
import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s\-]+$/),
  email: z.string().email(),
  role: z.enum(["viewer", "editor"]).default("viewer"),
});

app.post("/users", (req, res) => {
  const result = CreateUserSchema.safeParse(req.body);
  if (!result.success) {
    return res.status(400).json({ errors: result.error.flatten() });
  }
  // result.data is typed and validated
  await prisma.user.create({ data: result.data });
});
```

**File Upload Validation**

```python
# GOOD - validate MIME type (not just extension), size, and sanitize filename
import magic

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

def validate_upload(file_bytes: bytes, filename: str) -> bool:
    if len(file_bytes) > MAX_SIZE:
        raise ValueError("File too large")
    if magic.from_buffer(file_bytes, mime=True) not in ALLOWED_TYPES:
        raise ValueError("Disallowed file type")
    if ".." in filename or filename.startswith("."):
        raise ValueError("Invalid filename")
    return True
```

### 2. SQL Injection Prevention

Never concatenate user input into SQL strings. Always use parameterized queries or ORM methods.

**Raw SQL (Python)**

```python
# BAD - string interpolation creates injection vector
def get_user(user_id: str):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    # Input: "'; DROP TABLE users; --" destroys the table
    cursor.execute(query)

# GOOD - parameterized query
def get_user(user_id: str):
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cursor.fetchone()
```

**SQLAlchemy (Python)**

```python
# BAD - text() with f-string
from sqlalchemy import text
result = session.execute(text(f"SELECT * FROM users WHERE name = '{name}'"))

# GOOD - bound parameters with text()
result = session.execute(text("SELECT * FROM users WHERE name = :name"), {"name": name})

# GOOD - ORM query (automatically parameterized)
user = session.query(User).filter(User.name == name).first()
```

**Prisma (TypeScript)**

```typescript
// BAD - raw query with interpolation
const user = await prisma.$queryRawUnsafe(`SELECT * FROM users WHERE id = '${id}'`);

// GOOD - tagged template (auto-parameterized)
const user = await prisma.$queryRaw`SELECT * FROM users WHERE id = ${id}`;

// GOOD - Prisma client methods (always safe)
const user = await prisma.user.findUnique({ where: { id } });
```

### 3. XSS Prevention

Prevent cross-site scripting by encoding output, setting CSP headers, and sanitizing HTML.

**Output Encoding**

```typescript
// BAD - renders raw user content as HTML
element.innerHTML = userComment;

// GOOD - use textContent for plain text
element.textContent = userComment;

// GOOD - React auto-escapes by default (don't bypass it)
return <div>{userComment}</div>;

// BAD - dangerouslySetInnerHTML defeats React's protection
return <div dangerouslySetInnerHTML={{ __html: userComment }} />;
```

**Sanitizing HTML When You Must Render It**

```typescript
// GOOD - sanitize with DOMPurify when HTML rendering is required
import DOMPurify from "dompurify";

const cleanHtml = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ["b", "i", "em", "strong", "a", "p", "br"],
  ALLOWED_ATTR: ["href", "title"],
});
return <div dangerouslySetInnerHTML={{ __html: cleanHtml }} />;
```

### 4. Authentication Patterns

**Password Hashing**

```python
# BAD - plain text or weak hashing
hashed = hashlib.md5(password.encode()).hexdigest()  # trivially crackable

# GOOD - use argon2 (preferred) or bcrypt with proper cost
from passlib.hash import argon2

hashed = argon2.hash(password)
is_valid = argon2.verify(password, hashed)
```

```typescript
// GOOD - bcrypt in Node.js
import bcrypt from "bcrypt";

const SALT_ROUNDS = 12;
const hashed = await bcrypt.hash(password, SALT_ROUNDS);
const isValid = await bcrypt.compare(password, hashed);
```

**JWT Best Practices**

```python
# BAD - long-lived token, weak secret
token = jwt.encode({"user_id": 1, "exp": datetime.utcnow() + timedelta(days=365)},
                   "secret123", algorithm="HS256")

# GOOD - short expiry, strong secret, httpOnly cookie delivery
ACCESS_TOKEN_EXPIRY = timedelta(minutes=15)

def create_access_token(user_id: int) -> str:
    return jwt.encode(
        {"sub": user_id, "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRY},
        os.environ["JWT_SECRET_KEY"], algorithm="HS256",
    )

def set_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token", value=token,
        httponly=True, secure=True, samesite="lax",  # not accessible via JS, HTTPS only
        max_age=int(ACCESS_TOKEN_EXPIRY.total_seconds()),
    )
```

**Session Management Rules**

- Set session timeouts (30 minutes idle, 8 hours absolute)
- Regenerate session ID after login to prevent session fixation
- Store sessions server-side (Redis, database), not in cookies
- Clear sessions on logout (`request.session.clear()`)
- Use `httponly`, `secure`, and `samesite=lax` on session cookies

### 5. Authorization & Access Control

**RBAC Pattern**

```python
# GOOD - role-based access control with decorator
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    editor = "editor"
    viewer = "viewer"

ROLE_HIERARCHY = {Role.admin: 3, Role.editor: 2, Role.viewer: 1}

def require_role(minimum_role: Role):
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = request.state.user
            if ROLE_HIERARCHY.get(user.role, 0) < ROLE_HIERARCHY[minimum_role]:
                raise HTTPException(status_code=403)
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

@app.delete("/posts/{post_id}")
@require_role(Role.editor)
async def delete_post(request: Request, post_id: int): ...
```

**Middleware-Based Authorization (Express)**

```typescript
// GOOD - authorization middleware
function requireRole(...allowedRoles: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: "Forbidden" });
    }
    next();
  };
}

app.delete("/posts/:id", requireRole("admin", "editor"), deletePostHandler);
```

**Object-Level Permissions**

```python
# BAD - checks auth but not ownership (any user can edit any document)
@app.put("/documents/{doc_id}")
async def update_document(doc_id: int, payload: UpdateDoc, user=Depends(get_current_user)):
    doc = await db.get(Document, doc_id)
    doc.content = payload.content

# GOOD - verify ownership or admin role on every mutation
@app.put("/documents/{doc_id}")
async def update_document(doc_id: int, payload: UpdateDoc, user=Depends(get_current_user)):
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404)
    if doc.owner_id != user.id and user.role != Role.admin:
        raise HTTPException(status_code=403)
    doc.content = payload.content
```

### 6. CORS Configuration

**FastAPI**

```python
# BAD - allows everything
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# GOOD - restrictive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com", "https://staging.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Express**

```typescript
// BAD
app.use(cors({ origin: true, credentials: true }));

// GOOD - explicit allowlist with callback
const ALLOWED_ORIGINS = ["https://app.example.com"];
app.use(cors({
  origin: (origin, cb) => {
    if (!origin || ALLOWED_ORIGINS.includes(origin)) cb(null, true);
    else cb(new Error("Not allowed by CORS"));
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE"],
}));
```

### 7. Security Headers

**Express with Helmet**

```typescript
// GOOD - Helmet sets secure defaults for all critical headers
import helmet from "helmet";

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:"],
      frameAncestors: ["'none'"],
    },
  },
  hsts: { maxAge: 31536000, includeSubDomains: true, preload: true },
}));
```

**FastAPI**

```python
# GOOD - security headers middleware
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    return response
```

### 8. Secret Management

```python
# BAD - hardcoded secrets
DATABASE_URL = "postgresql://admin:p@ssw0rd@localhost/mydb"
API_KEY = "sk-1234567890abcdef"
JWT_SECRET = "mysecret"

# GOOD - environment variables with validation
import os

def get_required_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Required environment variable {key} is not set")
    return value

DATABASE_URL = get_required_env("DATABASE_URL")
API_KEY = get_required_env("API_KEY")
JWT_SECRET = get_required_env("JWT_SECRET")
```

**.env and .gitignore**

```bash
# .env (NEVER commit this file)
DATABASE_URL=postgresql://admin:securepass@localhost/mydb
JWT_SECRET=a-very-long-random-string-from-openssl-rand
API_KEY=sk-prod-xxxxxxxxxxxx
```

```gitignore
# .gitignore - always include these
.env
.env.*
!.env.example
*.pem
*.key
credentials.json
```

Commit a `.env.example` with empty values to document required variables without exposing secrets.

### 9. Rate Limiting

**Python (FastAPI with slowapi)**

```python
# GOOD - rate limiting on sensitive endpoints
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # brute force protection
async def login(request: Request, credentials: LoginRequest):
    ...

@app.post("/api/data")
@limiter.limit("100/minute")  # general API rate limit
async def get_data(request: Request):
    ...
```

**Express (express-rate-limit)**

```typescript
// GOOD - tiered rate limiting
import rateLimit from "express-rate-limit";

const generalLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 100 });
const authLimiter = rateLimit({ windowMs: 15 * 60 * 1000, max: 5 });

app.use("/api/", generalLimiter);
app.use("/auth/login", authLimiter);
app.use("/auth/register", authLimiter);
```

### 10. Dependency Security

```bash
# Python - audit dependencies
pip install pip-audit
pip-audit                          # scan for known vulnerabilities
pip-audit --fix                    # auto-fix where possible

# Node.js - audit dependencies
npm audit                          # list vulnerabilities
npm audit fix                      # auto-fix compatible updates
pnpm audit                         # pnpm equivalent

# Always commit lock files to ensure reproducible builds
# Python: requirements.txt or poetry.lock
# Node.js: package-lock.json, pnpm-lock.yaml, or yarn.lock
```

Run `npm audit --audit-level=high` and `pip-audit --strict` in CI (e.g., GitHub Actions on every PR and weekly schedule). Treat high-severity findings as build failures.

---

## Best Practices

1. **Validate at the boundary, trust nothing inside.** Every piece of user input -- query params, headers, request bodies, file uploads -- must be validated before processing. Use Pydantic or Zod schemas, not manual checks.

2. **Apply the principle of least privilege everywhere.** Default to the most restrictive access. Grant permissions explicitly. Use role-based access control and verify object-level ownership on every mutation.

3. **Never store or log secrets in plain text.** Use environment variables, a secret manager, or encrypted storage. Ensure secrets never appear in logs, error messages, or version control.

4. **Use strong, adaptive password hashing.** Always use argon2 or bcrypt with a sufficient work factor. Never use MD5, SHA-1, or SHA-256 alone for password storage.

5. **Set security headers on every response.** Enable HSTS, CSP, X-Content-Type-Options, X-Frame-Options, and Referrer-Policy. Use Helmet for Express and middleware for FastAPI.

6. **Fail closed, not open.** When authentication or authorization checks encounter errors, deny access by default. Never fall through to an unprotected code path on exception.

7. **Keep dependencies updated and audited.** Run `npm audit` and `pip-audit` in CI pipelines. Pin dependency versions with lock files. Review changelogs before major upgrades.

8. **Enforce rate limiting on all public-facing endpoints.** Apply stricter limits on authentication and password reset endpoints. Use IP-based and account-based limiting together for defense in depth.

---

## Common Pitfalls

1. **Trusting client-side validation alone.** Attackers bypass browser validation trivially. Always re-validate on the server.

2. **Using wildcard CORS with credentials.** `allow_origins=["*"]` with credentials is insecure and browsers reject it. Specify exact origins.

3. **Storing JWTs in localStorage.** Any XSS can steal them. Use httpOnly, secure, sameSite cookies instead.

4. **Returning detailed error messages in production.** Stack traces help attackers. Return generic messages to clients, log details server-side.

5. **Using ORM raw query methods unsafely.** `$queryRawUnsafe` and `text()` with f-strings bypass ORM protections. Audit every raw SQL call.

6. **Checking authentication but not authorization.** "Logged in" does not mean "authorized." Check object-level permissions on every write.

7. **Disabling security in dev and shipping it.** CSP, CORS, HTTPS disabled for convenience can reach production. Use environment-aware config.

8. **Ignoring dependency vulnerabilities.** Known CVEs in transitive deps are a top attack vector. Automate auditing in CI.

---

## Security Review Checklist

- [ ] All user input validated with schema (Pydantic / Zod) before processing
- [ ] No string concatenation or interpolation in SQL queries
- [ ] Passwords hashed with argon2 or bcrypt (never MD5/SHA)
- [ ] JWTs have short expiry, use httpOnly cookies, strong secret from env
- [ ] Authorization checked at object level, not just authentication
- [ ] CORS configured with explicit origin allowlist (no wildcards with credentials)
- [ ] Security headers set: CSP, HSTS, X-Content-Type-Options, X-Frame-Options
- [ ] No secrets hardcoded in source -- all from environment variables
- [ ] .env files listed in .gitignore, .env.example committed
- [ ] Rate limiting applied to login, registration, and password reset endpoints
- [ ] File uploads validated by MIME type, size, and sanitized filename
- [ ] Error responses do not leak stack traces or internal details
- [ ] Dependencies audited with npm audit / pip-audit (no high-severity CVEs)
- [ ] HTTPS enforced in production with HSTS preload
- [ ] No use of eval(), dangerouslySetInnerHTML (without DOMPurify), or innerHTML

---

## Related Skills

- `authentication` - Authentication and authorization implementation patterns
- `error-handling` - Secure error handling that avoids leaking sensitive information
- `docker` — Container security hardening
- `defense-in-depth` — Multi-layer security validation
