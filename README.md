# Agente de Atendimento — Empório da Música

Agente de atendimento em Python para a loja fictícia Empório da Música, em Campo Grande/MS. Combina consultas aos CSVs operacionais com busca RAG no manual de políticas em PDF.

## Arquitetura e escolhas técnicas

| Componente | Escolha | Motivo |
|---|---|---|
| Orquestração | LangGraph ReAct | Permite ao modelo selecionar ferramentas conforme a solicitação. |
| LLM | Gemini `gemini-2.5-flash` | Function calling para encaminhar perguntas às ferramentas do domínio. |
| Dados operacionais | pandas sobre CSV | Acessa diretamente os arquivos fornecidos sem exigir um banco separado. |
| Busca de políticas | FAISS + sentence-transformers | Recuperação vetorial local dos trechos do PDF. |
| Memória | SQLite por `thread_id` | Checkpoints persistentes entre reinicializações e isolamento lógico de conversas. |
| Interface | CLI e Streamlit | Permite testar pelo terminal ou por chat web. |

O fluxo ReAct decide quando consultar o catálogo, os pedidos ou o manual; o agente deve responder com base nos resultados das ferramentas.

**Exceções de catálogo:** disponibilidade distingue ID não encontrado, produto descontinuado, lançamento futuro, item sem estoque e item disponível. Pedidos de acessórios são direcionados a lojas parceiras.

**Limite dos guardrails:** padrões conhecidos de prompt injection e assuntos claramente fora do escopo são recusados antes da chamada ao modelo. Os filtros não detectam todas as variações e não constituem garantia completa de segurança; o system prompt também restringe o atendimento à loja.

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

Os testes offline cobrem ingestão, recuperação RAG, ferramentas de dados, guardrails, persistência SQLite e schemas/execução das ferramentas no grafo. Não fazem chamadas reais ao Gemini.

Para validar a seleção das ferramentas pelo Gemini, configure `GOOGLE_API_KEY` no `.env` e execute, conscientemente, o teste de integração:

```bash
RUN_GEMINI_INTEGRATION_TESTS=1 pytest -q tests/integration/test_gemini_tool_routing.py
```

Esse teste faz chamadas reais à API do Gemini e pode gerar cobrança. Sem a variável de ativação e a chave configurada, os casos de integração são ignorados.

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
