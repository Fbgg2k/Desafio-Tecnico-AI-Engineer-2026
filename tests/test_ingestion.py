from src.database.ingestion import (
    extract_pdf_documents,
    load_project_documents,
    read_markdown_sections,
)

POLICIES_PDF = "data/políticas_da_loja.pdf"
SCOPE_MD = "estrutura_do_escopo_do_projeto.md"


def test_load_project_documents_returns_mixed_types():
    docs = load_project_documents()
    assert len(docs) > 0
    types = {doc["type"] for doc in docs}
    assert "pdf" in types
    assert "markdown" in types


def test_extract_pdf_documents_policies():
    docs = extract_pdf_documents(POLICIES_PDF)
    assert len(docs) > 0
    assert all("content" in doc for doc in docs)
    assert all("source" in doc for doc in docs)
    assert all("page" in doc for doc in docs)


def test_read_markdown_sections():
    sections = read_markdown_sections(SCOPE_MD)
    assert len(sections) > 0
    first = sections[0]
    assert "title" in first
    assert "content" in first
