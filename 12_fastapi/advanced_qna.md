# FastAPI — Advanced Q&A & Patterns

---

## WEBSOCKETS IN FASTAPI

WebSockets provide full-duplex communication over a single TCP connection. FastAPI has built-in support via `WebSocket` and `WebSocketDisconnect`.

**Q: How do you implement a basic WebSocket endpoint in FastAPI?**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo [{client_id}]: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
```

**Q: How do you implement a broadcast chat server with connection management?**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def send_personal(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/chat/{room_id}")
async def chat_endpoint(websocket: WebSocket, room_id: str, username: str):
    await manager.connect(websocket)
    await manager.broadcast(f"[{room_id}] {username} joined the chat")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"[{room_id}] {username}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"[{room_id}] {username} left the chat")
```

**Q: How do you authenticate WebSocket connections (JWT over WS)?**
```python
from fastapi import WebSocket, Query, HTTPException, status
from jose import jwt, JWTError

async def get_ws_user(token: str = Query(...)):
    """Dependency for WebSocket auth via query param."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=403)
        return user_id
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.websocket("/ws/secure")
async def secure_ws(websocket: WebSocket, token: str = Query(...)):
    # Must validate before accept() — reject at handshake
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        await websocket.close(code=1008)  # Policy Violation
        return
    await websocket.accept()
    await websocket.send_json({"status": "authenticated", "user": user_id})
    # ... rest of handler
```

**Key WS Interview Points:**
- WS connections bypass HTTP middleware — authenticate at handshake via query param or cookie
- `receive_text()` / `receive_json()` / `send_text()` / `send_json()` are the core primitives
- Use `WebSocketDisconnect` exception to detect client disconnections
- For rooms/channels at scale, use Redis pub/sub as a message broker between server instances

---

## FILE UPLOADS

**Q: How do you handle file uploads in FastAPI?**
```python
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pathlib import Path
import aiofiles
import uuid

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload/single")
async def upload_single(file: UploadFile = File(...)):
    # Validate content type
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(400, detail="File type not allowed")

    # Read and check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, detail="File too large")

    # Save with unique name
    filename = f"{uuid.uuid4()}_{file.filename}"
    filepath = UPLOAD_DIR / filename
    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return {"filename": filename, "size": len(content), "content_type": file.content_type}

@app.post("/upload/multiple")
async def upload_multiple(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        content = await file.read()
        results.append({"filename": file.filename, "size": len(content)})
    return results

@app.post("/upload/with-metadata")
async def upload_with_form(
    file: UploadFile = File(...),
    description: str = Form(...),        # Form fields alongside file
    category: str = Form("general"),
):
    return {"filename": file.filename, "description": description, "category": category}
```

**Interview trap:** `UploadFile.read()` is async — always `await` it. The file is a SpooledTemporaryFile — small files stay in memory, large ones spill to disk. After `read()`, seek back with `await file.seek(0)` if you need to read again.

---

## BACKGROUND TASKS DEEP DIVE

**Q: What are FastAPI BackgroundTasks and when should you use them?**
```python
from fastapi import BackgroundTasks, Depends
import smtplib

def send_welcome_email(email: str, username: str):
    """Runs after HTTP response is sent. Don't use await here."""
    # This runs synchronously in a thread pool
    print(f"Sending welcome email to {email}")
    # ... smtplib logic

async def update_audit_log(user_id: int, action: str):
    """Async background tasks are also supported."""
    await some_db_write(user_id, action)

@app.post("/register")
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    db_user = await create_user(db, user)
    # Schedule tasks — runs AFTER response is returned to client
    background_tasks.add_task(send_welcome_email, user.email, user.username)
    background_tasks.add_task(update_audit_log, db_user.id, "register")
    return {"id": db_user.id, "status": "created"}
```

**BackgroundTasks vs Celery comparison:**

| Feature | BackgroundTasks | Celery |
|---------|----------------|--------|
| Setup | Zero — built-in | Redis/RabbitMQ broker required |
| Persistence | No — lost on crash | Yes — tasks survive restarts |
| Retry logic | No | Yes — configurable retries |
| Monitoring | No | Flower dashboard |
| Distributed | No — single process | Yes — multiple workers |
| Use case | Short, non-critical tasks | Long jobs, guaranteed delivery |

**Rule of thumb:** Use `BackgroundTasks` for things like sending notifications, logging audit events. Use Celery for sending reports, image processing, tasks that must not be lost.

---

## ALEMBIC MIGRATIONS

**Q: What is the full Alembic migration workflow with FastAPI/SQLAlchemy?**

```bash
# 1. Install
pip install alembic sqlalchemy

# 2. Initialize alembic in project root
alembic init alembic

# 3. Edit alembic.ini — set sqlalchemy.url
# sqlalchemy.url = postgresql+psycopg2://user:pass@localhost/mydb

# 4. Edit alembic/env.py to point at your models' metadata
```

