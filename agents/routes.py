import json
from utils.utils_repo import INTENTS
from langchain_core.messages import ToolMessage, HumanMessage
from langgraph.graph import END
from utils.utils_repo import MessageState
from agents.slot_filling_agent import SlotFillingAgent
from utils.utils_repo import llm, llm_tools

MAX_RETRIES = 3
slot_agent = SlotFillingAgent(llm, llm_tools)


def route_from_intent(messages: MessageState):
    if messages['intent'] in INTENTS:
        return messages['intent']
    else:
        return END


def route_from_tool_call(messages: MessageState):
    response = messages["messages"][-1]
    if response.tool_calls:
        return "tools"
    try:
        func_def = json.loads(response.content)
    except:
        func_def = {}

    if isinstance(func_def, dict) and response.content:
        return 'slot_fill'
    else:
        return END


def route_from_slot_fill(messages: MessageState):
    last_message = messages["messages"][-1]
    if last_message.additional_kwargs.get('enhanced_by_llm', False):
        return 'tool_call'
    else:
        return END




