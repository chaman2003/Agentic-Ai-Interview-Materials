/*
═══════════════════════════════════════════════════════════════════════════════
  EXPRESS.JS ADVANCED — COMPREHENSIVE GUIDE (BASICS TO ADVANCED)
═══════════════════════════════════════════════════════════════════════════════

This file covers:
1. Advanced Middleware Patterns
2. Error Handling & Async Errors
3. Request Validation & Sanitization
4. Streaming Responses
5. WebSockets & Real-time Communication
6. Security Best Practices
7. Performance Optimization
8. Testing Express Apps
9. Production-Ready Patterns

*/

const express = require('express');
const app = express();

// ─── 1. ADVANCED MIDDLEWARE PATTERNS ───────────────────────────────────────

/*
Middleware: Functions that execute during request-response cycle
Signature: (req, res, next) => { ... }

Types:
1. Application-level: app.use()
2. Router-level: router.use()
3. Error-handling: (err, req, res, next) => {}
4. Built-in: express.json(), express.static()
5. Third-party: helmet, cors, morgan
*/

// Pattern 1: Request ID middleware (for logging/tracing)
app.use((req, res, next) => {
  req.id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  res.setHeader('X-Request-ID', req.id);
  next();
});

// Pattern 2: Request timing middleware
app.use((req, res, next) => {
  const start = Date.now();

  // Hook into response finish event
  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`[${req.id}] ${req.method} ${req.url} - ${duration}ms - ${res.statusCode}`);
  });

  next();
});

// Pattern 3: Conditional middleware (only for specific routes)
const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    // Verify JWT token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Pattern 4: Role-based access control middleware
const requireRole = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

// Usage: Only admins can access this route
app.delete('/api/users/:id', authMiddleware, requireRole('admin'), (req, res) => {
  res.json({ message: 'User deleted' });
});

// Pattern 5: Rate limiting middleware (prevent abuse)
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Max 100 requests per windowMs
  message: { error: 'Too many requests, please try again later' },
  standardHeaders: true, // Return rate limit info in headers
  legacyHeaders: false
});

app.use('/api/', apiLimiter);

// Pattern 6: Request context middleware (attach common utilities)
app.use((req, res, next) => {
  // Attach utility functions to req
  req.getCurrentUser = async () => {
    if (!req.user) return null;
    return await User.findById(req.user.id);
  };

  // Attach custom response methods
  res.success = (data, statusCode = 200) => {
    res.status(statusCode).json({
      success: true,
      data
    });
  };

  res.error = (message, statusCode = 400) => {
    res.status(statusCode).json({
      success: false,
      error: message
    });
  };

  next();
});

// ─── 2. ERROR HANDLING & ASYNC ERRORS ──────────────────────────────────────

/*
Problem: Async errors don't trigger Express error handlers by default
Solution: Use try-catch or async error wrapper
*/

// Pattern 1: Async error wrapper (catch async errors automatically)
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

// Usage:
app.get('/api/users', asyncHandler(async (req, res) => {
  const users = await User.find({}); // If this throws, error handler catches it
  res.json(users);
}));

// Pattern 2: Custom error classes
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true; // Distinguish from programming errors

    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(message) {
    super(message, 400);
  }
}

class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, 404);
  }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Unauthorized') {
    super(message, 401);
  }
}

// Usage in routes:
app.get('/api/users/:id', asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id);

  if (!user) {
    throw new NotFoundError('User');
  }

  res.json(user);
}));

// Pattern 3: Centralized error handler (must be last middleware!)
app.use((err, req, res, next) => {
  console.error('Error:', err);

  // Default to 500 if statusCode not set
  const statusCode = err.statusCode || 500;

  // Different responses for dev vs production
  if (process.env.NODE_ENV === 'development') {
    return res.status(statusCode).json({
      success: false,
      error: err.message,
      stack: err.stack,
      details: err
    });
  }

  // Production: Don't leak error details
  if (err.isOperational) {
    // Operational errors: safe to send to client
    return res.status(statusCode).json({
      success: false,
      error: err.message
    });
  }

  // Programming errors: log but don't expose details
  console.error('Unexpected error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Pattern 4: 404 handler (catch all undefined routes)
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    error: `Route ${req.originalUrl} not found`
  });
});

// ─── 3. REQUEST VALIDATION & SANITIZATION ──────────────────────────────────

/*
Never trust user input!
Use validation libraries like Joi, Yup, or express-validator
*/

const { body, param, query, validationResult } = require('express-validator');

