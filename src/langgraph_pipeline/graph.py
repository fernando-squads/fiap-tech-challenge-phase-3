from langgraph.graph import StateGraph, END

from src.langgraph_pipeline.state import GraphState
from src.langgraph_pipeline.nodes import (
    load_patient,
    retrieve_docs,
    generate_answer,
    validate,
    explain
)

def build_graph():
    graph = StateGraph(GraphState)

    # nodes
    graph.add_node("load_patient", load_patient)
    graph.add_node("retrieve_docs", retrieve_docs)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("validate", validate)
    graph.add_node("explain", explain)

    # fluxo
    graph.set_entry_point("load_patient")

    graph.add_edge("load_patient", "retrieve_docs")
    graph.add_edge("retrieve_docs", "generate_answer")
    graph.add_edge("generate_answer", "validate")
    graph.add_edge("validate", "explain")
    graph.add_edge("explain", END)

    return graph.compile()