from agents.base_agent import BaseAgent
from utils.utils_repo import MessageState, INTENTS
from langchain_core.messages import HumanMessage

MAX_RETRIES = 3


class IntentAgent(BaseAgent):

    def _get_system_message(self) -> str:
        return """
        You are an intent classifier for the Jira application. You will be provided with a conversation.

    Your task:
    - Read the user’s query carefully.
    - Determine the user’s intent.

    Available intents:
    1. **tool_calling** -> Respond exactly with: "tool_call"
    If the user is requesting to perform one of these functions [create_user, create_ticket, view_ticket]

    2. Return **IRRELEVANT** if the user's query is requesting something outside these actions.

    3. Return **EXIT** if the user intends to end the conversation or doesn't need help with anything or has achieved
    his task.
    

    Rules:
    - Respond the intent value ("tool_call") when a tool matches.
    - Respond with EXIT if the user intends to end the conversation or doesn't need help with anything or has achieved
      his task.
    - Respond with IRRELEVANT if the user intent belong to something other than the mentioned functions.
    - INTENTS you return should be only in (EXIT, IRRELEVANT, tool_call) and nothing else.
    - Do not add any explanations, extra text, or punctuation.
    - Be precise and conservative — classify as "tool_call" only if user query means using one of these functions
    [create_user, create_ticket, view_ticket].

    """

    def process_intent(self, messages: MessageState):
        response = self.invoke_llm(messages)
        return {'messages': messages["messages"], 'intent': response.content, "agent_intent": ""}




