"""Ponto de entrada da aplicação do agente (interface CLI estilo chat)."""

from src.agent.workflow import create_agent_executor


def run_agent(question: str) -> str:
    executor = create_agent_executor()
    result = executor.invoke({"messages": [("user", question)]})
    messages = result.get("messages") or []
    last = messages[-1] if messages else None
    content = getattr(last, "content", "") or ""
    return content


def main() -> None:
    print("Agente Empório da Música pronto. Digite sua pergunta (Ctrl+C para sair).")
    while True:
        try:
            question = input("Cliente: ")
        except (EOFError, KeyboardInterrupt):
            break
        if not question.strip():
            continue
        answer = run_agent(question)
        print(f"Atendente: {answer}")


if __name__ == "__main__":
    main()
