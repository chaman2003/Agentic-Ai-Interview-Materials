/*
═══════════════════════════════════════════════════════════════════════════════
  NODE.JS FUNDAMENTALS & PATTERNS — COMPREHENSIVE GUIDE
═══════════════════════════════════════════════════════════════════════════════

Node.js: JavaScript runtime built on Chrome's V8 engine
Think: Run JavaScript outside the browser!

This file covers:
1. Node.js Core Concepts
2. Event Loop & Async Programming
3. Streams & Buffers
4. File System & Path
5. Child Processes
6. Common Patterns
7. Performance Optimization
8. Production Best Practices

*/

// ─── 1. NODE.JS CORE CONCEPTS ──────────────────────────────────────────────

/*
What is Node.js?
- JavaScript runtime (not a framework!)
- Built on V8 engine (Google Chrome)
- Event-driven, non-blocking I/O
- Single-threaded with event loop
- Perfect for I/O-heavy apps (not CPU-heavy)
*/

// Global objects (available everywhere, no require needed)
console.log(__dirname);  // Current directory
console.log(__filename); // Current file path
console.log(process.env); // Environment variables
console.log(process.argv); // Command-line arguments
console.log(process.cwd()); // Current working directory

// Module system (CommonJS)
// Each file is a module with its own scope

// Exporting
// single export
module.exports = function hello() {
  return 'Hello World';
};

// Multiple exports
module.exports = {
  add: (a, b) => a + b,
  subtract: (a, b) => a - b
};

// Or using exports shorthand
exports.add = (a, b) => a + b;
exports.subtract = (a, b) => a - b;

// Importing
const math = require('./math'); // Your module
const fs = require('fs');        // Built-in module
const express = require('express'); // NPM module

// ES6 Modules (require "type": "module" in package.json)
import fs from 'fs';
import { add, subtract } from './math.js';

export function multiply(a, b) {
  return a * b;
}

// ─── 2. EVENT LOOP & ASYNC PROGRAMMING ─────────────────────────────────────

/*
Event Loop: How Node.js handles async operations
Single-threaded but non-blocking!

Phases:
1. Timers (setTimeout, setInterval)
2. Pending callbacks (I/O errors)
3. Poll (I/O operations)
4. Check (setImmediate)
5. Close callbacks (socket.on('close'))

Micro-tasks (executed between phases):
- process.nextTick (highest priority)
- Promises (.then, async/await)
*/

// Example: Order of execution
console.log('1');

setTimeout(() => console.log('2'), 0);

setImmediate(() => console.log('3'));

process.nextTick(() => console.log('4'));

Promise.resolve().then(() => console.log('5'));

console.log('6');

// Output: 1, 6, 4, 5, 2, 3
// Explanation:
// - Synchronous code first (1, 6)
// - process.nextTick (4) — highest priority
// - Promises (5) — microtasks
// - setTimeout (2) — timers phase
// - setImmediate (3) — check phase

// async/await (modern way)
async function fetchUser(userId) {
  try {
    const response = await fetch(`/api/users/${userId}`);
    const user = await response.json();
    return user;
  } catch (error) {
    console.error('Error fetching user:', error);
    throw error;
  }
}

// Promises (old way)
function fetchUserPromise(userId) {
  return fetch(`/api/users/${userId}`)
    .then(response => response.json())
    .then(user => user)
    .catch(error => {
      console.error('Error:', error);
      throw error;
    });
}

// Callbacks (very old way, callback hell!)
function fetchUserCallback(userId, callback) {
  fetch(`/api/users/${userId}`, (error, response) => {
    if (error) return callback(error);

    response.json((error, user) => {
      if (error) return callback(error);
      callback(null, user);
    });
  });
}

// ─── 3. STREAMS & BUFFERS ──────────────────────────────────────────────────

/*
Streams: Process data chunk by chunk (memory efficient!)
Types:
1. Readable: Read data (fs.createReadStream, HTTP request)
2. Writable: Write data (fs.createWriteStream, HTTP response)
3. Duplex: Read and write (TCP socket)
4. Transform: Modify data as it passes (zlib compression)
*/

