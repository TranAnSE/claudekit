# Security Headers Reference

Comprehensive reference for HTTP security headers with recommended values and implementation examples.

---

## Header Reference Table

| Header | Purpose | Recommended Value |
|--------|---------|-------------------|
| `Content-Security-Policy` | Prevent XSS, data injection | See detailed section below |
| `Strict-Transport-Security` | Force HTTPS | `max-age=63072000; includeSubDomains; preload` |
| `X-Frame-Options` | Prevent clickjacking | `DENY` or `SAMEORIGIN` |
| `X-Content-Type-Options` | Prevent MIME sniffing | `nosniff` |
| `Referrer-Policy` | Control referer leakage | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | Restrict browser features | See detailed section below |

---

## Content-Security-Policy (CSP)

Controls which resources the browser is allowed to load.

**Starter policy (strict):**
```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'
```

**Key directives:**

| Directive | Controls | Example |
|-----------|----------|---------|
| `default-src` | Fallback for all resource types | `'self'` |
| `script-src` | JavaScript sources | `'self' https://cdn.example.com` |
| `style-src` | CSS sources | `'self' 'unsafe-inline'` |
| `img-src` | Image sources | `'self' data: https:` |
| `connect-src` | Fetch, XHR, WebSocket targets | `'self' https://api.example.com` |
| `frame-ancestors` | Who can embed this page | `'none'` |
| `form-action` | Form submission targets | `'self'` |

## Strict-Transport-Security (HSTS)

Forces browsers to use HTTPS for all future requests to this domain.

```
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
```

- `max-age=63072000` — 2 years (minimum for preload list)
- `includeSubDomains` — apply to all subdomains
- `preload` — opt into browser preload lists

## X-Frame-Options

Prevents the page from being embedded in iframes (clickjacking protection).

```
X-Frame-Options: DENY
```

| Value | Behavior |
|-------|----------|
| `DENY` | Never allow framing |
| `SAMEORIGIN` | Allow framing by same origin only |

Note: `frame-ancestors` in CSP is the modern replacement but set both for backward compatibility.

## X-Content-Type-Options

Prevents browsers from MIME-sniffing the response content type.

```
X-Content-Type-Options: nosniff
```

Always pair with correct `Content-Type` headers on responses.

## Referrer-Policy

Controls how much referrer information is sent with requests.

```
Referrer-Policy: strict-origin-when-cross-origin
```

| Value | Cross-Origin Sends | Same-Origin Sends |
|-------|-------------------|-------------------|
| `no-referrer` | Nothing | Nothing |
| `origin` | Origin only | Origin only |
| `strict-origin-when-cross-origin` | Origin (HTTPS only) | Full URL |
| `same-origin` | Nothing | Full URL |

## Permissions-Policy

Restricts which browser features the page can use.

```
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

| Feature | Recommended | Description |
|---------|-------------|-------------|
| `camera` | `()` | Disable camera access |
| `microphone` | `()` | Disable microphone |
| `geolocation` | `()` | Disable location |
| `payment` | `()` | Disable Payment API |
| `usb` | `()` | Disable USB access |
| `fullscreen` | `(self)` | Allow fullscreen for same origin |

---

## Implementation: Python (FastAPI)

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

app = FastAPI()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains; preload"
        )
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

## Implementation: Node.js (Express)

```typescript
import helmet from "helmet";
import express from "express";

const app = express();

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:", "https:"],
        frameAncestors: ["'none'"],
        baseUri: ["'self'"],
        formAction: ["'self'"],
      },
    },
    strictTransportSecurity: {
      maxAge: 63072000,
      includeSubDomains: true,
      preload: true,
    },
    frameguard: { action: "deny" },
    referrerPolicy: { policy: "strict-origin-when-cross-origin" },
    permissionsPolicy: {
      features: {
        camera: [],
        microphone: [],
        geolocation: [],
        payment: [],
      },
    },
  })
);
```

## Implementation: Next.js

```typescript
// next.config.ts
const securityHeaders = [
  { key: "Content-Security-Policy", value: "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; frame-ancestors 'none'" },
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), payment=()" },
];

export default {
  async headers() {
    return [{ source: "/(.*)", headers: securityHeaders }];
  },
};
```

---

## Verification

```bash
# Check headers on a live site
curl -I https://example.com

# Use securityheaders.com for a grade
# https://securityheaders.com/?q=https://example.com
```

*Source: [MDN HTTP Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers), [OWASP Secure Headers](https://owasp.org/www-project-secure-headers/)*
