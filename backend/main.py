"""
Step 5: FastAPI Application — The API layer exposing the LangGraph agent as a service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import APP_TITLE, APP_VERSION
from routers import query, feedback, analytics
from models import DefectRecord
from chroma_store import VectorStore

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description="Agentic AI DKI Assurance Platform — transforms a static knowledge base into a dynamic reasoning brain for Quality Engineering.",
)

# ── CORS for React frontend ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ──
app.include_router(query.router)
app.include_router(feedback.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    """Health check / welcome endpoint."""
    return {
        "name": APP_TITLE,
        "version": APP_VERSION,
        "status": "operational",
        "endpoints": {
            "query": "POST /api/query",
            "feedback": "POST /api/feedback",
            "analytics": "GET /api/analytics",
            "ingest": "POST /api/ingest",
            "seed": "POST /api/seed",
            "docs": "GET /docs",
        },
    }


@app.post("/api/ingest", tags=["Data Ingestion"])
async def ingest_defect(defect: DefectRecord):
    """Ingest a single defect record into the knowledge base."""
    store = VectorStore()
    point_id = store.ingest_defect(defect)
    return {"message": "Defect ingested successfully", "point_id": point_id}


@app.post("/api/seed", tags=["Data Ingestion"])
async def seed_database():
    """Seed the database with sample defect data."""
    from seed_data import seed_database as _seed
    ids = _seed()
    return {"message": f"Seeded {len(ids)} defect records", "point_ids": ids}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
