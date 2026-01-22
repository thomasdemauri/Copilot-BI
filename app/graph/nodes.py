from graph.state import AgentState

def agent_node(agent):
    def _node(state: AgentState):
        response = agent.invoke(state["messages"])
        return {"messages": [response]}
    return _node
