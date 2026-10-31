"""Workflow do agente de atendimento (arquitetura híbrida ReAct + Tools)."""

import atexit
import os
import threading
from contextlib import ExitStack
from pathlib import Path
from typing import List, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from src.agent.prompts import SYSTEM_PROMPT
from src.agent.tools.rag_tool import retrieve_policy
from src.agent.tools.sql_tool import (
    get_customer_orders,
    get_order_status,
    get_product,
    get_product_availability,
    list_categories,
    search_products,
)

DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-20b"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKPOINT_DB_PATH = PROJECT_ROOT / "conversations" / "checkpoints.sqlite"
_CHECKPOINT_STACK = ExitStack()
_CHECKPOINT_LOCK = threading.Lock()
_PERSISTENT_CHECKPOINTER: SqliteSaver | None = None


class LLMConfigurationError(ValueError):
    """Erro claro de configuração do provedor de modelo."""


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


def _retrieve_policy_for_agent(query: str, top_k: int = 3) -> str:
    results = retrieve_policy(query, top_k=top_k)
    if not results:
        return "Nenhum trecho relevante foi encontrado no manual da loja."
    return "\n\n".join(result["content"] for result in results)


def build_tools() -> List[BaseTool]:
    return [
        StructuredTool.from_function(
            func=_retrieve_policy_for_agent,
            name="retrieve_policy",
            description=(
                "Busca no manual interno da Empório da Música (políticas de troca, garantia, "
                "prazos, formas de pagamento e frete). Use SE a pergunta for sobre essas políticas."
            ),
        ),
        StructuredTool.from_function(
            func=search_products,
            name="search_products",
            description="Busca produtos por nome ou descrição. Use para recomendações e catálogo.",
        ),
        StructuredTool.from_function(
            func=get_product,
            name="get_product",
            description="Retorna os dados completos de um produto (preço, estoque, status).",
        ),
        StructuredTool.from_function(
            func=get_product_availability,
            name="check_stock",
            description=(
                "Verifica a disponibilidade pelo ID do produto e distingue: disponível, "
                "sem estoque, descontinuado, lançamento futuro ou ID não encontrado. "
                "Use o status e a mensagem retornados sem inferir disponibilidade apenas pela quantidade."
            ),
        ),
        StructuredTool.from_function(
            func=get_order_status,
            name="get_order_status",
            description="Retorna o status de um pedido do cliente (situação, pagamento, frete, entrega).",
        ),
        StructuredTool.from_function(
            func=get_customer_orders,
            name="get_customer_orders",
            description="Retorna o histórico de pedidos de um cliente.",
        ),
        StructuredTool.from_function(
            func=list_categories,
            name="list_categories",
            description="Lista as categorias de instrumentos musicais.",
        ),
    ]


def _get_llm(model: str | None = None):
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
    if provider == "ollama":
        return ChatOllama(
            model=model or os.getenv("OLLAMA_MODEL", "llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.0,
        )
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "Configure GROQ_API_KEY para usar Groq ou escolha outro LLM_PROVIDER."
            )
        return ChatGroq(
            model=model or os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
            temperature=0.0,
            max_tokens=512,
            api_key=api_key,
        )
    if provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMConfigurationError(
                "Configure GOOGLE_API_KEY para usar Gemini ou defina LLM_PROVIDER=ollama."
            )
        return ChatGoogleGenerativeAI(
            model=model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL),
            temperature=0.0,
            google_api_key=api_key,
        )
    raise LLMConfigurationError(
        f"Provedor LLM_PROVIDER={provider!r} não suportado. "
        "Use 'gemini', 'groq' ou 'ollama'."
    )


def create_agent_executor(
    tools: Optional[List[BaseTool]] = None,
    model: str | None = None,
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


def create_agent_for_thread(
    thread_id: str, tools: Optional[List[BaseTool]] = None, model: str | None = None
):
    """Cria o executor ReAct vinculado a uma thread (memória de conversa)."""
    agent = create_agent_executor(
        tools=tools,
        model=model,
        checkpointer=get_persistent_checkpointer(),
    )
    config = {"configurable": {"thread_id": thread_id}}
    return agent, config
