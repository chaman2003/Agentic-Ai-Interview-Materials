// ============================================================
// JAVASCRIPT PATTERNS & VARIATIONS
// Different ways to write the same thing + common patterns
// ============================================================

// ── 1. OBJECT CREATION PATTERNS ──────────────────────────────

// Version 1: Object literal (most common)
const user1 = { name: "Chaman", age: 21, greet() { return `Hi, I'm ${this.name}`; } };

// Version 2: Constructor function (old way)
function User(name, age) {
    this.name = name;
    this.age  = age;
}
User.prototype.greet = function() { return `Hi, I'm ${this.name}`; };
const user2 = new User("Chaman", 21);

// Version 3: ES6 class (modern — use this)
class User3 {
    constructor(name, age) {
        this.name = name;
        this.age  = age;
    }
    greet() { return `Hi, I'm ${this.name}`; }
    static create(name, age) { return new User3(name, age); }  // factory method
}

// Version 4: Object.create (prototype-based)
const userProto = {
    greet() { return `Hi, I'm ${this.name}`; }
};
const user4 = Object.create(userProto);
user4.name = "Chaman";

// ── 2. ASYNC PATTERNS ────────────────────────────────────────

// Version 1: Callbacks (old — callback hell)
function fetchUserCb(id, callback) {
    setTimeout(() => callback(null, { id, name: "Chaman" }), 100);
}
fetchUserCb(1, (err, user) => {
    if (err) return console.error(err);
    console.log(user);
});

// Version 2: Promises
function fetchUserPromise(id) {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve({ id, name: "Chaman" }), 100);
    });
}
fetchUserPromise(1).then(user => console.log(user)).catch(console.error);

// Version 3: async/await (modern — use this)
async function fetchUser(id) {
    const res  = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
}

// Version 4: parallel async calls
async function fetchMultiple(ids) {
    const users = await Promise.all(ids.map(id => fetchUser(id)));
    return users;
}

// ── 3. ERROR HANDLING PATTERNS ───────────────────────────────

// Version 1: try/catch (standard)
async function safeCall(id) {
    try {
        return await fetchUser(id);
    } catch (err) {
        console.error(err.message);
        return null;
    }
}

// Version 2: Result tuple (like Go) — avoids try/catch everywhere
async function safeFetch(id) {
    try {
        const data = await fetchUser(id);
        return [null, data];    // [error, data]
    } catch (err) {
        return [err, null];
    }
}
const [err, user] = await safeFetch(1);
if (err) { /* handle */ }

// Version 3: .catch on the promise
fetchUser(1)
    .then(user => processUser(user))
    .catch(err => handleError(err));

// ── 4. ARRAY MANIPULATION PATTERNS ───────────────────────────
const nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Filter + map + reduce chain
const result = nums
    .filter(n => n % 2 === 0)        // [2, 4, 6, 8, 10]
    .map(n => n * n)                 // [4, 16, 36, 64, 100]
    .reduce((sum, n) => sum + n, 0); // 220

// Find vs filter
const first = nums.find(n => n > 5);   // 6 — returns first match (or undefined)
const all   = nums.filter(n => n > 5); // [6,7,8,9,10] — returns all matches

// flat and flatMap
const nested = [[1,2], [3,4], [5,6]];
const flat   = nested.flat();        // [1,2,3,4,5,6]
const flat2  = nested.flatMap(arr => arr.map(n => n * 2));  // [2,4,6,8,10,12]

// ── 5. OBJECT MANIPULATION PATTERNS ─────────────────────────
const user = { id: 1, name: "Chaman", email: "c@y.com", password: "secret", age: 21 };

// Pick specific fields
const { id, name, email } = user;               // destructuring
const picked = { id: user.id, name: user.name };

// Omit fields (remove sensitive data before sending to client)
const { password, ...safeUser } = user;         // rest operator to omit
console.log(safeUser);  // { id, name, email, age }

// Object.entries for transformation
const upperCased = Object.fromEntries(
    Object.entries(user).map(([k, v]) => [k, typeof v === "string" ? v.toUpperCase() : v])
);

// ── 6. MIDDLEWARE PATTERN (Express) ──────────────────────────
// Middleware is just a function that processes the request and calls next()

// Auth middleware
const authenticate = async (req, res, next) => {
    const token = req.headers.authorization?.replace("Bearer ", "");
    if (!token) return res.status(401).json({ error: "Token required" });
    try {
        req.user = jwt.verify(token, process.env.JWT_SECRET);
        next();
    } catch {
        res.status(401).json({ error: "Invalid token" });
    }
};

// Role middleware (factory pattern — returns middleware)
const requireRole = (role) => (req, res, next) => {
    if (req.user?.role !== role) {
        return res.status(403).json({ error: "Insufficient permissions" });
    }
    next();
};

// Async wrapper to avoid try/catch in every route
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};

// Use:
// router.get("/admin", authenticate, requireRole("admin"), asyncHandler(async (req, res) => {
//     const data = await AdminService.getStats();  // no try/catch needed!
//     res.json(data);
// }));

// ── 7. MONGOOSE QUERY VARIATIONS ─────────────────────────────

// Find with various option patterns:
const findVariations = async (filter) => {
    // Version 1: simple
    const all = await User.find({ active: true });

    // Version 2: with select (field projection) and sort
    const sorted = await User
        .find({ active: true })
        .select("name email -_id")   // include name, email; exclude _id
        .sort({ name: 1 })
        .lean();    // plain JS objects, faster

    // Version 3: with population
    const withPosts = await User
        .find()
        .populate("posts", "title createdAt")   // only include title and createdAt from Post
        .lean();

    // Version 4: pagination helper
    const PAGE = 1, LIMIT = 10;
    const paginated = await User
        .find()
        .skip((PAGE - 1) * LIMIT)
        .limit(LIMIT);
    const total = await User.countDocuments();
    return { data: paginated, total, pages: Math.ceil(total / LIMIT) };
};

module.exports = { authenticate, requireRole, asyncHandler };
