# JavaScript / Node.js / Express / TypeScript Q&A — Comprehensive

## JAVASCRIPT FUNDAMENTALS

**Q: const vs let vs var?**
A: `const`: Block-scoped, cannot be reassigned (but object properties can mutate). Use by default.
   `let`: Block-scoped, can be reassigned. Use when value changes.
   `var`: Function-scoped, hoisted (can be used before declaration), no block scope. Never use!

**Q: What is hoisting?**
A: JavaScript moves declarations to top of scope before execution:
   ```js
   console.log(x) // undefined (not error)
   var x = 5

   // let/const are hoisted but not initialized (temporal dead zone)
   console.log(y) // ReferenceError
   let y = 5
   ```

**Q: What is closure?**
A: Function has access to variables from its outer scope even after outer function has returned:
   ```js
   function counter() {
     let count = 0
     return () => ++count // Closure over count
   }
   const increment = counter()
   increment() // 1
   increment() // 2
   ```

**Q: What is the `this` keyword?**
A: Context depends on how function is called:
   - Regular function: `this` = calling object (or global/undefined in strict mode)
   - Arrow function: `this` = inherited from surrounding scope (no own `this`)
   - Method: `this` = object the method belongs to
   - `call/apply/bind`: Explicitly set `this`

**Q: Arrow function vs regular function?**
A: Arrow: No own `this`, shorter syntax, can't be constructors.
   Regular: Has own `this`, can be constructors, `arguments` object exists.
   Use arrow for callbacks where you want parent's `this`.

**Q: What is the Prototype chain?**
A: Objects inherit from other objects via `__proto__`. When property not found on object, JS looks up prototype chain until `null`.
   `Array.prototype` has `.map()`, `.filter()` - all arrays inherit these.

**Q: What is Promise?**
A: Represents future value. States: pending → resolved or rejected.
   ```js
   const promise = new Promise((resolve, reject) => {
     setTimeout(() => resolve('done'), 1000)
   })
   promise.then(result => ...).catch(err => ...)
   ```

**Q: Promise.all vs Promise.allSettled vs Promise.race?**
A: `Promise.all`: Waits for ALL. Rejects if ANY rejects.
   `Promise.allSettled`: Waits for ALL. Never rejects. Returns { status, value/reason } for each.
   `Promise.race`: First promise to settle wins (resolve or reject).
   `Promise.any`: First to resolve wins, rejects only if ALL reject.

**Q: async/await?**
A: Syntactic sugar over Promises. `await` pauses until Promise settles. Must be inside `async function`.
   ```js
   async function getUser(id) {
     try {
       const user = await User.findById(id) // Pauses here
       return user
     } catch (err) {
       throw new Error('User not found')
     }
   }
   ```

**Q: What is Event Delegation?**
A: Add one listener on parent instead of many on children. Uses event bubbling:
   ```js
   document.getElementById('list').addEventListener('click', (e) => {
     if (e.target.tagName === 'LI') {
       // Handle click on any li item
     }
   })
   ```

**Q: Shallow copy vs deep copy?**
A: Shallow: Only copies top-level properties. Nested objects are still referenced.
   Deep: Recursively copies all levels.
   ```js
   const shallow = { ...obj }           // Spread (shallow)
   const deep = JSON.parse(JSON.stringify(obj)) // Simple deep (loses functions/dates)
   const deep2 = structuredClone(obj)   // Modern deep copy
   ```

**Q: What is the Event Loop in JavaScript?**
A: Single-threaded async mechanism:
   1. Synchronous code runs on call stack
   2. Async operations (setTimeout, fetch) pushed to Web APIs
   3. Callbacks queued in Macrotask queue
   4. Microtasks (Promises, queueMicrotask) queued in Microtask queue
   5. Event loop: call stack empty → run ALL microtasks → run ONE macrotask → repeat

**Q: What is generator function?**
A: Function that can pause and resume execution using `yield`:
   ```js
   function* count() {
     yield 1
     yield 2
     yield 3
   }
   const gen = count()
   gen.next() // {value: 1, done: false}
   gen.next() // {value: 2, done: false}
   ```

