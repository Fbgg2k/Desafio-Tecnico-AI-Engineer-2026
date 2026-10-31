"""Gerenciamento da memória de conversas e dos logs em Markdown."""

import re
from pathlib import Path
from typing import List

from langchain_core.messages import BaseMessage, HumanMessage

from src.agent.workflow import create_agent_for_thread

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONVERSATIONS_DIR = PROJECT_ROOT / "conversations" / "runtime"

_agents = {}
_THREAD_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def _validate_thread_id(thread_id: str) -> None:
    if not _THREAD_ID_PATTERN.fullmatch(thread_id):
        raise ValueError("O ID da conversa só pode conter letras, números, hífen e sublinhado.")


def _text_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts)
    return str(content)


def get_agent(thread_id: str = "conversa-001"):
    """Retorna (executor, config) do executor ReAct vinculado a uma thread (memória)."""
    _validate_thread_id(thread_id)
    if thread_id not in _agents:
        _agents[thread_id] = create_agent_for_thread(thread_id)
    return _agents[thread_id]


def format_conversation(messages: List[BaseMessage]) -> str:
    turns: List[dict] = []
    current_client: str | None = None
    current_answer: str | None = None

    def flush() -> None:
        nonlocal current_client, current_answer
        if current_client is not None and current_answer is not None:
            turns.append({"role": "Cliente", "text": current_client})
            turns.append({"role": "Atendente", "text": current_answer})
        current_client = None
        current_answer = None

    for m in messages:
        if type(m).__name__ in ("ToolMessage", "Tool"):
            continue
        text = _text_content(m.content).strip()
        if not text:
            continue
        if isinstance(m, HumanMessage):
            flush()
            current_client = text
            current_answer = None
        else:
            current_answer = text
    flush()

    lines: List[str] = []
    for turn in turns:
        lines.append(f"**{turn['role']}:** {turn['text']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def save_conversation(thread_id: str, messages: List[BaseMessage], directory: Path = CONVERSATIONS_DIR) -> Path:
    """Salva a conversa (thread) em um arquivo markdown dentro de conversations/."""
    _validate_thread_id(thread_id)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{thread_id}.md"
    path.write_text(f"# Conversa {thread_id}\n\n{format_conversation(messages)}", encoding="utf-8")
    return path
