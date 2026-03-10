"""
Analytics Router — /api/analytics endpoint.
Provides data for the Risk Heatmap and dashboard visualizations.
"""
from collections import Counter
from fastapi import APIRouter, HTTPException
from models import AnalyticsResponse, ModuleRisk
from chroma_store import VectorStore

router = APIRouter(prefix="/api", tags=["Analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics():
    """
    Aggregate analytics from the knowledge base for the dashboard.
    Returns module risks, severity distribution, and feedback stats.
    """
    try:
        store = VectorStore()
        payloads = store.get_all_points_payload()

        if not payloads:
            return AnalyticsResponse(
                total_defects=0,
                modules=[],
                severity_distribution={},
                feedback_stats={"total_feedback": 0, "corrections": 0},
            )

        # ── Severity Distribution ──
        severity_counter = Counter(p.get("severity", "unknown") for p in payloads)

        # ── Module Risk Aggregation ──
        module_data = {}
        for p in payloads:
            mod = p.get("module_id", "unknown")
            if mod not in module_data:
                module_data[mod] = {"count": 0, "root_causes": [], "severities": []}
            module_data[mod]["count"] += 1
            module_data[mod]["root_causes"].append(p.get("root_cause_category", "unknown"))
            module_data[mod]["severities"].append(p.get("severity", "unknown"))

        severity_weights = {"critical": 1.0, "high": 0.75, "medium": 0.5, "low": 0.25}
        modules = []
        for mod_id, data in module_data.items():
            # Calculate risk score based on count and severity
            avg_severity = sum(
                severity_weights.get(s, 0.3) for s in data["severities"]
            ) / max(len(data["severities"]), 1)
            risk_score = min(avg_severity * (data["count"] / max(len(payloads), 1)) * 5, 1.0)

            top_causes = [item for item, _ in Counter(data["root_causes"]).most_common(3)]

            modules.append(ModuleRisk(
                module_id=mod_id,
                risk_score=round(risk_score, 2),
                defect_count=data["count"],
                top_root_causes=top_causes,
            ))

        # Sort by risk score descending
        modules.sort(key=lambda m: m.risk_score, reverse=True)

        # ── Feedback Stats ──
        feedback_count = sum(1 for p in payloads if p.get("source") == "user_feedback")

        return AnalyticsResponse(
            total_defects=len(payloads),
            modules=modules,
            severity_distribution=dict(severity_counter),
            feedback_stats={
                "total_feedback": feedback_count,
                "corrections": feedback_count,
                "historical": len(payloads) - feedback_count,
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")