// Pattern 1: Validation middleware
const validate = (validations) => {
  return async (req, res, next) => {
    // Run all validations
    await Promise.all(validations.map(validation => validation.run(req)));

    // Check for errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    next();
  };
};

// Pattern 2: Reusable validation rules
const userValidationRules = {
  register: [
    body('email')
      .isEmail().withMessage('Invalid email')
      .normalizeEmail(),
    body('password')
      .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).withMessage('Password must contain uppercase, lowercase, and number'),
    body('username')
      .isLength({ min: 3, max: 20 }).withMessage('Username must be 3-20 characters')
      .matches(/^[a-zA-Z0-9_]+$/).withMessage('Username can only contain letters, numbers, and underscores')
      .trim()
  ],

  updateProfile: [
    body('bio')
      .optional()
      .isLength({ max: 500 }).withMessage('Bio must be under 500 characters')
      .trim()
      .escape(), // Prevent XSS
    body('age')
      .optional()
      .isInt({ min: 13, max: 120 }).withMessage('Invalid age')
  ]
};

// Usage:
app.post('/api/register', validate(userValidationRules.register), asyncHandler(async (req, res) => {
  const { email, password, username } = req.body;

  // Validation passed, safe to use input
  const user = await User.create({ email, password, username });

  res.status(201).json({ user });
}));

// Pattern 3: Parameter validation
app.get('/api/users/:id',
  validate([param('id').isMongoId().withMessage('Invalid user ID')]),
  asyncHandler(async (req, res) => {
    const user = await User.findById(req.params.id);
    if (!user) throw new NotFoundError('User');
    res.json(user);
  })
);

// Pattern 4: Query string validation
app.get('/api/posts',
  validate([
    query('page').optional().isInt({ min: 1 }).toInt(),
    query('limit').optional().isInt({ min: 1, max: 100 }).toInt(),
    query('sort').optional().isIn(['created_at', 'title', 'views'])
  ]),
  asyncHandler(async (req, res) => {
    const { page = 1, limit = 20, sort = 'created_at' } = req.query;
    const posts = await Post.find({})
      .sort({ [sort]: -1 })
      .skip((page - 1) * limit)
      .limit(limit);
    res.json(posts);
  })
);

// ─── 4. STREAMING RESPONSES ────────────────────────────────────────────────

/*
Streaming is efficient for large data (files, logs, real-time data)
Don't load entire file/data into memory - stream it chunk by chunk
*/

const fs = require('fs');
const path = require('path');

// Pattern 1: Stream file download
app.get('/api/download/:filename', (req, res) => {
  const filePath = path.join(__dirname, 'uploads', req.params.filename);

  // Check if file exists
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'File not found' });
  }

  // Set headers
  res.setHeader('Content-Type', 'application/octet-stream');
  res.setHeader('Content-Disposition', `attachment; filename="${req.params.filename}"`);

  // Stream file (memory efficient!)
  const fileStream = fs.createReadStream(filePath);
  fileStream.pipe(res);

  // Handle errors
  fileStream.on('error', (error) => {
    console.error('Stream error:', error);
    res.status(500).end();
  });
});

// Pattern 2: Stream JSON data (for large datasets)
app.get('/api/users/export', asyncHandler(async (req, res) => {
  res.setHeader('Content-Type', 'application/json');

  const userStream = User.find({}).cursor(); // Mongoose cursor (stream)

  res.write('[');

  let first = true;
  userStream.on('data', (user) => {
    if (!first) res.write(',');
    res.write(JSON.stringify(user));
    first = false;
  });

  userStream.on('end', () => {
    res.write(']');
    res.end();
  });

  userStream.on('error', (error) => {
    console.error('Stream error:', error);
    res.status(500).end();
  });
}));

// Pattern 3: Server-Sent Events (SSE) for real-time updates
app.get('/api/notifications/stream', (req, res) => {
  // Set headers for SSE
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Send notification every 5 seconds (example)
  const intervalId = setInterval(() => {
    const notification = {
      id: Date.now(),
      message: 'New notification!',
      timestamp: new Date()
    };

    res.write(`data: ${JSON.stringify(notification)}\n\n`);
  }, 5000);

  // Clean up when client disconnects
  req.on('close', () => {
    clearInterval(intervalId);
    res.end();
  });
});

// ─── 5. WEBSOCKETS & REAL-TIME COMMUNICATION ───────────────────────────────

