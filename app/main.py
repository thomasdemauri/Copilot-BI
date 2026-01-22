import os
from dotenv import load_dotenv
from langchain.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from agents.sql_agent import build_agent
from graph.graph import build_graph
from graph.state import ContextSchema
from helpers.panda import excel_to_db
from db.mysql import create_mysql_engine

load_dotenv()

API_KEY = os.getenv("API_KEY")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DATABASE = os.getenv("DATABASE")

engine = create_mysql_engine(user=USER, password=PASSWORD, host=HOST, port=PORT, database=DATABASE)
context=ContextSchema(llm=None, db=engine)

agent, tools, model = build_agent(API_KEY, context=context)
app = build_graph(agent, tools, model)

database = excel_to_db(engine=engine)

result = app.invoke({
    "messages": [
        HumanMessage(content="Which region is the most profitable?")
    ]
}, context=context)

print(result["messages"][-1].content)
print("#### INSIGHT ABAIXO ####")
print(result["insight"])

# def print_chunk_nice(chunk):
#     """Imprime cada chunk de forma organizada dependendo do tipo."""
#     if isinstance(chunk, ToolMessage):
#         print("\n=== TOOL MESSAGE ===")
#         print(f"Tool Name: {chunk.tool_name}")
#         print(f"Content: {chunk.content}")
#     elif isinstance(chunk, AIMessage):
#         print("\n=== AI MESSAGE ===")
#         print(chunk.content)
#     elif isinstance(chunk, HumanMessage):
#         print("\n=== HUMAN MESSAGE ===")
#         print(chunk.content)
#     elif isinstance(chunk, SystemMessage):
#         print("\n=== SYSTEM MESSAGE ===")
#         print(chunk.content)
#     else:
#         print("\n=== UNKNOWN MESSAGE TYPE ===")
#         print(chunk)

        
# for chunk in app.stream({"messages": [HumanMessage(content="Which customers is the most profitable?")]}, stream_mode="updates"):
#     print_chunk_nice(chunk)

