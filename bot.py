from utils.utils_repo import MessageState
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from agents.graph import get_graph, compile_graph
actions = []
intents = {'create_user': 'create_user'}


class JiraBOT:

    def __init__(self, graph: CompiledStateGraph):
        self.graph = graph

    def process(self, messages):
        return self.graph.invoke(messages)


if __name__ == "__main__":
    messages = {"messages": []}
    builder = get_graph()
    graph = compile_graph(builder)
    bot = JiraBOT(graph)
    user_query = input('Human: ')
    user_query = user_query.strip()
    messages["messages"].append(HumanMessage(content=user_query))
    messages = bot.process(messages)
    print(messages["messages"])







