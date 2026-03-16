# JavaScript / Node.js — Advanced Q&A, Tricky Questions & Patterns

---

## TRICKY OUTPUT QUESTIONS

**Q: What does this print?**
```js
console.log(typeof null);
```
**A:** `"object"` — This is a famous JavaScript bug. `null` is a primitive, not an object. It's been in the language since the beginning and can't be fixed without breaking existing code.

---

**Q: What does this print?**
```js
console.log(1 + "2");
console.log(1 - "2");
```
**A:** `"12"` (string concatenation — `+` converts number to string)
`-1` (subtraction always converts to number)

---

**Q: What does this print?**
```js
console.log([] == false);
console.log([] == 0);
console.log([] + []);
console.log({} + []);
```
**A:** `true`, `true`, `""`, `0`
**Why:** JavaScript's loose equality (`==`) does type coercion. Use `===` always.

---

**Q: What does this print?**
```js
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);
}
```
**A:** `3 3 3` — `var` is function-scoped, not block-scoped. The loop finishes (i=3) before any setTimeout fires.
**Fix with `let`:**
```js
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);  // 0 1 2 ✓
}
```

---

**Q: What does this print?**
```js
const obj = { name: "Chaman" };
const copy = obj;
copy.name = "Alice";
console.log(obj.name);
```
**A:** `"Alice"` — Objects are reference types. `copy = obj` makes both point to the same object in memory.
**Fix:** `const copy = { ...obj }` (shallow) or `structuredClone(obj)` (deep clone, Node 17+)

---

## `this` KEYWORD — Most Confusing Topic

**Q: What is `this` in JavaScript?**
A: `this` refers to the execution context — the object that "owns" the function call. Its value depends on HOW the function is called, not where it's defined.

```js
const user = {
    name: "Chaman",

    greet() {
        console.log(this.name);  // "Chaman" — this = user object
    },

    greetArrow: () => {
        console.log(this.name);  // undefined — arrow functions inherit this from enclosing scope
    },

    greetTimeout() {
        setTimeout(function() {
            console.log(this.name);  // undefined — regular function, this = global/undefined
        }, 0);

        setTimeout(() => {
            console.log(this.name);  // "Chaman" — arrow function, this = user
        }, 0);
    }
};
```

**Rule:** Arrow functions do NOT have their own `this`. They always use `this` from the enclosing scope. Regular functions get a new `this` on each call.

---

## PROMISES AND ASYNC IN DEPTH

**Q: What is the difference between `Promise.all`, `Promise.allSettled`, `Promise.any`, `Promise.race`?**

| Method | Behavior |
|--------|---------|
| `Promise.all([...])` | Resolves when ALL resolve. FAILS if ANY fails. |
| `Promise.allSettled([...])` | Waits for ALL to finish. Never rejects. Returns `{status, value/reason}`. |
| `Promise.any([...])` | Resolves when FIRST resolves. Fails only if ALL fail. |
| `Promise.race([...])` | Resolves/rejects as soon as the FASTEST one settles. |

```js
// Run 3 API calls in parallel — need ALL to succeed
const [users, orders, products] = await Promise.all([
    fetch("/api/users").then(r => r.json()),
    fetch("/api/orders").then(r => r.json()),
    fetch("/api/products").then(r => r.json()),
]);

// Run 3 API calls but don't fail if some fail
const results = await Promise.allSettled([fetchA(), fetchB(), fetchC()]);
results.forEach(r => {
    if (r.status === "fulfilled") console.log(r.value);
    else console.error(r.reason);
});
```

---

**Q: What is the event loop? Deep dive.**
A:
```
                  ┌─────────────────────┐
                  │        Call Stack   │  ← synchronous code runs here
                  └──────────┬──────────┘
                             │ if empty
                  ┌──────────▼──────────┐
                  │   Microtask Queue   │  ← Promise .then(), queueMicrotask()
                  │   (runs first!)     │     processed BEFORE macro tasks
                  └──────────┬──────────┘
                             │ if empty
                  ┌──────────▼──────────┐
                  │   Macrotask Queue   │  ← setTimeout, setInterval, I/O
                  └─────────────────────┘
```

```js
console.log("1");           // sync → stack
setTimeout(() => console.log("2"), 0);  // macro task
Promise.resolve().then(() => console.log("3"));  // micro task
console.log("4");           // sync → stack

// Output: 1, 4, 3, 2
// Sync first → microtasks → macrotasks
```

---

**Q: What is the difference between `async/await` and Promises?**
A: `async/await` is syntactic sugar over Promises — it compiles down to `.then()`/`.catch()` chains. Easier to read, especially for sequential async operations:
```js
// Promise chains — callback-like, harder to read
fetch("/api/user")
    .then(r => r.json())
    .then(user => fetch(`/api/posts/${user.id}`))
    .then(r => r.json())
    .catch(err => console.error(err));

// async/await — reads like synchronous code
async function getUserPosts() {
    try {
        const userRes = await fetch("/api/user");
        const user = await userRes.json();
        const postsRes = await fetch(`/api/posts/${user.id}`);
        return await postsRes.json();
    } catch (err) {
        console.error(err);
    }
}
```

