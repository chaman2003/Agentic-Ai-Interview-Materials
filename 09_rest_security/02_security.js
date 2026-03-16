// ============================================================
// API SECURITY — Interview Essentials
// ============================================================
// npm install helmet cors express-rate-limit express-validator

const express = require("express");
const helmet  = require("helmet");
const cors    = require("cors");
const rateLimit = require("express-rate-limit");
const { body, param, validationResult } = require("express-validator");

const app = express();
app.use(express.json());

// ── 1. HELMET — Security HTTP Headers ────────────────────────
// Sets many security headers in one line:
// - Content-Security-Policy (prevent XSS)
// - X-Frame-Options (prevent clickjacking)
// - X-XSS-Protection
// - Strict-Transport-Security (force HTTPS)
// - X-Content-Type-Options
app.use(helmet());


// ── 2. CORS — Cross-Origin Resource Sharing ──────────────────
// Controls which domains can call your API
// Without CORS header, browsers block cross-origin requests

// Development: allow all origins
app.use(cors());

// Production: restrict to your frontend only
app.use(cors({
    origin:      "https://app.mycompany.com",    // your frontend URL
    methods:     ["GET", "POST", "PUT", "PATCH", "DELETE"],
    credentials: true                       // allow cookies
}));

// Multiple origins
const allowedOrigins = ["https://app.mycompany.com", "https://admin.mycompany.com"];
app.use(cors({
    origin: (origin, callback) => {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error("Not allowed by CORS"));
        }
    }
}));


// ── 3. RATE LIMITING — Prevent Abuse ─────────────────────────
// Limits how many requests a single IP can make in a time window

const generalLimit = rateLimit({
    windowMs: 15 * 60 * 1000,  // 15 minutes
    max:      100,              // max 100 requests per window
    message:  { error: "Too many requests, please try again later" },
    standardHeaders: true       // include rate limit info in headers
});
app.use(generalLimit);

// Stricter limit for auth endpoints (prevent brute force)
const authLimit = rateLimit({
    windowMs: 15 * 60 * 1000,
    max:      10,   // only 10 login attempts per 15 min
    message:  { error: "Too many login attempts" }
});
app.use("/auth", authLimit);


// ── 4. INPUT VALIDATION — Never Trust req.body ────────────────
// Validate AND sanitize all user input before using it
// Prevents: SQL injection, XSS, unexpected data types

// Define validation rules
const validateCreateUser = [
    body("name")
        .trim()
        .notEmpty().withMessage("Name is required")
        .isLength({ min: 2, max: 100 }).withMessage("Name must be 2-100 chars")
        .escape(),   // sanitize: convert <, >, &, " to HTML entities (prevent XSS)

    body("email")
        .trim()
        .notEmpty().withMessage("Email is required")
        .isEmail().withMessage("Invalid email format")
        .normalizeEmail(),   // lowercase, remove dots in gmail, etc.

    body("password")
        .isLength({ min: 8 }).withMessage("Password must be at least 8 chars")
        .matches(/[A-Z]/).withMessage("Must contain uppercase letter")
        .matches(/[0-9]/).withMessage("Must contain a number"),

    body("age")
        .optional()
        .isInt({ min: 0, max: 150 }).withMessage("Age must be 0-150")
];

// Middleware to check validation results
const validate = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(422).json({
            error:  "Validation failed",
            fields: errors.array().map(e => ({ field: e.path, message: e.msg }))
        });
    }
    next();
};

// Use in route
app.post("/users", validateCreateUser, validate, (req, res) => {
    // req.body is now validated and sanitized
    res.status(201).json({ message: "User created" });
});


// ── 5. NEVER EXPOSE STACK TRACES ──────────────────────────────
app.use((err, req, res, next) => {
    const status = err.status || 500;

    const response = { error: err.message || "Something went wrong" };

    // Only show stack trace in development
    if (process.env.NODE_ENV !== "production") {
        response.stack = err.stack;
    }
    // In production: log to your logging service, not to the client
    console.error(err);

    res.status(status).json(response);
});


// ── 6. JWT BEST PRACTICES ─────────────────────────────────────
/*
- Short access tokens: 15 minutes. If stolen, it expires quickly.
- Long refresh tokens: 7 days. Stored in httpOnly cookie (not localStorage).
- httpOnly cookies: JavaScript cannot read them → XSS can't steal the token
- Rotate refresh tokens: each use → issue new refresh token, invalidate old one
- Never put sensitive data in JWT payload (it's base64 encoded, not encrypted)
- Use strong secret: at least 256-bit random string from crypto.randomBytes(32)
*/


// ── 7. PASSWORD HASHING ────────────────────────────────────────
/*
- Always use bcrypt. NEVER MD5, SHA1, or plain text.
- bcrypt is intentionally slow (prevents brute force):
  saltRounds=10 → ~100ms per hash → attacker needs 100ms per guess
- Never store the original password — only the hash
- Use bcrypt.compare() to verify (don't compare manually)
*/


// ── 8. SQL INJECTION PREVENTION ───────────────────────────────
/*
- NEVER concatenate user input into SQL strings:
  BAD:  `SELECT * FROM users WHERE id = ${req.params.id}`
  GOOD: use parameterized queries with placeholders:
  GOOD: `SELECT * FROM users WHERE id = $1`  (pg library)
  GOOD: User.findById(req.params.id)            (Mongoose)

- ORMs (Mongoose, SQLAlchemy, Prisma) handle this automatically.
- Raw queries: always use parameterized queries or prepared statements.
*/

app.listen(3000, () => console.log("Secure server running"));
