# REST + Security Q&A — Interview Ready

---

## REST DESIGN PRINCIPLES

**Q: What are the 6 REST constraints (Richardson Maturity Model)?**
A: The formal REST constraints defined by Roy Fielding:
1. **Client-Server**: UI concerns are separated from data storage — client and server evolve independently
2. **Stateless**: every request contains all info needed; server stores no client state between requests
3. **Cacheable**: responses declare whether they can be cached; clients and proxies can cache safely
4. **Uniform Interface**: consistent resource identification (URIs), manipulation through representations, self-descriptive messages, HATEOAS
5. **Layered System**: client doesn't know if it's talking to the actual server or a proxy/load balancer
6. **Code on Demand** (optional): server can send executable code (JavaScript) to client

**Q: What is HATEOAS and is it used in practice?**
A: Hypermedia As The Engine Of Application State — API responses include links to related actions. Example: a GET /orders/123 response includes `{"_links": {"cancel": "/orders/123/cancel", "items": "/orders/123/items"}}`. In theory: clients navigate the API without hardcoding URLs. In practice: rarely implemented fully — most "REST" APIs are actually RPC-over-HTTP. The Richardson Maturity Model levels 0-3 describe how "RESTful" an API is.

**Q: What is the difference between REST and RPC?**
A: REST organizes around resources (nouns): `/users/123`, `/orders/456`. Operations are expressed through HTTP verbs. RPC organizes around actions (verbs): `/getUser`, `/createOrder`, `/sendEmail`. REST is preferred for public APIs (more predictable, follows conventions). RPC (gRPC, tRPC) is often preferred for internal microservice communication (more efficient, strongly typed).

