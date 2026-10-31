import os

import pytest
from dotenv import load_dotenv

from src.agent.workflow import create_agent_executor

load_dotenv()

_HAS_GEMINI_KEY = bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
_RUN_GEMINI_TESTS = os.getenv("RUN_GEMINI_INTEGRATION_TESTS") == "1"
pytestmark = pytest.mark.skipif(
    not (_HAS_GEMINI_KEY and _RUN_GEMINI_TESTS),
    reason=(
        "Defina GOOGLE_API_KEY e RUN_GEMINI_INTEGRATION_TESTS=1 para fazer "
        "chamadas reais ao Gemini."
    ),
)


@pytest.mark.parametrize(
    ("question", "expected_tool"),
    [
        ("Qual é a política de garantia para instrumentos musicais?", "retrieve_policy"),
        ("Quais violões Yamaha estão disponíveis no catálogo?", "search_products"),
        ("Verifique se o produto de ID 81 está disponível em estoque.", "check_stock"),
        ("Qual é a situação atual do pedido de número 1?", "get_order_status"),
    ],
)
def test_gemini_selects_expected_tool(monkeypatch, question, expected_tool):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    agent = create_agent_executor()
    result = agent.invoke(
        {"messages": [("user", question)]},
        config={"configurable": {"thread_id": f"gemini-routing-{expected_tool}"}},
    )

    called_tools = [
        message.name for message in result["messages"] if message.type == "tool"
    ]
    assert expected_tool in called_tools
