import os
from dotenv import load_dotenv
from langchain.messages import HumanMessage
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

agent, tools = build_agent(API_KEY, context=context)
app = build_graph(agent, tools)

database = excel_to_db(engine=engine)

result = app.invoke({
    "messages": [
        HumanMessage(content="Whate are the most profits orders?")
    ]
}, context=context)

print(result["messages"][-1].content)

# for chunk in app.stream({"messages": [HumanMessage(content="Which are all the customers?")]}, stream_mode="updates"):
#     print(chunk)