/*
WebSockets: Full-duplex communication (client ↔ server)
Use cases: Chat apps, live dashboards, multiplayer games
*/

const http = require('http');
const { Server } = require('socket.io');

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.CLIENT_URL || 'http://localhost:3000',
    methods: ['GET', 'POST']
  }
});

// WebSocket connection handler
io.on('connection', (socket) => {
  console.log('User connected:', socket.id);

  // Handle custom events
  socket.on('join_room', (roomId) => {
    socket.join(roomId);
    console.log(`User ${socket.id} joined room ${roomId}`);

    // Notify others in the room
    socket.to(roomId).emit('user_joined', {
      userId: socket.id,
      timestamp: new Date()
    });
  });

  socket.on('send_message', (data) => {
    const { roomId, message } = data;

    // Broadcast to everyone in the room except sender
    socket.to(roomId).emit('receive_message', {
      userId: socket.id,
      message,
      timestamp: new Date()
    });
  });

  socket.on('disconnect', () => {
    console.log('User disconnected:', socket.id);
  });
});

// Pattern: Authenticate WebSocket connections
io.use((socket, next) => {
  const token = socket.handshake.auth.token;

  if (!token) {
    return next(new Error('Authentication required'));
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    socket.userId = decoded.id;
    next();
  } catch (error) {
    next(new Error('Invalid token'));
  }
});

// ─── 6. SECURITY BEST PRACTICES ────────────────────────────────────────────

const helmet = require('helmet');
const mongoSanitize = require('express-mongo-sanitize');
const xss = require('xss-clean');
const hpp = require('hpp');
const cors = require('cors');

// 1. Helmet: Secure HTTP headers
app.use(helmet());

// 2. CORS: Control which domains can access your API
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:3000',
  credentials: true, // Allow cookies
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// 3. Prevent NoSQL injection
app.use(mongoSanitize()); // Removes $ and . from user input

// 4. Prevent XSS attacks
app.use(xss()); // Sanitizes user input to prevent JavaScript injection

// 5. Prevent HTTP parameter pollution
app.use(hpp()); // Prevents duplicate query parameters

// 6. HTTPS only in production
if (process.env.NODE_ENV === 'production') {
  app.use((req, res, next) => {
    if (req.header('x-forwarded-proto') !== 'https') {
      return res.redirect(`https://${req.header('host')}${req.url}`);
    }
    next();
  });
}

// 7. Security headers for API responses
app.use((req, res, next) => {
  res.removeHeader('X-Powered-By'); // Hide Express
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
});

// ─── 7. PERFORMANCE OPTIMIZATION ───────────────────────────────────────────

const compression = require('compression');

// 1. Gzip compression (reduce response size)
app.use(compression());

// 2. Static file caching
app.use('/static', express.static(path.join(__dirname, 'public'), {
  maxAge: '1d', // Cache for 1 day
  etag: true
}));

// 3. Response caching with Redis
const RedisStore = require('rate-limit-redis');
const redisClient = require('redis').createClient();

const cacheMiddleware = (duration) => {
  return async (req, res, next) => {
    const key = `cache:${req.originalUrl}`;

    try {
      const cachedResponse = await redisClient.get(key);

      if (cachedResponse) {
        return res.json(JSON.parse(cachedResponse));
      }

      // Override res.json to cache response
      const originalJson = res.json.bind(res);
      res.json = (data) => {
        redisClient.setex(key, duration, JSON.stringify(data));
        return originalJson(data);
      };

      next();
    } catch (error) {
      console.error('Cache error:', error);
      next(); // Continue without cache on error
    }
  };
};

// Usage: Cache response for 5 minutes
app.get('/api/posts', cacheMiddleware(300), asyncHandler(async (req, res) => {
  const posts = await Post.find({});
  res.json(posts);
}));

// 4. Database connection pooling (MongoDB)
const mongoose = require('mongoose');

mongoose.connect(process.env.MONGODB_URI, {
  maxPoolSize: 10, // Max 10 concurrent connections
  minPoolSize: 2   // Keep 2 connections open
});

// ─── 8. TESTING EXPRESS APPS ───────────────────────────────────────────────

/*
Use supertest for HTTP testing
*/

const request = require('supertest');
const { describe, it, expect } = require('@jest/globals');

