from datetime import datetime
from typing import Annotated

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from langgraph.utils.runnable import RunnableCallable
from typing_extensions import TypedDict

from llm_models import SupportedLLMs, get_llm
from reservations import book_table, cancel_reservation, list_time_slots


class State(TypedDict):
    messages: Annotated[list, add_messages]


class Agent:
    def __init__(self, llm: BaseChatModel) -> None:
        self._llm = llm

    @property
    def _prompt(self) -> RunnableCallable:
        content = f""" You are a helpfull restaurant assistant responsible for reservations.

                    You need to follow this rules:
                    1. Choose your action using the tools that are available to you.
                    2. If there is no tool to call with the user request, ask for more context about what the user want.
                    3. Always elaborate a complete response to the user.
                    4. Never reference our tools to the user
                    5. Don't make up any rules for cancellation or scheduling
                                                
                    Name of the restaurant: Tastes of Brazil
                    Current Date: {datetime.now()}
                    """
        system_message = SystemMessage(content=content)
        return RunnableCallable(lambda state: [system_message] + state, name="Prompt")

    def conditional_router(self, state: State) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def call_model(self, state: State) -> State:
        assistant_runnable = self._prompt | self._llm.bind_tools(
            [list_time_slots, book_table, cancel_reservation]
        )
        response = assistant_runnable.invoke(state["messages"])
        return {"messages": [response]}

    def build_agent(self) -> CompiledStateGraph:
        graph_builder = StateGraph(state_schema=State)
        graph_builder.add_node(node="call_model", action=self.call_model)
        graph_builder.add_node(
            node="tools",
            action=ToolNode([list_time_slots, book_table, cancel_reservation]),
        )

        graph_builder.add_edge(start_key=START, end_key="call_model")
        graph_builder.add_conditional_edges(
            source="call_model", path=self.conditional_router, path_map=["tools", END]
        )
        graph_builder.add_edge(start_key="tools", end_key="call_model")

        return graph_builder.compile()


def stream_graph_updates(graph: CompiledStateGraph, user_input: str) -> None:
    messages = {"messages": [("user", user_input)]}
    events = graph.invoke(messages, stream_mode="values")
    print(f"Assistant: {events['messages'][-1].content}")


def main() -> None:
    llm = get_llm(llm_model=SupportedLLMs.llama3_1)
    chatbot = Agent(llm=llm)
    graph = chatbot.build_agent()

    print("Assistant: Welcome to Tastes of Brazil! How can I help you today?")
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit"]:
                print("Goodbye!")
                break

            stream_graph_updates(graph=graph, user_input=user_input)
        except Exception as e:
            print(f"Error {e}")


if __name__ == "__main__":
    main()