const fs = require('fs');
const zlib = require('zlib');

// Example 1: Copy large file (memory efficient!)
function copyFileLarge(source, destination) {
  const readStream = fs.createReadStream(source);
  const writeStream = fs.createWriteStream(destination);

  // Pipe: Connect readable to writable
  readStream.pipe(writeStream);

  readStream.on('error', (error) => {
    console.error('Read error:', error);
  });

  writeStream.on('finish', () => {
    console.log('File copied successfully');
  });
}

// Example 2: Compress file on the fly
function compressFile(source, destination) {
  const readStream = fs.createReadStream(source);
  const gzip = zlib.createGzip();
  const writeStream = fs.createWriteStream(destination);

  // Chain pipes: read → compress → write
  readStream
    .pipe(gzip)
    .pipe(writeStream)
    .on('finish', () => console.log('Compressed!'));
}

// Example 3: HTTP streaming (send large response)
const http = require('http');

http.createServer((req, res) => {
  if (req.url === '/download') {
    res.writeHead(200, { 'Content-Type': 'application/octet-stream' });

    // Stream file to client (no memory overhead!)
    const fileStream = fs.createReadStream('./large-file.zip');
    fileStream.pipe(res);
  }
}).listen(3000);

// Buffers: Raw binary data
const buf1 = Buffer.from('Hello'); // From string
const buf2 = Buffer.alloc(10);     // Empty buffer (10 bytes)
const buf3 = Buffer.from([1, 2, 3]); // From array

console.log(buf1.toString());      // 'Hello'
console.log(buf1.length);          // 5 bytes
console.log(buf1[0]);              // 72 (ASCII code for 'H')

// ─── 4. FILE SYSTEM & PATH ─────────────────────────────────────────────────

const path = require('path');

// Path operations
console.log(path.join('/users', 'john', 'docs', 'file.txt'));
// /users/john/docs/file.txt

console.log(path.resolve('file.txt'));
// /current/working/directory/file.txt (absolute path)

console.log(path.dirname('/users/john/file.txt'));  // /users/john
console.log(path.basename('/users/john/file.txt')); // file.txt
console.log(path.extname('/users/john/file.txt'));  // .txt

// File operations (async - recommended)
const fs = require('fs').promises;

async function fileOperations() {
  // Read file
  const data = await fs.readFile('./file.txt', 'utf8');
  console.log(data);

  // Write file
  await fs.writeFile('./output.txt', 'Hello World');

  // Append to file
  await fs.appendFile('./output.txt', '\nNew line');

  // Check if file exists
  try {
    await fs.access('./file.txt');
    console.log('File exists');
  } catch {
    console.log('File does not exist');
  }

  // Delete file
  await fs.unlink('./temp.txt');

  // Create directory
  await fs.mkdir('./new-dir', { recursive: true });

  // Read directory
  const files = await fs.readdir('./');
  console.log(files);

  // File stats
  const stats = await fs.stat('./file.txt');
  console.log({
    size: stats.size,
    isFile: stats.isFile(),
    isDirectory: stats.isDirectory(),
    created: stats.birthtime,
    modified: stats.mtime
  });
}

// File operations (sync - blocking, avoid in production!)
const dataSync = fs.readFileSync('./file.txt', 'utf8');
fs.writeFileSync('./output.txt', 'Hello World');

// ─── 5. CHILD PROCESSES ────────────────────────────────────────────────────

/*
Run external commands or spawn new Node processes
*/

const { exec, spawn, fork } = require('child_process');

// exec: Run shell command (buffered output)
exec('ls -la', (error, stdout, stderr) => {
  if (error) {
    console.error('Error:', error);
    return;
  }

  console.log('Output:', stdout);
  if (stderr) console.error('Error output:', stderr);
});

// spawn: Stream output (for long-running commands)
const ls = spawn('ls', ['-la']);

ls.stdout.on('data', (data) => {
  console.log(`Output: ${data}`);
});

ls.stderr.on('data', (data) => {
  console.error(`Error: ${data}`);
});

ls.on('close', (code) => {
  console.log(`Process exited with code ${code}`);
});

