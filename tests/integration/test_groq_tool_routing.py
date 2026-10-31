import os

import pytest
from dotenv import load_dotenv

from src.agent.workflow import create_agent_executor

load_dotenv()

_HAS_GROQ_KEY = bool(os.getenv("GROQ_API_KEY"))
_RUN_GROQ_TESTS = os.getenv("RUN_GROQ_INTEGRATION_TESTS") == "1"
pytestmark = pytest.mark.skipif(
    not (_HAS_GROQ_KEY and _RUN_GROQ_TESTS),
    reason=(
        "Defina GROQ_API_KEY e RUN_GROQ_INTEGRATION_TESTS=1 para fazer "
        "uma chamada real à API da Groq."
    ),
)


def test_groq_selects_product_search_tool():
    agent = create_agent_executor()
    result = agent.invoke(
        {"messages": [("user", "Quais violões Yamaha estão disponíveis?")]},
        config={"configurable": {"thread_id": "groq-routing-product-search"}},
    )

    called_tools = [
        message.name for message in result["messages"] if message.type == "tool"
    ]
    assert "search_products" in called_tools
