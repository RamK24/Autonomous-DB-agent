from agents.base_agent import BaseAgent
from utils.utils_repo import MessageState, INTENTS
from langchain_core.messages import HumanMessage

MAX_RETRIES = 3


class IntentAgent(BaseAgent):

    def _get_system_message(self) -> str:
        return """
        You are an intent classifier for the Jira application.

    Your task:
    - Read the user’s query carefully.
    - Determine the user’s intent.

    Available intents:
    1. **tool_calling** -> Respond exactly with: "tool_call"
    If the user is requesting to perform one of these functions [create_user, create_ticket, view_ticket]

    2. If user’s query does not require any tool call and is requesting something irrelevant other than requesting above
     mentioned tasks, Respond naturally stating something like I can't assist with the task. Would you like help with something
      else? something along these lines. Keep the response natural.

    3. Return **EXIT** if the user intends to end the conversation or doesn't need help with anything or has achieved
    his task.

    Rules:
    - Respond the intent value ("tool_call") when a tool matches.
    - When user greets be polite and then asks what he needs help with.
    - Respond with EXIT if the user intends to end the conversation or doesn't need help with anything or has achieved
      his task.
    - Do not add any explanations, extra text, or punctuation.
    - Be precise and conservative — classify as "tool_call" only if user query means using one of these functions
    [create_user, create_ticket, view_ticket].

    """

    def process_intent(self, messages: MessageState):
        curr_tries = 0
        response = None
        while curr_tries <= MAX_RETRIES:
            response = self.invoke_llm(messages)
            if response.content in INTENTS or response.content.strip('\n').strip() == "EXIT":
                return {'messages': messages["messages"], 'intent': response.content}

            curr_tries += 1
            print('\n', 'Assistant: ', response.content, '\n')
            user_input = input("Human:")
            self.append_to_state(messages, HumanMessage(content=user_input))
        return {'messages': messages["messages"], 'intent': response.content}



