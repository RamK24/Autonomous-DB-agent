from agents.base_agent import BaseAgent
import json
from langchain_core.messages import HumanMessage, AIMessage
from utils.utils_repo import MessageState


class SlotFillingAgent(BaseAgent):
    MAX_RETRIES = 3

    def _get_system_message(self) -> str:
        return """
        You are a user query enhancer based on slot-filling assistant.

        You will always be provided with two inputs:
        1. A partially filled function call (some arguments would be missing) in the format of JSON.
        2. A conversation history between the user and the assistant.

        Your task:
        - Identify if the missing argument(s) can be inferred from the conversation.
        - If you find a candidate value, present it back to the user for confirmation (e.g., “Say ID argument is missing
        and you found out that the argument ID to be 123 from conversation, you respond: <Is the ID 123 ?>”).
        - Once the user confirms, Your job based on the conversation is to improve the user query with missing arguments
        so it is understandable and clear and has all the details.
        For example, if available tools are multiply and it accepts a, b as arguments and
        user asks `what is the product 2 ?`, If you've confirmed the second argument to be 12. You return
        "what is the product of 2 and 12 ?"

        - If the missing argument information is no where to be found. You return an empty string "" and not '""' or "''"

        Important:
        - Never guess or make up values. Only extract what is explicitly mentioned in the conversation.
        - Always ask the user for confirmation before finalizing the JSON response.
        - Dont add any extra punctuations or extra stuff.
        """

    def process_slot_filling(self, messages: MessageState):
        curr_tries = 1
        last_message = messages["messages"][-1]
        func_def = json.loads(last_message.content)
        while curr_tries <= SlotFillingAgent.MAX_RETRIES:
            prompt = (f"Assistant: Sure, Your request is missing these parameters: "
                      f"{[param for param in func_def['args'] if func_def['args'][param] == 'missing']}. Provide "
                      f"these parameters to finish the action")
            print('\n', prompt, '\n')
            user_input = input('Human: ')
            self.append_to_state(messages, AIMessage(content=prompt))
            self.append_to_state(messages, HumanMessage(content=user_input))
            response = self.invoke_llm(messages)
            if response.content and response.content not in ['""', "''"]:
                response.additional_kwargs['enhanced_by_llm'] = True
                self.append_to_state(messages, response)
                return {'messages': messages["messages"]}
            else:
                curr_tries += 1
        return {'messages': messages["messages"]}


