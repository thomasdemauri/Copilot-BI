from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from graph.state import AgentState
from graph.nodes import unified_analysis_node


def should_continue(state: AgentState) -> str:
    """Decide se deve executar tools ou terminar."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Se a última mensagem tem tool_calls, executar tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Se já executou pelo menos uma tool (ToolMessage presente), terminar
    from langchain_core.messages import ToolMessage
    has_tool_message = any(isinstance(msg, ToolMessage) for msg in messages)
    
    if has_tool_message:
        return "end"
    
    # Caso contrário, continuar
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
    
    # Depois de executar tools, volta para análise uma vez apenas
    graph.add_edge("tools", "unified_analysis")

    return graph.compile()
