# Flask / Django Q&A — Comprehensive

## FLASK BASICS

**Q: What is Flask?**
A: Lightweight Python web framework. "Micro" - gives essentials and lets you add what you need (unlike Django which includes everything). Perfect for APIs and small to medium apps.

**Q: Flask vs Django?**
A: Flask: Lightweight, flexible, explicit, best for REST APIs, microservices, custom architecture.
   Django: Full-stack, batteries included (ORM, admin, auth, forms), opinionated, best for large apps with DB-heavy operations.
   Rule: Flask for APIs, Django for full web applications with complex business logic.

**Q: request.json vs request.args vs request.form?**
A: `request.json`: JSON body (Content-Type: application/json)
   `request.args`: Query string (`?key=value`)
   `request.form`: HTML form data (multipart/form-data)
   `request.data`: Raw bytes
   `request.headers`: HTTP headers

**Q: What is jsonify()?**
A: Converts Python dict to JSON HTTP response with `Content-Type: application/json`. Always use jsonify() not json.dumps() in routes.

**Q: What are status codes and when to use them?**
A: 200 OK (GET success), 201 Created (POST creates resource), 204 No Content (DELETE success),
   400 Bad Request (invalid data), 401 Unauthorized (not authenticated), 403 Forbidden (authenticated but no permission),
   404 Not Found, 409 Conflict (duplicate), 422 Unprocessable (validation failed), 500 Server Error

**Q: What is abort()?**
A: Immediately stops request and returns HTTP error: `abort(404)` → 404 response. Like `raise` but for HTTP errors.

**Q: How to define error handlers?**
A: ```python
   @app.errorhandler(404)
   def not_found(e):
       return jsonify({'error': 'Not found'}), 404

   @app.errorhandler(Exception)
   def handle_all(e):
       return jsonify({'error': str(e)}), 500
   ```

**Q: What is the g object?**
A: Request-scoped global storage. Lives for duration of single request. Used to store user, db connections per request.
   ```python
   @app.before_request
   def load_user():
       g.user = get_current_user()
   ```

**Q: What is current_app?**
A: Proxy to the current Flask app instance. Used inside app context (useful in extensions and blueprints).

---

## APP FACTORY & BLUEPRINTS

**Q: What is the App Factory pattern?**
A: Wrap app creation in `create_app()` function. Benefits:
   1. Easy testing (fresh app per test)
   2. Avoid circular imports
   3. Multiple app instances
   ```python
   def create_app(config=None):
       app = Flask(__name__)
       db.init_app(app)
       app.register_blueprint(users_bp, url_prefix='/api/users')
       return app
   ```

**Q: What is a Blueprint?**
A: Mini-app organizing related routes. Registered on main app with URL prefix:
   ```python
   users_bp = Blueprint('users', __name__)

   @users_bp.route('/')
   def get_all_users():
       ...

   app.register_blueprint(users_bp, url_prefix='/api/v1/users')
   ```

**Q: When to split into multiple blueprints?**
A: - Large routers (> 10 routes)
   - Different functional areas (users, products, orders, auth)
   - Different URL prefixes (/admin, /api, /auth)

---

## FLASK-SQLALCHEMY (ORM)

**Q: What is an ORM?**
A: Object Relational Mapper. Maps Python classes to database tables. Work with Python objects instead of raw SQL.

**Q: How to define models?**
A: ```python
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(120), unique=True, nullable=False)
       name = db.Column(db.String(80))
       posts = db.relationship('Post', backref='author', lazy=True)
   ```

**Q: What is lazy loading in relationships?**
A: lazy=True: Load related objects when accessed (default, causes N+1 problem)
   lazy='joined': JOIN query immediately
   lazy='subquery': Separate query for all related objects
   lazy='dynamic': Returns query builder instead of list

**Q: What is session in SQLAlchemy?**
A: Unit of work. Tracks objects you want to save. Must commit to persist, rollback to undo:
   ```python
   db.session.add(user)       # Queue for insert
   db.session.commit()        # Persist to DB
   db.session.rollback()      # Undo changes
   db.session.delete(user)    # Queue for delete
   ```

**Q: How to query?**
A: ```python
   User.query.all()                          # All users
   User.query.get(1)                         # By primary key
   User.query.filter_by(email=email).first() # First match
   User.query.filter(User.age > 18).all()    # Filter expression
   User.query.order_by(User.name).limit(10)  # Sort + limit
   ```

**Q: What is N+1 problem in SQLAlchemy?**
A: Accessing relationship causes 1 query per object:
   ```python
   posts = Post.query.all()
   for post in posts:
       print(post.author.name)  # 1 query per post = N+1!
   ```
   Fix: Use `joinedload`:
   ```python
   posts = Post.query.options(joinedload(Post.author)).all()
   ```

---

## JWT AUTHENTICATION

**Q: What is JWT?**
A: JSON Web Token. Signed string proving identity: `header.payload.signature`. Server creates on login, client sends in every request header.

**Q: JWT structure?**
A: `eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiMSJ9.signature`
   header (algo) . payload (claims) . HMAC signature

**Q: Why are access tokens short-lived?**
A: If stolen, it only works for short time. Long-lived refresh tokens are stored securely (httpOnly cookie) to get new access tokens.

**Q: @jwt_required() decorator?**
A: Reads `Authorization: Bearer <token>` header, verifies signature, returns 401 if missing/invalid. Inside route, use `get_jwt_identity()` to get user ID.

