---
name: authentication
description: >
  Authentication and authorization patterns for web applications. Use this skill when implementing JWT tokens, OAuth2 flows, session management, role-based access control (RBAC), password hashing, or multi-factor authentication. Trigger whenever code handles login, signup, token refresh, protected routes, permission checks, or user identity verification. Also applies to middleware auth guards and API key authentication.
---

# Authentication & Authorization Patterns

## When to Use

- Implementing login, signup, or logout flows for web applications
- Setting up JWT access tokens and refresh token rotation
- Building OAuth2 integrations (Google, GitHub, or custom providers)
- Adding role-based or permission-based access control to API endpoints
- Protecting routes with middleware guards in Next.js, Express, or FastAPI

## When NOT to Use

- Public-only APIs that require no identity verification (e.g., open data endpoints)
- Internal services secured entirely at the network level (VPC, service mesh mTLS) with no application-layer auth
- Static sites with no user-specific content or server-side logic

---

## Core Patterns

### 1. JWT Patterns

Use short-lived access tokens for API authorization and long-lived refresh tokens for session continuity. Never store access tokens in localStorage.

**Token structure and signing**

```python
# BAD - long-lived token, weak secret, symmetric HS256 with hardcoded key
import jwt

token = jwt.encode(
    {"user_id": 1, "exp": datetime.utcnow() + timedelta(days=365)},
    "secret123",
    algorithm="HS256",
)

# GOOD - short-lived access token, strong secret from env, RS256 for production
import jwt
import os
from datetime import datetime, timedelta, timezone

ACCESS_TOKEN_EXPIRY = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRY = timedelta(days=7)

def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "role": role,
            "iat": now,
            "exp": now + ACCESS_TOKEN_EXPIRY,
            "type": "access",
        },
        os.environ["JWT_PRIVATE_KEY"],
        algorithm="RS256",
    )

def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": str(user_id),
            "iat": now,
            "exp": now + REFRESH_TOKEN_EXPIRY,
            "type": "refresh",
            "jti": str(uuid.uuid4()),  # unique ID for revocation
        },
        os.environ["JWT_PRIVATE_KEY"],
        algorithm="RS256",
    )

def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        os.environ["JWT_PUBLIC_KEY"],
        algorithms=["RS256"],
        options={"require": ["sub", "exp", "type"]},
    )
```

**TypeScript -- JWT creation and verification**

```typescript
// GOOD - short-lived tokens with jose (works in Node.js and edge runtimes)
import { SignJWT, jwtVerify } from "jose";

const privateKey = new TextEncoder().encode(process.env.JWT_SECRET!);

async function createAccessToken(userId: string, role: string): Promise<string> {
  return new SignJWT({ role, type: "access" })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(userId)
    .setIssuedAt()
    .setExpirationTime("15m")
    .sign(privateKey);
}

async function createRefreshToken(userId: string): Promise<string> {
  return new SignJWT({ type: "refresh", jti: crypto.randomUUID() })
    .setProtectedHeader({ alg: "HS256" })
    .setSubject(userId)
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(privateKey);
}

async function verifyToken(token: string): Promise<{ sub: string; role?: string }> {
  const { payload } = await jwtVerify(token, privateKey, {
    algorithms: ["HS256"],
    requiredClaims: ["sub", "exp", "type"],
  });
  return payload as { sub: string; role?: string };
}
```

**Secure cookie delivery**

```python
# GOOD - deliver tokens in httpOnly cookies, not in response body
from fastapi import Response

def set_auth_cookies(response: Response, access_token: str, refresh_token: str):
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,       # not accessible via JavaScript
        secure=True,         # HTTPS only
        samesite="lax",      # CSRF protection
        max_age=int(ACCESS_TOKEN_EXPIRY.total_seconds()),
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=int(REFRESH_TOKEN_EXPIRY.total_seconds()),
        path="/auth/refresh",  # only sent to refresh endpoint
    )

def clear_auth_cookies(response: Response):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth/refresh")
```

### 2. OAuth2 Flows

**Authorization code flow with PKCE (for SPAs and mobile apps)**

```typescript
// GOOD - PKCE flow for single-page applications (no client secret exposed)
import crypto from "crypto";

// Step 1: Generate code verifier and challenge
function generatePKCE(): { verifier: string; challenge: string } {
  const verifier = crypto.randomBytes(32).toString("base64url");
  const challenge = crypto
    .createHash("sha256")
    .update(verifier)
    .digest("base64url");
  return { verifier, challenge };
}

// Step 2: Redirect user to authorization server
function getAuthorizationUrl(codeChallenge: string): string {
  const params = new URLSearchParams({
    response_type: "code",
    client_id: process.env.OAUTH_CLIENT_ID!,
    redirect_uri: process.env.OAUTH_REDIRECT_URI!,
    scope: "openid profile email",
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
    state: crypto.randomBytes(16).toString("hex"),
  });
  return `https://auth.example.com/authorize?${params}`;
}

