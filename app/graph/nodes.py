from graph.state import AgentState
from langchain.messages import HumanMessage, SystemMessage
from langchain.agents import create_agent

def agent_node(agent):
    def _node(state: AgentState):
        prompt = """"
            "REPORTING GUIDELINES:
            Clarity & Objectivity: Get straight to the point. Focus on the insight, not just the numbers.
            NO TABLES: You are strictly forbidden from rendering tables (e.g., using pipes | or rows).
            List Format: Present all findings, breakdowns, and data comparisons using bulleted lists (Markdown * or -)."
        """;
        
        state["messages"].append(SystemMessage(content=prompt))
        response = agent.invoke(state["messages"])
        return {"messages": [response]}
    
    return _node

def insight_node(model, tools):
    def _node(state: AgentState):
        prompt = """
            You are a Senior Data Strategist & Root Cause Investigator.
            Your goal is not to report *what* happened, but *precisely why* it happened by identifying the Dominant Drivers.

            Dominant Driver Test (Composição)

            Hipótese: Um subgrupo específico provavelmente está pesando no resultado.

            Ação: Execute um SQL para GROUP BY dimensões baixas (ex.: Produto, Cidade, Subcategoria) e ordene pelo valor do métrico.

            Meta: Identificar se uma entidade contribui >50%.

            Ex.: "O lucro caiu, principalmente por uma queda de -40% em 'Mesas', enquanto o restante das categorias se manteve estável."

            Volatility Check (Se houver data)

            Verifique se a tabela possui coluna de data.

            Se sim, agrupe por mês/ano para identificar quando a mudança ocorreu e se foi gradual ou abrupta.

            Se não, pule essa etapa.

            Contextual Benchmark

            Compare o Dominant Driver com o resto do conjunto.

            Ex.: "Enquanto 'Smartphones' cresceram 20%, o restante da loja ficou estável (0%)."

            ### FINAL CONSTRAINT:
            - You **MUST** execute a SQL query that breaks the data down by a Dimension (Category, Region, etc.) or Time (if available) to prove your insight.
            - You MUST execute at least one new SQL query to investigate the 'Why'.
            - IF a Date column exists, prioritize a Trend query. IF NOT, prioritize a Composition query.
            - Do NOT provide generic insights like "This is higher than average" without explaining the driver.
            - Do NOT put a separation "insight". Just provide the final insight directly.
        """

        agent = create_agent(model, tools=tools)
        messages = state["messages"] + [SystemMessage(content=prompt)]
        result = agent.invoke({"messages": messages})

        final_insight = result["messages"][-1].content
        
        return {"insight": final_insight}

    return _node