describe('User API', () => {
  it('should register a new user', async () => {
    const res = await request(app)
      .post('/api/register')
      .send({
        email: 'test@example.com',
        password: 'Password123',
        username: 'testuser'
      });

    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty('user');
  });

  it('should reject invalid email', async () => {
    const res = await request(app)
      .post('/api/register')
      .send({
        email: 'invalid-email',
        password: 'Password123',
        username: 'testuser'
      });

    expect(res.statusCode).toBe(400);
    expect(res.body.errors).toBeDefined();
  });

  it('should require authentication for protected route', async () => {
    const res = await request(app)
      .get('/api/profile');

    expect(res.statusCode).toBe(401);
  });

  it('should allow authenticated requests', async () => {
    // First, login to get token
    const loginRes = await request(app)
      .post('/api/login')
      .send({ email: 'test@example.com', password: 'Password123' });

    const token = loginRes.body.token;

    // Then, access protected route
    const res = await request(app)
      .get('/api/profile')
      .set('Authorization', `Bearer ${token}`);

    expect(res.statusCode).toBe(200);
  });
});

// ─── 9. PRODUCTION-READY PATTERNS ──────────────────────────────────────────

// Pattern 1: Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');

  server.close(() => {
    console.log('HTTP server closed');

    // Close database connections
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

// Pattern 2: Healthcheck endpoint
app.get('/health', asyncHandler(async (req, res) => {
  // Check database connection
  const dbStatus = mongoose.connection.readyState === 1 ? 'connected' : 'disconnected';

  // Check Redis connection (if using)
  let redisStatus = 'disconnected';
  try {
    await redisClient.ping();
    redisStatus = 'connected';
  } catch (error) {
    console.error('Redis healthcheck failed:', error);
  }

  const health = {
    status: 'ok',
    timestamp: new Date(),
    uptime: process.uptime(),
    database: dbStatus,
    redis: redisStatus,
    memory: process.memoryUsage()
  };

  const statusCode = (dbStatus === 'connected') ? 200 : 503;

  res.status(statusCode).json(health);
}));

// Pattern 3: Request/Response logging
const morgan = require('morgan');

if (process.env.NODE_ENV === 'production') {
  // Log to file in production
  const accessLogStream = fs.createWriteStream(
    path.join(__dirname, 'logs', 'access.log'),
    { flags: 'a' }
  );
  app.use(morgan('combined', { stream: accessLogStream }));
} else {
  // Log to console in development
  app.use(morgan('dev'));
}

// ─── INTERVIEW SUMMARY ─────────────────────────────────────────────────────

/*
KEY CONCEPTS TO MEMORIZE:

1. MIDDLEWARE:
   - What is middleware? (Functions that execute during request-response cycle)
   - Middleware types: app-level, router-level, error-handling
   - Order matters! (middleware executes in order of app.use())

2. ERROR HANDLING:
   - Async errors need try-catch or asyncHandler wrapper
   - Custom error classes (AppError, ValidationError, etc.)
   - Centralized error handler (must be last middleware)
   - Different error responses for dev vs production

3. VALIDATION:
   - Never trust user input!
   - Use express-validator or Joi
   - Validate body, params, query separately
   - Sanitize to prevent XSS

4. SECURITY:
   - helmet() for secure headers
   - CORS configuration
   - Rate limiting to prevent abuse
   - mongoSanitize() to prevent NoSQL injection
   - xss() to prevent XSS attacks

5. PERFORMANCE:
   - Compression middleware
   - Response caching with Redis
   - Database connection pooling
   - Streaming for large responses

6. WEBSOCKETS:
   - Full-duplex communication
   - socket.io for real-time features
   - Room-based messaging
   - Authenticate WebSocket connections

7. PRODUCTION:
   - Graceful shutdown
   - Healthcheck endpoint
   - Logging (morgan)
   - HTTPS enforcement
   - Environment-based configuration

COMMON INTERVIEW QUESTIONS:

Q: How does Express middleware work?
A: Functions with (req, res, next) that execute in order. Call next() to pass control.

Q: How to handle async errors in Express?
A: Use asyncHandler wrapper or try-catch, or Express 5's native async support.

Q: How to implement authentication?
A: JWT in Authorization header, verify in middleware, attach user to req.

Q: How to prevent DDOS attacks?
A: Rate limiting middleware (express-rate-limit).

Q: How to make Express production-ready?
A: Helmet, CORS, compression, logging, graceful shutdown, healthcheck, HTTPS.

Q: Streaming vs loading entire file?
A: Streaming is memory-efficient for large files (use fs.createReadStream).

Q: How to test Express routes?
A: Use supertest library to make HTTP requests in tests.
*/

// Start server
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = { app, server };
