# Agente de Atendimento — Empório da Música

Agente de atendimento em Python para a loja fictícia Empório da Música, em Campo Grande/MS. Combina consultas aos CSVs operacionais com busca RAG no manual de políticas em PDF.

## Arquitetura

- **Agente:** LangGraph ReAct com Gemini (`gemini-2.5-flash`).
- **Dados operacionais:** ferramentas pandas para catálogo, estoque, categorias e pedidos.
- **Políticas:** FAISS e sentence-transformers para recuperar trechos do PDF.
- **Memória:** checkpoints SQLite persistentes por `thread_id`; logs legíveis em `conversations/runtime/`.
- **Interfaces:** CLI e Streamlit.
- **Guardrails:** padrões conhecidos de prompt injection e pedidos claramente fora do escopo são recusados antes de chamar o modelo. O system prompt também restringe o atendimento à loja.

Os guardrails por padrões não detectam todas as formas possíveis de conteúdo fora de escopo ou de prompt injection; não são uma garantia de segurança completa.

## Requisitos

- Python 3.10 ou superior.
- Uma chave de API do Google AI Studio para executar o agente com Gemini.

## Instalação

```bash
git clone https://github.com/Fbgg2k/Desafio-Tecnico-AI-Engineer-2026.git
cd Desafio-Tecnico-AI-Engineer-2026
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` e configure `GOOGLE_API_KEY` com sua chave do Google AI Studio. Não compartilhe nem versione esse arquivo.

## Executar

CLI:

```bash
python src/app.py
```

Interface web:

```bash
streamlit run src/app.py
```

Cada sessão Streamlit recebe um identificador de conversa próprio. A CLI usa `conversa-001` para retomar o mesmo histórico entre execuções.

## Testes

```bash
pytest -q
```

Os testes cobrem ingestão, recuperação RAG, ferramentas de dados, guardrails e persistência de checkpoints SQLite. Eles não fazem chamadas reais à API do Gemini.

## Estrutura

```text
src/agent/       Prompt, workflow, memória e guardrails
src/agent/tools/ Consultas operacionais e recuperação de políticas
src/database/    Ingestão de documentos e armazenamento RAG
data/            CSVs operacionais e PDF de políticas
examples/        Conversas de exemplo
tests/           Testes automatizados
```

O SQLite e os logs gerados em `conversations/runtime/` são locais e ignorados pelo Git. Não armazene dados reais de clientes sem definir controles de acesso, retenção e privacidade apropriados.

## Uso de IA

O projeto foi desenvolvido com apoio de ferramentas de IA para código e documentação.
