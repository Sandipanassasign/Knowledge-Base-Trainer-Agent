"""
Step 1: Data Ingestion & Memory Setup — Qdrant Vector Store.
Handles collection creation, embedding generation, and hybrid search.
"""
import uuid
from typing import List, Optional, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)
from sentence_transformers import SentenceTransformer

from config import (
    QDRANT_URL,
    QDRANT_API_KEY,
    QDRANT_COLLECTION,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSION,
    TOP_K_RESULTS,
)
from models import DefectRecord, DefectPayload


class QdrantStore:
    """Manages the Qdrant vector database for defect knowledge."""

    def __init__(self):
        self.client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY if QDRANT_API_KEY else None,
        )
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self._ensure_collection()

    # ── Collection Setup ──
    def _ensure_collection(self):
        """Create the collection if it doesn't exist, with payload indexes for hybrid search."""
        collections = [c.name for c in self.client.get_collections().collections]
        if QDRANT_COLLECTION not in collections:
            self.client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=Distance.COSINE,
                ),
            )
            # Create payload indexes for efficient metadata filtering
            for field in ["severity", "module_id", "root_cause_category", "release_version", "source"]:
                self.client.create_payload_index(
                    collection_name=QDRANT_COLLECTION,
                    field_name=field,
                    field_schema=PayloadSchemaType.KEYWORD,
                )
            print(f"✅ Created Qdrant collection: {QDRANT_COLLECTION}")
        else:
            print(f"ℹ️  Collection '{QDRANT_COLLECTION}' already exists.")

    # ── Embedding ──
    def _embed(self, text: str) -> List[float]:
        """Generate embedding vector for a text string."""
        return self.encoder.encode(text).tolist()

    # ── Ingest ──
    def ingest_defect(self, defect: DefectRecord, confidence: float = 0.5, source: str = "historical") -> str:
        """Ingest a single defect record into Qdrant."""
        point_id = str(uuid.uuid4())
        combined_text = f"{defect.title}. {defect.description}"
        if defect.resolution:
            combined_text += f" Resolution: {defect.resolution}"

        payload = DefectPayload(
            title=defect.title,
            description=defect.description,
            severity=defect.severity.value,
            module_id=defect.module_id,
            root_cause_category=defect.root_cause_category,
            release_version=defect.release_version,
            resolution=defect.resolution,
            test_type=defect.test_type,
            confidence=confidence,
            source=source,
        )

        self.client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=self._embed(combined_text),
                    payload=payload.model_dump(),
                )
            ],
        )
        return point_id

    def ingest_batch(self, defects: List[DefectRecord]) -> List[str]:
        """Ingest multiple defect records."""
        ids = []
        for defect in defects:
            pid = self.ingest_defect(defect)
            ids.append(pid)
        return ids

    # ── Hybrid Search (Semantic + Metadata Filters) ──
    def search(
        self,
        query: str,
        module_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
        top_k: int = TOP_K_RESULTS,
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search: semantic similarity + optional metadata filters.
        This is the 'Pro Tip' from Step 1 — find 'Login issues' (semantic)
        specifically in the 'Payment Module' (metadata filter).
        """
        conditions = []
        if module_filter:
            conditions.append(
                FieldCondition(field_name="module_id", match=MatchValue(value=module_filter))
            )
        if severity_filter:
            conditions.append(
                FieldCondition(field_name="severity", match=MatchValue(value=severity_filter))
            )

        query_filter = Filter(must=conditions) if conditions else None

        results = self.client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=self._embed(query),
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )

        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                **hit.payload,
            }
            for hit in results.points
        ]

    # ── Upsert Feedback (Step 3: Trainer) ──
    def upsert_feedback(self, original_query: str, correction: str, context: Optional[str] = None) -> str:
        """
        Save user-corrected knowledge back into Qdrant as a
        'High-Confidence Reference' — this is the self-correction loop.
        """
        point_id = str(uuid.uuid4())
        combined_text = f"{original_query}. Corrected answer: {correction}"
        if context:
            combined_text += f" Context: {context}"

        payload = {
            "title": f"User Feedback: {original_query[:80]}",
            "description": correction,
            "severity": "medium",
            "module_id": "user_feedback",
            "root_cause_category": "user_correction",
            "release_version": "feedback",
            "resolution": correction,
            "confidence": 0.95,  # High-Confidence Reference
            "source": "user_feedback",
        }

        self.client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=self._embed(combined_text),
                    payload=payload,
                )
            ],
        )
        return point_id

    # ── Analytics Helpers ──
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics for the dashboard."""
        info = self.client.get_collection(QDRANT_COLLECTION)
        return {
            "total_points": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status.value,
        }

    def get_all_points_payload(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve all payloads for analytics aggregation."""
        results = self.client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )
        return [point.payload for point in results[0]]
