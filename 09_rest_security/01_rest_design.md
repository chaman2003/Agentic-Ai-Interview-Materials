# REST API Design — Interview Essentials

---

## REST Principles

**REST** = Representational State Transfer. A set of conventions for designing APIs.

### 1. Resource Naming — nouns, plural, lowercase
```
GOOD:   GET /api/v1/cases
BAD:    GET /api/v1/getCases
BAD:    GET /api/v1/Case

GOOD:   GET /api/v1/cases/123
GOOD:   GET /api/v1/cases/123/documents
BAD:    GET /api/v1/getCaseDocuments?caseId=123
```

### 2. HTTP Verbs
| Method | Purpose | Example | Idempotent? |
|--------|---------|---------|-------------|
| GET    | Read    | GET /cases | Yes |
| POST   | Create  | POST /cases | **No** |
| PUT    | Replace whole resource | PUT /cases/1 | Yes |
| PATCH  | Update part of resource | PATCH /cases/1 | Yes |
| DELETE | Remove  | DELETE /cases/1 | Yes |

**Idempotent** = calling multiple times gives the same result as calling once. GET /cases always returns the same data. DELETE /cases/1 — second call still results in case being gone.

### 3. Status Codes (memorize all of these)
| Code | Name | When to Use |
|------|------|-------------|
| 200 | OK | Success (GET, PUT, PATCH) |
| 201 | Created | Resource created (POST) |
| 204 | No Content | Success, no body (DELETE) |
| 400 | Bad Request | Invalid data from client |
| 401 | Unauthorized | Not authenticated (no/bad token) |
| 403 | Forbidden | Authenticated but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate (email already exists) |
| 422 | Unprocessable | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Bug on server |

### 4. Consistent Error Response
**Always** return errors in the same format:
```json
{
    "error": "User not found",
    "code":  404,
    "field": "email"
}
```
Never just return a string like `"User not found"`.

### 5. URL Structure
```
/api/v1/cases                    → all cases
/api/v1/cases/123                → specific case
/api/v1/cases/123/documents      → documents of a specific case
/api/v1/cases?status=open&page=1 → filtered + paginated
```

---

## Swagger / OpenAPI

**Swagger** = visual documentation for your API. Developers can see all endpoints, try them out, see request/response schemas.

**OpenAPI** = the specification format. Swagger UI renders it.

### How it works in Express
```
npm install swagger-jsdoc swagger-ui-express
```

1. **swagger-jsdoc** — reads JSDoc comments in your code and generates the OpenAPI spec (JSON)
2. **swagger-ui-express** — serves a visual UI at `/api-docs`

```js
// server.js
const swaggerJsdoc = require("swagger-jsdoc");
const swaggerUi    = require("swagger-ui-express");

const options = {
    definition: {
        openapi: "3.0.0",
        info: { title: "Case Management API", version: "1.0.0" },
        components: {
            securitySchemes: {
                BearerAuth: { type: "http", scheme: "bearer" }
            }
        }
    },
    apis: ["./routes/*.js"]  // files with JSDoc comments
};

const spec = swaggerJsdoc(options);
app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(spec));
```

```js
// routes/cases.js
/**
 * @swagger
 * /api/v1/cases:
 *   get:
 *     summary: Get all cases
 *     security:
 *       - BearerAuth: []
 *     parameters:
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: List of cases
 */
router.get("/", authenticate, getCases);
```

---

## SDLC (Software Development Life Cycle)

1. **Requirements** — what to build, stakeholder meetings
2. **Design** — architecture, DB schema, API design, wireframes
3. **Development** — write code, code reviews, unit tests
4. **Testing** — QA, integration tests, load tests
5. **Deployment** — staging → production, CI/CD pipelines
6. **Maintenance** — monitoring, bug fixes, feature updates

---

## API Versioning
```
/api/v1/users   ← current version
/api/v2/users   ← new version with breaking changes
```
Always version your API. When you make breaking changes, create v2 instead of modifying v1 (which would break existing clients).

---

## Pagination
```json
{
    "data": [...],
    "pagination": {
        "page":       1,
        "limit":      10,
        "total":      153,
        "totalPages": 16
    }
}
```
