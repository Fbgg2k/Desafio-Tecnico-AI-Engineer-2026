"""Ingestão e leitura de documentos do desafio: PDFs (políticas) + Markdowns (escopo)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
POLICIES_PDF = DATA_DIR / "políticas_da_loja.pdf"
ARTEFACT_PDF = PROJECT_ROOT / "desafio_tecnico_ai_eng_artefact.pdf"
SCOPE_MD = PROJECT_ROOT / "estrutura_do_escopo_do_projeto.md"
EXAMPLES_DIR = PROJECT_ROOT / "examples"


def extract_pdf_documents(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """Extrai o texto de cada página de um PDF como um documento."""
    reader = PdfReader(str(pdf_path))
    documents: List[Dict[str, Any]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            documents.append(
                {
                    "source": str(pdf_path),
                    "page": page_number,
                    "content": text,
                }
            )
    return documents


def read_markdown_sections(md_path: str | Path) -> List[Dict[str, str]]:
    """Lê um arquivo Markdown e o divide em seções a partir dos headings."""
    path = Path(md_path)
    content = path.read_text(encoding="utf-8")
    sections: List[Dict[str, str]] = []
    current_title = path.stem
    current_lines: List[str] = []

    def flush() -> None:
        body = "\n".join(current_lines).strip()
        if body:
            sections.append({"title": current_title, "content": body})

    for line in content.splitlines():
        if re.match(r"^#{1,6}\s+.+$", line):
            flush()
            current_title = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)
    flush()
    return sections


def load_project_documents() -> List[Dict[str, Any]]:
    """Carrega todos os documentos de conhecimento do projeto (PDFs + Markdowns)."""
    documents: List[Dict[str, Any]] = []

    pdf_paths = [p for p in (ARTEFACT_PDF, POLICIES_PDF) if p.exists()]
    for pdf_path in pdf_paths:
        for doc in extract_pdf_documents(pdf_path):
            documents.append({"type": "pdf", "source": str(pdf_path), **doc})

    md_paths = [SCOPE_MD]
    if EXAMPLES_DIR.exists():
        md_paths += sorted(EXAMPLES_DIR.glob("*.md"))
    for md_path in md_paths:
        if not md_path.exists():
            continue
        for section in read_markdown_sections(md_path):
            documents.append({"type": "markdown", "source": str(md_path), **section})

    return documents


if __name__ == "__main__":
    docs = load_project_documents()
    print(f"Total de documentos carregados: {len(docs)}")
    for doc in docs:
        content = doc.get("content", "")
        preview = content[:120].replace("\n", " ")
        extra = f" | page={doc['page']}" if "page" in doc else f" | title={doc.get('title', '')}"
        print(f"- [{doc['type']}] {doc['source']}{extra} :: {preview}...")
