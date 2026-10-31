"""Ferramenta de RAG: busca no manual de políticas da Empório da Música (PDF)."""

from __future__ import annotations

from typing import Any, Dict, List

from src.database.rag_store import retrieve


def retrieve_policy(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Busca no manual de políticas respostas sobre troca, garantia, prazos, pagamento e frete."""
    return retrieve(query, top_k=top_k)
