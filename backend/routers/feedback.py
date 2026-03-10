"""
Feedback Router — /api/feedback endpoint.
Step 3: The Feedback Loop (The Trainer).
"""
from fastapi import APIRouter, HTTPException
from models import FeedbackRequest, FeedbackResponse, FeedbackType
from chroma_store import VectorStore

router = APIRouter(prefix="/api", tags=["Feedback"])

# In-memory session store (in production, use Redis or a DB)
_session_store: dict = {}


def store_session(session_id: str, data: dict):
    """Store session data for feedback reference."""
    _session_store[session_id] = data


def get_session(session_id: str) -> dict:
    """Retrieve session data."""
    return _session_store.get(session_id, {})


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    Step 3: Human-in-the-Loop Feedback.

    - If 'correct': The agent's recommendation is validated. Confidence is boosted.
    - If 'incorrect': The agent saves the user's correction back into ChromaDB
      as a 'High-Confidence Reference' — self-correction loop.
    """
    try:
        session = get_session(request.session_id)
        store = VectorStore()

        if request.feedback_type == FeedbackType.CORRECT:
            # Positive feedback — optionally boost confidence of matched records
            return FeedbackResponse(
                message="✅ Thank you! Your positive feedback has been recorded. "
                        "The agent will prioritize similar patterns in future queries.",
                knowledge_updated=False,
            )

        elif request.feedback_type == FeedbackType.INCORRECT:
            if not request.correction:
                raise HTTPException(
                    status_code=400,
                    detail="Correction text is required when feedback type is 'incorrect'.",
                )

            # Step 3: Upsert corrected knowledge back into ChromaDB
            original_query = session.get("query", request.session_id)
            point_id = store.upsert_feedback(
                original_query=original_query,
                correction=request.correction,
                context=request.additional_context,
            )

            return FeedbackResponse(
                message=f"🔄 Knowledge base updated! Your correction has been saved as a "
                        f"High-Confidence Reference (ID: {point_id[:8]}...). "
                        f"The agent will prioritize this in future queries.",
                knowledge_updated=True,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback error: {str(e)}")
