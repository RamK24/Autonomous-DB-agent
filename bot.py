from utils.utils_repo import MessageState
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import AIMessage, ToolMessage
from agents.graph import get_graph, compile_graph
import os
from datetime import datetime
import json

IRRELEVANT_PROMPT = "Assistant: I am sorry, I cannot assist you with that. Please request a mentioned action"


class TaskManager:
    """
    Manages tasks in memory and batch saves to JSON when limit is reached.
    """

    def __init__(self, save_limit=2):
        """
        Initialize task manager.

        Args:
            json_file: JSON file to save tasks
            save_limit: Number of tasks before saving to file
        """
        self.save_limit = save_limit
        self.tasks = []

    def structure_json(self, messages):
        """Structure the task data from messages."""
        tool_call_msg = messages["messages"][-2]
        tool_result = messages["messages"][-1]
        tasks = []

        for tool_call in tool_call_msg.tool_calls:
            info = {
                'task_name': tool_call['name'],
                'parameters': tool_call['args'],
                'result': tool_result.content,
                'timestamp': datetime.now().isoformat()
            }
            tasks.append(info)
        return tasks

    def add_task(self, messages: MessageState):
        """
        Add completed task to memory and auto-save when limit reached.

        Args:
            messages: Current message state

        Returns:
            bool: True if task was added, False otherwise
        """

        new_tasks = self.structure_json(messages)

        for task in new_tasks:
            self.tasks.append(task)
        if len(self.tasks) >= self.save_limit:
            self.save_and_empty()

        return True

    def save_and_empty(self):
        """Save current tasks to JSON file and empty the tasks list."""
        if not self.tasks:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = f"tasks_batch_{timestamp}.json"

        with open(archive_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

        self.tasks = []

    def get_task_count(self):
        """Get current number of tasks in memory."""
        return len(self.tasks)

    def get_current_tasks(self):
        """Get current tasks in memory."""
        return self.tasks.copy()

class JiraBOT:
    """
    A bot that processes messages using a compiled state graph.

    This bot handles user interactions through a graph-based processing system,
    managing conversation state and intent classification.
    """

    def __init__(self, graph: CompiledStateGraph):
        """
        Initialize the JiraBOT with a compiled state graph.

        Args:
            graph (CompiledStateGraph): The compiled graph for message processing
        """
        self.graph = graph

    def process(self, messages):
        """
        Process messages through the state graph.

        Args:
            messages: Message state containing conversation history

        Returns:
            Updated message state after processing
        """
        return self.graph.invoke(messages)


def append_message(messages, message):
    """
    Append a message to the messages list.

    Args:
        messages: Message state dictionary
        message: Message object to append
    """
    messages["messages"].append(message)


def get_user_input(prompt="Human: "):
    """
    Get user input with a given prompt.

    Args:
        prompt (str): The prompt to display to the user

    Returns:
        str: Stripped user input
    """
    return input(prompt).strip()


def handle_clarification(bot, messages):
    """
    Handle clarification requests from the bot.

    Args:
        bot (JiraBOT): The bot instance
        messages: Message state

    Returns:
        Updated message state after clarification
    """
    last_message = messages["messages"][-1]
    print("Assistant: ", last_message.content)

    user_input = get_user_input()
    append_message(messages, HumanMessage(content=user_input))
    messages['agent_intent'] = ''
    messages['intent'] = ''
    return bot.process(messages)


def handle_irrelevant_intent(bot, messages):
    """
    Handle irrelevant intent responses.

    Args:
        bot (JiraBOT): The bot instance
        messages: Message state

    Returns:
        Updated message state after handling irrelevant intent
    """
    messages['intent'] = ''
    print(IRRELEVANT_PROMPT)
    append_message(messages, AIMessage(content=IRRELEVANT_PROMPT))

    user_input = get_user_input()
    append_message(messages, HumanMessage(content=user_input))

    return bot.process(messages)


def initialize_bot():
    """
    Initialize and return a JiraBOT instance with compiled graph.

    Returns:
        JiraBOT: Initialized bot instance
    """
    builder = get_graph()
    graph = compile_graph(builder)
    return JiraBOT(graph)


def trim_history_for_llm(messages, normal_limit=5, extended_limit=7):
    """
    Trim message history for LLM context.

    Args:
        messages: Message state dictionary
        normal_limit: Keep last 10 messages normally
        extended_limit: Extend to 20 if no ToolMessage in recent 10

    Returns:
        Updated messages with trimmed history
    """
    current_messages = messages["messages"]

    if len(current_messages) <= normal_limit:
        return messages

    recent_messages = current_messages[-normal_limit:]
    has_tool_message = any(isinstance(msg, ToolMessage) for msg in recent_messages)

    if has_tool_message:
        messages["messages"] = current_messages[-normal_limit:]
        print(f"Trimming")
    else:
        if len(current_messages) > extended_limit:
            messages["messages"] = current_messages[-extended_limit:]
            print(f" Trimmed to {extended_limit} messages (no recent ToolMessage)")

    return messages


def run_conversation_loop():
    """
    Run the main conversation loop with the bot.

    This function handles the interactive chat session, processing user input
    and managing different conversation states including clarifications and
    irrelevant queries.
    """
    messages = {"messages": []}
    bot = initialize_bot()
    task_manager = TaskManager()
    while True:
        user_query = get_user_input()
        append_message(messages, HumanMessage(content=user_query))
        # messages = trim_history_for_llm(messages)
        messages = bot.process(messages)
        if isinstance(messages['messages'][-1], ToolMessage):
            task_manager.add_task(messages)

        if messages.get("agent_intent") == 'clarify':
            messages = handle_clarification(bot, messages)

        if messages.get('intent') == "IRRELEVANT":
            messages = handle_irrelevant_intent(bot, messages)

        print(messages['messages'][-1].content)


if __name__ == "__main__":
    run_conversation_loop()
