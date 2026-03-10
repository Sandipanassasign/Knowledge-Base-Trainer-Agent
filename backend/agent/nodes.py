"""
Step 2 & 4: Agent Nodes — The functions that do the work.
  - Retriever Node:  Calls ChromaDB for top-K similar defects (hybrid search).
  - Pattern Recognition Node:  LLM analyzes results to find commonalities.
  - Predictive Node:  Matches current changes against patterns to flag risk areas.
"""
import re
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from config import OPENAI_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from agent.state import AgentState
from agent.prompts import (
    PATTERN_RECOGNITION_PROMPT,
    RECOMMENDATION_PROMPT,
    PREDICTIVE_GUIDANCE_PROMPT,
)

# ── Shared LLM instance ──
_llm = None

def _get_llm() -> ChatOpenAI:
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            api_key=OPENAI_API_KEY,
        )
    return _llm


# ═══════════════════════════════════════════════
# Node 1 — Retriever (Step 1 + Step 2)
# ═══════════════════════════════════════════════
def retriever_node(state: AgentState) -> Dict[str, Any]:
    """
    Calls ChromaDB to find the top 5 similar historical defects.
    Uses hybrid search — semantic + optional metadata filters.
    """
    # Import here to avoid circular imports at module level
    from chroma_store import VectorStore

    store = VectorStore()
    results = store.search(
        query=state["query"],
        module_filter=state.get("module_filter"),
        severity_filter=state.get("severity_filter"),
    )

    return {"historical_context": results}


# ═══════════════════════════════════════════════
# Node 2 — Pattern Recognition (Step 2)
# ═══════════════════════════════════════════════
def pattern_recognition_node(state: AgentState) -> Dict[str, Any]:
    """
    An LLM analyzes the retrieved defects to find commonalities.
    E.g., 'All these bugs happen when DB latency > 200ms'.
    """
    context = state.get("historical_context", [])

    if not context:
        return {
            "patterns": ["No historical data found for this query."],
            "recommendation": "No historical context available. Consider adding defect records to the knowledge base first.",
        }

    # Format context for the LLM
    context_str = "\n".join([
        f"- [{i+1}] Title: {d.get('title', 'N/A')} | "
        f"Severity: {d.get('severity', 'N/A')} | "
        f"Module: {d.get('module_id', 'N/A')} | "
        f"Root Cause: {d.get('root_cause_category', 'N/A')} | "
        f"Description: {d.get('description', 'N/A')[:200]} | "
        f"Resolution: {d.get('resolution', 'N/A')}"
        for i, d in enumerate(context)
    ])

    # ── Pattern Recognition ──
    pattern_prompt = PATTERN_RECOGNITION_PROMPT.format(
        count=len(context),
        query=state["query"],
        context=context_str,
    )
    llm = _get_llm()
    pattern_response = llm.invoke([HumanMessage(content=pattern_prompt)])
    patterns = [line.strip() for line in pattern_response.content.strip().split("\n") if line.strip()]

    # ── Recommendation ──
    rec_prompt = RECOMMENDATION_PROMPT.format(
        query=state["query"],
        context=context_str,
        patterns="\n".join(patterns),
    )
    rec_response = llm.invoke([HumanMessage(content=rec_prompt)])

    return {
        "patterns": patterns,
        "recommendation": rec_response.content.strip(),
    }


# ═══════════════════════════════════════════════
# Node 3 — Predictive Guidance (Step 4)
# ═══════════════════════════════════════════════
def predictive_node(state: AgentState) -> Dict[str, Any]:
    """
    Matches current release requirements against identified patterns
    to flag high-risk areas and generate BDD scenarios.
    """
    code_changes = state.get("code_changes")
    if not code_changes:
        return {"predictive_risks": []}

    context = state.get("historical_context", [])
    context_str = "\n".join([
        f"- {d.get('title', 'N/A')} (Module: {d.get('module_id', 'N/A')}, "
        f"Root Cause: {d.get('root_cause_category', 'N/A')})"
        for d in context
    ])

    prompt = PREDICTIVE_GUIDANCE_PROMPT.format(
        context=context_str or "No historical context available.",
        patterns="\n".join(state.get("patterns", ["No patterns identified."])),
        code_changes=code_changes,
    )

    llm = _get_llm()
    response = llm.invoke([HumanMessage(content=prompt)])

    # Parse the structured response
    risks = _parse_predictive_response(response.content)
    return {"predictive_risks": risks}


def _parse_predictive_response(text: str):
    """Parse the LLM's predictive response into structured data."""
    risks = []
    # Split by MODULE: markers
    blocks = re.split(r"MODULE:\s*", text)
    for block in blocks[1:]:  # Skip the part before first MODULE:
        risk = {}
        # Extract module name
        lines = block.strip().split("\n")
        risk["module"] = lines[0].strip()

        # Extract risk score
        score_match = re.search(r"RISK_SCORE:\s*([\d.]+)", block)
        risk["risk_score"] = float(score_match.group(1)) if score_match else 0.5

        # Extract reason
        reason_match = re.search(r"REASON:\s*(.+?)(?=BDD_SCENARIO:|$)", block, re.DOTALL)
        risk["reason"] = reason_match.group(1).strip() if reason_match else ""

        # Extract BDD scenario
        bdd_match = re.search(r"```gherkin\s*\n(.+?)```", block, re.DOTALL)
        risk["suggested_bdd_scenario"] = bdd_match.group(1).strip() if bdd_match else ""

        risks.append(risk)

    return risks[:3]  # Return top 3