**Q: What are REST naming conventions for endpoints?**
A:
- Use nouns, not verbs: `/articles` not `/getArticles`
- Use plural for collections: `/users`, `/products`, `/orders`
- Use lowercase with hyphens for multi-word: `/blog-posts` not `/blogPosts`
- Nest for relationships: `/users/123/orders` (user's orders)
- Don't nest more than 2 levels deep: avoid `/users/123/orders/456/items/789/reviews`
- Query params for filtering/sorting/pagination: `/products?category=electronics&sort=price&page=2`
- Actions that don't fit CRUD: use verb-like endpoints sparingly: `POST /orders/456/cancel`

**Q: What makes an operation safe vs. unsafe?**
A: Safe operations have no observable side effects on server state (GET, HEAD, OPTIONS). Unsafe operations modify state (POST, PUT, PATCH, DELETE). All safe operations are also idempotent. Unsafe operations may or may not be idempotent. Safety matters for: caching (safe = cacheable by default), analytics (safe requests shouldn't be counted as meaningful actions).

**Q: What is content negotiation?**
A: Client and server negotiate response format via headers:
- Request: `Accept: application/json` or `Accept: text/xml, application/json;q=0.9`
- Response: `Content-Type: application/json; charset=utf-8`
- Response when format unavailable: `406 Not Acceptable`
Allows one endpoint to serve JSON, XML, CSV depending on client needs.

**Q: What is API versioning and what strategies exist?**
A:
1. **URL versioning**: `/api/v1/users` vs `/api/v2/users`. Most visible, easy to route, easy to maintain separate code branches. Most common in practice.
2. **Header versioning**: `Accept: application/vnd.company.v2+json` or custom `X-API-Version: 2`. Cleaner URLs but harder to test in browsers.
3. **Query parameter**: `/users?version=2`. Simple but pollutes query params.
4. **Subdomain**: `v2.api.example.com`. Allows full infrastructure separation.

Recommendation: URL versioning for public APIs. Never remove a version without long deprecation notice and migration guides. Only version when making breaking changes.

**Q: What constitutes a breaking change in a REST API?**
A: Breaking changes that require a new version:
- Removing or renaming a field in the response
- Changing a field's data type
- Removing an endpoint
- Changing URL structure
- Adding a required request parameter
- Changing authentication scheme

Non-breaking (additive) changes:
- Adding new optional request fields
- Adding new response fields
- Adding new endpoints
- Adding new optional query parameters

**Q: What is pagination and what patterns exist?**
A:
1. **Offset-based**: `?page=2&limit=20` or `?offset=40&limit=20`. Simple but has issues with real-time data (items can shift positions). SQL: `LIMIT 20 OFFSET 40`.
2. **Cursor-based**: `?after=eyJpZCI6NDV9` (base64 encoded cursor). Stable with real-time data, works well for infinite scroll. Cursor = opaque pointer to last seen record.
3. **Keyset (seek method)**: `?last_id=45&limit=20`. Similar to cursor, uses actual field values. Requires indexed columns.

Response should include: `total`, `page`, `pageSize`, `hasNextPage`, and optionally `nextCursor`.

---

## HTTP METHODS

**Q: Describe each HTTP method and when to use it.**
A:
- **GET**: retrieve a resource. Safe, idempotent. Never modify data in GET. Response can be cached.
- **POST**: create a resource or trigger an action. Not idempotent (two POSTs = two resources). Returns 201 Created.
- **PUT**: replace a resource entirely. Idempotent. Client sends the full representation. If doesn't exist: creates it. Returns 200 or 204.
- **PATCH**: partial update. Not necessarily idempotent (depends on implementation). Send only the fields to change. Returns 200 or 204.
- **DELETE**: remove a resource. Idempotent (deleting twice = same result: gone). Returns 200 or 204.
- **HEAD**: same as GET but no response body. Used to check resource existence, get headers/metadata, validate cache.
- **OPTIONS**: returns allowed methods for a URL. Used by CORS preflight requests.
- **CONNECT**: establishes a tunnel (used for HTTPS through proxies).
- **TRACE**: diagnostic — echoes back the received request (disabled on most servers, security risk).

**Q: When should you use PUT vs PATCH?**
A: Use PUT when replacing the entire resource (client must send all fields). Use PATCH when partially updating. Example: to update just a user's email, PATCH `/users/123` with `{"email": "new@example.com"}`. With PUT, you'd need to send all user fields even if only email changed. PATCH is more bandwidth efficient but requires careful implementation on the server (merge semantics).

**Q: Why is POST not idempotent and why does that matter?**
A: Calling `POST /orders` twice creates two orders. This matters for: retry logic (never retry POST without checking if the first succeeded), network timeouts (if response is lost but request was processed, retry creates duplicate), UI (clicking submit twice). Solutions: idempotency keys (send a unique key with each POST; server deduplicates), or use PUT with a client-generated ID.

---

## HTTP STATUS CODES

**Q: What are the 5 status code classes?**
A:
- **1xx Informational**: request received, continuing (100 Continue, 101 Switching Protocols)
- **2xx Success**: request successfully received and processed
- **3xx Redirection**: further action needed to complete request
- **4xx Client Errors**: client made a bad request
- **5xx Server Errors**: server failed to fulfill a valid request

**Q: What are the most important status codes to know?**
A:
**2xx Success:**
- `200 OK` — standard success with response body
- `201 Created` — resource was created (include Location header with new resource URL)
- `204 No Content` — success but no response body (used for DELETE, sometimes PATCH)
- `206 Partial Content` — range request fulfilled (file downloads)

**3xx Redirection:**
- `301 Moved Permanently` — URL has changed forever; client should update links
- `302 Found` — temporary redirect (client should keep using original URL)
- `304 Not Modified` — response not changed since last request; use cached version (used with ETags)

**4xx Client Errors:**
- `400 Bad Request` — malformed request, invalid JSON, validation failure
- `401 Unauthorized` — not authenticated (misleadingly named — means "unauthenticated")
- `403 Forbidden` — authenticated but not authorized
- `404 Not Found` — resource doesn't exist
- `405 Method Not Allowed` — HTTP method not supported on this endpoint
- `409 Conflict` — state conflict (e.g., creating duplicate, version conflict)
- `410 Gone` — resource permanently deleted (unlike 404, explicitly indicates deletion)
- `422 Unprocessable Entity` — well-formed but semantically invalid (validation errors)
- `429 Too Many Requests` — rate limited; include `Retry-After` header

**5xx Server Errors:**
- `500 Internal Server Error` — generic server crash; never expose stack traces
- `502 Bad Gateway` — upstream server returned bad response (load balancer to dead app server)
- `503 Service Unavailable` — server overloaded or in maintenance; include `Retry-After`
- `504 Gateway Timeout` — upstream server didn't respond in time

**Q: When should you return 400 vs 422?**
A: `400 Bad Request` for structural problems: malformed JSON, wrong content type, missing required headers. `422 Unprocessable Entity` for semantic validation: valid JSON structure but invalid business rules (email format wrong, value out of range, invalid enum). Many APIs use 400 for both — the distinction matters more for API clients to know if retrying will help.

**Q: How should error responses be structured?**
A:
```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Invalid email format" },
      { "field": "age", "message": "Must be at least 18" }
    ],
    "requestId": "req_abc123",
    "timestamp": "2025-03-16T10:00:00Z"
  }
}
```
Key principles: consistent structure across all errors, machine-readable error codes, human-readable messages, include field-level details for validation, never expose stack traces in production.

---

## AUTHENTICATION METHODS

**Q: What are the main API authentication methods and their tradeoffs?**
A:
- **API Keys**: simple `X-API-Key: abc123` header. Easy to implement, easy for clients. Drawbacks: no expiry by default, no user identity, hard to rotate without downtime. Use for: server-to-server, developer APIs, third-party integrations.
- **JWT (JSON Web Token)**: stateless, self-contained, signed. Supports expiry. Can contain claims. Drawbacks: can't revoke before expiry, payload is visible. Use for: stateless APIs, microservices, mobile apps.
- **Session Cookies**: server stores session, client has cookie. Instantly revocable. Drawbacks: requires shared session store for multi-instance, CSRF vulnerable (need SameSite protection). Use for: traditional web apps.
- **OAuth 2.0**: delegated authorization. User authorizes third-party app to access their data. Complex but industry standard. Use for: social login, third-party integrations.
- **mTLS (mutual TLS)**: both client and server present certificates. Strongest security. Drawbacks: certificate management complexity. Use for: high-security M2M, financial APIs, internal microservices.
- **HTTP Basic Auth**: Base64(user:password) in Authorization header. Never use over HTTP. Only over HTTPS. Generally deprecated for APIs.

**Q: What is JWT in detail — structure and verification?**
A: JWT = Base64URL(header) . Base64URL(payload) . signature

- **Header**: `{"alg": "HS256", "typ": "JWT"}` — signing algorithm
- **Payload**: claims — `{"sub": "user123", "email": "alice@example.com", "exp": 1741000000, "iat": 1740999100}`
- **Signature**: HMACSHA256(base64Header + "." + base64Payload, secret) for symmetric, or RSA/ECDSA for asymmetric

Verification: decode header, decode payload, recompute signature, compare. Also verify `exp` (expiry) and `iss` (issuer).

Never put sensitive data in payload — it's only base64 encoded, not encrypted. Use JWE (JSON Web Encryption) if you need encrypted payloads.

**Q: What is the difference between symmetric and asymmetric JWT signing?**
A:
- **Symmetric (HS256/HS512)**: same secret used to sign and verify. All services must share the secret. Simpler. Use when only one service verifies tokens.
- **Asymmetric (RS256/ES256)**: private key signs, public key verifies. Auth service keeps private key, all other services use public key (can be published). Preferred for microservices — no need to share secrets. ES256 (ECDSA) preferred over RS256 (RSA) for performance.

**Q: What is mTLS and when is it used?**
A: Mutual TLS requires both client and server to present X.509 certificates, authenticating both directions. Steps: TLS handshake → server sends cert → client verifies → client sends cert → server verifies. Use cases: API authentication for financial institutions, healthcare (HIPAA), internal microservice mesh (instead of API keys), PSD2 (European open banking). Drawback: certificate lifecycle management is complex — use a service mesh (Istio, Linkerd) to automate.

---

## AUTHORIZATION PATTERNS

**Q: What is RBAC (Role-Based Access Control)?**
A: Users are assigned roles, roles have permissions. Simple to implement and understand.

```javascript
const permissions = {
  admin:   ["read", "write", "delete", "manage_users"],
  editor:  ["read", "write"],
  viewer:  ["read"],
};

function can(user, action) {
  return permissions[user.role]?.includes(action) ?? false;
}
// Usage: if (!can(req.user, "write")) return res.status(403).json({error: "Forbidden"})
```

Works well for: small teams, clear role hierarchies, simple permission models. Doesn't scale well when: users need custom permissions, context matters (own resource vs. others'), large number of resource types.

**Q: What is ABAC (Attribute-Based Access Control)?**
A: Access decisions based on attributes of user, resource, and environment. More flexible than RBAC but more complex.

```javascript
function canAccess(user, resource, action, environment) {
  // User attributes: role, department, clearanceLevel
  // Resource attributes: ownerId, classification, department
  // Environment: time, IP, location
  if (action === "read" && resource.classification === "public") return true;
  if (resource.ownerId === user.id) return true; // owner can always access own resources
  if (user.role === "admin") return true;
  if (user.department === resource.department && action !== "delete") return true;
  return false;
}
```

**Q: What is the principle of least privilege?**
A: Each component/user/service should have only the minimum permissions needed to perform its function. In practice: narrow API key scopes, read-only DB users for read-only services, time-limited access tokens, IP allowlisting for sensitive operations. Reduces blast radius if credentials are compromised.

**Q: What are ACLs (Access Control Lists)?**
A: Per-resource lists of which users/roles can perform which operations. More granular than RBAC. Example: Google Drive permissions — each file has an ACL of who can view/edit/own. More flexible but harder to audit at scale ("who has access to all documents?").

---

## SECURITY ATTACKS AND PREVENTION

**Q: What is Cross-Origin Resource Sharing (CORS) and how do you configure it properly?**
A: Browsers block cross-origin requests by default (Same-Origin Policy). CORS headers tell the browser which origins are allowed.

```javascript
app.use(cors({
  origin: (origin, callback) => {
    const allowed = ["https://app.example.com", "https://admin.example.com"];
    if (!origin || allowed.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error("CORS not allowed for: " + origin));
    }
  },
  methods: ["GET", "POST", "PUT", "PATCH", "DELETE"],
  allowedHeaders: ["Content-Type", "Authorization"],
  credentials: true,   // Required for cookies, requires specific origin (not *)
  maxAge: 86400,       // Cache preflight for 24 hours
}));
```

Never use `origin: "*"` with `credentials: true` — the browser blocks it and it's a security risk.

**Q: What is XSS (Cross-Site Scripting) and how do you prevent it?**
A: Attacker injects malicious JavaScript that runs in the victim's browser, stealing cookies, session tokens, or performing actions as the victim.

Types:
- **Reflected**: malicious script in URL, returned in response
- **Stored**: malicious script stored in DB, served to all users
- **DOM-based**: client-side JS reads from URL and inserts unsafely

Prevention:
- Always escape user-generated content before rendering: use template engine auto-escaping
- Content-Security-Policy header: `CSP: default-src 'self'; script-src 'self'` — blocks inline scripts
- `X-XSS-Protection: 1; mode=block` (legacy browsers)
- `httpOnly` cookies — can't be accessed by JavaScript
- Never use `innerHTML` with user data — use `textContent`
- Validate and sanitize input with libraries (DOMPurify for HTML, validator.js for strings)

**Q: What is CSRF (Cross-Site Request Forgery) and how do you prevent it?**
A: Attacker tricks a victim (who is logged into your site) into making unintended requests to your site. The victim's browser automatically sends cookies, so your server can't distinguish a legitimate request from a forged one.

Prevention:
1. **SameSite cookies**: `SameSite=Strict` or `SameSite=Lax` — browser won't send cookie in cross-site requests
2. **CSRF token**: unique per-session token in hidden form field and validated server-side
3. **Double submit cookie**: match cookie value to request header/parameter
4. **Custom headers**: `X-Requested-With: XMLHttpRequest` — browsers won't include in cross-origin forms
5. **Origin/Referer header validation**: check that request came from your domain

Note: if using JWT in Authorization header (not cookies), CSRF is not a concern — browsers don't auto-include headers.

**Q: What is SQL injection and how do you prevent it completely?**
A: Attacker injects SQL into user input that gets executed: `'; DROP TABLE users; --`

```javascript
// VULNERABLE:
const query = `SELECT * FROM users WHERE email = '${req.body.email}'`;

// SAFE: Parameterized queries
const { rows } = await pool.query(
  "SELECT * FROM users WHERE email = $1",
  [req.body.email]
);

// ALSO SAFE: ORM (Mongoose, Prisma, Sequelize) handles parameterization
const user = await User.findOne({ email: req.body.email });
```

Defense in depth: also use least-privilege DB users (app user has no DROP TABLE permission), input validation (reject obviously invalid inputs early), WAF (Web Application Firewall).

**Q: What is NoSQL injection and how does it differ?**
A: MongoDB is vulnerable when user input is used directly as query objects. Attackers can inject operators (`$gt`, `$where`).

```javascript
// VULNERABLE:
app.post("/login", async (req, res) => {
  const user = await User.findOne({ email: req.body.email, password: req.body.password });
  // If email = { $gt: "" }, this matches ANY user!
});

// SAFE: Validate types and sanitize
const { email, password } = req.body;
if (typeof email !== "string" || typeof password !== "string") {
  return res.status(400).json({ error: "Invalid input types" });
}
const user = await User.findOne({ email, password }); // Now strings, not objects
```

Also use: `express-mongo-sanitize` middleware to strip `$` and `.` from req.body/params/query.

**Q: What is XXE (XML External Entity) injection?**
A: When your server parses XML, attackers can inject entity declarations that read local files or make SSRF requests.

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<root>&xxe;</root>
```

Prevention: disable external entity processing in your XML parser. In Node.js with `xml2js`: it's not vulnerable by default. In Java: `dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)`.

**Q: What is SSRF (Server-Side Request Forgery)?**
A: Attacker tricks your server into making HTTP requests to internal services or cloud metadata endpoints. Example: a webhook URL feature where attacker submits `http://169.254.169.254/latest/meta-data/` (AWS metadata API).

