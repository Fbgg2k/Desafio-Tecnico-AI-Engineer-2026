"""Ponto de entrada da aplicação do agente (interface CLI estilo chat)."""

from langchain_core.messages import HumanMessage

from dotenv import load_dotenv

from src.agent.memory import _text_content, get_agent, save_conversation


def run_agent(question: str, thread_id: str = "conversa-001") -> str:
    """Roda o agente com memória da thread e persiste a conversa."""
    agent, config = get_agent(thread_id)
    result = agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)
    messages = result.get("messages") or []
    last = messages[-1] if messages else None
    content = _text_content(getattr(last, "content", "") or "")
    save_conversation(thread_id, messages)
    return content


def main() -> None:
    thread_id = "conversa-001"
    agent, config = get_agent(thread_id)
    print(f"Agente Empório da Música pronto. Conversa: {thread_id} (Ctrl+C para sair).")
    while True:
        try:
            question = input("Cliente: ")
        except (EOFError, KeyboardInterrupt):
            break
        if not question.strip():
            continue
        result = agent.invoke({"messages": [HumanMessage(content=question)]}, config=config)
        messages = result.get("messages") or []
        last = messages[-1] if messages else None
        answer = _text_content(getattr(last, "content", "") or "")
        save_conversation(thread_id, messages)
        print(f"Atendente: {answer}")


if __name__ == "__main__":
    main()
