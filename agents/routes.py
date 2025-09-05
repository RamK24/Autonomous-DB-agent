import json
from utils.utils_repo import INTENTS
from langgraph.graph import END
from utils.utils_repo import MessageState


def route_from_intent(messages: MessageState):
    """
    Determines the next node based on the classified intent.

    This function acts as a conditional edge in the state graph. It checks the 'intent'
    field in the message state. If the intent is a recognized tool-related action,
    it returns the intent string to route to the appropriate node (e.g., 'tool_call').
    Otherwise, it routes to an exit node.

    Args:
        messages (MessageState): The current state of the graph, which includes
                                 the classified 'intent'.

    Returns:
        str: The name of the next node to execute ('tool_call') or 'EXIT' to terminate.
    """
    if messages['intent'] in INTENTS:
        return messages['intent']
    else:
        return "EXIT"


def route_from_tool_call(messages: MessageState):
    """
    Routes to the next step after the tool calling agent has processed the query.

    This function inspects the last message in the state to decide the path:
    1.  If the message contains `tool_calls`, it means a function can be executed,
        so it routes to the 'tools' node.
    2.  If the message content is a JSON string (indicating a partial match with
        missing parameters), it routes to the 'slot_fill' node to gather the
        missing information.
    3.  If neither of the above is true, it routes to the end of the graph.

    Args:
        messages (MessageState): The current state of the graph.

    Returns:
        str: The name of the next node: 'tools', 'slot_fill', or the END sentinel.
    """
    response = messages["messages"][-1]
    if response.tool_calls:
        return "tools"
    try:
        # Check if the response content is a JSON indicating missing parameters
        func_def = json.loads(response.content)
    except (json.JSONDecodeError, TypeError):
        func_def = {}

    if isinstance(func_def, dict) and response.content:
        return 'slot_fill'
    else:
        return END


def route_from_slot_fill(messages: MessageState):
    """
    Determines the next step after the slot-filling process.

    This function checks if the slot-filling agent successfully enhanced the user's
    query. It does this by looking for an 'enhanced_by_llm' flag in the last
    message's additional keyword arguments.

    - If the flag is True, it routes back to 'tool_call' to re-attempt the tool call
      with the now-complete information.
    - If the flag is False or absent, it means slot filling was unsuccessful or
      timed out, and the process terminates by routing to END.

    Args:
        messages (MessageState): The current state of the graph.

    Returns:
        str: The name of the next node ('tool_call') or the END sentinel.
    """
    last_message = messages["messages"][-1]
    if last_message.additional_kwargs.get('enhanced_by_llm', False):
        return 'tool_call'
    else:
        return END