**Q: Access token vs refresh token?**
A: Access: Short-lived (15min), in Memory/header, used for API requests.
   Refresh: Long-lived (7 days), httpOnly cookie, used only to get new access token.

**Q: How to revoke JWT?**
A: JWTs are stateless by design - can't be revoked.
   Solutions: 1) Blacklist in Redis (check every request). 2) Short expiry. 3) Use sessions instead.

---

## FLASK TESTING

**Q: How to test Flask routes?**
A: Use `app.test_client()`:
   ```python
   def test_login(client):
       res = client.post('/auth/login', json={'email': 'test@test.com', 'password': 'pass'})
       assert res.status_code == 200
       assert 'access_token' in res.get_json()
   ```

**Q: What is the test fixture pattern?**
A: ```python
   @pytest.fixture
   def app():
       app = create_app({'TESTING': True, 'DATABASE_URI': 'sqlite:///:memory:'})
       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()

   @pytest.fixture
   def client(app):
       return app.test_client()
   ```

**Q: How to test with authentication?**
A: ```python
   def test_protected(client, auth_token):
       res = client.get('/profile', headers={'Authorization': f'Bearer {auth_token}'})
       assert res.status_code == 200
   ```

---

## FLASK ADVANCED

**Q: What is a Flask context?**
A: Application context (app ctx) and Request context (req ctx).
   App ctx: `current_app`, `g`. Active when processing request.
   Request ctx: `request`, `session`. Active during request handling.

**Q: What is @app.before_request and @app.after_request?**
A: ```python
   @app.before_request
   def check_auth():
       # Runs before EVERY request
       g.user = verify_token(request.headers.get('Authorization'))

   @app.after_request
   def add_cors_headers(response):
       # Runs after EVERY request
       response.headers['Access-Control-Allow-Origin'] = '*'
       return response
   ```

**Q: Flask-Migrate?**
A: Handles database schema migrations with Alembic. Commands:
   ```bash
   flask db init       # Initialize migration dir
   flask db migrate    # Detect model changes, create migration script
   flask db upgrade    # Apply pending migrations
   flask db downgrade  # Revert migration
   ```

**Q: How to handle async in Flask?**
A: Flask 2.0+ supports async routes: `async def`. But Flask is wsgi-based, not as efficient as FastAPI/aiohttp for high async concurrency.

**Q: Flask-SocketIO?**
A: Add WebSocket support to Flask:
   ```python
   from flask_socketio import SocketIO, emit
   socketio = SocketIO(app, cors_allowed_origins="*")

   @socketio.on('message')
   def handle_message(data):
       emit('response', {'data': 'Got it!'}, broadcast=True)
   ```

**Q: Rate limiting in Flask?**
A: Use flask-limiter:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(get_remote_address, app=app, default_limits=['100/hour'])

   @app.route('/api/login')
   @limiter.limit('5 per minute')  # Extra strict for login
   def login():
       ...
   ```

---

## DJANGO

**Q: Django vs Flask?**
A: Django: Full-stack framework, batteries included (ORM, admin, auth, forms). Best for large data-heavy apps.
   Flask: Minimal, flexible, explicit. Best for REST APIs, microservices.

**Q: Django ORM vs SQLAlchemy?**
A: Django ORM: Simpler, built into Django, less flexible, tighter coupling.
   SQLAlchemy: More powerful, flexible, can use standalone, better for complex queries.

**Q: What is Django's admin?**
A: Auto-generated web interface for managing database records. Register models and get CRUD interface immediately.

**Q: Django signals?**
A: Post-save/pre-save hooks for decoupled logic:
   ```python
   @receiver(post_save, sender=User)
   def send_welcome_email(sender, instance, created, **kwargs):
       if created:
           send_email(instance.email, 'Welcome!')
   ```

**Q: Django REST Framework (DRF)?**
A: Toolkit for building REST APIs in Django. Serializers (like Pydantic), ViewSets (auto CRUD), Permissions, Authentication.

**Q: What is Django's select_related vs prefetch_related?**
A: `select_related`: SQL JOIN. For ForeignKey/OneToOne (1-to-1 or many-to-1).
   `prefetch_related`: Separate query. For ManyToMany or reverse ForeignKey.
   Both solve N+1 problem.

---

## TRICKY QUESTIONS

**Q: Flask circular import problem?**
A: Common when extensions (db, jwt) are imported between modules. Fix: Use app factory pattern, initialize extensions separately, import inside functions.

**Q: What happens if you forget `db.session.commit()`?**
A: Changes are lost when the request ends. SQLAlchemy rolls back uncommitted changes automatically.

**Q: Flask thread safety?**
A: Each Flask request runs in its own thread. `current_app`, `request`, `g` are thread-local proxies - safe across threads.

**Q: What is WSGI?**
A: Web Server Gateway Interface. Interface between Python web frameworks and web servers (Gunicorn, uWSGI). Flask is WSGI-based, FastAPI is ASGI-based (async).

**Q: How to deploy Flask in production?**
A: Don't use Flask's built-in dev server! Use Gunicorn + Nginx:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
   ```
   4 worker processes, binds to port 8000.

**Q: Flask `debug=True` in production?**
A: NEVER! Shows full stack traces including source code. Enables interactive debugger (allows RCE). Always `debug=False` in production.
