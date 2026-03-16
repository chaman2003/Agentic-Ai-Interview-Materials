# ============================================================
# FASTAPI ADVANCED — Dependency Injection, Auth, Async, Middleware
# ============================================================

from fastapi import FastAPI, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Annotated
import time, jose
from jose import jwt


# ── SETTINGS (Config Management) ─────────────────────────────
# Use Pydantic BaseSettings to read from environment variables
# Much better than os.environ.get() scattered everywhere

class Settings(BaseSettings):
    app_name:      str   = "Case Management API"
    jwt_secret:    str   = "dev-secret"
    jwt_algorithm: str   = "HS256"
    database_url:  str   = "sqlite:///./dev.db"
    debug:         bool  = False

    class Config:
        env_file = ".env"   # reads from .env file automatically

settings = Settings()   # instantiate once — reuse everywhere


# ── APP ───────────────────────────────────────────────────────
app = FastAPI(title=settings.app_name)


# ── MIDDLEWARE ────────────────────────────────────────────────
# Middleware runs on EVERY request/response

# 1. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mycompany.com"],  # production: specify domains
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# 2. Custom middleware for request timing + logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)             # pass to next handler
    duration = time.time() - start
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration:.3f}s)")
    response.headers["X-Process-Time"] = str(duration)
    return response


# ── DEPENDENCY INJECTION ──────────────────────────────────────
# Dependencies = reusable functions injected into routes
# Use for: auth, DB sessions, settings, pagination params

# Dependency 1: Get current settings
def get_settings() -> Settings:
    return settings

# Dependency 2: Pagination params reusable across routes
class PaginationParams:
    def __init__(self, page: int = 1, limit: int = 10):
        self.page  = page
        self.limit = limit
        self.skip  = (page - 1) * limit

def paginate(page: int = 1, limit: int = 10) -> PaginationParams:
    return PaginationParams(page, limit)

# Dependency 3: JWT Auth
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data. Used as dependency in protected routes."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"id": user_id, "role": payload.get("role", "user")}
    except jose.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

# Role-based dependency (factory pattern)
def require_role(role: str):
    def check_role(user = Depends(get_current_user)):
        if user["role"] != role:
            raise HTTPException(status_code=403, detail=f"Role '{role}' required")
        return user
    return check_role


# ── ROUTES WITH DEPENDENCIES ──────────────────────────────────

# Protected route — injects current user
@app.get("/me")
async def get_profile(current_user = Depends(get_current_user)):
    return {"user": current_user}

# Route with pagination dependency
@app.get("/cases")
async def list_cases(
    pagination: Annotated[PaginationParams, Depends(paginate)],
    current_user = Depends(get_current_user)
):
    return {
        "page":  pagination.page,
        "limit": pagination.limit,
        "skip":  pagination.skip,
        "user":  current_user["id"]
    }

# Admin-only route
@app.delete("/cases/{id}")
async def delete_case(id: int, admin = Depends(require_role("admin"))):
    return {"deleted": id, "by": admin["id"]}

# Route with settings dependency
@app.get("/info")
async def app_info(s: Settings = Depends(get_settings)):
    return {"name": s.app_name, "debug": s.debug}


# ── BACKGROUND TASKS ─────────────────────────────────────────
# Run tasks AFTER returning response to client (don't make user wait)

def send_notification(case_id: int, email: str):
    """This runs after the response is sent — client doesn't wait."""
    print(f"Sending email to {email} about case {case_id}")
    # time.sleep(2)  # simulate slow email send — client already got response!

@app.post("/cases")
async def create_case(body: dict, background_tasks: BackgroundTasks):
    case_id = 99
    # Schedule background task — runs after response is sent
    background_tasks.add_task(send_notification, case_id, body.get("email", ""))
    return {"id": case_id, "message": "Case created, notification queued"}


# ── ASYNC ROUTES ──────────────────────────────────────────────
# async def routes handle many concurrent requests efficiently
# Use await for: DB queries, HTTP calls, file I/O

import asyncio
import httpx  # async HTTP client (like requests but async)

@app.get("/external-data")
async def fetch_external(case_id: int):
    """Fetch from multiple external APIs concurrently."""
    async with httpx.AsyncClient() as client:
        # Run both requests AT THE SAME TIME (not sequentially)
        results = await asyncio.gather(
            client.get(f"https://api.example.com/case/{case_id}"),
            client.get(f"https://api.example.com/parties/{case_id}"),
        )
    return {
        "case":    results[0].json(),
        "parties": results[1].json()
    }


# ── EXCEPTION HANDLERS ────────────────────────────────────────
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Customize the 422 validation error response format."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "fields": [{"field": e["loc"][-1], "message": e["msg"]} for e in exc.errors()]
        }
    )
