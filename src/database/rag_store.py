"""RAG: chunking, embeddings e busca vetorial (FAISS) sobre os documentos do projeto."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from src.database.ingestion import POLICIES_PDF, load_project_documents

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 500


class RagStore:
    def __init__(self) -> None:
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.dimension = self.model.get_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dimension)
        self._documents: List[Dict[str, Any]] = []

    def _embed(self, texts: List[str]) -> np.ndarray:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.astype("float32")

    def _chunk(self, text: str, size: int = CHUNK_SIZE) -> List[str]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p and p.strip()]
        chunks: List[str] = []
        current = ""
        for paragraph in paragraphs:
            if current and len(current) + len(paragraph) > size:
                chunks.append(current)
                current = paragraph
            else:
                current = f"{current} {paragraph}".strip() if current else paragraph
        if current:
            chunks.append(current)
        return chunks

    def build(self, documents: List[Dict[str, Any]]) -> None:
        self._documents = documents
        texts = [doc["content"] for doc in documents]
        embeddings = self._embed(texts)
        faiss.normalize_L2(embeddings)
        self.index = faiss.IndexFlatIP(self.dimension)
        if len(documents) > 0:
            self.index.add(embeddings)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if len(self._documents) == 0:
            return []
        query_embedding = self._embed([query])
        faiss.normalize_L2(query_embedding)
        scores, indices = self.index.search(query_embedding, min(top_k, len(self._documents)))
        results = []
        for score, idx in zip(scores[0].tolist(), indices[0].tolist()):
            if idx < 0 or idx >= len(self._documents):
                continue
            doc = dict(self._documents[int(idx)])
            doc["score"] = float(score)
            results.append(doc)
        return results


_STORE: RagStore | None = None


def get_rag_store() -> RagStore:
    global _STORE
    if _STORE is None:
        store = RagStore()
        policy_docs = [
            doc
            for doc in load_project_documents()
            if doc.get("type") == "pdf" and doc.get("source") == str(POLICIES_PDF)
        ]
        store.build(policy_docs)
        _STORE = store
    return _STORE


def retrieve(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    return get_rag_store().search(query, top_k=top_k)
