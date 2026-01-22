from langchain_openai import ChatOpenAI
from tools.sql_tool import build_sql_tool
from graph.state import ContextSchema

def build_agent(api_key: str, context: ContextSchema):
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=api_key, 
        verbose=True,
        cache=None
    )

    sql_tool = build_sql_tool(context)
    context.llm = model
    model_with_tools = model.bind_tools([sql_tool])

    return model_with_tools, [sql_tool], model