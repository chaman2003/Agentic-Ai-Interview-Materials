# ============================================================
# FASTAPI BASICS — Interview Essentials
# ============================================================
# pip install fastapi uvicorn[standard] pydantic

# WHY FASTAPI vs FLASK?
# FastAPI = async-first, automatic OpenAPI docs, Pydantic validation built-in
# Flask   = sync-first, manual docs, manual validation
# FastAPI is 2-3x faster than Flask for I/O-bound tasks due to async support

from fastapi import FastAPI, HTTPException, status, Query, Path
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
import uvicorn

app = FastAPI(
    title="Case Management API",
    description="Case management REST API",
    version="1.0.0"
)

# ── PYDANTIC MODELS ───────────────────────────────────────────
# Pydantic = data validation library. FastAPI uses it for:
# - Request body validation (auto 422 if invalid)
# - Response serialization
# - OpenAPI schema generation (auto-docs!)

class CaseCreate(BaseModel):
    title:       str               = Field(..., min_length=3, max_length=200)
    description: str               = Field(..., min_length=10)
    party_a:     str               = Field(..., min_length=2)
    party_b:     str               = Field(..., min_length=2)
    amount:      float             = Field(..., gt=0, description="Dispute amount in INR")
    case_type:   str               = Field(default="contract", description="Type of dispute")

    @validator("amount")
    def amount_must_be_reasonable(cls, v):
        if v > 100_000_000:   # 10 crore limit
            raise ValueError("Amount exceeds maximum limit")
        return round(v, 2)

class CaseResponse(BaseModel):
    id:          int
    title:       str
    status:      str
    amount:      float
    party_a:     str
    party_b:     str

    class Config:
        from_attributes = True   # allows creating from SQLAlchemy models (was orm_mode in v1)

class CaseUpdate(BaseModel):
    title:       Optional[str]  = None
    description: Optional[str] = None
    status:      Optional[str] = None   # all fields optional for PATCH


# ── ROUTES ────────────────────────────────────────────────────

# GET — list with query params
@app.get("/cases", response_model=List[CaseResponse], status_code=200)
async def get_cases(
    status:  Optional[str] = Query(None, description="Filter by status"),
    page:    int           = Query(1, ge=1),
    limit:   int           = Query(10, ge=1, le=100),
    sort_by: str           = Query("created_at", regex="^(created_at|amount|title)$")
):
    """Get all cases with optional filtering and pagination."""
    # In real app: query DB with filters
    mock_cases = [
        {"id": 1, "title": "Smith vs Jones", "status": "open", "amount": 50000, "party_a": "Smith", "party_b": "Jones"},
        {"id": 2, "title": "Corp vs LLC",    "status": "closed", "amount": 120000, "party_a": "Corp", "party_b": "LLC"},
    ]
    if status:
        mock_cases = [c for c in mock_cases if c["status"] == status]
    return mock_cases


# GET — single resource with path parameter
@app.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int = Path(..., ge=1, description="Case ID must be positive")
):
    """Get a specific case by ID."""
    # Simulate not found
    if case_id > 100:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Case not found", "case_id": case_id}
        )
    return {"id": case_id, "title": "Mock Case", "status": "open", "amount": 50000, "party_a": "A", "party_b": "B"}


# POST — create with request body validation
@app.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(case: CaseCreate):
    """Create a new case. Body is automatically validated by Pydantic."""
    # case.title, case.amount, etc. are already validated
    new_case = {"id": 99, **case.dict(), "status": "open"}
    return new_case


# PATCH — partial update
@app.patch("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, updates: CaseUpdate):
    """Update specific fields of a case."""
    update_data = updates.dict(exclude_none=True)   # only include provided fields
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    return {"id": case_id, "title": "Updated", "status": "open", "amount": 50000, "party_a": "A", "party_b": "B"}


# DELETE
@app.delete("/cases/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(case_id: int):
    """Delete a case. Returns 204 No Content."""
    if case_id > 100:
        raise HTTPException(status_code=404, detail="Case not found")
    return None   # 204 returns no body


# ── STARTUP / SHUTDOWN EVENTS ─────────────────────────────────
@app.on_event("startup")
async def startup():
    print("App starting up — connect to DB here")
    # await database.connect()

@app.on_event("shutdown")
async def shutdown():
    print("App shutting down — disconnect DB here")
    # await database.disconnect()


# ── HEALTH CHECK ──────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    # Run with: uvicorn 01_fastapi_basics:app --reload
    uvicorn.run("01_fastapi_basics:app", host="0.0.0.0", port=8000, reload=True)

# Auto-generated docs available at:
# http://localhost:8000/docs     ← Swagger UI
# http://localhost:8000/redoc    ← ReDoc
# http://localhost:8000/openapi.json ← raw OpenAPI schema
