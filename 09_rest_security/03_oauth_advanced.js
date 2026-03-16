/**
 * 03_oauth_advanced.js — OAuth 2.0, PKCE, OIDC, Passport.js, Social Login
 * =========================================================================
 * Covers:
 *  1. OAuth 2.0 flows (Authorization Code, Client Credentials, Implicit, Device Code)
 *  2. PKCE (Proof Key for Code Exchange)
 *  3. OpenID Connect (OIDC) on top of OAuth 2.0
 *  4. JWT vs Session vs OAuth comparison
 *  5. Implementing OAuth with Passport.js
 *  6. Social login (Google, GitHub, Discord)
 *  7. Token refresh and rotation
 */

"use strict";

require("dotenv").config();
const express    = require("express");
const session    = require("express-session");
const passport   = require("passport");
const jwt        = require("jsonwebtoken");
const crypto     = require("crypto");
const axios      = require("axios");

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// ─────────────────────────────────────────────────────────────────────────────
// SESSION SETUP (required for Passport OAuth strategies)
// ─────────────────────────────────────────────────────────────────────────────

app.use(session({
  secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString("hex"),
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,          // not accessible via document.cookie (XSS protection)
    secure: process.env.NODE_ENV === "production",  // HTTPS only in prod
    sameSite: "lax",         // CSRF protection
    maxAge: 1000 * 60 * 15,  // 15 minutes
  },
}));

app.use(passport.initialize());
app.use(passport.session());

// ─────────────────────────────────────────────────────────────────────────────
// SECTION 1: OAuth 2.0 FLOWS EXPLAINED
// ─────────────────────────────────────────────────────────────────────────────

/**
 * AUTHORIZATION CODE FLOW (most secure, for server-side apps)
 * ─────────────────────────────────────────────────────────────
 * Steps:
 *  1. Your app redirects user to auth server with client_id, redirect_uri, scope, state
 *  2. User authenticates and grants permission
 *  3. Auth server redirects back with ?code=AUTH_CODE&state=...
 *  4. Your server exchanges code for tokens (POST to /token endpoint)
 *  5. Auth server returns access_token + refresh_token + id_token(OIDC)
 *
 * The code is short-lived (~10 min) and single-use.
 * Tokens are exchanged server-to-server (client_secret never exposed to browser).
 * This is the ONLY flow to use for new applications.
 */

// Step 1: Redirect user to authorization server
app.get("/auth/authorize", (req, res) => {
  const state = crypto.randomBytes(16).toString("hex"); // CSRF protection
  req.session.oauthState = state;

  const params = new URLSearchParams({
    response_type: "code",
    client_id:     process.env.OAUTH_CLIENT_ID,
    redirect_uri:  process.env.OAUTH_REDIRECT_URI || "http://localhost:3000/auth/callback",
    scope:         "openid profile email",
    state,
    // For PKCE (see Section 2), also add: code_challenge, code_challenge_method
  });

  const authServerUrl = `${process.env.AUTH_SERVER_URL}/authorize?${params}`;
  res.redirect(authServerUrl);
});

