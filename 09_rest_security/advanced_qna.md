# REST + Security — Advanced Q&A & Production Patterns

---

## API DESIGN ADVANCED

**Q: How would you design pagination? Cursor vs offset?**

| Method | How it Works | Pros | Cons |
|--------|-------------|------|------|
| Offset (?page=2&limit=10) | Skip N rows | Simple | Slow on large offsets, inconsistent with inserts |
| Cursor (?after=cursor_id) | Start from a specific record | Fast, consistent | Can't jump to page 5 |

```js
// Offset pagination (simple, most common)
GET /api/cases?page=2&limit=10
// Server: Case.find().skip(10).limit(10)

// Cursor pagination (better for large datasets)
GET /api/cases?after=64a7f...&limit=10
// Server: Case.find({ _id: { $gt: cursor } }).limit(10)
// Response: { data: [...], nextCursor: "64b8g..." }
```

---

**Q: How do you version an API when you need breaking changes?**
A:
1. **URL versioning** (recommended): `/api/v1/`, `/api/v2/` — clear, easy to route
2. **Header versioning**: `Accept: application/vnd.myapi.v2+json` — clean URLs, harder to test in browser
3. **Query param**: `?version=2` — simple but pollutes URLs
4. Keep v1 alive for at least 6-12 months after v2 ships. Document deprecation timeline.

---

**Q: How do you design an idempotent POST endpoint?**
A: POST is normally not idempotent. Make it idempotent with idempotency keys:
```js
// Client generates a unique key per request
POST /api/payments
Headers: { "Idempotency-Key": "unique-uuid-per-request" }

// Server: check if this key was already processed
const existing = await PaymentAttempt.findOne({ idempotencyKey });
if (existing) return res.json(existing.result);  // return cached result

// Process the payment
const result = await processPayment(req.body);
await PaymentAttempt.create({ idempotencyKey, result });
return res.status(201).json(result);
```

---

## OAUTH 2.0 vs JWT vs SESSION

**Q: What is the difference between OAuth 2.0, JWT, and session-based auth?**

| Approach | How It Works | Best For |
|----------|-------------|----------|
| Session | Server stores session in DB/Redis, sends cookie with session ID | Traditional web apps |
| JWT | Self-contained token, server is stateless | APIs, microservices, mobile |
| OAuth 2.0 | Delegation protocol — "Login with Google" | Third-party access |

```
OAuth 2.0 flow (simplified):
1. User clicks "Login with Google"
2. App redirects to Google's auth server with client_id, scope, redirect_uri
3. User approves → Google sends authorization code to redirect_uri
4. App exchanges code for access_token + id_token (JWT)
5. App uses access_token to call Google APIs on user's behalf
```

---

**Q: What is CSRF and how do you prevent it?**
A: Cross-Site Request Forgery — attacker tricks user's browser into making requests to your API using the user's cookies.

Prevention:
1. **httpOnly cookies with SameSite=Strict** — browser won't send cookie on cross-site requests
2. **CSRF token** — include a random token in every form, verify server-side
3. **JWT in Authorization header** — can't be set by cross-site requests (unlike cookies)

---

**Q: What is XSS and how do you prevent it?**
A: Cross-Site Scripting — attacker injects malicious JavaScript into your page.
Prevention:
1. **Escape user input** — `express-validator`'s `.escape()`, React does this by default
2. **Content-Security-Policy header** — helmet sets this
3. **Never use `innerHTML` with user data** — use `textContent` or React's JSX
4. **httpOnly cookies** — XSS can't steal tokens stored in httpOnly cookies

---

## RATE LIMITING ADVANCED

**Q: What are different rate limiting strategies?**

| Strategy | How It Works | Use Case |
|----------|-------------|----------|
| Fixed window | Count requests in fixed time window | Simple |
| Sliding window | Rolling window of last N seconds | More accurate |
| Token bucket | Refill tokens at a rate, each request costs a token | Allows burst |
| Leaky bucket | Queue requests, process at fixed rate | Smooth traffic |

**Q: How do you rate limit by user ID instead of IP?**
```js
const rateLimit = require("express-rate-limit");

app.post("/api/generate", authenticate, rateLimit({
    windowMs: 60 * 1000,  // 1 minute
    max: 10,
    keyGenerator: (req) => req.user.id,   // rate limit per user, not per IP
    message: { error: "Rate limit exceeded" }
}));
```

---

## MICROSERVICES SECURITY

**Q: How do you handle auth in microservices?**
A: Two common patterns:
1. **API Gateway auth** — gateway validates JWT, passes user info in headers to services:
```
Client → [API Gateway: validate JWT] → [User Service: trust header X-User-Id]
                                      → [Case Service: trust header X-User-Id]
                                      → [Doc Service: trust header X-User-Id]
```
2. **Service-to-service auth** — internal services authenticate to each other with service tokens (different from user tokens).

---

## LOGGING AND MONITORING

**Q: What should you log in production?**
A:
- Every request: method, path, status code, response time, user ID
- Error details: stack trace (server-side only, never sent to client)
- Authentication events: login success/failure, token refresh
- Business events: case created, payment processed
- NOT: passwords, tokens, personal data (GDPR compliance)

```js
// Morgan for HTTP request logging
const morgan = require("morgan");
app.use(morgan(":method :url :status :res[content-length] - :response-time ms"));

// Winston for structured logging
const winston = require("winston");
const logger = winston.createLogger({
    level: "info",
    format: winston.format.json(),
    transports: [
        new winston.transports.File({ filename: "error.log", level: "error" }),
        new winston.transports.Console()
    ]
});
logger.info("Case created", { caseId: id, userId: req.user.id });
```
