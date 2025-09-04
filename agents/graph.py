from agents.intent_agent import IntentAgent
from agents.tool_calling_agent import ToolCallingAgent
from agents.slot_filling_agent import SlotFillingAgent
from langgraph.graph import StateGraph, START, END
from utils.utils_repo import llm, llm_tools, MessageState, TOOLS
from langgraph.prebuilt import ToolNode, tools_condition
from agents.routes import route_from_intent, route_from_tool_call, route_from_slot_fill


def init_agents():
    intent_agent = IntentAgent(llm, llm_tools)
    tool_calling_agent = ToolCallingAgent(llm, llm_tools)
    slot_filling_agent = SlotFillingAgent(llm, llm_tools)
    return intent_agent, tool_calling_agent, slot_filling_agent


def get_graph():

    intent_agent, tool_calling_agent, slot_filling_agent = init_agents()
    builder = StateGraph(MessageState)
    builder.add_node("process_intent", intent_agent.process_intent)
    builder.add_node("tool_call", tool_calling_agent.process_tool_call)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("slot_fill", slot_filling_agent.process_slot_filling)
    # edges
    builder.add_edge(START, "process_intent")
    builder.add_conditional_edges("process_intent", route_from_intent)
    builder.add_conditional_edges("tool_call", route_from_tool_call)
    builder.add_conditional_edges("slot_fill", route_from_slot_fill)  # tries 3 times to extract information
    builder.add_edge("tool_call", "tools")
    builder.add_edge("tools", END)
    return builder


def compile_graph(graph):
    return graph.compile()







