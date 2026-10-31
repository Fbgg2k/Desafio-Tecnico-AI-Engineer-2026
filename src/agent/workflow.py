"""Workflow do agente de atendimento (arquitetura híbrida ReAct + Tools)."""

import os
from typing import List, Optional

from langchain_core.tools import BaseTool, Tool
from langgraph.checkpoint.memory import MemorySaver
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
    checkpointer: Optional = None,
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
    agent = create_react_agent(
        model=_get_llm(model),
        tools=tools or build_tools(),
        prompt=SYSTEM_PROMPT,
        checkpointer=MemorySaver(),
    )
    config = {"configurable": {"thread_id": thread_id}}
    return agent, config
