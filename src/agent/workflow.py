"""Workflow do agente de atendimento (arquitetura híbrida ReAct + Tools)."""

import os
from typing import List

from langchain_core.tools import BaseTool, Tool
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

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

DEFAULT_MODEL = "gpt-4o-mini"


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


def create_agent_executor(tools: List[BaseTool] | None = None, model: str = DEFAULT_MODEL):
    """Cria o executor ReAct do agente."""
    agent = create_react_agent(
        model=ChatOpenAI(model=model, temperature=0.0, api_key=os.getenv("OPENAI_API_KEY")),
        tools=tools or build_tools(),
        prompt=SYSTEM_PROMPT,
    )
    return agent
