# Flask — Advanced Q&A, Edge Cases & Production Patterns

---

## MIDDLEWARE AND REQUEST LIFECYCLE

**Q: What is the order of operations when a Flask request comes in?**
A:
1. `before_request` hooks run (auth checks, DB connections)
2. Route matched → view function executes
3. `after_request` hooks run (add CORS headers, log response)
4. `teardown_request` hooks run (cleanup, even on exception)
5. Response sent to client

```python
@app.before_request
def check_auth():
    if request.path.startswith("/api/") and not request.headers.get("Authorization"):
        return jsonify({"error": "Unauthorized"}), 401

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.teardown_request
def close_db(error=None):
    db_session = g.pop("db", None)
    if db_session:
        db_session.close()
```

---

**Q: What is Flask's `g` object?**
A: `g` (global) is a request-scoped storage object — it lives only for the duration of a single request. Use it to store resources you want to reuse within a request (e.g., DB connection, current user).
```python
from flask import g

@app.before_request
def load_user():
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        g.user = verify_token(token)  # store decoded user for this request

@app.route("/profile")
def profile():
    return jsonify(g.user)  # access the stored user
```

---

## SQLALCHEMY ADVANCED

**Q: What is lazy loading vs eager loading?**
A:
- `lazy="dynamic"` — relationship not loaded until accessed. Each access hits DB.
- `lazy="select"` (default) — loaded when first accessed (one extra SELECT)
- `lazy="joined"` / `lazy="subquery"` — loaded eagerly in same/second query
- Use `options(joinedload(...))` on individual queries to eager load when needed

```python
# N+1 problem — BAD
posts = Post.query.all()
for post in posts:
    print(post.author.name)  # one SELECT per post → N+1 queries!

# Fix with eager loading
from sqlalchemy.orm import joinedload
posts = Post.query.options(joinedload(Post.author)).all()
# One query with JOIN → no N+1
```

---

**Q: What is the N+1 query problem?**
A: If you have 100 posts and get each post's author separately, you execute 1 (get posts) + 100 (get each author) = 101 queries. Fix with `joinedload` or `subqueryload` to load all data in 1-2 queries.

---

**Q: How do you run migrations in Flask-SQLAlchemy?**
A: Use `Flask-Migrate` (wraps Alembic):
```bash
flask db init       # create migrations folder
flask db migrate -m "add users table"   # detect changes, create migration
flask db upgrade    # apply migrations
flask db downgrade  # rollback
```
This tracks schema changes in version files — safe for production.

---

## JWT EDGE CASES

**Q: How would you blacklist/revoke a JWT?**
A: JWTs are stateless — you can't revoke them by default. Strategies:
1. **Short expiry** — 15 min access tokens. Stolen token expires fast.
2. **Blocklist** — store revoked JWT IDs (jti) in Redis. Check on every request.
3. **Version number** — store `token_version` in DB. Increment on logout. Token's version must match DB.

```python
# flask-jwt-extended has blocklist support
from flask_jwt_extended import get_jwt

BLOCKLIST = set()   # use Redis in production

@jwt.token_in_blocklist_loader
def check_if_revoked(jwt_header, jwt_data):
    return jwt_data["jti"] in BLOCKLIST   # jti = JWT ID (unique per token)

@app.route("/logout", methods=["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    BLOCKLIST.add(jti)       # block this specific token
    return jsonify({"message": "Logged out"})
```

---

**Q: What is the difference between `@jwt_required()` and `@jwt_required(optional=True)`?**
A:
- `@jwt_required()` — must have valid token. Returns 401 if missing/invalid.
- `@jwt_required(optional=True)` — works with or without token. `get_jwt_identity()` returns `None` if no token. Use for routes that show different content to authenticated vs anonymous users.

---

## FLASK TESTING

**Q: How do you write tests for a Flask API?**
```python
import pytest
from app import create_app   # app factory

@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_get_users(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data

def test_create_user(client):
    response = client.post("/api/v1/users",
        json={"name": "Chaman", "email": "c@test.com"},
        content_type="application/json"
    )
    assert response.status_code == 201
    assert response.get_json()["email"] == "c@test.com"

def test_create_user_missing_email(client):
    response = client.post("/api/v1/users", json={"name": "Chaman"})
    assert response.status_code == 400
```

---

## FLASK IN PRODUCTION

**Q: What is Gunicorn and why do you need it?**
A: Flask's built-in server (`app.run()`) is single-threaded and not production-safe. Gunicorn is a WSGI server that:
- Runs multiple worker processes (4 workers = 4 concurrent requests)
- Handles worker crashes and restarts
- Plays well with Nginx reverse proxy

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
# -w 4 → 4 worker processes
# -b → bind address
```

---

**Q: What is the difference between WSGI and ASGI?**
A:
- **WSGI** (synchronous) — Flask, Django. One request at a time per worker.
- **ASGI** (asynchronous) — FastAPI, Starlette. Handles many concurrent requests in one process using async/await. Better for real-time, WebSocket, high I/O concurrency.

---

**Q: How do you handle file uploads in Flask?**
```python
from flask import request
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = "/tmp/uploads"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    filename = secure_filename(file.filename)  # ALWAYS sanitize filename!
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return jsonify({"message": "Uploaded", "filename": filename}), 201
```

---

## CONFIGURATION PATTERNS

**Q: How do you manage config for different environments (dev/test/prod)?**
```python
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-default")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]   # must be set

config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
}

def create_app():
    app = Flask(__name__)
    env = os.environ.get("FLASK_ENV", "development")
    app.config.from_object(config_map[env])
    return app
```

---

## COMMON FLASK INTERVIEW TRAPS

**Q: What is `current_app` and when do you use it?**
A: A proxy to the active Flask app. Use it inside blueprints, extensions, or helper functions where you don't have direct access to the `app` object: `current_app.config["SECRET_KEY"]`.

**Q: What is the application context vs request context?**
A:
- **Application context** — active whenever the app is processing anything. `current_app`, `g`. Created by `app.app_context()`.
- **Request context** — active during an HTTP request. `request`, `session`. Created automatically on each request.

**Q: When would you use `abort()` vs returning an error response?**
A: Use `abort()` when you want to immediately exit anywhere in a nested call stack — it raises an HTTP exception that bubbles up. Use `return jsonify({"error": ...}), 400` in your route function for normal validation errors.