Prevention:
```javascript
const { URL } = require("url");
const dns = require("dns").promises;

async function isSafeUrl(urlString) {
  try {
    const url = new URL(urlString);
    // Block non-HTTP schemes
    if (!["http:", "https:"].includes(url.protocol)) return false;
    // Block private IP ranges
    const addresses = await dns.lookup(url.hostname, { all: true });
    for (const { address } of addresses) {
      if (isPrivateIP(address)) return false;
    }
    return true;
  } catch {
    return false;
  }
}

function isPrivateIP(ip) {
  return /^(10\.|172\.(1[6-9]|2\d|3[01])\.|192\.168\.|127\.|169\.254\.|::1|fc|fd)/.test(ip);
}
```

**Q: What is path traversal and how do you prevent it?**
A: Attacker uses `../` to access files outside the intended directory: `GET /files?name=../../etc/passwd`

```javascript
const path = require("path");

function safeFilePath(userInput, baseDir) {
  const requestedPath = path.resolve(baseDir, userInput);
  // Ensure resolved path starts with baseDir
  if (!requestedPath.startsWith(path.resolve(baseDir))) {
    throw new Error("Path traversal detected");
  }
  return requestedPath;
}
```

**Q: What is the OWASP Top 10 (2021)?**
A:
1. **Broken Access Control** — most common, failing to restrict what authenticated users can do
2. **Cryptographic Failures** — weak encryption, data transmitted in plaintext
3. **Injection** — SQL, NoSQL, OS, LDAP injection
4. **Insecure Design** — missing security requirements in design phase
5. **Security Misconfiguration** — default passwords, unnecessary features enabled, verbose errors
6. **Vulnerable and Outdated Components** — dependencies with known CVEs
7. **Identification and Authentication Failures** — weak passwords, broken session management
8. **Software and Data Integrity Failures** — insecure CI/CD, auto-update without verification
9. **Security Logging and Monitoring Failures** — not detecting breaches in time
10. **Server-Side Request Forgery (SSRF)** — server fetching user-provided URLs