// Step 3 + 4: Handle callback and exchange code for tokens
app.get("/auth/callback", async (req, res) => {
  const { code, state, error } = req.query;

  // Validate state to prevent CSRF attacks
  if (!state || state !== req.session.oauthState) {
    return res.status(400).json({ error: "State mismatch — possible CSRF attack" });
  }
  delete req.session.oauthState;

  if (error) {
    return res.status(400).json({ error: `OAuth error: ${error}` });
  }

  try {
    // Exchange authorization code for tokens
    const tokenResponse = await axios.post(`${process.env.AUTH_SERVER_URL}/token`, {
      grant_type:    "authorization_code",
      code,
      redirect_uri:  process.env.OAUTH_REDIRECT_URI,
      client_id:     process.env.OAUTH_CLIENT_ID,
      client_secret: process.env.OAUTH_CLIENT_SECRET,
    }, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    const { access_token, refresh_token, id_token, expires_in } = tokenResponse.data;

    // Store tokens securely
    req.session.accessToken  = access_token;
    req.session.refreshToken = refresh_token; // store in httpOnly cookie or DB
    req.session.tokenExpiry  = Date.now() + (expires_in * 1000);

    // Verify and decode id_token (OIDC)
    if (id_token) {
      const user = jwt.decode(id_token); // In production: verify signature with JWKS
      req.session.user = { id: user.sub, email: user.email, name: user.name };
    }

    res.redirect("/dashboard");
  } catch (err) {
    console.error("Token exchange failed:", err.response?.data || err.message);
    res.status(500).json({ error: "Token exchange failed" });
  }
});


/**
 * CLIENT CREDENTIALS FLOW (for machine-to-machine, no user)
 * ─────────────────────────────────────────────────────────────
 * Used by:
 *  - Background jobs calling APIs
 *  - Microservice-to-microservice calls
 *  - Cron jobs, data pipelines
 *
 * No user is involved. The client authenticates with client_id + client_secret
 * directly to get an access_token. No refresh token (just re-request when expired).
 */

async function getM2MAccessToken() {
  const response = await axios.post(`${process.env.AUTH_SERVER_URL}/token`, {
    grant_type:    "client_credentials",
    client_id:     process.env.OAUTH_CLIENT_ID,
    client_secret: process.env.OAUTH_CLIENT_SECRET,
    scope:         "api:read api:write",
  }, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data.access_token;
}

// Token cache for M2M (avoid re-requesting on every call)
let m2mTokenCache = { token: null, expiresAt: 0 };

async function getCachedM2MToken() {
  if (m2mTokenCache.token && Date.now() < m2mTokenCache.expiresAt - 30_000) {
    return m2mTokenCache.token; // Return cached token with 30s buffer
  }
  const token = await getM2MAccessToken();
  const decoded = jwt.decode(token);
  m2mTokenCache = {
    token,
    expiresAt: decoded.exp ? decoded.exp * 1000 : Date.now() + 3600_000,
  };
  return token;
}

app.get("/internal/data", async (req, res) => {
  const token = await getCachedM2MToken();
  // Use token to call downstream service
  const data = await axios.get("https://api.example.com/data", {
    headers: { Authorization: `Bearer ${token}` },
  });
  res.json(data.data);
});


/**
 * DEVICE CODE FLOW (for devices without browsers: CLI, TV apps, IoT)
 * ─────────────────────────────────────────────────────────────────────
 * Steps:
 *  1. Device requests a device_code and user_code from auth server
 *  2. Device displays user_code and instructs user to visit verification_uri on another device
 *  3. User visits the URI and enters the code (in their browser/phone)
 *  4. Device polls the /token endpoint until user completes auth or timeout
 *
 * Used by: GitHub CLI, AWS CLI, Smart TV apps
 */

async function deviceCodeFlow() {
  // Step 1: Request device code
  const deviceResponse = await axios.post(`${process.env.AUTH_SERVER_URL}/device/code`, {
    client_id: process.env.OAUTH_CLIENT_ID,
    scope:     "openid profile",
  });

  const { device_code, user_code, verification_uri, expires_in, interval } = deviceResponse.data;

  console.log(`\nTo authenticate, visit: ${verification_uri}`);
  console.log(`Enter code: ${user_code}`);
  console.log(`Code expires in ${expires_in} seconds\n`);

  // Step 2: Poll for token
  const pollInterval = (interval || 5) * 1000;
  const expiresAt    = Date.now() + (expires_in * 1000);

  while (Date.now() < expiresAt) {
    await new Promise(resolve => setTimeout(resolve, pollInterval));
    try {
      const tokenResponse = await axios.post(`${process.env.AUTH_SERVER_URL}/token`, {
        grant_type:  "urn:ietf:params:oauth:grant-type:device_code",
        device_code,
        client_id:   process.env.OAUTH_CLIENT_ID,
      });
      console.log("Authentication successful!");
      return tokenResponse.data.access_token;
    } catch (err) {
      const errorCode = err.response?.data?.error;
      if (errorCode === "authorization_pending") {
        process.stdout.write(".");  // User hasn't approved yet
        continue;
      }
      if (errorCode === "slow_down") {
        await new Promise(resolve => setTimeout(resolve, 5000));
        continue;
      }
      throw err; // access_denied, expired_token, etc.
    }
  }
  throw new Error("Device code expired");
}


// ─────────────────────────────────────────────────────────────────────────────
// SECTION 2: PKCE (Proof Key for Code Exchange)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * PKCE prevents authorization code interception attacks.
 * Critical for: Single Page Apps (SPAs), Mobile apps, any public client.
 * Now recommended for ALL Authorization Code flows, even confidential clients.
 *
 * How it works:
 *  1. Client generates a random code_verifier (43-128 chars)
 *  2. Client hashes it: code_challenge = BASE64URL(SHA256(code_verifier))
 *  3. Client sends code_challenge + code_challenge_method="S256" in the auth request
 *  4. Auth server stores the code_challenge
 *  5. During token exchange, client sends code_verifier
 *  6. Auth server verifies: BASE64URL(SHA256(verifier)) === stored challenge
 *
 * Even if an attacker intercepts the code, they can't exchange it without the verifier.
 */

function generateCodeVerifier(length = 64) {
  // Generate a cryptographically secure random string
  return crypto.randomBytes(length).toString("base64url").slice(0, length);
}

function generateCodeChallenge(verifier) {
  return crypto.createHash("sha256").update(verifier).digest("base64url");
}

// PKCE Authorization Code Flow endpoint
app.get("/auth/pkce/start", (req, res) => {
  const codeVerifier  = generateCodeVerifier();
  const codeChallenge = generateCodeChallenge(codeVerifier);
  const state         = crypto.randomBytes(16).toString("hex");

  // Store verifier server-side (or in httpOnly cookie for SPAs)
  req.session.pkceVerifier = codeVerifier;
  req.session.oauthState   = state;

  const params = new URLSearchParams({
    response_type:          "code",
    client_id:              process.env.OAUTH_CLIENT_ID,
    redirect_uri:           process.env.OAUTH_REDIRECT_URI,
    scope:                  "openid profile email",
    state,
    code_challenge:         codeChallenge,
    code_challenge_method:  "S256",
  });

  res.redirect(`${process.env.AUTH_SERVER_URL}/authorize?${params}`);
});

app.get("/auth/pkce/callback", async (req, res) => {
  const { code, state } = req.query;
  const { pkceVerifier, oauthState } = req.session;

  if (state !== oauthState) {
    return res.status(400).json({ error: "State mismatch" });
  }

  try {
    const tokenResponse = await axios.post(`${process.env.AUTH_SERVER_URL}/token`, {
      grant_type:    "authorization_code",
      code,
      redirect_uri:  process.env.OAUTH_REDIRECT_URI,
      client_id:     process.env.OAUTH_CLIENT_ID,
      code_verifier: pkceVerifier,  // <-- PKCE: send verifier, NOT client_secret
      // For public clients: no client_secret needed
    }, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    delete req.session.pkceVerifier;
    req.session.tokens = tokenResponse.data;
    res.json({ success: true, message: "PKCE flow complete" });
  } catch (err) {
    res.status(400).json({ error: err.response?.data || err.message });
  }
});


// ─────────────────────────────────────────────────────────────────────────────
// SECTION 3: OpenID Connect (OIDC)
// ─────────────────────────────────────────────────────────────────────────────

/**
 * OIDC is an identity layer built on top of OAuth 2.0.
 * OAuth 2.0 = Authorization (can this app access your data?)
 * OIDC = Authentication (who is this user?)
 *
 * OIDC adds:
 *  - id_token: a signed JWT with user identity claims (sub, email, name, picture)
 *  - /userinfo endpoint: returns user profile given an access_token
 *  - Discovery document: /.well-known/openid-configuration
 *  - Standard scopes: openid (required), profile, email, address, phone
 *
 * Claims in the id_token:
 *  - sub: unique user identifier (never changes, use as your user ID)
 *  - iss: token issuer URL
 *  - aud: intended audience (your client_id)
 *  - exp: expiry timestamp
 *  - iat: issued at timestamp
 *  - email, name, picture (if profile/email scopes requested)
 */

const { createRemoteJWKSet, jwtVerify } = require("jose").catch(() => null) || {};

async function verifyIdToken(idToken) {
  /**
   * Proper OIDC id_token verification steps:
   * 1. Fetch JWKS (JSON Web Key Set) from provider's discovery document
   * 2. Verify signature using matching public key
   * 3. Verify iss matches expected issuer
   * 4. Verify aud matches your client_id
   * 5. Verify exp is in the future
   * 6. Verify iat is reasonable (not too far in the past)
   */
  try {
    // Using 'jose' library for proper JWT verification
    if (!jwtVerify) {
      // Fallback: just decode (NOT secure — for development only)
      const decoded = jwt.decode(idToken, { complete: true });
      return decoded?.payload;
    }

    const JWKS = createRemoteJWKSet(
      new URL(`${process.env.AUTH_SERVER_URL}/.well-known/jwks.json`)
    );

    const { payload } = await jwtVerify(idToken, JWKS, {
      issuer:   process.env.AUTH_SERVER_URL,
      audience: process.env.OAUTH_CLIENT_ID,
    });

    return payload;
  } catch (err) {
    throw new Error(`Invalid id_token: ${err.message}`);
  }
}

// Fetch user profile from OIDC /userinfo endpoint
async function getUserInfo(accessToken) {
  const response = await axios.get(`${process.env.AUTH_SERVER_URL}/userinfo`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return response.data;
}

// OIDC Discovery document endpoint (if you're building an auth server)
app.get("/.well-known/openid-configuration", (req, res) => {
  const baseUrl = process.env.BASE_URL || "http://localhost:3000";
  res.json({
    issuer:                 baseUrl,
    authorization_endpoint: `${baseUrl}/authorize`,
    token_endpoint:         `${baseUrl}/token`,
    userinfo_endpoint:      `${baseUrl}/userinfo`,
    jwks_uri:               `${baseUrl}/.well-known/jwks.json`,
    response_types_supported: ["code"],
    grant_types_supported:    ["authorization_code", "client_credentials", "refresh_token"],
    subject_types_supported:  ["public"],
    id_token_signing_alg_values_supported: ["RS256"],
    scopes_supported: ["openid", "profile", "email"],
    claims_supported: ["sub", "iss", "aud", "exp", "iat", "email", "name", "picture"],
  });
});


// ─────────────────────────────────────────────────────────────────────────────
// SECTION 4: JWT vs Session vs OAuth Comparison
// ─────────────────────────────────────────────────────────────────────────────

/**
 * JWT (JSON Web Token) based auth:
 *  ✓ Stateless — server doesn't store anything
 *  ✓ Works across microservices and domains
 *  ✓ Contains claims — services can verify without DB lookup
 *  ✗ Cannot revoke instantly (must wait for expiry)
 *  ✗ Payload visible (base64, not encrypted) — never put secrets in JWT
 *  ✗ Token theft is catastrophic until expiry
 *  Use: microservices, stateless APIs, inter-service auth
 *
 * Session based auth:
 *  ✓ Instant revocation (delete session from store)
 *  ✓ Payload hidden (session ID is opaque)
 *  ✗ Requires shared session store (Redis) for multi-instance apps
 *  ✗ Doesn't work easily across domains
 *  Use: traditional web apps, single-domain, when instant revocation is required
 *
 * OAuth 2.0 / OIDC:
 *  ✓ Delegates auth to trusted provider (Google, Auth0, etc.)
 *  ✓ Users don't share passwords with your app
 *  ✓ Standard protocol — audited, battle-tested
 *  ✓ Supports granular scopes for third-party integrations
 *  ✗ Complex to implement correctly from scratch
 *  ✗ Dependency on external provider
 *  Use: social login, third-party API access, enterprise SSO
 *
 * Practical recommendation:
 *  - Internal API auth: JWT with short expiry + refresh token rotation
 *  - User sessions in web app: httpOnly session cookie + Redis
 *  - Third-party integrations: OAuth 2.0 Authorization Code + PKCE
 *  - Enterprise SSO: OIDC (built on OAuth 2.0)
 */


// ─────────────────────────────────────────────────────────────────────────────
// SECTION 5: Passport.js Setup
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Passport.js is authentication middleware for Node.js.
 * "Strategies" handle specific auth methods. 500+ strategies available.
 * Core concepts:
 *  - Strategy: handles one auth method (local, google, github, jwt, etc.)
 *  - serialize/deserialize: how user is stored in session
 *  - authenticate(): the middleware that runs a strategy
 */

// User serialization: what gets stored in the session
passport.serializeUser((user, done) => {
  done(null, user.id);  // Only store user ID in session
});

// User deserialization: how to reconstruct user from session ID
passport.deserializeUser(async (id, done) => {
  try {
    const user = await findUserById(id); // Your DB lookup function
    done(null, user);
  } catch (err) {
    done(err, null);
  }
});

// Mock DB functions
const userStore = new Map();
async function findUserById(id) {
  return userStore.get(id) || null;
}
async function findOrCreateUser(profile) {
  const existing = [...userStore.values()].find(
    u => u.provider === profile.provider && u.providerId === profile.id
  );
  if (existing) return existing;

  const user = {
    id:         crypto.randomUUID(),
    provider:   profile.provider,
    providerId: profile.id,
    email:      profile.emails?.[0]?.value,
    name:       profile.displayName,
    avatar:     profile.photos?.[0]?.value,
    createdAt:  new Date(),
  };
  userStore.set(user.id, user);
  return user;
}


// ─────────────────────────────────────────────────────────────────────────────
// SECTION 6: Social Login — Google, GitHub, Discord
// ─────────────────────────────────────────────────────────────────────────────

// --- Google OAuth 2.0 Strategy ---
// npm install passport-google-oauth20
// Requires: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_CALLBACK_URL

try {
  const { Strategy: GoogleStrategy } = require("passport-google-oauth20");

  passport.use("google", new GoogleStrategy({
    clientID:     process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL:  process.env.GOOGLE_CALLBACK_URL || "http://localhost:3000/auth/google/callback",
    // Request extra scopes
    scope: ["profile", "email"],
    // Get refresh token (requires offline access)
    accessType: "offline",
    prompt: "consent",  // Force consent screen to get refresh token
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // profile contains: id, displayName, emails, photos
      const user = await findOrCreateUser({
        ...profile,
        provider:     "google",
        accessToken,  // store for Google API calls on behalf of user
        refreshToken, // store securely for long-term access
      });
      return done(null, user);
    } catch (err) {
      return done(err, null);
    }
  }));

  // Routes
  app.get("/auth/google", passport.authenticate("google", {
    scope: ["profile", "email"],
    accessType: "offline",
    prompt: "consent",
  }));

  app.get("/auth/google/callback",
    passport.authenticate("google", { failureRedirect: "/login?error=google_failed" }),
    (req, res) => {
      // Successful login
      res.redirect("/dashboard");
    }
  );
} catch (err) {
  console.log("passport-google-oauth20 not installed. Run: npm install passport-google-oauth20");
}


// --- GitHub OAuth Strategy ---
// npm install passport-github2
// Requires: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

try {
  const { Strategy: GitHubStrategy } = require("passport-github2");

  passport.use("github", new GitHubStrategy({
    clientID:     process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    callbackURL:  process.env.GITHUB_CALLBACK_URL || "http://localhost:3000/auth/github/callback",
    scope: ["user:email"],  // Request email access
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // GitHub profile: id, displayName, username, emails, photos, profileUrl
      const user = await findOrCreateUser({ ...profile, provider: "github", accessToken });
      return done(null, user);
    } catch (err) {
      return done(err, null);
    }
  }));

  app.get("/auth/github", passport.authenticate("github"));

  app.get("/auth/github/callback",
    passport.authenticate("github", { failureRedirect: "/login" }),
    (req, res) => res.redirect("/dashboard")
  );
} catch (err) {
  console.log("passport-github2 not installed. Run: npm install passport-github2");
}


// --- Discord OAuth Strategy ---
// npm install passport-discord
// Requires: DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET

try {
  const { Strategy: DiscordStrategy } = require("passport-discord");

  passport.use("discord", new DiscordStrategy({
    clientID:     process.env.DISCORD_CLIENT_ID,
    clientSecret: process.env.DISCORD_CLIENT_SECRET,
    callbackURL:  process.env.DISCORD_CALLBACK_URL || "http://localhost:3000/auth/discord/callback",
    scope:        ["identify", "email", "guilds"],  // Discord-specific scopes
  },
  async (accessToken, refreshToken, profile, done) => {
    try {
      // Discord profile: id, username, discriminator, avatar, email, guilds
      const user = await findOrCreateUser({
        ...profile,
        provider:    "discord",
        displayName: `${profile.username}#${profile.discriminator}`,
        emails:      [{ value: profile.email }],
        photos:      profile.avatar ? [{ value: `https://cdn.discordapp.com/avatars/${profile.id}/${profile.avatar}.png` }] : [],
        accessToken,
        refreshToken,
      });
      return done(null, user);
    } catch (err) {
      return done(err, null);
    }
  }));

  app.get("/auth/discord", passport.authenticate("discord"));

  app.get("/auth/discord/callback",
    passport.authenticate("discord", { failureRedirect: "/login" }),
    (req, res) => res.redirect("/dashboard")
  );
} catch (err) {
  console.log("passport-discord not installed. Run: npm install passport-discord");
}


// ─────────────────────────────────────────────────────────────────────────────
// SECTION 7: Token Refresh and Rotation
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Token Rotation Security Pattern:
 *  - Access tokens: short-lived (15 min). Used for API calls.
 *  - Refresh tokens: long-lived (7-30 days). Used ONLY to get new access tokens.
 *  - Rotation: each refresh creates a NEW refresh token and invalidates the old one.
 *  - This way: if a refresh token is stolen, the legitimate user will detect it
 *    (their valid token gets invalidated on next use by attacker).
 *
 * Refresh Token Storage:
 *  - Server-side web apps: httpOnly, Secure, SameSite=Strict cookie
 *  - SPAs: httpOnly cookie (NOT localStorage — XSS accessible)
 *  - Mobile apps: secure keychain/keystore
 *  - Never: localStorage, sessionStorage, regular cookies (not httpOnly)
 */

// Refresh token store (use Redis/DB in production)
const refreshTokenStore = new Map();
// Map: token → { userId, family, createdAt, used }

function generateTokens(userId) {
  const accessToken = jwt.sign(
    { sub: userId, type: "access" },
    process.env.JWT_SECRET || "dev-secret-change-in-production",
    { expiresIn: "15m" }
  );

  const refreshToken = crypto.randomBytes(40).toString("hex");
  const family = crypto.randomBytes(16).toString("hex"); // Rotation family ID

  refreshTokenStore.set(refreshToken, {
    userId,
    family,
    createdAt: new Date(),
    used: false,
  });

  return { accessToken, refreshToken, expiresIn: 900 };
}

// Middleware to check if access token is expired and silently refresh
async function withTokenRefresh(req, res, next) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) return next();

  try {
    const payload = jwt.verify(
      token,
      process.env.JWT_SECRET || "dev-secret-change-in-production"
    );
    req.user = payload;
    return next();
  } catch (err) {
    if (err.name === "TokenExpiredError") {
      // Try to use refresh token from cookie
      const refreshToken = req.cookies?.refreshToken;
      if (refreshToken) {
        try {
          const newTokens = await rotateRefreshToken(refreshToken);
          // Send new tokens
          res.setHeader("X-New-Access-Token", newTokens.accessToken);
          res.cookie("refreshToken", newTokens.refreshToken, {
            httpOnly: true, secure: true, sameSite: "strict", maxAge: 7 * 24 * 3600 * 1000
          });
          const payload = jwt.verify(
            newTokens.accessToken,
            process.env.JWT_SECRET || "dev-secret-change-in-production"
          );
          req.user = payload;
          return next();
        } catch (refreshErr) {
          // Refresh also failed — clear cookies
          res.clearCookie("refreshToken");
        }
      }
    }
    res.status(401).json({ error: "Unauthorized — please log in again" });
  }
}

