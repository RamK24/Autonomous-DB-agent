from agents.base_agent import BaseAgent
import json
from langchain_core.messages import HumanMessage, AIMessage
from utils.utils_repo import MessageState


class ClarifyAgent(BaseAgent):

    def _get_system_message(self) -> str:
        return """
        You are a clarity requesting agent.

        You will always be provided with two inputs:
        1. A partially filled function call (some arguments would be missing) in the format of JSON.
        2. A conversation history between the user and the assistant.

        Your task:
        - Ask the user for clarification on the missing arguments.
        - You will explain the args in natural language and ask them for their input.
        
        - eg:  {"name": "multiply", "args": {"a": 2, "b": "missing"}}, user_query: multiply 2
        You request the user saying something like, I need a second number to multiply with 2.
        Important:
        - Never guess or make up values. Only extract what is explicitly mentioned in the conversation.
        - Dont add any extra punctuations or extra stuff.
        """

    def process_clarity(self, messages: MessageState):
        response = self.invoke_llm(messages)
        return {'messages': response, 'agent_intent': 'clarify'}