---

## RATE LIMITING PATTERNS

**Q: What is rate limiting and why does it matter?**
A: Limits how many requests a client can make in a time window. Protects against: brute force attacks (password guessing), DDoS, scraping, API abuse, runaway client bugs. Also enables fair usage and cost control (per-tier limits for SaaS APIs).

**Q: What rate limiting algorithms exist?**
A:
1. **Fixed window counter**: count requests per time window (e.g., 100/minute). Simple but allows burst at window boundaries (99 at end of minute + 99 at start of next = 198 in 2 seconds).
2. **Sliding window log**: log timestamp of each request, count requests in last N seconds. More accurate, more memory.
3. **Sliding window counter**: combination — interpolate using previous window's count. Good accuracy, low memory.
4. **Token bucket**: bucket holds N tokens, refills at rate R tokens/second. Requests consume a token; rejected if empty. Allows bursts up to bucket size.
5. **Leaky bucket**: requests enter a queue, processed at fixed rate. Smooths traffic, prevents bursts.

**Q: How do you implement distributed rate limiting?**
A: Use Redis as the shared counter across multiple app instances.

```javascript
const redis = require("ioredis");
const client = new redis(process.env.REDIS_URL);

async function checkRateLimit(identifier, windowSeconds, maxRequests) {
  const key = `ratelimit:${identifier}:${Math.floor(Date.now() / (windowSeconds * 1000))}`;
  const count = await client.incr(key);
  if (count === 1) {
    await client.expire(key, windowSeconds);
  }
  return {
    allowed: count <= maxRequests,
    remaining: Math.max(0, maxRequests - count),
    resetAt: Math.ceil(Date.now() / (windowSeconds * 1000)) * windowSeconds,
  };
}
```