```python
# alembic/env.py — key section
from app.database import Base   # Import your Base with all models loaded
from app import models          # Ensure all models are imported so metadata is populated

target_metadata = Base.metadata  # Autogenerate compares this to actual DB state
```

```bash
# 5. Generate a migration (autogenerate compares models to DB)
alembic revision --autogenerate -m "add users table"

# 6. Review the generated migration in alembic/versions/
# ALWAYS review autogenerated migrations — they miss some changes (e.g., check constraints)

# 7. Apply migration
alembic upgrade head

# 8. Rollback one step
alembic downgrade -1

# 9. View migration history
alembic history --verbose

# 10. Show current applied revision
alembic current
```

```python
# Typical migration file structure
def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

def downgrade() -> None:
    op.drop_table('users')
```

**Interview trap:** Alembic autogenerate does NOT detect: renamed tables/columns (sees drop+add), check constraints (database-level), stored procedures, partial indexes. Always review generated migrations manually.

---

## TESTING FASTAPI

**Q: How do you write unit and integration tests for FastAPI?**
```python
# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the DB dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_user():
    response = client.post("/users", json={"email": "test@example.com", "name": "Alice"})
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"

def test_duplicate_user_returns_409():
    client.post("/users", json={"email": "same@example.com", "name": "Alice"})
    response = client.post("/users", json={"email": "same@example.com", "name": "Bob"})
    assert response.status_code == 409
```

**Q: How do you test async FastAPI endpoints with pytest-asyncio?**
```python
import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-endpoint")
    assert response.status_code == 200

# Override auth dependency for testing
def mock_get_current_user():
    return {"id": 1, "email": "admin@test.com", "role": "admin"}

@pytest.fixture
def authenticated_client():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield TestClient(app)
    app.dependency_overrides.clear()
```

**Key testing concepts:**
- `TestClient` wraps the ASGI app with `requests` — no server needed
- `dependency_overrides` is the key mechanism for mocking auth, DB, external services
- Use `httpx.AsyncClient` for testing async endpoints properly with `pytest-asyncio`
- Always clear `dependency_overrides` after tests to avoid cross-test pollution

---

## FASTAPI vs FLASK vs DJANGO

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| Async support | Native (async/await) | Limited (via asyncio) | Partial (ASGI with Django 3.1+) |
| Performance | Very high (Starlette/uvicorn) | Moderate | Moderate |
| Data validation | Pydantic (built-in) | Manual or marshmallow | DRF serializers |
| Auto docs | Swagger + ReDoc built-in | Flask-RESTX/Flasgger | DRF browsable API |
| ORM | Any (SQLAlchemy recommended) | Any | Django ORM (built-in) |
| Admin panel | No | Flask-Admin (plugin) | Built-in Django Admin |
| Auth | Manual or FastAPI-Users | Flask-Login | Built-in auth system |
| Learning curve | Low-medium | Low | Medium-high |
| Best for | Modern APIs, ML serving, microservices | Simple APIs, prototypes | Full-stack web, content sites |
| Type safety | Excellent (Pydantic) | Optional | Moderate |
| Maturity | 2018 | 2010 | 2005 |

**When to choose FastAPI:** High-throughput APIs, ML model serving, LangChain/AI integrations, microservices that need clear schema contracts, teams that prefer type hints.

**When to choose Django:** Projects needing admin panel, complex user/permissions systems, CMS-like applications, teams familiar with Django ecosystem.

**When to choose Flask:** Rapid prototypes, simple REST APIs with minimal overhead, embedding in existing Python apps.

---

## DEPENDENCY INJECTION PATTERNS

**Q: How does FastAPI's dependency injection work at depth?**
```python
from fastapi import Depends, Header, HTTPException
from functools import lru_cache

# 1. Simple dependency
def get_settings():
    return Settings()  # Reads from env vars

# 2. Cached dependency (singleton pattern)
@lru_cache()
def get_cached_settings():
    return Settings()  # Created once, reused

# 3. Dependency with parameters using closures
def require_role(role: str):
    async def checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(403, f"Requires {role} role")
        return current_user
    return checker

@app.delete("/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(require_role("admin"))   # Parameterized dependency
):
    ...

# 4. Class-based dependencies (for shared state)
class PaginationParams:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = min(skip, 0)
        self.limit = min(limit, 100)

@app.get("/items")
async def list_items(pagination: PaginationParams = Depends()):
    return db.query(Item).offset(pagination.skip).limit(pagination.limit).all()

# 5. Dependency chains
async def get_db() -> AsyncSession: ...

async def get_current_user(
    token: str = Depends(oauth2_scheme),   # Depends on token extraction
    db: AsyncSession = Depends(get_db)     # Depends on DB session
) -> User: ...

@app.get("/profile")
async def get_profile(
    user: User = Depends(get_current_user)  # Chains get_db + oauth2 automatically
): ...
```

