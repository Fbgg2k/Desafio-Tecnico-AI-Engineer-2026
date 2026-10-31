# Desafio Técnico AI Engineer 2026 — Agente de Atendimento: Empório da Música

## 📌 Sobre o Projeto

Construção de um **agente inteligente de atendimento em Python** para a loja fictícia **Empório da Música** (Campo Grande/MS).

O agente simula um **especialista em atendimento via WhatsApp**, unindo:

- **Consultas de dados operacionais** (produtos, pedidos, clientes, promoções) em arquivos **CSV**;
- **Políticas internas e procedimentos** (troca, garantia, prazos, pagamento, frete) em **PDF**.

## 🏗️ Arquitetura

Arquitetura híbrida (**ReAct + Router/Tools**):

1. **RAG** — recuperacão aumentada por geração sobre o manual interno (`data/políticas_da_loja.pdf`): chunking → embeddings → busca vetorial (FAISS) → retriever.
2. **Function Calling / Text-to-SQL** — consultas analíticas/operacionais sobre os CSVs (`src/agent/tools/sql_tool.py`).
3. **Guardrails** — recusa amigável para fora de escopo e *prompt injection*.

Fluxo do agente: recebe a pergunta → decide entre RAG e tools (via LangGraph ReAct) → responde com base nos fatos recuperados.

## 🛠️ Stack Tecnológica

