from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import MessagesState, START, StateGraph
from typing import TypedDict


class CounterState(TypedDict):
    count: int


def _build_counter(checkpointer):
    graph_builder = StateGraph(CounterState)
    graph_builder.add_node("increment", lambda state: {"count": state["count"] + 1})
    graph_builder.add_edge(START, "increment")
    return graph_builder.compile(checkpointer=checkpointer)


def test_checkpoint_survives_reopening_sqlite_database(tmp_path):
    database_path = tmp_path / "conversations.sqlite"
    config = {"configurable": {"thread_id": "customer-123"}}

    with SqliteSaver.from_conn_string(str(database_path)) as checkpointer:
        graph = _build_counter(checkpointer)
        graph.invoke({"count": 0}, config)
        assert graph.get_state(config).values["count"] == 1

    with SqliteSaver.from_conn_string(str(database_path)) as checkpointer:
        graph = _build_counter(checkpointer)
        assert graph.get_state(config).values["count"] == 1


def test_guardrail_turn_can_be_saved_without_running_graph(tmp_path):
    database_path = tmp_path / "guardrails.sqlite"
    graph_builder = StateGraph(MessagesState)
    graph_builder.add_node("noop", lambda _state: {})
    graph_builder.add_edge(START, "noop")
    config = {"configurable": {"thread_id": "guardrail-thread"}}

    with SqliteSaver.from_conn_string(str(database_path)) as checkpointer:
        graph = graph_builder.compile(checkpointer=checkpointer)
        graph.update_state(
            config,
            {
                "messages": [
                    HumanMessage(content="pedido fora de escopo"),
                    AIMessage(content="recusa"),
                ]
            },
        )
        messages = graph.get_state(config).values["messages"]

    assert [message.content for message in messages] == ["pedido fora de escopo", "recusa"]
