"""
Step 2: Agent State — The agent's memory during a conversation.
"""
from typing import TypedDict, List, Optional, Dict, Any


class AgentState(TypedDict):
    """
    LangGraph state that flows through every node.
    This is the agent's working memory for a single query.
    """
    # ── Input ──
    query: str                          # User's current testing problem
    module_filter: Optional[str]        # Optional module filter for hybrid search
    severity_filter: Optional[str]      # Optional severity filter
    code_changes: Optional[str]         # Current code changes for predictive analysis

    # ── Processing ──
    historical_context: List[Dict[str, Any]]  # Retrieved similar cases from Qdrant
    patterns: List[str]                       # Identified trends / commonalities
    recommendation: str                       # Final strategic output

    # ── Predictive ──
    predictive_risks: List[Dict[str, Any]]    # Predicted risky modules + BDD scenarios

    # ── Feedback Loop (Step 3) ──
    feedback: Optional[str]             # User feedback data
    session_id: str                     # Unique session ID for feedback tracking
