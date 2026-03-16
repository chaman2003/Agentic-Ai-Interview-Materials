# ============================================================
# FLASK BASICS — Interview Essentials
# ============================================================
# pip install flask

from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# ── BASIC ROUTES ─────────────────────────────────────────────
# HTTP methods: GET(read), POST(create), PUT(replace), PATCH(update), DELETE(remove)

@app.route("/")
def home():
    return jsonify({"message": "API is running"})


# GET — fetch data
@app.route("/users", methods=["GET"])
def get_users():
    users = [
        {"id": 1, "name": "Chaman", "email": "chaman@example.com"},
        {"id": 2, "name": "Alice",  "email": "alice@example.com"},
    ]
    return jsonify({"users": users})   # 200 OK (default)


# GET with URL parameter (:id in the URL)
@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # Simulate finding user
    if user_id == 1:
        return jsonify({"id": 1, "name": "Chaman"})
    abort(404)   # immediately return 404 from anywhere


# GET with query parameters (?page=2&limit=10)
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")           # ?q=python
    page  = request.args.get("page", 1, type=int)  # ?page=2
    return jsonify({"query": query, "page": page})


# POST — create new resource
@app.route("/users", methods=["POST"])
def create_user():
    data = request.json   # parse JSON body from request
    if not data:
        return jsonify({"error": "No data provided"}), 400

    name  = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    # Normally you'd save to DB here
    new_user = {"id": 3, "name": name, "email": email}
    return jsonify(new_user), 201   # 201 Created


# PUT — replace entire resource
@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.json
    return jsonify({"id": user_id, "name": data.get("name"), "email": data.get("email")})


# PATCH — update part of resource
@app.route("/users/<int:user_id>", methods=["PATCH"])
def patch_user(user_id):
    data = request.json
    # Only update fields that were provided
    return jsonify({"id": user_id, "updated_fields": list(data.keys())})


# DELETE — remove resource
@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    return jsonify({"message": f"User {user_id} deleted"}), 200   # or 204 No Content


# ── request OBJECT ────────────────────────────────────────────
# request.json      — JSON body (Content-Type: application/json)
# request.form      — form data (Content-Type: multipart/form-data)
# request.args      — query string params (?key=value)
# request.headers   — HTTP headers
# request.method    — GET, POST, etc.
# request.files     — uploaded files


# ── STATUS CODES ─────────────────────────────────────────────
# 200 OK            — success (GET, PUT, PATCH)
# 201 Created       — resource created (POST)
# 204 No Content    — success but no body (DELETE)
# 400 Bad Request   — client sent invalid data
# 401 Unauthorized  — not logged in
# 403 Forbidden     — logged in but no permission
# 404 Not Found     — resource doesn't exist
# 409 Conflict      — resource already exists (duplicate email)
# 422 Unprocessable — validation failed
# 429 Too Many      — rate limit exceeded
# 500 Server Error  — bug on server side


# ── ERROR HANDLERS ────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found", "code": 404}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad request", "code": 400}), 400

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "code": 500}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
