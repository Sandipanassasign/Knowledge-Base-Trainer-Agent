"""
Pydantic models for API request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ── Enums ──
class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeedbackType(str, Enum):
    CORRECT = "correct"
    INCORRECT = "incorrect"


# ── Defect Models ──
class DefectRecord(BaseModel):
    """A single defect record to ingest into the knowledge base."""
    title: str = Field(..., description="Short title of the defect")
    description: str = Field(..., description="Detailed defect description")
    severity: Severity = Field(..., description="Severity level")
    module_id: str = Field(..., description="Module where the defect was found")
    root_cause_category: str = Field(..., description="Root cause category (e.g., race_condition, null_pointer)")
    release_version: str = Field(..., description="Release version where defect was found")
    resolution: Optional[str] = Field(None, description="How the defect was resolved")
    test_type: Optional[str] = Field(None, description="Type of testing (unit, integration, e2e)")


class DefectPayload(BaseModel):
    """Payload stored alongside the vector in Qdrant."""
    title: str
    description: str
    severity: str
    module_id: str
    root_cause_category: str
    release_version: str
    resolution: Optional[str] = None
    test_type: Optional[str] = None
    confidence: float = Field(default=0.5, description="Confidence score (0-1)")
    source: str = Field(default="historical", description="historical | user_feedback")


# ── Query Models ──
class QueryRequest(BaseModel):
    """User query to the DKI agent."""
    query: str = Field(..., description="The testing problem or question")
    module_filter: Optional[str] = Field(None, description="Optional module filter for hybrid search")
    severity_filter: Optional[str] = Field(None, description="Optional severity filter")
    code_changes: Optional[str] = Field(None, description="Current code changes for predictive analysis")


class HistoricalMatch(BaseModel):
    """A single historical defect match."""
    title: str
    description: str
    severity: str
    module_id: str
    root_cause_category: str
    release_version: str
    resolution: Optional[str] = None
    similarity_score: float


class PatternInsight(BaseModel):
    """A pattern identified from historical data."""
    pattern: str
    frequency: int
    affected_modules: List[str]
    risk_level: str


class PredictiveRisk(BaseModel):
    """A predicted risk with mitigation."""
    module: str
    risk_score: float
    reason: str
    suggested_bdd_scenario: str


class QueryResponse(BaseModel):
    """Full response from the DKI agent."""
    query: str
    historical_matches: List[HistoricalMatch]
    patterns: List[str]
    recommendation: str
    predictive_risks: List[PredictiveRisk] = []
    session_id: str


# ── Feedback Models ──
class FeedbackRequest(BaseModel):
    """User feedback on agent recommendation."""
    session_id: str = Field(..., description="Session ID from the query response")
    feedback_type: FeedbackType
    correction: Optional[str] = Field(None, description="Correct answer if feedback is 'incorrect'")
    additional_context: Optional[str] = Field(None, description="Any additional context")


class FeedbackResponse(BaseModel):
    """Response after processing feedback."""
    message: str
    knowledge_updated: bool


# ── Analytics Models ──
class ModuleRisk(BaseModel):
    """Risk data for a single module."""
    module_id: str
    risk_score: float
    defect_count: int
    top_root_causes: List[str]


class AnalyticsResponse(BaseModel):
    """Analytics data for the dashboard."""
    total_defects: int
    modules: List[ModuleRisk]
    severity_distribution: dict
    feedback_stats: dict
