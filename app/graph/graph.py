from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from graph.state import AgentState
from graph.nodes import unified_analysis_node


def should_continue(state: AgentState) -> str:
    """Decide se deve executar tools ou terminar."""
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return "end"


def build_graph(agent, tools, llm):
    """Grafo simplificado com análise unificada em um único nó."""
    graph = StateGraph(AgentState)

    # Nó de análise e nó de execução de tools
    graph.add_node("unified_analysis", unified_analysis_node(agent, tools))
    graph.add_node("tools", ToolNode(tools))
    
    # Entrada
    graph.set_entry_point("unified_analysis")
    
    # Rotas condicionais
    graph.add_conditional_edges(
        "unified_analysis",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # Depois de executar tools, volta para análise
    graph.add_edge("tools", "unified_analysis")

    return graph.compile()
