# ============================================================
# FLASK JWT AUTH — Interview Essentials
# ============================================================
# pip install flask flask-jwt-extended

from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from datetime import timedelta

app = Flask(__name__)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = "super-secret-key"   # use env var in production
app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = timedelta(minutes=15)  # short-lived
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)      # long-lived

jwt = JWTManager(app)

# ── MOCK USERS (normally stored in DB) ───────────────────────
users_db = {
    "chaman@example.com": {
        "id": 1,
        "name": "Chaman",
        "password": "hashed_password_here"  # in real app: bcrypt hash
    }
}

# ── HOW JWT WORKS ─────────────────────────────────────────────
# 1. User logs in with email + password
# 2. Server validates credentials
# 3. Server creates a signed JWT token → sends to client
# 4. Client stores token (localStorage or httpOnly cookie)
# 5. Client sends token on every request: "Authorization: Bearer <token>"
# 6. Server verifies token with @jwt_required() decorator
# 7. Server reads user identity with get_jwt_identity()

# JWT Structure: header.payload.signature
# - header: algorithm type (HS256)
# - payload: claims (user id, expiry, custom data) — NOT encrypted, don't put passwords!
# - signature: proves token wasn't tampered with

# ── REGISTER ─────────────────────────────────────────────────
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    email    = data.get("email")
    password = data.get("password")
    name     = data.get("name")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    if email in users_db:
        return jsonify({"error": "Email already registered"}), 409

    # In real app: hash password with bcrypt
    # from werkzeug.security import generate_password_hash
    # hashed = generate_password_hash(password)

    users_db[email] = {"id": len(users_db) + 1, "name": name, "password": password}
    return jsonify({"message": "Registered successfully"}), 201


# ── LOGIN ─────────────────────────────────────────────────────
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email    = data.get("email")
    password = data.get("password")

    user = users_db.get(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # In real app: check with bcrypt
    # from werkzeug.security import check_password_hash
    # if not check_password_hash(user["password"], password):
    if user["password"] != password:
        return jsonify({"error": "Invalid password"}), 401

    # Create tokens
    identity = str(user["id"])   # must be a string
    access_token  = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return jsonify({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user": {"id": user["id"], "name": user["name"]}
    })


# ── PROTECTED ROUTE ───────────────────────────────────────────
# @jwt_required() reads Authorization header: "Bearer <token>"
# If token is missing or invalid → 401 Unauthorized automatically
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()   # gets the 'identity' from token
    return jsonify({"user_id": user_id, "message": "This is protected data"})


# ── REFRESH TOKEN ─────────────────────────────────────────────
# When access token expires (15 min), use refresh token to get new one
@app.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)   # requires refresh token, not access token
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access_token})


# ── OPTIONAL AUTH ─────────────────────────────────────────────
@app.route("/public", methods=["GET"])
@jwt_required(optional=True)   # works with or without token
def public():
    user_id = get_jwt_identity()   # None if no token
    if user_id:
        return jsonify({"message": f"Hello user {user_id}"})
    return jsonify({"message": "Hello anonymous visitor"})


# ── JWT ERROR HANDLERS ────────────────────────────────────────
@jwt.expired_token_loader
def expired_token(jwt_header, jwt_data):
    return jsonify({"error": "Token has expired"}), 401

@jwt.invalid_token_loader
def invalid_token(error):
    return jsonify({"error": "Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token(error):
    return jsonify({"error": "Authorization token required"}), 401


if __name__ == "__main__":
    app.run(debug=True)
