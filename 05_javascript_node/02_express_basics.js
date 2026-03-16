// ============================================================
// EXPRESS.JS BASICS — Interview Essentials
// ============================================================
// npm install express

const express = require("express");
const app = express();

// ── MIDDLEWARE SETUP ─────────────────────────────────────────
app.use(express.json());        // parse JSON request bodies
app.use(express.urlencoded({ extended: true }));   // parse form data

// ── WHAT IS MIDDLEWARE? ───────────────────────────────────────
// A function that runs BETWEEN the request arriving and your route handler
// Can: modify req/res, end the request, or call next() to continue
// If you don't call next(), the request HANGS

// Simple middleware example
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url} - ${new Date().toISOString()}`);
    next();   // MUST call next() to pass control to next middleware/route
});

// ── ROUTES ───────────────────────────────────────────────────
// app.get/post/put/patch/delete(path, handler)
// req: incoming request, res: response to send

app.get("/", (req, res) => {
    res.json({ message: "API is running" });
});

// URL parameters — :id becomes req.params.id
app.get("/users/:id", (req, res) => {
    const { id } = req.params;
    res.json({ id, name: "Chaman" });
});

// Query params — ?page=2&limit=10 becomes req.query
app.get("/users", (req, res) => {
    const page  = parseInt(req.query.page)  || 1;
    const limit = parseInt(req.query.limit) || 10;
    res.json({ page, limit, users: [] });
});

// POST — body data → req.body (after express.json() middleware)
app.post("/users", (req, res) => {
    const { name, email } = req.body;
    if (!name || !email) {
        return res.status(400).json({ error: "name and email required" });
    }
    const newUser = { id: Date.now(), name, email };
    res.status(201).json(newUser);   // 201 Created
});

// PUT — replace entire resource
app.put("/users/:id", (req, res) => {
    const { id } = req.params;
    const { name, email } = req.body;
    res.json({ id, name, email, message: "User replaced" });
});

// PATCH — update part of resource
app.patch("/users/:id", (req, res) => {
    const { id } = req.params;
    const updates = req.body;   // only the fields that changed
    res.json({ id, ...updates, message: "User updated" });
});

// DELETE
app.delete("/users/:id", (req, res) => {
    const { id } = req.params;
    res.json({ message: `User ${id} deleted` });
    // or: res.status(204).send()  — 204 = success, no body
});

// ── CUSTOM MIDDLEWARE ─────────────────────────────────────────

// Auth middleware — protect routes
const requireAuth = (req, res, next) => {
    const token = req.headers.authorization?.split(" ")[1];  // "Bearer <token>"
    if (!token) {
        return res.status(401).json({ error: "No token provided" });
    }
    // Verify token here (see JWT file)
    req.user = { id: 1, email: "user@example.com" };  // attach user to req
    next();   // pass control to next middleware/route
};

// Protected route — pass middleware as second argument
app.get("/profile", requireAuth, (req, res) => {
    res.json({ user: req.user });
});

// Multiple middleware on one route
const validate = (req, res, next) => {
    if (!req.body.name) return res.status(400).json({ error: "name required" });
    next();
};

app.post("/admin/users", requireAuth, validate, (req, res) => {
    res.status(201).json({ message: "User created by admin" });
});

// ── EXPRESS ROUTER ────────────────────────────────────────────
// Organise routes in separate files

const userRouter = express.Router();

userRouter.get("/", (req, res) => res.json({ users: [] }));
userRouter.post("/", (req, res) => res.status(201).json({ message: "Created" }));
userRouter.get("/:id", (req, res) => res.json({ id: req.params.id }));

// Register router with a prefix
app.use("/api/v1/users", userRouter);
// Now: GET /api/v1/users, POST /api/v1/users, GET /api/v1/users/123

// ── ERROR MIDDLEWARE ──────────────────────────────────────────
// MUST have 4 parameters — Express identifies error middleware by (err, req, res, next)
// Register AFTER all routes

app.use((err, req, res, next) => {
    console.error(err.stack);
    const status = err.status || 500;
    const message = err.message || "Internal server error";

    // Don't expose stack traces in production!
    const response = { error: message };
    if (process.env.NODE_ENV !== "production") {
        response.stack = err.stack;
    }
    res.status(status).json(response);
});

// 404 handler — if no route matched
app.use((req, res) => {
    res.status(404).json({ error: "Route not found" });
});

// ── START SERVER ──────────────────────────────────────────────
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});
