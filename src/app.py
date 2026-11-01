"""Ponto de entrada da aplicação do agente (CLI ou interface Streamlit)."""

import os
import sys
import uuid
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from langchain_core.messages import AIMessage, HumanMessage
import httpx

from dotenv import load_dotenv
from langchain_google_genai.chat_models import GoogleRateLimitError
from groq import (
    APIStatusError as GroqAPIStatusError,
    APIConnectionError as GroqAPIConnectionError,
    AuthenticationError as GroqAuthenticationError,
    RateLimitError as GroqRateLimitError,
)

from src.agent.guardrails import guardrail_response
from src.agent.memory import _text_content, get_agent, save_conversation
from src.agent.workflow import LLMConfigurationError

load_dotenv()

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx

_GEMINI_RATE_LIMIT_MESSAGE = (
    "O Gemini atingiu o limite de uso da API. Confira a cota e o faturamento "
    "do projeto no Google AI Studio; depois tente novamente quando houver cota disponível."
)
_GROQ_AUTHENTICATION_MESSAGE = (
    "A chave da Groq não foi aceita. Confira GROQ_API_KEY no arquivo .env."
)
_GROQ_RATE_LIMIT_MESSAGE = (
    "O limite de uso da Groq foi atingido. Confira os limites da sua conta e tente novamente."
)
_GROQ_CONNECTION_MESSAGE = (
    "Não foi possível conectar à API da Groq. Verifique a internet e tente novamente."
)
_EMPTY_RESPONSE_MESSAGE = (
    "O modelo concluiu a solicitação sem gerar uma resposta. "
    "Tente novamente ou reformule a pergunta."
)


class AgentResponseError(RuntimeError):
    """O agente terminou sem uma resposta textual para apresentar."""


def _ollama_connection_message() -> str | None:
    if os.getenv("LLM_PROVIDER", "gemini").strip().lower() == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return (
            f"Não foi possível conectar ao Ollama em {base_url}. "
            "Instale e inicie o Ollama, confirme que o modelo está baixado e tente novamente."
        )
    return None


def _provider_error_message(error: Exception) -> str | None:
    if isinstance(error, AgentResponseError):
        return str(error)
    if isinstance(error, LLMConfigurationError):
        return str(error)
    if isinstance(error, GoogleRateLimitError):
        return _GEMINI_RATE_LIMIT_MESSAGE
    if isinstance(error, GroqAuthenticationError):
        return _GROQ_AUTHENTICATION_MESSAGE
    if isinstance(error, GroqRateLimitError):
        return _GROQ_RATE_LIMIT_MESSAGE
    if isinstance(error, GroqAPIConnectionError):
        return _GROQ_CONNECTION_MESSAGE
    if isinstance(error, GroqAPIStatusError):
        if error.status_code in (413, 429):
            return _GROQ_RATE_LIMIT_MESSAGE
        if error.status_code == 404:
            return (
                "O modelo configurado não está disponível na Groq. "
                "Confira GROQ_MODEL e os modelos habilitados para sua conta."
            )
        return (
            f"A API da Groq retornou HTTP {error.status_code}. "
            "Confira a configuração do provedor e tente novamente."
        )
    if isinstance(error, httpx.ConnectError):
        return _ollama_connection_message()
    return None


def _run_agent(thread_id: str, question: str):
    """Roda o agente com memória da thread e persiste a conversa."""
    agent, config = get_agent(thread_id)
    refusal = guardrail_response(question)
    if refusal:
        agent.update_state(
            config,
            {"messages": [HumanMessage(content=question), AIMessage(content=refusal)]},
        )
        messages = agent.get_state(config).values.get("messages") or []
        answer = refusal
    else:
        result = agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)
        messages = result.get("messages") or []
        last = messages[-1] if messages else None
        answer = _text_content(getattr(last, "content", "") or "")
        if not answer.strip():
            raise AgentResponseError(_EMPTY_RESPONSE_MESSAGE)
    save_conversation(thread_id, messages)
    return answer, messages


def run_streamlit() -> None:
    """Interface web (Streamlit) estilo chat do agente."""
    st.set_page_config(page_title="Empório da Música", page_icon="🎸")
    st.title("🎸 Empório da Música — Agente de Atendimento")
    st.caption("Atendente virtual especializado em instrumentos musicais.")

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = uuid.uuid4().hex
    thread_id = st.session_state.thread_id

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("error"):
                st.error(msg["content"])
            else:
                st.markdown(msg["content"])

    prompt = st.chat_input(
        "Como posso te ajudar hoje?",
        submit_mode="disable",
    )
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                with st.spinner("Consultando o atendente...", show_time=True):
                    answer, _ = _run_agent(thread_id, prompt)
            except (
                AgentResponseError,
                LLMConfigurationError,
                GoogleRateLimitError,
                GroqAuthenticationError,
                GroqRateLimitError,
                GroqAPIConnectionError,
                GroqAPIStatusError,
                httpx.ConnectError,
            ) as error:
                message = _provider_error_message(error)
                if message is None:
                    raise
                st.error(message)
                st.session_state.messages.append(
                    {"role": "assistant", "content": message, "error": True}
                )
            else:
                st.markdown(answer)
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )


def main() -> None:
    """Interface CLI (estilo chat) do agente."""
    thread_id = "conversa-001"
    print(f"Agente Empório da Música pronto. Conversa: {thread_id} (Ctrl+C para sair).")
    while True:
        try:
            question = input("Cliente: ")
        except (EOFError, KeyboardInterrupt):
            break
        if not question.strip():
            continue
        try:
            answer, _ = _run_agent(thread_id, question)
        except (
            AgentResponseError,
            LLMConfigurationError,
            GoogleRateLimitError,
            GroqAuthenticationError,
            GroqRateLimitError,
            GroqAPIConnectionError,
            GroqAPIStatusError,
            httpx.ConnectError,
        ) as error:
            message = _provider_error_message(error)
            if message is None:
                raise
            print(f"Atendente: {message}")
            continue
        print(f"Atendente: {answer}")


if __name__ == "__main__":
    if get_script_run_ctx() is not None:
        run_streamlit()
    else:
        main()