// Step 3: Exchange code for tokens on the callback
async function exchangeCode(code: string, codeVerifier: string): Promise<TokenSet> {
  const response = await fetch("https://auth.example.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      grant_type: "authorization_code",
      code,
      redirect_uri: process.env.OAUTH_REDIRECT_URI!,
      client_id: process.env.OAUTH_CLIENT_ID!,
      code_verifier: codeVerifier,
    }),
  });

  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.status}`);
  }
  return response.json() as Promise<TokenSet>;
}
```

**Client credentials flow (server-to-server)**

```python
# GOOD - machine-to-machine auth with client credentials
import httpx
import os

async def get_service_token() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://auth.example.com/token",
            data={
                "grant_type": "client_credentials",
                "client_id": os.environ["SERVICE_CLIENT_ID"],
                "client_secret": os.environ["SERVICE_CLIENT_SECRET"],
                "scope": "read:data write:data",
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]
```

**Python -- OAuth2 callback handling with FastAPI**

```python
# GOOD - secure callback handler with state validation
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import httpx

router = APIRouter(prefix="/auth")

@router.get("/callback")
async def oauth_callback(request: Request, code: str, state: str):
    # Validate state to prevent CSRF
    stored_state = request.session.get("oauth_state")
    if not stored_state or state != stored_state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    code_verifier = request.session.pop("code_verifier")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://auth.example.com/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": os.environ["OAUTH_REDIRECT_URI"],
                "client_id": os.environ["OAUTH_CLIENT_ID"],
                "code_verifier": code_verifier,
            },
        )
        token_response.raise_for_status()
        tokens = token_response.json()

    # Create local session from OAuth tokens
    user_info = await fetch_user_info(tokens["access_token"])
    user = await get_or_create_user(user_info)
    response = RedirectResponse(url="/dashboard")
    set_auth_cookies(response, create_access_token(user.id, user.role), create_refresh_token(user.id))
    return response
```

### 3. Password Security

**Python -- argon2 (preferred) and bcrypt**

```python
# BAD - MD5 or SHA-256 alone is trivially crackable
import hashlib
hashed = hashlib.sha256(password.encode()).hexdigest()

# GOOD - argon2id (recommended by OWASP)
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,        # iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, password)
    except VerifyMismatchError:
        return False

# GOOD - bcrypt alternative
from passlib.hash import bcrypt

hashed = bcrypt.using(rounds=12).hash(password)
is_valid = bcrypt.verify(password, hashed)
```

**TypeScript -- bcrypt**

```typescript
// GOOD - bcrypt with sufficient cost factor
import bcrypt from "bcrypt";

const SALT_ROUNDS = 12; // ~250ms on modern hardware, adjust as needed

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

**Password validation rules**

```typescript
// GOOD - enforce minimum complexity without overly restrictive rules
import { z } from "zod";

const PasswordSchema = z
  .string()
  .min(8, "Password must be at least 8 characters")
  .max(128, "Password must not exceed 128 characters")
  .regex(/[a-z]/, "Must contain at least one lowercase letter")
  .regex(/[A-Z]/, "Must contain at least one uppercase letter")
  .regex(/[0-9]/, "Must contain at least one digit");

// Python equivalent with Pydantic
from pydantic import BaseModel, field_validator
import re

class PasswordInput(BaseModel):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        if not re.search(r"[a-z]", v):
            raise ValueError("Must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Must contain at least one digit")
        return v
```

**Timing-safe comparison**

```python
# BAD - standard equality leaks timing information
if stored_token == provided_token:
    grant_access()

# GOOD - constant-time comparison prevents timing attacks
import hmac

def safe_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())
```

```typescript
// GOOD - timing-safe comparison in Node.js
import crypto from "crypto";

