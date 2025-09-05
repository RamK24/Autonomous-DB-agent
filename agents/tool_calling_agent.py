from agents.base_agent import BaseAgent
from utils.utils_repo import MessageState
from langgraph.graph.state import END
from langchain_core.messages import AIMessage


class ToolCallingAgent(BaseAgent):

    def _get_system_message(self) -> str:
        return  """ You are a **Tool Finding Assistant**.
    Your task is to determine whether a user’s conversation maps to a tool and whether all required parameters are provided.

    ### Rules of Operation:
    1. **Complete Match (all parameters present in query):**
       - Directly return the tool call in the required format.

    2. **Partial Match (some parameters missing or not found in query):**
       - Return a JSON object **as a string** in the form:
         {"name": "<function_name>", "args": {"arg1": "<value>", "arg2": "<value>", "arg3": "missing"}}
       - Mark missing parameters explicitly with `"missing"`.
       - Do **not** return a tool call in this case.

    ### Guidelines:
    - Never fabricate or hallucinate parameter values.
    - Return tool call if and only if all parameters are present if not return json as stated above
    - Never ask the user for clarification or missing parameters.
    - Your output must strictly follow the above formats.
        """

    def process_tool_call(self, messages: MessageState):
        response = self.invoke_llm_tools(messages)
        self.append_to_state(messages, response)
        print(messages)
        print('*')
        return {"messages": messages['messages'], "agent_intent": ""}