// fork: Spawn new Node process (for parallel JS execution)
const child = fork('./worker.js');

child.send({ task: 'heavy-computation', data: [1, 2, 3] });

child.on('message', (result) => {
  console.log('Result from child:', result);
});

// worker.js
process.on('message', (msg) => {
  const result = performHeavyComputation(msg.data);
  process.send(result);
});

// ─── 6. COMMON PATTERNS ─────────────────────────────────────────────────────

// Pattern 1: Singleton (one instance only)
class Database {
  constructor() {
    if (Database.instance) {
      return Database.instance;
    }

    this.connection = null;
    Database.instance = this;
  }

  connect() {
    if (!this.connection) {
      this.connection = 'Connected to DB';
    }
    return this.connection;
  }
}

const db1 = new Database();
const db2 = new Database();
console.log(db1 === db2); // true (same instance)

// Pattern 2: Factory
class UserFactory {
  static createUser(type, data) {
    switch (type) {
      case 'admin':
        return new AdminUser(data);
      case 'customer':
        return new CustomerUser(data);
      default:
        return new GuestUser(data);
    }
  }
}

const admin = UserFactory.createUser('admin', { name: 'Alice' });

// Pattern 3: Observer (Pub/Sub)
const EventEmitter = require('events');

class NotificationService extends EventEmitter {
  sendEmail(user, message) {
    console.log(`Sending email to ${user}`);

    // Emit event
    this.emit('emailSent', { user, message });
  }
}

const notifications = new NotificationService();

// Subscribe to event
notifications.on('emailSent', (data) => {
  console.log('Email sent event:', data);
  // Log to analytics, etc.
});

notifications.sendEmail('alice@example.com', 'Welcome!');

// Pattern 4: Middleware (Express-style)
function middleware1(req, res, next) {
  console.log('Middleware 1');
  req.user = { id: 1 };
  next(); // Pass to next middleware
}

function middleware2(req, res, next) {
  console.log('Middleware 2, user:', req.user);
  next();
}

function finalHandler(req, res) {
  res.send('Done!');
}

// Execute middleware chain
function executeMiddleware(middlewares, req, res) {
  let index = 0;

  function next() {
    if (index >= middlewares.length) return;

    const middleware = middlewares[index++];
    middleware(req, res, next);
  }

  next();
}

// Pattern 5: Promisify callback-based functions
const { promisify } = require('util');

function callbackFunction(arg, callback) {
  setTimeout(() => callback(null, `Result: ${arg}`), 100);
}

const promisified = promisify(callbackFunction);

promisified('test').then(result => console.log(result));

// Or use async/await
async function example() {
  const result = await promisified('test');
  console.log(result);
}

// ─── 7. PERFORMANCE OPTIMIZATION ────────────────────────────────────────────

// Tip 1: Use clustering (utilize multiple CPU cores)
const cluster = require('cluster');
const numCPUs = require('os').cpus().length;

