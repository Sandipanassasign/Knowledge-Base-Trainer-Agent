"""
Query Router — /api/query endpoint.
Handles user queries by running the full LangGraph agent pipeline.
"""
from fastapi import APIRouter, HTTPException
from models import QueryRequest, QueryResponse, HistoricalMatch, PredictiveRisk
from agent.graph import run_query

router = APIRouter(prefix="/api", tags=["Query"])


@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Submit a testing problem to the DKI agent.
    The agent will:
      1. Retrieve similar historical defects (hybrid search)
      2. Identify patterns across matches
      3. Generate a strategic recommendation
      4. (If code_changes provided) Predict high-risk modules with BDD scenarios
    """
    try:
        result = run_query(
            query=request.query,
            module_filter=request.module_filter,
            severity_filter=request.severity_filter,
            code_changes=request.code_changes,
        )

        # Transform historical context into structured matches
        matches = [
            HistoricalMatch(
                title=d.get("title", ""),
                description=d.get("description", ""),
                severity=d.get("severity", "medium"),
                module_id=d.get("module_id", ""),
                root_cause_category=d.get("root_cause_category", ""),
                release_version=d.get("release_version", ""),
                resolution=d.get("resolution"),
                similarity_score=d.get("score", 0.0),
            )
            for d in result.get("historical_context", [])
        ]

        # Transform predictive risks
        risks = [
            PredictiveRisk(
                module=r.get("module", ""),
                risk_score=r.get("risk_score", 0.5),
                reason=r.get("reason", ""),
                suggested_bdd_scenario=r.get("suggested_bdd_scenario", ""),
            )
            for r in result.get("predictive_risks", [])
        ]

        return QueryResponse(
            query=request.query,
            historical_matches=matches,
            patterns=result.get("patterns", []),
            recommendation=result.get("recommendation", ""),
            predictive_risks=risks,
            session_id=result.get("session_id", ""),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")
