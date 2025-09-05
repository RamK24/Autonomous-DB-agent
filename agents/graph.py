from agents.intent_agent import IntentAgent
from agents.tool_calling_agent import ToolCallingAgent
from agents.slot_filling_agent import ClarifyAgent
from langgraph.graph import StateGraph, START, END
from utils.utils_repo import llm, llm_tools, MessageState, TOOLS
from langgraph.prebuilt import ToolNode, tools_condition
from agents.routes import route_from_intent, route_from_tool_call, route_from_slot_fill


def init_agents():
    intent_agent = IntentAgent(llm, llm_tools)
    tool_calling_agent = ToolCallingAgent(llm, llm_tools)
    slot_filling_agent = ClarifyAgent(llm, llm_tools)
    return intent_agent, tool_calling_agent, slot_filling_agent


def get_graph():

    intent_agent, tool_calling_agent, slot_filling_agent = init_agents()
    builder = StateGraph(MessageState)
    builder.add_node("process_intent", intent_agent.process_intent)
    builder.add_node("tool_call", tool_calling_agent.process_tool_call)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("slot_fill", slot_filling_agent.process_clarity)
    # edges
    builder.add_edge(START, "process_intent")
    builder.add_conditional_edges("process_intent", route_from_intent, {'EXIT': END,
                                                                        'tool_call': 'tool_call', 'IRRELEVANT': END})
    builder.add_conditional_edges("tool_call", route_from_tool_call)
    builder.add_edge("slot_fill", END)
    return builder


def compile_graph(graph):
    return graph.compile()