if (cluster.isMaster) {
  console.log(`Master process ${process.pid} is running`);

  // Fork workers (one per CPU core)
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died. Spawning new worker...`);
    cluster.fork();
  });
} else {
  // Worker processes run the server
  const express = require('express');
  const app = express();

  app.get('/', (req, res) => {
    res.send(`Handled by process ${process.pid}`);
  });

  app.listen(3000);
  console.log(`Worker ${process.pid} started`);
}

// Tip 2: Use caching
const NodeCache = require('node-cache');
const cache = new NodeCache({ stdTTL: 600 }); // 10 minutes

async function getUser(id) {
  // Check cache first
  const cachedUser = cache.get(`user:${id}`);
  if (cachedUser) return cachedUser;

  // Fetch from database
  const user = await User.findById(id);

  // Store in cache
  cache.set(`user:${id}`, user);

  return user;
}

// Tip 3: Use streams for large data
// ❌ Bad: Load entire file into memory
const dataAll = fs.readFileSync('./huge-file.json', 'utf8');
res.json(JSON.parse(dataAll));

// ✅ Good: Stream file
const stream = fs.createReadStream('./huge-file.json');
stream.pipe(res);

// Tip 4: Avoid blocking the event loop
// ❌ Bad: Synchronous heavy computation
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

app.get('/slow', (req, res) => {
  const result = fibonacci(40); // Blocks event loop!
  res.json({ result });
});

// ✅ Good: Use worker threads
const { Worker } = require('worker_threads');

app.get('/fast', (req, res) => {
  const worker = new Worker('./fibonacci-worker.js', {
    workerData: { n: 40 }
  });

  worker.on('message', (result) => {
    res.json({ result });
  });
});

// ─── 8. PRODUCTION BEST PRACTICES ──────────────────────────────────────────

// 1. Environment variables
require('dotenv').config();

const PORT = process.env.PORT || 3000;
const DB_URL = process.env.DATABASE_URL;
const SECRET = process.env.JWT_SECRET;

// 2. Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');

  server.close(() => {
    console.log('HTTP server closed');

    mongoose.connection.close(false, () => {
      console.log('MongoDB connection closed');
      process.exit(0);
    });
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    console.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
});

// 3. Error handling
process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// 4. Logging
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// 5. Process monitoring
console.log('Memory usage:', process.memoryUsage());
console.log('CPU usage:', process.cpuUsage());
console.log('Uptime:', process.uptime());

// ─── INTERVIEW SUMMARY ─────────────────────────────────────────────────────

/*
KEY CONCEPTS TO MEMORIZE:

1. WHAT IS NODE.JS:
   - JavaScript runtime (not a framework!)
   - Built on V8 engine
   - Event-driven, non-blocking I/O
   - Single-threaded with event loop

2. EVENT LOOP:
   - Phases: Timers, Poll, Check, Close
   - Micro-tasks: process.nextTick (highest priority), Promises
   - Non-blocking: Can handle many connections simultaneously

3. ASYNC PATTERNS:
   - Callbacks (old, callback hell)
   - Promises (.then, .catch)
   - async/await (modern, preferred)

4. STREAMS:
   - Memory efficient for large data
   - Types: Readable, Writable, Duplex, Transform
   - Use .pipe() to connect streams

5. MODULES:
   - CommonJS: require() / module.exports
   - ES6: import / export
   - Each file is a module with own scope

6. COMMON PATTERNS:
   - Singleton (one instance)
   - Factory (create objects)
   - Observer (Pub/Sub with EventEmitter)
   - Middleware (chain of functions)

7. PERFORMANCE:
   - Clustering (use all CPU cores)
   - Caching (avoid repeated work)
   - Streams (large data)
   - Worker threads (CPU-intensive tasks)

8. PRODUCTION:
   - Environment variables (.env)
   - Graceful shutdown
   - Error handling (uncaughtException, unhandledRejection)
   - Logging (Winston, Bunyan)
   - Monitoring (memory, CPU)

COMMON INTERVIEW QUESTIONS:

Q: What is Node.js?
A: JavaScript runtime built on V8. Event-driven, non-blocking I/O.

Q: Node.js single-threaded?
A: Yes for JavaScript execution. But uses libuv thread pool for I/O.

Q: What is Event Loop?
A: Handles async operations. Processes callbacks from different queues in phases.

Q: What's the difference between setImmediate and process.nextTick?
A: nextTick: Executes before event loop phases (highest priority).
   setImmediate: Executes in Check phase of event loop.

Q: Streams vs loading entire file?
A: Streams: Memory efficient (chunk by chunk).
   Load all: Faster for small files, but risky for large files.

Q: How to handle errors in async code?
A: Use try-catch with async/await, or .catch() with Promises.

Q: What's the purpose of package.json?
A: Defines project metadata, dependencies, scripts, entry point.

Q: npm vs npx?
A: npm: Package manager (install packages).
   npx: Execute packages without installing globally.

Q: How to scale Node.js?
A: 1) Clustering (multiple processes)
   2) Load balancing
   3) Microservices
   4) Caching (Redis)

Q: When NOT to use Node.js?
A: CPU-intensive tasks (image processing, video encoding).
   Use: Python, Java, Go for heavy computation.
*/

module.exports = {
  copyFileLarge,
  compressFile,
  fileOperations,
  getUser
};
