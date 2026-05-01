"""LangGraph-based multi-agent orchestrator for LankaVoyage AI.

This module defines the StateGraph workflow that orchestrates the
Research, Optimizer, and Personalizer agents in a stateful manner.
"""

from __future__ import annotations

from langgraph.graph import StateGraph

from agents.optimizer_agent import optimizer_node
from agents.personalizer_agent import personalizer_node
from agents.research_agent import research_node
from tools.graph_state import PlanningState
from tools.observability import log_event


def create_planning_graph() -> StateGraph:
    """Create and return the LangGraph StateGraph for trip planning.
    
    The graph follows this workflow:
    START → research_node → optimizer_node → personalizer_node → END
    
    Each node receives the full planning state, processes it, updates
    the state with its outputs, and passes it to the next node.
    
    Returns:
        StateGraph: The compiled LangGraph workflow.
    """
    # Initialize the graph with state schema
    graph = StateGraph(PlanningState)

    # Add nodes (agent functions)
    graph.add_node("research", research_node)
    graph.add_node("optimizer", optimizer_node)
    graph.add_node("personalizer", personalizer_node)

    # Define edges (workflow transitions)
    graph.add_edge("research", "optimizer")
    graph.add_edge("optimizer", "personalizer")

    # Set entry and exit points
    graph.set_entry_point("research")
    graph.set_finish_point("personalizer")

    # Compile the graph
    compiled_graph = graph.compile()

    log_event(
        "orchestrator",
        "graph_created",
        {
            "nodes": ["research", "optimizer", "personalizer"],
            "edges": ["research->optimizer", "optimizer->personalizer"],
        },
    )

    return compiled_graph


def run_planning_workflow(
    query: str,
    model: str = "llama3.2",
    limit: int = 10,
    output_filename: str = "itinerary.md",
) -> PlanningState:
    """Execute the multi-agent planning workflow.
    
    This is the main entry point for running the LangGraph workflow.
    It creates the initial state, runs the graph, and returns the
    final state with all agent outputs.
    
    Args:
        query: User travel planning request
        model: Ollama model name (default: llama3.2)
        limit: Max records to fetch from tourism DB (default: 10)
        output_filename: Output markdown filename (default: itinerary.md)
    
    Returns:
        PlanningState: The final state with all agent outputs
    
    Raises:
        ValueError: If graph execution fails
    """
    log_event(
        "orchestrator",
        "workflow_started",
        {
            "query": query,
            "model": model,
            "limit": limit,
            "output_filename": output_filename,
        },
    )

    # Create initial state
    initial_state = PlanningState(
        query=query,
        model=model,
        limit=limit,
        output_filename=output_filename,
    )

    # Create the graph
    graph = create_planning_graph()

    # Execute the workflow
    try:
        final_state = graph.invoke(initial_state)
        log_event(
            "orchestrator",
            "workflow_completed",
            {
                "query": query,
                "report_path": final_state.report_path,
            },
        )
        return final_state
    except Exception as exc:
        log_event(
            "orchestrator",
            "workflow_failed",
            {
                "query": query,
                "error": str(exc),
            },
        )
        raise ValueError(f"Workflow execution failed: {exc}") from exc