function safeCompare(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
```

### 4. Session Management

**Cookie-based sessions with Redis store (Express)**

```typescript
// GOOD - server-side sessions stored in Redis
import session from "express-session";
import RedisStore from "connect-redis";
import { createClient } from "redis";

const redisClient = createClient({ url: process.env.REDIS_URL });
await redisClient.connect();

app.use(
  session({
    store: new RedisStore({ client: redisClient, prefix: "sess:" }),
    secret: process.env.SESSION_SECRET!,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 30 * 60 * 1000, // 30 minutes
    },
    name: "sid", // custom name -- do not use default "connect.sid"
  }),
);
```

**Session fixation prevention**

```typescript
// GOOD - regenerate session ID after login to prevent fixation
app.post("/login", async (req, res) => {
  const user = await authenticateUser(req.body.email, req.body.password);
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  // Regenerate session to prevent fixation attacks
  req.session.regenerate((err) => {
    if (err) return res.status(500).json({ error: "Session error" });
    req.session.userId = user.id;
    req.session.role = user.role;
    req.session.loginAt = Date.now();
    res.json({ user: { id: user.id, name: user.name } });
  });
});

// GOOD - clear session fully on logout
app.post("/logout", (req, res) => {
  req.session.destroy((err) => {
    if (err) return res.status(500).json({ error: "Logout failed" });
    res.clearCookie("sid");
    res.json({ message: "Logged out" });
  });
});
```

**Python -- FastAPI session with Redis**

```python
# GOOD - server-side session using Redis
from fastapi import Request, Response
import redis.asyncio as redis
import uuid
import json

redis_client = redis.from_url(os.environ["REDIS_URL"])

SESSION_TTL = 1800  # 30 minutes

async def create_session(response: Response, data: dict) -> str:
    session_id = str(uuid.uuid4())
    await redis_client.setex(f"session:{session_id}", SESSION_TTL, json.dumps(data))
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=SESSION_TTL,
    )
    return session_id

async def get_session(request: Request) -> dict | None:
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    data = await redis_client.get(f"session:{session_id}")
    if data:
        # Refresh TTL on access (sliding expiry)
        await redis_client.expire(f"session:{session_id}", SESSION_TTL)
        return json.loads(data)
    return None

async def destroy_session(request: Request, response: Response):
    session_id = request.cookies.get("session_id")
    if session_id:
        await redis_client.delete(f"session:{session_id}")
    response.delete_cookie("session_id")
```

### 5. RBAC Patterns

**Role and permission model**

```python
# GOOD - permission-based RBAC, not just role names
from enum import Enum

class Permission(str, Enum):
    READ_POSTS = "read:posts"
    WRITE_POSTS = "write:posts"
    DELETE_POSTS = "delete:posts"
    MANAGE_USERS = "manage:users"
    ADMIN_ALL = "admin:all"

ROLE_PERMISSIONS: dict[str, set[Permission]] = {
    "viewer": {Permission.READ_POSTS},
    "editor": {Permission.READ_POSTS, Permission.WRITE_POSTS},
    "admin": {Permission.READ_POSTS, Permission.WRITE_POSTS, Permission.DELETE_POSTS, Permission.MANAGE_USERS},
    "superadmin": {Permission.ADMIN_ALL},
}

def has_permission(user_role: str, required: Permission) -> bool:
    permissions = ROLE_PERMISSIONS.get(user_role, set())
    return required in permissions or Permission.ADMIN_ALL in permissions
```

**FastAPI -- dependency-based authorization**

```python
# GOOD - reusable auth dependency with permission check
from fastapi import Depends, HTTPException, Request

async def get_current_user(request: Request) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
        user = await user_repo.get(int(payload["sub"]))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_permission(permission: Permission):
    async def checker(user: User = Depends(get_current_user)):
        if not has_permission(user.role, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    user: User = Depends(require_permission(Permission.DELETE_POSTS)),
):
    post = await post_repo.get(post_id)
    if not post:
        raise HTTPException(status_code=404)
    await post_repo.delete(post_id)
    return {"deleted": True}
```

**Express -- middleware-based authorization**

```typescript
// GOOD - composable permission middleware
interface AuthUser {
  id: string;
  role: string;
  permissions: string[];
}

