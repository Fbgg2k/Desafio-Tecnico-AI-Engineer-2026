"""Ponto de entrada da aplicação do agente (CLI ou interface Streamlit)."""

import sys
import uuid
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from langchain_core.messages import AIMessage, HumanMessage

from dotenv import load_dotenv

from src.agent.guardrails import guardrail_response
from src.agent.memory import _text_content, get_agent, save_conversation

load_dotenv()

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx


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
            st.markdown(msg["content"])

    prompt = st.chat_input("Como posso te ajudar hoje?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        answer, _messages = _run_agent(thread_id, prompt)
        st.session_state.messages.append({"role": "assistant", "content": answer})


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
        answer, _messages = _run_agent(thread_id, question)
        print(f"Atendente: {answer}")


if __name__ == "__main__":
    if get_script_run_ctx() is not None:
        run_streamlit()
    else:
        main()