**Q: WeakMap vs Map?**
A: Map: Strong references, keys can be any type, iterable, `.size` property.
   WeakMap: Weak references (keys get GC'd), keys must be objects, not iterable. Good for metadata/private data.

**Q: Symbol in JavaScript?**
A: Guaranteed unique primitive. Used for object property keys that won't conflict:
   ```js
   const ID = Symbol('id')
   obj[ID] = 123 // Private-ish, not enumerable in for..in
   ```

---

## NODE.JS

**Q: What is Node.js?**
A: JavaScript runtime built on V8 engine. Non-blocking I/O, event-driven, single-threaded with event loop. Perfect for I/O-heavy apps (APIs, real-time), not CPU-heavy (use Python/Go for ML, video encoding).

**Q: How does Node.js handle concurrency if it's single-threaded?**
A: Uses event loop + libuv thread pool for I/O operations. While waiting for I/O, Node serves other requests. Illusion of concurrency with single thread.

**Q: process.nextTick vs setImmediate vs setTimeout?**
A: `process.nextTick`: Runs after current operation, before any I/O (highest priority)
   Promises: Same phase as nextTick (microtasks)
   `setImmediate`: Runs after I/O callbacks in Check phase
   `setTimeout(fn, 0)`: Runs in next Timers phase (slightly later than setImmediate)
   Order: nextTick → Promises → setImmediate ≈ setTimeout

**Q: What is the module system in Node.js?**
A: CommonJS (default): `require()` / `module.exports` - synchronous, cached on first load.
   ES Modules: `import` / `export` - requires `"type": "module"` in package.json.

**Q: What is npm?**
A: Node Package Manager. Install packages, manage dependencies, run scripts.
   `npm install` → downloads packages listed in package.json
   `npm install express --save` → adds to dependencies
   `npm install jest --save-dev` → adds to devDependencies (not in production)

**Q: package.json vs package-lock.json?**
A: package.json: Defines project, dependencies with version ranges (e.g., `^1.2.3`).
   package-lock.json: Exact versions of every installed package tree. Ensures reproducible installs.

**Q: What are Node streams?**
A: Process data chunk by chunk (memory efficient for large files):
   ```js
   const readStream = fs.createReadStream('./big-file.csv')
   const writeStream = fs.createWriteStream('./output.csv')
   readStream.pipe(writeStream) // Stream from file to file
   ```
   Types: Readable, Writable, Duplex, Transform

**Q: What is the Buffer?**
A: Raw binary data storage. Used for file I/O, network protocols, encoding/decoding.
   ```js
   const buf = Buffer.from('Hello')
   buf.toString('base64') // 'SGVsbG8='
   buf.length             // 5 (bytes)
   ```

**Q: What is clustering in Node.js?**
A: Use all CPU cores by spawning multiple worker processes. Each handles requests independently:
   ```js
   if (cluster.isMaster) {
     for (let i = 0; i < numCPUs; i++) cluster.fork()
   } else {
     app.listen(3000) // Each worker listens independently
   }
   ```

**Q: Worker Threads vs Child Processes?**
A: Worker Threads: Share memory, lightweight, good for CPU-intensive JS tasks.
   Child Processes: Separate memory, heavy, good for running external commands (Python scripts, system commands).

**Q: EventEmitter?**
A: Core Node.js pub/sub mechanism:
   ```js
   const emitter = new EventEmitter()
   emitter.on('data', (chunk) => console.log(chunk))
   emitter.emit('data', 'hello')
   emitter.once('end', () => console.log('Done!')) // Fire once only
   ```

---

## EXPRESS

**Q: What is Express?**
A: Minimal Node.js web framework. Routing, middleware, HTTP utilities.

**Q: What is middleware?**
A: Function with signature `(req, res, next)` that runs between request and response. Must call `next()` to pass control or send a response to end the chain.

**Q: What is error middleware?**
A: 4-parameter middleware `(err, req, res, next)`. Catches errors from route handlers. Must be registered LAST.

**Q: How to handle async errors?**
A: ```js
   // Option 1: try-catch in every route (verbose)
   app.get('/users', async (req, res) => {
     try {
       const users = await User.find()
       res.json(users)
     } catch (err) {
       next(err)
     }
   })

   // Option 2: asyncHandler wrapper (clean)
   const asyncHandler = fn => (req, res, next) =>
     Promise.resolve(fn(req, res, next)).catch(next)

   app.get('/users', asyncHandler(async (req, res) => {
     const users = await User.find()
     res.json(users)
   }))
   ```

**Q: Express Router?**
A: Mini-Express app for organizing routes:
   ```js
   const router = express.Router()
   router.get('/', getAllUsers)
   router.post('/', createUser)
   router.get('/:id', getUser)
   app.use('/api/users', router)
   ```

**Q: What is express.json() and why needed?**
A: Middleware that parses JSON request bodies. Without it, `req.body` is undefined for JSON requests.

**Q: How to access request data?**
A: `req.params.id` → URL params (`:id`)
   `req.query.page` → query string (`?page=2`)
   `req.body.name` → JSON body (needs express.json())
   `req.headers.authorization` → request headers
   `req.ip` → client IP address

**Q: How does Express routing work?**
A: Routes match in registration order. First match wins. Be careful with route ordering (specific before general):
   ```js
   app.get('/users/new', ...) // Must be before /:id!
   app.get('/users/:id', ...)
   ```

---

## TYPESCRIPT

**Q: What is TypeScript?**
A: JavaScript with static types. Catches errors at compile time. Transpiles to JS. All valid JS is valid TS.

**Q: interface vs type?**
A: interface: Object/class shapes, can extend, can be declared multiple times (merged).
   type: More flexible (unions, intersections, primitives, computed). Can't be merged.
   Rule: interface for object shapes, type for unions/aliases.

**Q: What is generics?**
A: Type parameters that let functions/classes work with any type while maintaining safety:
   ```ts
   function first<T>(arr: T[]): T | undefined {
     return arr[0]
   }
   first([1, 2, 3])    // returns number
   first(['a', 'b'])   // returns string
   ```

**Q: any vs unknown?**
A: `any`: Disables type checking entirely. Avoid!
   `unknown`: Type-safe alternative. Must type-check before use.
   ```ts
   let x: unknown = getInput()
   if (typeof x === 'string') { x.toUpperCase() } // OK after check
   ```

**Q: Readonly and Partial?**
A: `Readonly<T>`: All properties immutable.
   `Partial<T>`: All properties optional.
   `Required<T>`: All properties required.
   `Pick<T, K>`: Keep only listed properties.
   `Omit<T, K>`: Remove listed properties.

**Q: Utility types?**
A: ```ts
   type UserUpdate = Partial<User>     // All optional
   type UserView = Readonly<User>      // All readonly
   type UserMin = Pick<User, 'id' | 'name'> // Only id + name
   type UserPublic = Omit<User, 'password'>  // Remove password
   type UserRecord = Record<string, User>    // {[key: string]: User}
   ```

**Q: How to extend Express Request type?**
A: ```ts
   declare global {
     namespace Express {
       interface Request {
         user?: { id: string; role: string }
       }
     }
   }
   // Now req.user is typed in all route handlers
   ```

**Q: What is Declaration Merging?**
A: Interfaces with same name are merged:
   ```ts
   interface User { name: string }
   interface User { age: number }
   // Merged: User = { name: string, age: number }
   ```

**Q: What are decorators in TypeScript?**
A: Functions that add metadata or modify class/method behavior. Used in NestJS:
   ```ts
   @Controller('users')    // Route prefix
   class UsersController {
     @Get(':id')           // GET /users/:id
     getUser(@Param('id') id: string) { ... }
   }
   ```

**Q: TypeScript strict mode?**
A: Set `"strict": true` in tsconfig.json. Enables: noImplicitAny, strictNullChecks, strictFunctionTypes, etc. Always use strict mode!

---

## TRICKY QUESTIONS

**Q: What is the output?**
A: ```js
   console.log(typeof null)     // 'object' (JS bug, never fixed)
   console.log(typeof undefined) // 'undefined'
   console.log(0 == false)      // true (loose equality coerces)
   console.log(0 === false)     // false (strict equality)
   console.log([] == false)     // true (!!)
   console.log([] === false)    // false
   ```

**Q: Explain == vs ===?**
A: `==` (loose): Type coercion before comparison. Avoid!
   `===` (strict): No coercion, checks type and value. Always use!

**Q: What is event bubbling?**
A: Events bubble up from target element to parent elements. Can be stopped with `event.stopPropagation()`.

**Q: Memoization in JS?**
A: Cache function results to avoid recomputation:
   ```js
   function memoize(fn) {
     const cache = new Map()
     return (...args) => {
       const key = JSON.stringify(args)
       if (cache.has(key)) return cache.get(key)
       const result = fn(...args)
       cache.set(key, result)
       return result
     }
   }
   ```

**Q: What is debounce vs throttle?**
A: Debounce: Wait until user stops triggering event (search input).
   Throttle: Execute at most once per interval (scroll events).
   ```js
   const debounce = (fn, delay) => {
     let timer
     return (...args) => {
       clearTimeout(timer)
       timer = setTimeout(() => fn(...args), delay)
     }
   }
   ```