| Camada / Função | Tecnologias | Justificativa |
|---|---|---|
| Linguagem | Python 3.10+ | Requisito do desafio |
| Framework de agentes | LangGraph / LangChain | Orquestração ReAct, estado, tools |
| LLM | OpenAI (`gpt-4o-mini`) | Custo/velocidade/precisão para function calling |
| Busca SQL/CSV | pandas | Consultas analíticas sobre CSVs |
| Vetorização & RAG | FAISS + sentence-transformers | Busca local, fácil execução |
| Interface | CLI (Streamlit no roadmap | Chat rápido para testes |

## 📁 Estrutura do Repositório

```text
Desafio-Tecnico-AI-Engineer-2026/
├── data/                     # CSVs operacionais + politicas_da_loja.pdf
├── src/
│   ├── agent/
│   │   ├── prompts.py        # System prompt e persona
│   │   ├── workflow.py       # Grafo / executor ReAct (LangGraph)
│   │   └── tools/
│   │       ├── sql_tool.py   # Consulta de dados (produtos, pedidos, estoque)
│   │       └── rag_tool.py   # Busca vetorial no PDF de políticas
│   ├── database/
│   │   ├── ingestion.py      # Leitura de PDF + Markdown
│   │   └── rag_store.py      # Chunking + embeddings + FAISS
│   └── app.py                # Ponto de entrada (CLI chat)
├── tests/                    # Testes de ingestão, tools e RAG
├── examples/                 # Conversas de exemplo (Entregável 3)
├── README.md
├── requirements.txt
└── .env.example              # OPENAI_API_KEY
```

## 🚀 Instalação e Execução (Linux)

```bash
# 1. Clone o repositório
git clone https://github.com/Fbgg2k/Desafio-Tecnico-AI-Engineer-2026.git
cd Desafio-Tecnico-AI-Engineer-2026

# 2. Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Dependências
pip install -r requirements.txt

# 4. Chave da OpenAI (obrigatória)
cp .env.example .env
# edite .env e coloque sua OPENAI_API_KEY

# 5. Testes
python -m pytest tests/ -v

# 6. Execução do agente (CLI)
python src/app.py
```

## 🧪 Testes

```bash
python -m pytest tests/ -v
```

Cobre: ingestão de documentos (PDF/Markdown), ferramentas de dados e retriever RAG.

## 📚 Exemplos

- `examples/conversa_01_catalogo.md` — recomendação e catálogo.
- `examples/conversa_02_politicas.md` — trocas, garantia, prazos, pagamento, frete.
- `examples/conversa_03_rastreio.md` — rastreamento de pedidos.

## 🤖 Uso de IA

Este projeto foi desenvolvido com apoio de ferramentas de IA (assistência de código e geração de documentação).

## ⚠️ Limitações e Evoluções

- LLM com custo por token; estratégias de caching/contexto.
- Embeddings OpenAI no lugar de locais.
- Interface Streamlit no lugar da CLI.
- Persistência de memória de conversa.

## ✅ Entregáveis

- [x] Check-in 1 — Ambiente, dados e ingestão.
- [ ] Check-in 2 — Tools e system prompt.
- [ ] Check-in 3 — Orquestração e memória.
- [ ] Check-in 4 — Interface, exemplos, README final.
```

Hmm, I marked check-ins inconsistently. Let me make it coherent.

Let me rewrite the README more carefully and completely. Actually, let me just write it well in one go.

Also, I should keep the README not overly long. Let me finalize.

After README, commit + push, then ask about LLM key.

Let me write the final README.</think>Agora vou finalizar o **README.md** completo:<tool_call>write<arg_key>content</arg_key><arg_value># Desafio Técnico AI Engineer 2026 — Agente de Atendimento: Empório da Música

## 📌 Sobre o Projeto

Construção de um **agente inteligente de atendimento em Python** para a loja fictícia **Empório da Música** (Campo Grande/MS).

O agente simula um **especialista em atendimento via WhatsApp**, unindo:

- **Consultas de dados operacionais** (produtos, pedidos, clientes, promoções) em arquivos **CSV**;
- **Políticas internas e procedimentos** (troca, garantia, prazos, pagamento, frete) em **PDF**.

## 🏗️ Arquitetura

Arquitetura híbrida (**ReAct + Router/Tools**):

1. **RAG** — recuperação aumentada por geração sobre o manual interno (`data/políticas_da_loja.pdf`): chunking → embeddings → busca vetorial (FAISS) → retriever;
2. **Function Calling / Text-to-SQL** — consultas analíticas/operacionais sobre os CSVs (`src/agent/tools/sql_tool.py`);
3. **Guardrails** — recusa amigável para fora de escopo e *prompt injection*.

Fluxo do agente: a pergunta chega → o executor ReAct (LangGraph) decide entre RAG e tools → monta resposta com os fatos recuperados.

## 🛠️ Stack Tecnológica

| Camada / Função | Tecnologias | Justificativa |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.10+ | Requisito obrigatório do desafio |
| **Framework de Agentes** | LangGraph / LangChain | Orquestração ReAct, estado e tools |
| **LLM** | OpenAI (`gpt-4o-mini`) | Equilíbrio entre custo, velocidade e precisão |
| **Busca SQL/CSV** | pandas | Consultas analíticas sobre CSVs |
| **Vetorização & RAG** | FAISS + sentence-transformers | Busca local, fácil execução |
| **Interface** | CLI (Streamlit no roadmap) | Chat rápido para testes |

## 📁 Estrutura do Repositório

```text
Desafio-Tecnico-AI-Engineer-2026/
├── data/                        # CSVs operacionais + politicas_da_loja.pdf
├── src/
│   ├── agent/
│   │   ├── prompts.py           # System prompt e persona
│   │   ├── workflow.py          # Executor ReAct (LangGraph)
│   │   └── tools/
│   │       ├── sql_tool.py      # Consulta de dados (produtos, pedidos, estoque)
│   │       └── rag_tool.py      # Busca vetorial no PDF de políticas
│   ├── database/
│   │   ├── ingestion.py         # Leitura de PDF + Markdown
│   │   └── rag_store.py         # Chunking + embeddings + FAISS
│   └── app.py                   # Ponto de entrada (CLI chat)
├── tests/                       # Testes de ingestão, tools e RAG
├── examples/                    # Conversas de exemplo (Entregável 3)
├── README.md
├── requirements.txt
└── .env.example                 # OPENAI_API_KEY
```

## 🚀 Instalação e Execução (Linux)

```bash
git clone https://github.com/Fbgg2k/Desafio-Tecnico-AI-Engineer-2026.git
cd Desafio-Tecnico-AI-Engineer-2026

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # colar a OPENAI_API_KEY
python -m pytest tests/ -v
python src/app.py
```

## 🧪 Testes

```bash
python -m pytest tests/ -v
```

Cobre ingestão de documentos (PDF/Markdown), ferramentas de dados e retriever RAG.

## 📚 Exemplos

- `examples/conversa_01_catalogo.md` — recomendação e catálogo.
- `examples/conversa_02_politicas.md` — trocas, garantia, prazos, pagamento, frete.
- `examples/conversa_03_rastreio.md` — rastreamento de pedidos.

## 🤖 Uso de IA

Este projeto foi desenvolvido com apoio de ferramentas de IA para aceleração de código e documentação.

## ⚠️ Limitações e Evoluções

- LLM com custo por token; estratégias de caching/contexto.
- Embeddings OpenAI no lugar de locais.
- Interface Streamlit no lugar da CLI.
- Memória persistente de conversa.

## ✅ Entregáveis

- [x] Check-in 1 — Ambiente, dados e ingestão.
- [ ] Check-in 2 — Tools e system prompt.
- [ ] Check-in 3 — Orquestração e memória.
- [ ] Check-in 4 — Interface, exemplos, README final.
