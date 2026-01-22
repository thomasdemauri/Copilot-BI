from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from graph.state import AgentState
from graph.nodes import agent_node

def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "continue"
    return "end"

def build_graph(agent, tools):
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node(agent))
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )

    graph.add_edge("tools", "agent")

    return graph.compile()