**Q: What rate limit headers should your API return?**
A: Follow the `RateLimit` draft standard (or the older de-facto `X-RateLimit-*`):
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1741000000
Retry-After: 30    (on 429 responses)
```

**Q: What is the difference between rate limiting and throttling?**
A: Rate limiting REJECTS requests over the limit (returns 429). Throttling SLOWS requests (adds artificial delay, queues excess requests). Throttling provides better UX but requires more infrastructure. APIs typically use rate limiting. CDNs and gateways may use throttling.

---

## API GATEWAY PATTERNS

**Q: What is an API Gateway and what does it do?**
A: A single entry point for all API clients, sitting in front of backend services. Handles cross-cutting concerns:
- **Routing**: directs requests to appropriate backend services
- **Authentication/Authorization**: validates tokens before passing to services
- **Rate limiting**: enforces per-client limits
- **Load balancing**: distributes traffic across service instances
- **SSL termination**: handles HTTPS, backends can use HTTP internally
- **Request/Response transformation**: modify headers, body, add/remove fields
- **Caching**: cache common responses
- **Logging/Monitoring**: centralized request logging and metrics
- **Circuit breaking**: stop routing to unhealthy services

Examples: AWS API Gateway, Kong, Nginx, Traefik, Envoy.

**Q: What is the Backend for Frontend (BFF) pattern?**
A: Create separate backend APIs tailored to each frontend (mobile BFF, web BFF). Each BFF aggregates calls to multiple microservices and returns exactly what the frontend needs. Benefits: frontends get optimized data (no over/under-fetching), different authentication schemes per platform, frontends don't need to know internal service topology. Used by Netflix, SoundCloud.

**Q: What is circuit breaker pattern?**
A: Prevents cascading failures when a downstream service is struggling. Three states:
- **Closed**: requests pass through normally, failures counted
- **Open**: after N failures, all requests fail immediately without calling the service (fail fast)
- **Half-open**: after timeout, allow a few test requests; if they succeed, back to Closed; if fail, back to Open

```javascript
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.state = "CLOSED";
    this.failures = 0;
    this.threshold = threshold;
    this.timeout = timeout;
    this.nextAttempt = null;
  }

  async call(fn) {
    if (this.state === "OPEN") {
      if (Date.now() < this.nextAttempt) throw new Error("Circuit is OPEN");
      this.state = "HALF_OPEN";
    }
    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (err) {
      this.onFailure();
      throw err;
    }
  }

  onSuccess() { this.failures = 0; this.state = "CLOSED"; }
  onFailure() {
    this.failures++;
    if (this.failures >= this.threshold) {
      this.state = "OPEN";
      this.nextAttempt = Date.now() + this.timeout;
    }
  }
}
```

**Q: What is the difference between an API Gateway and a Service Mesh?**
A:
- **API Gateway**: sits at the edge, handles external traffic. North-South traffic (client ↔ services). Focused on external API concerns.
- **Service Mesh** (Istio, Linkerd): handles internal service-to-service traffic. East-West traffic (service ↔ service). Provides: mTLS between services, distributed tracing, traffic splitting, retries, circuit breaking. Uses sidecar proxies (Envoy) alongside each service.

Use both: API Gateway for external traffic, Service Mesh for internal.

**Q: What is request deduplication and why does it matter?**
A: Idempotency keys allow clients to safely retry requests. The server stores a record of processed request IDs and returns the same response on retry without re-executing the operation.

```javascript
app.post("/payments", async (req, res) => {
  const idempotencyKey = req.headers["idempotency-key"];
  if (!idempotencyKey) return res.status(400).json({ error: "Idempotency-Key header required" });

  // Check cache
  const cached = await redis.get(`idempotency:${idempotencyKey}`);
  if (cached) {
    return res.status(200).json(JSON.parse(cached));
  }

  // Process payment
  const result = await processPayment(req.body);

  // Cache result for 24 hours
  await redis.setex(`idempotency:${idempotencyKey}`, 86400, JSON.stringify(result));
  res.status(201).json(result);
});
```

**Q: What are the common REST API security headers?**
A:
```javascript
app.use(helmet()); // Sets all of these at once

// Key headers:
// Strict-Transport-Security: max-age=31536000; includeSubDomains   (HTTPS only, 1 year)
// Content-Security-Policy: default-src 'self'                       (block external resources)
// X-Content-Type-Options: nosniff                                   (prevent MIME sniffing)
// X-Frame-Options: DENY                                             (prevent clickjacking)
// Referrer-Policy: strict-origin-when-cross-origin                  (limit referrer info)
// Permissions-Policy: camera=(), microphone=(), geolocation=()      (disable browser features)
// Cache-Control: no-store                                           (for sensitive endpoints)
```

**Q: What is the difference between 401 and 403 and why does it matter?**
A:
- `401 Unauthorized` (confusingly named): "I don't know who you are." The request lacks valid authentication credentials. Response should include `WWW-Authenticate` header telling client how to authenticate. Client should log in and retry.
- `403 Forbidden`: "I know who you are, but you can't do this." Authenticated but lacking permission. Client should NOT retry with same credentials — get the permission or contact admin.

Important nuance: sometimes use 404 instead of 403 when you don't want to reveal that a resource exists to unauthorized users (security by obscurity). Example: GitHub returns 404 for private repos to unauthorized users, not 403.
