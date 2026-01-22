from graph.state import AgentState
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent

def agent_node(agent):
    def _node(state: AgentState):
        response = agent.invoke(state["messages"])
        return {"messages": [response]}
    return _node

def insight_node(model, tools):
    def _node(state: AgentState):
        prompt = """
            You are a Senior Data Strategist. 
            Your mission is to explain the ROOT CAUSE of the data, not just compare it to the average.

            INVESTIGATION PROTOCOL (Follow this priority):

            1. COMPOSITION ANALYSIS (High Priority):
            - If the result is a specific entity (e.g., a Customer or Region), investigate WHAT drives their performance.
            - ACTION: Use SQL to Group By 'Category', 'Sub-Category', or 'Segment'.
            - Example: "Tamara's profit comes 90% from Technology products, not Office Supplies."

            2. TREND ANALYSIS (Medium Priority):
            - Is this performance consistent over time or a one-off spike?
            - ACTION: Use SQL to Group By Year or Month.

            3. BENCHMARKING (Low Priority):
            - Compare with the global average ONLY if composition or trends reveal no specific patterns.

           Use the following structured patterns to guide your investigation and derive actionable insights. 
            These patterns are examples of how to ask investigative questions. You can adapt them or create similar approaches 
            as needed to uncover root causes in the data.
                1. THE PARETO TEST (Concentration):
                    - Question: "Is the performance concentrated in a few top entities?"
                    - Action: Group by the main categorical column and check if the top 20% generate 80% of the results.
                    - Insight Ex: "Action is needed as 80% of the output comes from only 3 sources, representing high risk."

                2. THE TREND TEST (Volatility):
                    - Question: "Is the result stable, growing, or volatile over time?"
                    - Action: If a date column exists, group results by Month/Year.
                    - Insight Ex: "The total is high, but it has been declining for the last 3 periods."

                3. THE OUTLIER TEST (Anomalies):
                    - Question: "Is there any entity performing significantly above/below the standard deviation?"
                    - Action: Compare the specific result against the average of its group.
                    - Insight Ex: "Item X is an anomaly, performing 300% above the category average."

                4. THE MIX TEST (Composition):
                    - Question: "What is the internal composition of this result?"
                    - Action: Drill down into sub-categories or segments.

            CONSTRAINT:
            - You MUST execute at least one new SQL query to investigate the 'Why'.
            - Do NOT provide generic insights like "This is higher than average" without explaining the driver.
        """

        agent = create_agent(model, tools=tools)
        messages = state["messages"] + [SystemMessage(content=prompt)]
        result = agent.invoke({"messages": messages})

        final_insight = result["messages"][-1].content
        
        return {"insight": final_insight}

    return _node