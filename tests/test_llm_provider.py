import pytest

from src.agent import workflow


def test_ollama_provider_needs_no_api_key(monkeypatch):
    captured = {}
    expected_client = object()

    def fake_chat_ollama(**kwargs):
        captured.update(kwargs)
        return expected_client

    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.1")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(workflow, "ChatOllama", fake_chat_ollama)

    assert workflow._get_llm() is expected_client
    assert captured == {
        "model": "llama3.1",
        "base_url": "http://localhost:11434",
        "temperature": 0.0,
    }


def test_ollama_model_can_be_overridden(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setattr(workflow, "ChatOllama", lambda **kwargs: kwargs)

    llm = workflow._get_llm(model="mistral")

    assert llm["model"] == "mistral"


def test_groq_provider_uses_api_key_and_default_model(monkeypatch):
    captured = {}
    expected_client = object()

    def fake_chat_groq(**kwargs):
        captured.update(kwargs)
        return expected_client

    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    monkeypatch.setattr(workflow, "ChatGroq", fake_chat_groq)

    assert workflow._get_llm() is expected_client
    assert captured == {
        "model": "openai/gpt-oss-20b",
        "temperature": 0.0,
        "max_tokens": 512,
        "api_key": "test-key",
    }


def test_groq_provider_can_override_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("GROQ_MODEL", "custom-model")
    monkeypatch.setattr(workflow, "ChatGroq", lambda **kwargs: kwargs)

    llm = workflow._get_llm(model="explicit-model")

    assert llm["model"] == "explicit-model"


def test_groq_provider_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Configure GROQ_API_KEY"):
        workflow._get_llm()


def test_gemini_provider_requires_google_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="Configure GOOGLE_API_KEY"):
        workflow._get_llm()


def test_unknown_provider_fails_with_supported_options(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "unknown")

    with pytest.raises(ValueError, match="Use 'gemini', 'groq' ou 'ollama'"):
        workflow._get_llm()
