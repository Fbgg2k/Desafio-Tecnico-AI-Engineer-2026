import pytest
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from pydantic import Field

from src.agent import workflow


class ToolCallingFakeModel(FakeMessagesListChatModel):
    bound_tool_names: list[str] = Field(default_factory=list)

    def bind_tools(self, tools, *, tool_choice=None, **kwargs):
        self.bound_tool_names = [tool.name for tool in tools]
        return self


@pytest.mark.parametrize(
    ("question", "tool_name", "arguments"),
    [
        ("Qual é a garantia?", "retrieve_policy", {"query": "garantia"}),
        ("Quais violões Yamaha vocês têm?", "search_products", {"query": "Yamaha"}),
        ("Mostre o produto 81.", "get_product", {"product_id": 81}),
        ("O produto 81 está em estoque?", "check_stock", {"product_id": 81}),
        ("Qual a situação do pedido 1?", "get_order_status", {"order_id": 1}),
        ("Quais pedidos o cliente 1 fez?", "get_customer_orders", {"customer_id": 1}),
        ("Quais categorias vocês vendem?", "list_categories", {}),
    ],
)
def test_agent_exposes_named_schemas_and_executes_requested_tool(
    monkeypatch, question, tool_name, arguments
):
    def retrieve_policy_stub(query: str, top_k: int = 3):
        return [{"content": f"Política encontrada para: {query}", "score": 1.0}]

    monkeypatch.setattr(workflow, "retrieve_policy", retrieve_policy_stub)

    model = ToolCallingFakeModel(
        responses=[
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": tool_name,
                        "args": arguments,
                        "id": "tool-call-1",
                        "type": "tool_call",
                    }
                ],
            ),
            AIMessage(content="Resposta de teste."),
        ]
    )
    monkeypatch.setattr(workflow, "_get_llm", lambda _model: model)

    agent = workflow.create_agent_executor(checkpointer=MemorySaver())
    result = agent.invoke(
        {"messages": [("user", question)]},
        config={"configurable": {"thread_id": f"routing-{tool_name}"}},
    )

    assert set(model.bound_tool_names) == {
        "retrieve_policy",
        "search_products",
        "get_product",
        "check_stock",
        "get_order_status",
        "get_customer_orders",
        "list_categories",
    }
    tool_messages = [
        message for message in result["messages"] if message.type == "tool"
    ]
    assert [message.name for message in tool_messages] == [tool_name]
    assert tool_messages[0].content
    assert result["messages"][-1].content == "Resposta de teste."


def test_tools_expose_structured_arguments():
    tools = {tool.name: tool for tool in workflow.build_tools()}

    expected_arguments = {
        "retrieve_policy": {"query", "top_k"},
        "search_products": {"query", "category", "limit"},
        "get_product": {"product_id"},
        "check_stock": {"product_id"},
        "get_order_status": {"order_id"},
        "get_customer_orders": {"customer_id", "limit"},
        "list_categories": set(),
    }

    assert {name: set(tool.args) for name, tool in tools.items()} == expected_arguments


def test_policy_tool_returns_text_for_chat_provider(monkeypatch):
    monkeypatch.setattr(
        workflow,
        "retrieve_policy",
        lambda _query, top_k=3: [
            {"content": "Prazo para arrependimento: 7 dias.", "score": 0.9},
            {"content": "O frete de devolução é custeado pela loja.", "score": 0.8},
        ],
    )
    tools = {tool.name: tool for tool in workflow.build_tools()}

    result = tools["retrieve_policy"].invoke({"query": "devolução"})

    assert result == (
        "Prazo para arrependimento: 7 dias.\n\n"
        "O frete de devolução é custeado pela loja."
    )


def test_policy_tool_reports_when_no_policy_chunk_matches(monkeypatch):
    monkeypatch.setattr(workflow, "retrieve_policy", lambda _query, top_k=3: [])
    tools = {tool.name: tool for tool in workflow.build_tools()}

    result = tools["retrieve_policy"].invoke({"query": "assunto sem resultado"})

    assert result == "Nenhum trecho relevante foi encontrado no manual da loja."