function requirePermission(...required: string[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = req.user as AuthUser | undefined;
    if (!user) {
      return res.status(401).json({ error: "Not authenticated" });
    }

    const hasAll = required.every(
      (perm) => user.permissions.includes(perm) || user.permissions.includes("admin:all"),
    );

    if (!hasAll) {
      return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
  };
}

// Usage
app.delete("/posts/:id", requirePermission("delete:posts"), deletePostHandler);
app.get("/admin/users", requirePermission("manage:users"), listUsersHandler);
```

### 6. Protected Routes

**Next.js middleware (App Router)**

```typescript
// middleware.ts -- runs on every matching request at the edge
import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const PUBLIC_PATHS = ["/", "/login", "/signup", "/api/auth"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) {
    return NextResponse.next();
  }

  const token = request.cookies.get("access_token")?.value;
  if (!token) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  try {
    const secret = new TextEncoder().encode(process.env.JWT_SECRET!);
    await jwtVerify(token, secret);
    return NextResponse.next();
  } catch {
    // Token invalid or expired -- redirect to login
    const response = NextResponse.redirect(new URL("/login", request.url));
    response.cookies.delete("access_token");
    return response;
  }
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

**FastAPI -- dependency injection guard**

```python
# GOOD - protect entire router with a dependency
from fastapi import APIRouter, Depends

protected_router = APIRouter(
    prefix="/api/v1",
    dependencies=[Depends(get_current_user)],  # all routes require auth
)

@protected_router.get("/profile")
async def get_profile(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "role": user.role}

@protected_router.get("/admin/stats")
async def admin_stats(user: User = Depends(require_permission(Permission.ADMIN_ALL))):
    return await compute_stats()

# Mount protected and public routers separately
app.include_router(auth_router)       # /auth/* -- public
app.include_router(protected_router)  # /api/v1/* -- requires auth
```

**Express -- route-level guard**

```typescript
// GOOD - auth middleware applied selectively
function requireAuth(req: Request, res: Response, next: NextFunction) {
  const token = req.cookies.access_token;
  if (!token) {
    return res.status(401).json({ error: "Authentication required" });
  }

  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET!);
    req.user = payload as AuthUser;
    next();
  } catch {
    res.clearCookie("access_token");
    return res.status(401).json({ error: "Invalid or expired token" });
  }
}

// Public routes
app.post("/auth/login", loginHandler);
app.post("/auth/register", registerHandler);

// Protected routes
app.use("/api", requireAuth);
app.get("/api/profile", profileHandler);
app.get("/api/posts", listPostsHandler);
```

### 7. Multi-Factor Authentication (TOTP)

**Python -- pyotp**

```python
# GOOD - TOTP setup and verification
import pyotp

def generate_totp_secret() -> str:
    """Generate a new TOTP secret for a user."""
    return pyotp.random_base32()

def get_totp_provisioning_uri(secret: str, user_email: str, issuer: str = "MyApp") -> str:
    """Generate a QR code URI for authenticator app setup."""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=user_email,
        issuer_name=issuer,
    )

def verify_totp(secret: str, code: str) -> bool:
    """Verify a TOTP code with a 30-second window tolerance."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # allows +/- 30 seconds
```

**TypeScript -- otplib**

```typescript
// GOOD - TOTP with otplib
import { authenticator } from "otplib";

function generateTotpSecret(): string {
  return authenticator.generateSecret();
}

function getTotpUri(secret: string, email: string): string {
  return authenticator.keyuri(email, "MyApp", secret);
}

function verifyTotp(secret: string, code: string): boolean {
  return authenticator.check(code, secret);
}
```

**Backup codes**

```python
# GOOD - generate one-time backup codes for MFA recovery
import secrets

def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate single-use backup codes. Store hashed, show once."""
    return [secrets.token_hex(4).upper() for _ in range(count)]
    # Example output: ["A1B2C3D4", "E5F6A7B8", ...]

# Store hashed backup codes in the database
from argon2 import PasswordHasher
ph = PasswordHasher()

async def store_backup_codes(user_id: int, codes: list[str]):
    hashed_codes = [ph.hash(code) for code in codes]
    await db.execute(
        "UPDATE users SET backup_codes = $1 WHERE id = $2",
        [json.dumps(hashed_codes), user_id],
    )

async def verify_backup_code(user_id: int, code: str) -> bool:
    user = await db.get(User, user_id)
    hashed_codes = json.loads(user.backup_codes)
    for i, hashed in enumerate(hashed_codes):
        try:
            if ph.verify(hashed, code):
                # Remove used code (single-use)
                hashed_codes.pop(i)
                await db.execute(
                    "UPDATE users SET backup_codes = $1 WHERE id = $2",
                    [json.dumps(hashed_codes), user_id],
                )
                return True
        except Exception:
            continue
    return False
```

**MFA login flow**

```python
# GOOD - two-step login: credentials first, then MFA
@router.post("/auth/login")
async def login(credentials: LoginRequest, response: Response):
    user = await authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.mfa_enabled:
        # Issue a short-lived MFA challenge token (not a full session)
        mfa_token = create_mfa_challenge_token(user.id)
        return {"requires_mfa": True, "mfa_token": mfa_token}

    # No MFA -- issue full tokens
    set_auth_cookies(response, create_access_token(user.id, user.role), create_refresh_token(user.id))
    return {"user": {"id": user.id, "name": user.name}}

@router.post("/auth/mfa/verify")
async def verify_mfa(payload: MfaVerifyRequest, response: Response):
    # Validate the MFA challenge token
    challenge = decode_mfa_challenge_token(payload.mfa_token)
    user = await user_repo.get(challenge["user_id"])

    if not verify_totp(user.totp_secret, payload.code):
        # Also check backup codes as fallback
        if not await verify_backup_code(user.id, payload.code):
            raise HTTPException(status_code=401, detail="Invalid MFA code")

    set_auth_cookies(response, create_access_token(user.id, user.role), create_refresh_token(user.id))
    return {"user": {"id": user.id, "name": user.name}}
```

---

## Best Practices

1. **Use short-lived access tokens (5-15 minutes) paired with refresh tokens (7-30 days).** Short access tokens limit the damage window if a token is compromised. Refresh tokens allow seamless re-authentication without re-entering credentials.

2. **Deliver tokens in httpOnly, secure, sameSite cookies.** Never return tokens in JSON response bodies for browser-based apps. httpOnly prevents XSS from reading the token, secure ensures HTTPS-only transmission, and sameSite=lax mitigates CSRF.

3. **Hash passwords with argon2id or bcrypt, never with MD5, SHA-1, or SHA-256 alone.** Adaptive hashing functions include a work factor that makes brute-force attacks computationally expensive. Increase the cost factor as hardware improves.

4. **Regenerate session IDs after login.** Session fixation attacks exploit predictable or reused session IDs. Always issue a new session ID after successful authentication.

5. **Validate the state parameter in OAuth2 callbacks.** The state parameter prevents CSRF attacks during the authorization flow. Generate a cryptographically random value, store it in the session, and verify it when the callback arrives.

6. **Implement token revocation for refresh tokens.** Store refresh token JTIs (unique identifiers) in a database or Redis. On logout, revoke all active refresh tokens for the user. Check the revocation list on every refresh attempt.

7. **Apply the principle of least privilege in RBAC.** Default new users to the most restrictive role. Grant permissions explicitly, not implicitly. Check permissions at the object level, not just the role level.

8. **Rate-limit authentication endpoints aggressively.** Apply strict rate limits (5-10 attempts per minute) on login, registration, password reset, and MFA verification endpoints. Use both IP-based and account-based limiting.

---

## Common Pitfalls

1. **Storing JWTs in localStorage.** Any XSS vulnerability can steal the token. Use httpOnly cookies instead. If you must use localStorage (e.g., for native apps), pair it with strict CSP and regular XSS auditing.

2. **Not validating the token type claim.** Without a `type` field in the JWT payload, a refresh token could be used as an access token and vice versa. Always include and verify a `type` claim.

3. **Using symmetric keys (HS256) with shared secrets across services.** If multiple services verify tokens, any service that can verify can also forge tokens. Use asymmetric keys (RS256/ES256) so only the auth service holds the private key.

4. **Checking authentication but not authorization.** A valid token proves identity but not permission. Always verify that the authenticated user has the specific permission required for the requested action.

5. **Returning different error messages for "user not found" vs "wrong password."** This leaks information about which accounts exist (user enumeration). Return a generic "Invalid credentials" message for both cases.

6. **Not setting absolute session timeouts.** Sliding expiry alone means a session can live forever with continuous activity. Set an absolute maximum lifetime (e.g., 8 hours) in addition to idle timeout (e.g., 30 minutes).

---

## Security Checklist

- [ ] Access tokens expire within 15 minutes, refresh tokens within 7-30 days
- [ ] Tokens delivered in httpOnly, secure, sameSite cookies (not localStorage)
- [ ] Passwords hashed with argon2id or bcrypt (12+ rounds)
- [ ] Session IDs regenerated after successful login
- [ ] OAuth2 state parameter validated on callback
- [ ] Refresh tokens have unique JTI and can be revoked
- [ ] RBAC permissions checked at object level, not just role level
- [ ] Login, registration, and password reset endpoints are rate-limited
- [ ] Error messages do not distinguish between "user not found" and "wrong password"
- [ ] MFA backup codes are hashed and single-use
- [ ] TOTP secrets are stored encrypted at rest
- [ ] Absolute session timeout enforced alongside sliding expiry
- [ ] CSRF protection in place for all state-changing endpoints

---

## Related Skills

- `security/owasp` - OWASP Top 10 security patterns and secure coding practices
- `patterns/api-client` - HTTP client patterns including auth token injection and refresh flows
- `frameworks/fastapi` - FastAPI-specific dependency injection and middleware patterns
- `frameworks/nextjs` - Next.js middleware and route protection patterns
