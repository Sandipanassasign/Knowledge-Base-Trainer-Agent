"""
Configuration for the DKI Assurance Platform.
Uses environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Qdrant Configuration ──
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "defect_knowledge_base")

# ── LLM Configuration ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# ── Embedding Configuration ──
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# ── Application ──
APP_TITLE = "DKI Assurance Platform"
APP_VERSION = "1.0.0"
TOP_K_RESULTS = 5
