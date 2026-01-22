from langchain_core.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage
from langchain_community.utilities import SQLDatabase

def build_sql_tool(context):
    """Factory to create the tool with context injected."""
    
    @tool
    def do_sql_query(query: str):
        """This tool is responsible for making a consult to database and
        performing a query."""

        raw_engine = context.db
        model = context.llm

        db = SQLDatabase(raw_engine)
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        sql_tools = toolkit.get_tools()

        sql_agent = create_agent(model, tools=sql_tools)

        result = sql_agent.invoke({
            "messages": [
                SystemMessage(content="""
                    You are an agent designed to interact with a SQL database.
                    Given an input question, create a syntactically correct dialect query to run,
                    then look at the results of the query and return the answer. Unless the user
                    specifies a specific number of examples they wish to obtain, always limit your
                    query to at most 15 results.

                    You can order the results by a relevant column to return the most interesting
                    examples in the database. Never query for all the columns from a specific table,
                    only ask for the relevant columns given the question.

                    You MUST double check your query before executing it. If you get an error while
                    executing a query, rewrite the query and try again.

                    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
                    database.

                    To start you should ALWAYS look at the tables in the database to see what you
                    can query. Do NOT skip this step.
                              
                    Mandatory execution strategy:
                        1. First, check which tables exist in the database using the appropriate tool.
                        2. Then, inspect the schema (columns and data types) of the table(s) that appear most relevant.
                        3. Only after that, construct and execute the SQL query.

                    Then you should query the schema of the most relevant tables.

                    Whenever you encounter a column that looks like an ID (e.g., customer_id, product_id) and it has a relationship with another table (foreign key), you MUST retrieve the human-readable value associated with that ID, such as the name or description. Do not return the ID alone. Always follow the relationship to show the meaningful value instead of just the ID.
                    """
                ),HumanMessage(content=query)
            ]
        })

        return {"response": result["messages"][-1].content}

    return do_sql_query