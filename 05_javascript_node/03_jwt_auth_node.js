// ============================================================
// JWT AUTH IN NODE.JS — Full Flow
// ============================================================
// npm install jsonwebtoken bcryptjs

const express = require("express");
const jwt     = require("jsonwebtoken");
const bcrypt  = require("bcryptjs");

const app = express();
app.use(express.json());

const JWT_SECRET = process.env.JWT_SECRET || "dev-secret-key";

// Mock database
const users = [];

// ── REGISTER ─────────────────────────────────────────────────
// Hash password with bcrypt → save user
app.post("/auth/register", async (req, res) => {
    try {
        const { name, email, password } = req.body;

        if (!email || !password) {
            return res.status(400).json({ error: "email and password required" });
        }

        // Check duplicate
        if (users.find(u => u.email === email)) {
            return res.status(409).json({ error: "Email already registered" });
        }

        // Hash password — NEVER store plaintext passwords
        // bcrypt.hash(password, saltRounds)
        // saltRounds=10 → 2^10 hashing rounds → ~100ms (slow is intentional, slows brute force)
        const passwordHash = await bcrypt.hash(password, 10);

        const user = {
            id:           users.length + 1,
            name,
            email,
            passwordHash  // store hash, never the original password
        };
        users.push(user);

        res.status(201).json({ message: "Registered successfully", id: user.id });
    } catch (err) {
        res.status(500).json({ error: "Registration failed" });
    }
});

// ── LOGIN ─────────────────────────────────────────────────────
// Verify password → create JWT token
app.post("/auth/login", async (req, res) => {
    try {
        const { email, password } = req.body;

        // Find user
        const user = users.find(u => u.email === email);
        if (!user) {
            return res.status(404).json({ error: "User not found" });
        }

        // Compare password with stored hash
        const isMatch = await bcrypt.compare(password, user.passwordHash);
        if (!isMatch) {
            return res.status(401).json({ error: "Invalid password" });
        }

        // Create JWT token
        // jwt.sign(payload, secret, options)
        // payload: data stored IN the token (user ID, role)
        // — don't put sensitive data (password, SSN) in payload (it's base64, not encrypted!)
        const token = jwt.sign(
            { id: user.id, email: user.email },   // payload
            JWT_SECRET,
            { expiresIn: "7d" }                   // expires in 7 days
        );

        res.json({
            token,
            user: { id: user.id, name: user.name, email: user.email }
        });
    } catch (err) {
        res.status(500).json({ error: "Login failed" });
    }
});

// ── AUTH MIDDLEWARE ───────────────────────────────────────────
// Reads Authorization header, verifies JWT, attaches user to req.user
const authenticate = (req, res, next) => {
    try {
        // Get token from "Authorization: Bearer <token>"
        const authHeader = req.headers.authorization;
        if (!authHeader || !authHeader.startsWith("Bearer ")) {
            return res.status(401).json({ error: "Authorization token required" });
        }

        const token = authHeader.split(" ")[1];

        // Verify token — throws error if invalid or expired
        const decoded = jwt.verify(token, JWT_SECRET);
        req.user = decoded;   // attach decoded payload to request

        next();  // pass to route handler
    } catch (err) {
        if (err.name === "TokenExpiredError") {
            return res.status(401).json({ error: "Token has expired" });
        }
        return res.status(401).json({ error: "Invalid token" });
    }
};

// ── PROTECTED ROUTES ──────────────────────────────────────────
app.get("/profile", authenticate, (req, res) => {
    // req.user contains the decoded JWT payload
    res.json({ message: "Protected data", user: req.user });
});

// Role-based authorization middleware (built on top of authenticate)
const requireRole = (role) => (req, res, next) => {
    if (req.user.role !== role) {
        return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
};

app.delete("/admin/users/:id", authenticate, requireRole("admin"), (req, res) => {
    res.json({ message: `Admin deleted user ${req.params.id}` });
});

// ── START SERVER ──────────────────────────────────────────────
app.listen(3000, () => console.log("Auth server running on port 3000"));