async function rotateRefreshToken(oldToken) {
  const tokenData = refreshTokenStore.get(oldToken);

  if (!tokenData) {
    throw new Error("Invalid refresh token");
  }

  // Detect token reuse attack: if token was already used, revoke entire family
  if (tokenData.used) {
    // Someone is using a consumed token → possible token theft
    // Revoke all tokens in this family (both old and new)
    for (const [token, data] of refreshTokenStore.entries()) {
      if (data.family === tokenData.family) {
        refreshTokenStore.delete(token);
      }
    }
    throw new Error("Refresh token reuse detected — all sessions invalidated");
  }

  // Mark old token as used (but keep for detection)
  tokenData.used = true;
  refreshTokenStore.set(oldToken, tokenData);

  // Generate new token pair
  const { accessToken, refreshToken: newRefreshToken } = generateTokens(tokenData.userId);

  // New refresh token inherits the same family
  const newData = refreshTokenStore.get(newRefreshToken);
  newData.family = tokenData.family;
  refreshTokenStore.set(newRefreshToken, newData);

  // Clean up old (used) token after grace period (allow for race conditions)
  setTimeout(() => refreshTokenStore.delete(oldToken), 30_000);

  return { accessToken, refreshToken: newRefreshToken };
}

// Token refresh endpoint
app.post("/auth/refresh", async (req, res) => {
  const refreshToken = req.cookies?.refreshToken || req.body?.refreshToken;

  if (!refreshToken) {
    return res.status(400).json({ error: "Refresh token required" });
  }

  try {
    const tokens = await rotateRefreshToken(refreshToken);

    // Set new refresh token in httpOnly cookie
    res.cookie("refreshToken", tokens.refreshToken, {
      httpOnly: true,
      secure:   process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge:   7 * 24 * 60 * 60 * 1000, // 7 days
      path:     "/auth/refresh", // Only sent to this endpoint
    });

    res.json({
      accessToken: tokens.accessToken,
      expiresIn:   900,
    });
  } catch (err) {
    res.clearCookie("refreshToken");
    res.status(401).json({ error: err.message });
  }
});

