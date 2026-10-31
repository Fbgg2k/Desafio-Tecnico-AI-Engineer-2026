"""Workflow do agente de atendimento (arquitetura híbrida ReAct + Tools)."""

import atexit
import os
import threading
from contextlib import ExitStack
from pathlib import Path
from typing import List, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.tools import BaseTool, Tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.tools.rag_tool import retrieve_policy
from src.agent.tools.sql_tool import (
    check_stock,
    get_customer_orders,
    get_order_status,
    get_product,
    list_categories,
    search_products,
)

DEFAULT_MODEL = "gemini-2.5-flash"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DB_PATH = PROJECT_ROOT / "conversations" / "checkpoints.sqlite"
_CHECKPOINT_STACK = ExitStack()
_CHECKPOINT_LOCK = threading.Lock()
_PERSISTENT_CHECKPOINTER: SqliteSaver | None = None


def get_persistent_checkpointer() -> SqliteSaver:
    """Abre um checkpoint SQLite compartilhado e persistente para as conversas."""
    global _PERSISTENT_CHECKPOINTER
    with _CHECKPOINT_LOCK:
        if _PERSISTENT_CHECKPOINTER is None:
            CHECKPOINT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            _PERSISTENT_CHECKPOINTER = _CHECKPOINT_STACK.enter_context(
                SqliteSaver.from_conn_string(str(CHECKPOINT_DB_PATH))
            )
            _PERSISTENT_CHECKPOINTER.setup()
    return _PERSISTENT_CHECKPOINTER


atexit.register(_CHECKPOINT_STACK.close)


def build_tools() -> List[BaseTool]:
    return [
        Tool(
            name="retrieve_policy",
            description=(
                "Busca no manual interno da Empório da Música (políticas de troca, garantia, "
                "prazos, formas de pagamento e frete). Use SE a pergunta for sobre essas políticas."
            ),
            func=retrieve_policy,
        ),
        Tool(
            name="search_products",
            description="Busca produtos por nome ou descrição. Use para recomendações e catálogo.",
            func=search_products,
        ),
        Tool(
            name="get_product",
            description="Retorna os dados completos de um produto (preço, estoque, status).",
            func=get_product,
        ),
        Tool(
            name="check_stock",
            description="Verifica se um produto está em estoque (disponível para venda).",
            func=check_stock,
        ),
        Tool(
            name="get_order_status",
            description="Retorna o status de um pedido do cliente (situação, pagamento, frete, entrega).",
            func=get_order_status,
        ),
        Tool(
            name="get_customer_orders",
            description="Retorna o histórico de pedidos de um cliente.",
            func=get_customer_orders,
        ),
        Tool(
            name="list_categories",
            description="Lista as categorias de instrumentos musicais.",
            func=list_categories,
        ),
    ]


def _get_llm(model: str = DEFAULT_MODEL):
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=0.0,
        google_api_key=api_key,
    )


def create_agent_executor(
    tools: Optional[List[BaseTool]] = None,
    model: str = DEFAULT_MODEL,
    checkpointer: BaseCheckpointSaver | None = None,
):
    """Cria o executor ReAct do agente."""
    agent = create_react_agent(
        model=_get_llm(model),
        tools=tools or build_tools(),
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer or MemorySaver(),
    )
    return agent


def create_agent_for_thread(thread_id: str, tools: Optional[List[BaseTool]] = None, model: str = DEFAULT_MODEL):
    """Cria o executor ReAct vinculado a uma thread (memória de conversa)."""
    agent = create_agent_executor(
        tools=tools,
        model=model,
        checkpointer=get_persistent_checkpointer(),
    )
    config = {"configurable": {"thread_id": thread_id}}
    return agent, config
