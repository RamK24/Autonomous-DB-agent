from langchain_ollama import ChatOllama
from tools.ticket_tools import view_ticket, create_ticket
from tools.user_tools import create_user
from langgraph.graph.message import add_messages
from typing import TypedDict, List, Union, Annotated
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

DB_name = "jira_ticketing.db"
MODEL_ID = "qwen3:14b"
INTENTS = ["tool_call", "END"]
TOOLS = [create_user, create_ticket, view_ticket]


llm = ChatOllama(
    model=MODEL_ID,
    temperature=0.1, verbose=True
)
llm_tools = llm.bind_tools(TOOLS)


class MessageState(TypedDict):
    messages: Annotated[List[Union[HumanMessage, AIMessage, SystemMessage, ToolMessage]], add_messages]
    intent: str




