from abc import ABC, abstractmethod
from langchain_core.messages import SystemMessage
from utils.utils_repo import MessageState


class BaseAgent(ABC):
    def __init__(self, llm, llm_tools):
        self.llm = llm
        self.llm_tools = llm_tools

    def invoke_llm(self, state: MessageState):
        system_message = SystemMessage(self._get_system_message())
        # state["messages"] = [system_message] + state["messages"]
        response = self.llm.invoke([system_message] + state["messages"])
        response.content = self.remove_thoughts(response.content)
        return response

    def invoke_llm_tools(self, state: MessageState):
        system_message = SystemMessage(self._get_system_message())
        # state["messages"] = [system_message] + state["messages"]
        response = self.llm_tools.invoke([system_message] + state["messages"])
        response.content = self.remove_thoughts(response.content)
        return response

    @staticmethod
    def append_to_state(state: MessageState, message):
        state['messages'].append(message)

    @staticmethod
    def remove_thoughts(response):
        end_id = response.find('</think>')
        response = response[end_id + len('</think>'):]
        response = response.strip().strip('\n').strip('.')
        return response

    def _get_system_message(self) -> str:
        pass









