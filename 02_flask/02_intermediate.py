# ============================================================
# FLASK INTERMEDIATE — App Factory + Blueprints + SQLAlchemy
# ============================================================
# pip install flask flask-sqlalchemy

# ── APP FACTORY PATTERN ───────────────────────────────────────
# Instead of creating app globally, wrap it in a function.
# Benefit: easier testing (create fresh app per test) + avoids circular imports

# In a real project, structure would be:
# app/
#   __init__.py      ← create_app() lives here
#   models.py        ← SQLAlchemy models
#   routes/
#     users.py       ← Blueprint for users
#     cases.py       ← Blueprint for cases
#   config.py        ← Config classes

from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()   # initialize without app — attach later

def create_app(config=None):
    app = Flask(__name__)

    # Configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "dev-secret-key"

    if config:
        app.config.update(config)

    # Initialize extensions with app
    db.init_app(app)

    # Register blueprints
    from flask import Blueprint  # import here to avoid circular imports

    # Register the users blueprint
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")

    # Create tables
    with app.app_context():
        db.create_all()

    return app


# ── BLUEPRINTS ────────────────────────────────────────────────
# Blueprints = mini-apps that organise routes into separate files

from flask import Blueprint
users_bp = Blueprint("users", __name__)


# ── SQLALCHEMY MODELS ─────────────────────────────────────────
class User(db.Model):
    __tablename__ = "users"

    id    = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True)

    # Relationship — one user has many posts
    posts = db.relationship("Post", back_populates="author", lazy="dynamic")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}

    def __repr__(self):
        return f"<User {self.email}>"


class Post(db.Model):
    __tablename__ = "posts"

    id        = db.Column(db.Integer, primary_key=True)
    title     = db.Column(db.String(200), nullable=False)
    body      = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    author = db.relationship("User", back_populates="posts")


# ── BLUEPRINT ROUTES ──────────────────────────────────────────
@users_bp.route("/", methods=["GET"])
def get_users():
    users = User.query.filter_by(active=True).all()
    return jsonify({"users": [u.to_dict() for u in users]})


@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@users_bp.route("/", methods=["POST"])
def create_user():
    data = request.json
    if not data or not data.get("email"):
        abort(400)

    # Check for duplicate email
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already exists"}), 409

    user = User(name=data.get("name", ""), email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.name  = data.get("name", user.name)
    user.email = data.get("email", user.email)
    db.session.commit()
    return jsonify(user.to_dict())


@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


# ── QUERYING ──────────────────────────────────────────────────
def query_examples():
    # Get all users
    all_users = User.query.all()

    # Filter
    active = User.query.filter_by(active=True).all()

    # Filter with comparison
    users = User.query.filter(User.id > 5).all()

    # Find by primary key
    user = User.query.get(1)           # returns None if not found
    user = User.query.get_or_404(1)    # returns 404 if not found

    # First match
    user = User.query.filter_by(email="x@y.com").first()

    # Count
    count = User.query.filter_by(active=True).count()

    # Order
    users = User.query.order_by(User.name.asc()).all()

    # Pagination
    page = User.query.paginate(page=1, per_page=10)


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