**Interview trap:** FastAPI shares dependency instances within the same request but creates new instances per request by default. Use `use_cache=False` in `Depends(get_db, use_cache=False)` to force a new instance.

---

## PERFORMANCE

**Q: What makes FastAPI fast and how do you optimize it further?**

**Async I/O — never block the event loop:**
```python
# BAD — blocks event loop for entire duration of DB call
@app.get("/users")
async def get_users():
    import time
    time.sleep(2)  # Blocks ALL other requests!
    return users

# GOOD — yields control while waiting
@app.get("/users")
async def get_users():
    await asyncio.sleep(2)  # Other requests run during this wait
    result = await db.execute(select(User))  # asyncpg, not psycopg2
    return result.scalars().all()

# ALSO GOOD — run sync blocking code in thread pool
from fastapi.concurrency import run_in_threadpool

@app.get("/users")
async def get_users():
    result = await run_in_threadpool(sync_db_query)  # Doesn't block event loop
    return result
```

**Connection pooling:**
```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,          # Connections to maintain
    max_overflow=0,        # No extra connections beyond pool_size
    pool_pre_ping=True,    # Check connections before use (avoid stale conn errors)
    pool_recycle=3600,     # Recycle connections after 1 hour
)
```

**Response optimization:**
```python
# Use response_model_exclude_unset to omit None fields
@app.get("/users/{id}", response_model=UserResponse, response_model_exclude_unset=True)
async def get_user(id: int): ...

# Use ORJSONResponse for 2-5x faster JSON serialization
from fastapi.responses import ORJSONResponse
app = FastAPI(default_response_class=ORJSONResponse)
```

**Startup/shutdown lifespan events:**
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create connection pool, load ML model, warm cache
    app.state.db_pool = await create_pool(DATABASE_URL)
    app.state.ml_model = load_model("model.pkl")
    yield
    # Shutdown: close connections cleanly
    await app.state.db_pool.close()

app = FastAPI(lifespan=lifespan)
```

---

## AUTHENTICATION PATTERNS

**Q: How do you implement JWT authentication in FastAPI?**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user

@app.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    token = create_access_token({"sub": str(user.id)}, timedelta(minutes=30))
    return {"access_token": token, "token_type": "bearer"}
```

**Q: How do you implement API Key authentication?**
```python
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Depends(API_KEY_HEADER), db = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=403, detail="API key required")
    key = await db.execute(select(APIKey).where(APIKey.key == api_key, APIKey.is_active == True))
    if not key.scalar():
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/data", dependencies=[Depends(verify_api_key)])
async def get_data(): ...
```

**Q: `Depends()` vs `Security()` — what is the difference?**
A: `Security()` is a subclass of `Depends()` specifically for authentication dependencies. It shows a lock icon and auth input in Swagger UI. Functionally identical — the difference is purely documentation/OpenAPI schema generation. Use `Security()` for auth dependencies, `Depends()` for everything else.

---

## COMMON INTERVIEW TRAPS

**Trap 1: async endpoint with a synchronous blocking call**
```python
# WRONG — time.sleep() blocks the event loop
@app.get("/bad")
async def bad_endpoint():
    time.sleep(5)  # Blocks ALL concurrent requests during this time
    return {"status": "done"}

# CORRECT — offload to thread pool
@app.get("/good")
async def good_endpoint():
    await run_in_threadpool(time.sleep, 5)  # Other requests still run
    return {"status": "done"}
```

**Trap 2: Pydantic v1 vs v2 breaking changes**
- `@validator` (v1) → `@field_validator` (v2)
- `__fields__` (v1) → `model_fields` (v2)
- `dict()` (v1) → `model_dump()` (v2)
- `parse_obj()` (v1) → `model_validate()` (v2)
- FastAPI 0.100+ ships with Pydantic v2. Be aware when reading older code.

**Trap 3: Mutable default arguments in route handlers**
```python
# WRONG — list is created once and shared across all requests
@app.post("/items")
async def add_item(item: str, store: list = []):
    store.append(item)
    return store  # State leaks between requests!

# CORRECT — use a proper store (database, cache, app.state)
```

**Trap 4: Response model leaking internal fields**
```python
# Model has password_hash field
class User(Base):
    password_hash: str

# Without response_model, the hash would be serialized!
@app.get("/users/{id}", response_model=UserPublic)  # UserPublic excludes sensitive fields
async def get_user(id: int): ...
```

**Trap 5: Not awaiting `file.read()` in upload handlers**
`UploadFile.read()` is a coroutine. Forgetting `await` returns a coroutine object, not the bytes.

**Trap 6: 422 Unprocessable Entity vs 400 Bad Request**
FastAPI returns 422 (not 400) when Pydantic validation fails on request body. This is per the OpenAPI spec. Interviewers may ask about this — 422 means the request was well-formed but semantically invalid.

**Trap 7: Middleware order matters**
Middleware executes in reverse registration order. The last middleware added is the first to process the request (LIFO for request phase).