---

## PROTOTYPE AND CLASSES

**Q: What is the prototype chain?**
A: Every JavaScript object has a hidden `__proto__` property pointing to its prototype. When you access a property, JS looks up the chain until it finds it or hits `null`.
```js
const arr = [1, 2, 3];
// arr.__proto__ → Array.prototype → has .map, .filter, .forEach
// arr.__proto__.__proto__ → Object.prototype → has .toString, .hasOwnProperty
// arr.__proto__.__proto__.__proto__ → null  (end of chain)

arr.map(x => x * 2);   // found on Array.prototype
arr.toString();        // found on Object.prototype
```

**Q: Are ES6 classes syntactic sugar over prototypes?**
A: Yes. `class Dog { }` compiles to prototype-based code. Classes are just a cleaner syntax — under the hood, methods are still added to `Dog.prototype`.

---

## NODE.JS INTERNALS

**Q: What is the difference between `process.nextTick` and `setImmediate`?**
A:
- `process.nextTick` — runs before ANYTHING else in the next iteration, before I/O, before promises. Highest priority.
- `setImmediate` — runs in the check phase of the event loop, after I/O callbacks.
- `Promise.then` — runs in microtask queue, after `nextTick`.

Order: `nextTick` → `Promise.then` → I/O callbacks → `setImmediate` → `setTimeout`

---

**Q: What is `require` vs `import`?**
A:
- `require` — CommonJS, synchronous, works anywhere in code, `module.exports`
- `import` — ES Modules, statically analyzed, must be at top level, `export default`/`export`
- Node.js supports both. In `.mjs` files: use `import`. In `.cjs` files: use `require`. In your package.json: `"type": "module"` makes `.js` use ES Modules.

---

## EXPRESS INTERNALS

**Q: How does Express routing work internally?**
A: Express maintains a list of layers (middleware and routes). On each request, it walks the list and calls each layer's handler if the path and method match. Each layer calls `next()` to pass to the next one.

**Q: What is the difference between `app.use()` and `app.get()`?**
A:
- `app.use(path, fn)` — matches any HTTP method, matches if path STARTS WITH the route
- `app.get(path, fn)` — matches only GET, exact path match
- `app.use("/api")` matches `/api`, `/api/users`, `/api/users/1`
- `app.get("/api")` matches only `/api`

**Q: What happens if you don't call `next()` in middleware?**
A: The request hangs forever. The client waits for a response that never comes, and eventually times out. Always either call `next()` or send a response — never both.

---

## COMMON NODE.JS PATTERNS

**Q: How do you handle unhandled promise rejections in production?**
```js
// Catch all unhandled promise rejections
process.on("unhandledRejection", (reason, promise) => {
    console.error("Unhandled rejection:", reason);
    // Log to error monitoring service (Sentry, etc.)
    process.exit(1);  // crash so process manager (PM2) restarts
});

// Catch all uncaught synchronous exceptions
process.on("uncaughtException", (error) => {
    console.error("Uncaught exception:", error);
    process.exit(1);
});
```

**Q: What is clustering in Node.js?**
A: Node.js is single-threaded. Clustering creates multiple worker processes (one per CPU core), each running the server. The master process distributes incoming connections round-robin.
```js
const cluster = require("cluster");
const os = require("os");

if (cluster.isPrimary) {
    for (let i = 0; i < os.cpus().length; i++) {
        cluster.fork();  // create worker for each CPU
    }
} else {
    // Each worker runs the server
    const app = require("./app");
    app.listen(3000);
}
```
Production: use **PM2** instead of manual clustering: `pm2 start app.js -i max`

---

## JAVASCRIPT INTERVIEW CODE VARIATIONS

**Q: Different ways to clone an object:**
```js
const user = { name: "Chaman", addr: { city: "Bangalore" } };

// Shallow clone (nested objects still shared)
const c1 = { ...user };                    // spread
const c2 = Object.assign({}, user);        // Object.assign
const c3 = JSON.parse(JSON.stringify(user)); // deep clone (lossy — no functions/dates)
const c4 = structuredClone(user);          // deep clone (modern, handles more types)
```

**Q: Different ways to check if a key exists in an object:**
```js
const obj = { name: "Chaman", age: undefined };

"name" in obj          // true  — checks prototype chain too
obj.hasOwnProperty("name")  // true  — only own properties
Object.hasOwn(obj, "name")  // true  — modern, same as hasOwnProperty
obj.name !== undefined      // true for "name", FALSE for "age" (pitfall!)
```

**Q: Debounce vs Throttle:**
```js
// Debounce: wait until user STOPS doing something (N ms of inactivity)
// Use for: search input (don't search on every keystroke)
function debounce(fn, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
    };
}

// Throttle: at most once every N ms no matter how often triggered
// Use for: scroll events, window resize
function throttle(fn, interval) {
    let lastTime = 0;
    return (...args) => {
        const now = Date.now();
        if (now - lastTime >= interval) {
            lastTime = now;
            return fn(...args);
        }
    };
}
```
