# FastAPI Q&A — Interview Ready

---

**Q: What is FastAPI and how is it different from Flask?**
A:
| Feature | FastAPI | Flask |
|---------|---------|-------|
| Async | Native (`async def`) | Needs extra work |
| Validation | Built-in via Pydantic | Manual |
| Docs | Auto-generated at `/docs` | Manual (swagger-jsdoc) |
| Performance | ~3x faster (ASGI) | Slower (WSGI) |
| Type hints | First-class | Optional |
| Learning curve | Medium | Low |

Use FastAPI for new async-first APIs. Flask is still fine for simple scripts/services.

**Q: What is Pydantic?**
A: A data validation library. You define a model with type annotations, Pydantic validates incoming data and raises errors if it doesn't match. FastAPI uses Pydantic for request body parsing and response serialization.
```python
class User(BaseModel):
    name:  str
    email: str
    age:   int = Field(gt=0, lt=150)
```

**Q: What happens when Pydantic validation fails in FastAPI?**
A: FastAPI automatically returns HTTP 422 Unprocessable Entity with detailed error messages showing which fields failed and why. You don't write this logic — it's built-in.

**Q: What is dependency injection in FastAPI?**
A: `Depends()` — a way to inject reusable logic into routes. When you declare `user = Depends(get_current_user)`, FastAPI calls `get_current_user()` and passes the result. Use for: auth, DB sessions, pagination, settings.

**Q: What is `async def` vs `def` in FastAPI routes?**
A:
- `async def` — FastAPI runs it on the async event loop. Use when your route awaits I/O (DB, API calls).
- `def` — FastAPI runs it in a separate thread pool. Use for CPU-bound or sync-only code.
- Wrong choice causes performance issues but not bugs.

**Q: What is ASGI?**
A: Asynchronous Server Gateway Interface — the async version of WSGI. FastAPI runs on ASGI servers (Uvicorn, Hypercorn). Handles many concurrent connections without blocking.

**Q: How does FastAPI generate automatic documentation?**
A: FastAPI reads your route decorators, path/query params, Pydantic models, and function signatures. It builds an OpenAPI 3.0 spec automatically. Available at:
- `/docs` — Swagger UI (interactive, can test requests)
- `/redoc` — ReDoc (cleaner reading)
- `/openapi.json` — raw JSON schema

**Q: What is `response_model` in FastAPI?**
A: Filters and serializes the response using a Pydantic model. Even if your function returns extra data (like a password hash), `response_model` strips it to only the fields in the model.

**Q: How do you run FastAPI?**
A: `uvicorn main:app --reload` — Uvicorn is an ASGI server. `--reload` restarts on code changes (development only).

**Q: What are background tasks in FastAPI?**
A: `BackgroundTasks` — runs a function AFTER the response is sent. Good for: sending emails, writing logs, triggering webhooks — things the client doesn't need to wait for.

**Q: How do you handle settings/config in FastAPI?**
A: Use `pydantic-settings` `BaseSettings` class. It reads from environment variables and `.env` files automatically. Better than `os.environ.get()` because you get type validation and IDE autocomplete.

**Q: How do you test a FastAPI app?**
```python
from fastapi.testclient import TestClient
client = TestClient(app)

def test_get_cases():
    response = client.get("/cases")
    assert response.status_code == 200

def test_create_case():
    response = client.post("/cases", json={"title": "Test", ...})
    assert response.status_code == 201
```
TestClient wraps your app in an httpx client — no server needed.
