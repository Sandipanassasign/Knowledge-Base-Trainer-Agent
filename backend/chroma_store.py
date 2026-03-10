"""
Step 1: Data Ingestion & Memory Setup — ChromaDB Vector Store.
Handles collection creation, embedding generation, and hybrid search.
Replaces Qdrant with local ChromaDB for zero-dependency vector storage.
"""
import uuid
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
)
from models import DefectRecord, DefectPayload


class VectorStore:
    """Manages the ChromaDB vector database for defect knowledge."""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        self.encoder = SentenceTransformer(EMBEDDING_MODEL)
        self.collection = self._ensure_collection()

    # ── Collection Setup ──
    def _ensure_collection(self):
        """Get or create the collection."""
        collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )
        print(f"ℹ️  ChromaDB collection '{CHROMA_COLLECTION}' ready ({collection.count()} points).")
        return collection

    # ── Embedding ──
    def _embed(self, text: str) -> List[float]:
        """Generate embedding vector for a text string."""
        return self.encoder.encode(text).tolist()

    # ── Ingest ──
    def ingest_defect(self, defect: DefectRecord, confidence: float = 0.5, source: str = "historical") -> str:
        """Ingest a single defect record into ChromaDB."""
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

        # ChromaDB stores metadata as flat dict; documents as text
        metadata = payload.model_dump()
        # ChromaDB metadata values must be str, int, float, or bool
        for k, v in list(metadata.items()):
            if v is None:
                metadata[k] = ""

        self.collection.upsert(
            ids=[point_id],
            embeddings=[self._embed(combined_text)],
            metadatas=[metadata],
            documents=[combined_text],
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
        Find 'Login issues' (semantic) specifically in the 'Payment Module' (metadata filter).
        """
        where_filters = []
        if module_filter:
            where_filters.append({"module_id": {"$eq": module_filter}})
        if severity_filter:
            where_filters.append({"severity": {"$eq": severity_filter}})

        # Build the where clause
        where = None
        if len(where_filters) == 1:
            where = where_filters[0]
        elif len(where_filters) > 1:
            where = {"$and": where_filters}

        results = self.collection.query(
            query_embeddings=[self._embed(query)],
            n_results=top_k,
            where=where,
            include=["metadatas", "distances", "documents"],
        )

        # ChromaDB returns distances (lower = more similar for cosine).
        # Convert to similarity scores (1 - distance) for consistency.
        hits = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0.0
                score = 1.0 - distance  # Convert distance to similarity
                hits.append({
                    "id": doc_id,
                    "score": round(score, 4),
                    **metadata,
                })

        return hits

    # ── Upsert Feedback (Step 3: Trainer) ──
    def upsert_feedback(self, original_query: str, correction: str, context: Optional[str] = None) -> str:
        """
        Save user-corrected knowledge back into ChromaDB as a
        'High-Confidence Reference' — this is the self-correction loop.
        """
        point_id = str(uuid.uuid4())
        combined_text = f"{original_query}. Corrected answer: {correction}"
        if context:
            combined_text += f" Context: {context}"

        metadata = {
            "title": f"User Feedback: {original_query[:80]}",
            "description": correction,
            "severity": "medium",
            "module_id": "user_feedback",
            "root_cause_category": "user_correction",
            "release_version": "feedback",
            "resolution": correction,
            "confidence": 0.95,  # High-Confidence Reference
            "source": "user_feedback",
            "test_type": "",
        }

        self.collection.upsert(
            ids=[point_id],
            embeddings=[self._embed(combined_text)],
            metadatas=[metadata],
            documents=[combined_text],
        )
        return point_id

    # ── Analytics Helpers ──
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics for the dashboard."""
        count = self.collection.count()
        return {
            "total_points": count,
            "vectors_count": count,
            "status": "green",
        }

    def get_all_points_payload(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve all payloads for analytics aggregation."""
        count = self.collection.count()
        if count == 0:
            return []

        results = self.collection.get(
            limit=min(count, limit),
            include=["metadatas"],
        )
        return results["metadatas"] if results["metadatas"] else []


# ── Backward-compatible alias ──
QdrantStore = VectorStore
