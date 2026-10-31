"""Defesas determinísticas para pedidos claramente maliciosos ou fora de escopo."""

import re

_INJECTION_PATTERNS = (
    re.compile(
        r"\b(?:ignore|desconsidere|esque[cç]a)\b.{0,60}"
        r"\b(?:todas?\s+as?\s+)?(?:instru[cç][oõ]es|regras)\b.{0,30}"
        r"\b(?:anteriores|do sistema|da conversa|de seguran[cç]a)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:reveal|show|print|repeat|revele|mostre|exiba|imprima|repita)\b"
        r".{0,60}\b(?:system prompt|prompt do sistema|instru[cç][oõ]es ocultas)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above|earlier)"
        r"\s+(?:instructions|rules|prompts)\b",
        re.IGNORECASE,
    ),
)

_ACCESSORY_REQUEST_PATTERN = re.compile(
    r"\b(?:vende(?:m)?|comercializa(?:m)?|tem|t[eê]m|procuro|"
    r"quero comprar|preciso de|gostaria de comprar)\b.{0,50}"
    r"\b(?:cordas?|cabos?|palhetas?|pedais?|capotrastes?|afinadores?|"
    r"correias?|baquetas?|encordoamentos?)\b",
    re.IGNORECASE | re.DOTALL,
)

_OUT_OF_SCOPE_PATTERNS = (
    re.compile(
        r"\b(?:escreva|escrever|crie|criar|implemente|desenvolva|debugue|depure)\b"
        r".{0,60}\b(?:c[oó]digo|script|programa[cç][aã]o|aplicativo|site|python)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"\b(?:receita|cozinhar|previs[aã]o do tempo|clima de hoje|"
        r"pol[ií]tica partid[aá]ria|pol[ií]tica brasileira|elei[cç][aã]o|"
        r"diagn[oó]stico|rem[eé]dio|sintomas|aposta esportiva)\b",
        re.IGNORECASE,
    ),
)

_INJECTION_REFUSAL = (
    "Posso ajudar com produtos, pedidos e políticas da Empório da Música, "
    "mas não posso revelar instruções internas nem alterar minhas regras de atendimento."
)
_SCOPE_REFUSAL = (
    "Posso ajudar com instrumentos musicais, pedidos e políticas da Empório da Música. "
    "Esse assunto está fora do atendimento da loja."
)
_ACCESSORY_REFUSAL = (
    "A Empório da Música comercializa apenas instrumentos musicais. "
    "Para acessórios como esse, posso indicar que procure uma de nossas lojas parceiras."
)


def guardrail_response(message: str) -> str | None:
    """Retorna uma recusa para padrões inequívocos; caso contrário, deixa seguir ao agente."""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(message):
            return _INJECTION_REFUSAL

    if _ACCESSORY_REQUEST_PATTERN.search(message):
        return _ACCESSORY_REFUSAL

    for pattern in _OUT_OF_SCOPE_PATTERNS:
        if pattern.search(message):
            return _SCOPE_REFUSAL

    return None
