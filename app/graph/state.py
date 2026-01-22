from dataclasses import dataclass
from typing import Annotated, Sequence, TypedDict
from langgraph.graph.message import add_messages
from langchain.messages import AnyMessage
from langchain_openai import ChatOpenAI

@dataclass
class ContextSchema:
    llm: ChatOpenAI
    db: any

class AgentState(TypedDict):
    messages: Annotated[Sequence[AnyMessage], add_messages]
    insight: str