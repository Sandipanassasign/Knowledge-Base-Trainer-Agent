"""
Step 2: LangGraph Workflow — Assembles nodes into a directed graph.
This is the orchestration layer that ties retrieval, analysis, and prediction together.
"""
import uuid
from typing import Dict, Any

from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import retriever_node, pattern_recognition_node, predictive_node


def _should_predict(state: AgentState) -> str:
    """Conditional edge: only run predictive node if code_changes are provided."""
    if state.get("code_changes"):
        return "predict"
    return "finish"


def build_agent_graph() -> StateGraph:
    """
    Build the LangGraph workflow:

    [START] → Retriever → Pattern Recognition → (conditional) → Predictive → [END]
                                                               ↘ [END]
    """
    graph = StateGraph(AgentState)

    # ── Add Nodes ──
    graph.add_node("retriever", retriever_node)
    graph.add_node("pattern_recognition", pattern_recognition_node)
    graph.add_node("predictive", predictive_node)

    # ── Define Edges ──
    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "pattern_recognition")

    # Conditional: only predict if code_changes are provided
    graph.add_conditional_edges(
        "pattern_recognition",
        _should_predict,
        {
            "predict": "predictive",
            "finish": END,
        },
    )
    graph.add_edge("predictive", END)

    return graph.compile()


# ── Singleton compiled graph ──
_compiled_graph = None


def get_agent():
    """Get the compiled LangGraph agent (singleton)."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_agent_graph()
    return _compiled_graph


def run_query(
    query: str,
    module_filter: str = None,
    severity_filter: str = None,
    code_changes: str = None,
) -> Dict[str, Any]:
    """
    Run a full agent query and return the final state.
    """
    agent = get_agent()
    session_id = str(uuid.uuid4())

    initial_state: AgentState = {
        "query": query,
        "module_filter": module_filter,
        "severity_filter": severity_filter,
        "code_changes": code_changes,
        "historical_context": [],
        "patterns": [],
        "recommendation": "",
        "predictive_risks": [],
        "feedback": None,
        "session_id": session_id,
    }

    final_state = agent.invoke(initial_state)
    return final_state
