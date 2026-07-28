from langgraph.graph import StateGraph, START, END
from ai_agent.nodes import AgentState, extract_and_format, retrieve_context, analyze_visuals, synthesize_and_diagnose

def build_graph():
    """Build the LangGraph workflow."""
    builder = StateGraph(AgentState)
    
    builder.add_node("extract", extract_and_format)
    builder.add_node("retrieve", retrieve_context)
    builder.add_node("analyze_visuals", analyze_visuals)
    builder.add_node("synthesize", synthesize_and_diagnose)
    
    builder.add_edge(START, "extract")
    builder.add_edge("extract", "retrieve")
    builder.add_edge("retrieve", "analyze_visuals")
    builder.add_edge("analyze_visuals", "synthesize")
    builder.add_edge("synthesize", END)
    
    return builder.compile()

graph = build_graph()

def run_agent(log_id: int, raw_log: str, image_path: str = None):
    """Entry point to execute the graph."""
    initial_state = AgentState(
        log_id=log_id,
        raw_log=raw_log,
        structured_data={},
        retrieved_context="",
        image_path=image_path if image_path else "",
        visual_context="",
        final_analysis={}
    )
    
    result = graph.invoke(initial_state)
    return result