// Logout — revoke refresh token
app.post("/auth/logout", (req, res) => {
  const refreshToken = req.cookies?.refreshToken;
  if (refreshToken) {
    refreshTokenStore.delete(refreshToken);
  }
  req.session?.destroy();
  res.clearCookie("refreshToken");
  res.json({ success: true });
});

// Login endpoint that returns tokens
app.post("/auth/login", async (req, res) => {
  const { email, password } = req.body;

  // In production: validate credentials against DB with bcrypt
  // Mock validation here
  if (!email || !password) {
    return res.status(400).json({ error: "Email and password required" });
  }

  const userId = crypto.randomUUID(); // In production: look up from DB
  const tokens = generateTokens(userId);

  res.cookie("refreshToken", tokens.refreshToken, {
    httpOnly: true,
    secure:   process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge:   7 * 24 * 60 * 60 * 1000,
    path:     "/auth",
  });

  res.json({
    accessToken: tokens.accessToken,
    expiresIn:   tokens.expiresIn,
    user: { id: userId, email },
  });
});


// ─────────────────────────────────────────────────────────────────────────────
// PROTECTED ROUTE EXAMPLES
// ─────────────────────────────────────────────────────────────────────────────

function requireAuth(req, res, next) {
  if (req.isAuthenticated()) return next(); // Passport session
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (token) {
    try {
      req.user = jwt.verify(token, process.env.JWT_SECRET || "dev-secret");
      return next();
    } catch (err) {
      return res.status(401).json({ error: "Invalid or expired token" });
    }
  }
  res.status(401).json({ error: "Authentication required" });
}

app.get("/dashboard", requireAuth, (req, res) => {
  res.json({ message: "Welcome to the dashboard", user: req.user });
});

app.get("/profile", requireAuth, (req, res) => {
  res.json({ user: req.user });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`OAuth server running on http://localhost:${PORT}`);
  console.log("Available OAuth routes:");
  console.log("  GET  /auth/authorize        — Standard Authorization Code");
  console.log("  GET  /auth/callback         — OAuth Callback");
  console.log("  GET  /auth/pkce/start       — PKCE Authorization Code");
  console.log("  GET  /auth/pkce/callback    — PKCE Callback");
  console.log("  GET  /auth/google           — Google OAuth");
  console.log("  GET  /auth/github           — GitHub OAuth");
  console.log("  GET  /auth/discord          — Discord OAuth");
  console.log("  POST /auth/login            — Login (JWT)");
  console.log("  POST /auth/refresh          — Refresh Token Rotation");
  console.log("  POST /auth/logout           — Logout");
  console.log("  GET  /.well-known/openid-configuration — OIDC Discovery");
});

module.exports = app;
