from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from graph.state import AgentState
from graph.nodes import agent_node
from graph.nodes import insight_node
from langchain.messages import ToolMessage


def router(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    
    messages = state["messages"]
    has_used_tool = any(isinstance(m, ToolMessage) for m in messages)

    if has_used_tool:
        return "insight"
    
    return "end"

def build_graph(agent, tools, llm):
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node(agent))
    graph.add_node("insight_generator", insight_node(llm, tools))
    graph.add_node("tools", ToolNode(tools))

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        router,
        {
            "tools": "tools",
            "insight": "insight_generator",
            "end": END
        }
    )

    graph.add_edge("tools", "agent")
    graph.add_edge("insight_generator", END)

    return graph.compile()
