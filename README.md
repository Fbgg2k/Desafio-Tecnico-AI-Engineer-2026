# Agente de Atendimento — Empório da Música

Agente de atendimento em Python para a loja fictícia Empório da Música, em Campo Grande/MS. Combina consultas aos CSVs operacionais com busca RAG no manual de políticas em PDF.

## Arquitetura e escolhas técnicas

| Componente | Escolha | Motivo |
|---|---|---|
| Orquestração | LangGraph ReAct | Permite ao modelo selecionar ferramentas conforme a solicitação. |
| LLM | Gemini, Groq ou Ollama local | Function calling; Ollama funciona localmente sem chave de API. |
| Dados operacionais | pandas sobre CSV | Acessa diretamente os arquivos fornecidos sem exigir um banco separado. |
| Busca de políticas | FAISS + sentence-transformers | Recuperação vetorial local dos trechos do PDF. |
| Memória | SQLite por `thread_id` | Checkpoints persistentes entre reinicializações e isolamento lógico de conversas. |
| Interface | CLI e Streamlit | Permite testar pelo terminal ou por chat web. |

O fluxo ReAct decide quando consultar o catálogo, os pedidos ou o manual; o agente deve responder com base nos resultados das ferramentas.

**Exceções de catálogo:** disponibilidade distingue ID não encontrado, produto descontinuado, lançamento futuro, item sem estoque e item disponível. Pedidos de acessórios são direcionados a lojas parceiras.

**Limite dos guardrails:** padrões conhecidos de prompt injection e assuntos claramente fora do escopo são recusados antes da chamada ao modelo. Os filtros não detectam todas as variações e não constituem garantia completa de segurança; o system prompt também restringe o atendimento à loja.

## Requisitos

- Python 3.10 ou superior.
- Para Gemini: uma chave de API do Google AI Studio.
- Para Groq: uma chave de API do GroqCloud.
- Para Ollama: Ollama instalado e um modelo compatível com chamadas de ferramentas baixado localmente.

## Instalação

```bash
git clone https://github.com/Fbgg2k/Desafio-Tecnico-AI-Engineer-2026.git
cd Desafio-Tecnico-AI-Engineer-2026
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` e escolha o provedor:

- **Gemini (padrão):** mantenha `LLM_PROVIDER=gemini` e configure `GOOGLE_API_KEY`.
- **Groq:** configure `LLM_PROVIDER=groq`, `GROQ_API_KEY` e, opcionalmente, `GROQ_MODEL`. O modelo padrão é `openai/gpt-oss-20b`.
- **Ollama (local):** configure `LLM_PROVIDER=ollama`, `OLLAMA_MODEL=llama3.1` e `OLLAMA_BASE_URL=http://localhost:11434`. Não precisa de API key externa.

Crie uma chave no [console da Groq](https://console.groq.com/keys) e configure no `.env`:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=sua-chave-do-groq
GROQ_MODEL=openai/gpt-oss-20b
```

Não compartilhe nem versione `.env`. A camada gratuita da Groq tem limites que variam por modelo e conta; confira os [limites atuais](https://console.groq.com/docs/rate-limits). O agente continua executando as ferramentas localmente; somente as mensagens enviadas ao modelo são processadas pela Groq.

Para Ollama no Linux, instale o aplicativo conforme a documentação oficial e baixe um modelo:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

No `.env`, ajuste a configuração para:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1
OLLAMA_BASE_URL=http://localhost:11434
```

Depois da instalação, encerre e abra o terminal para atualizar o `PATH`. Confirme que o comando está disponível:

```bash
ollama -v
```

Baixe o modelo configurado:

```bash
ollama pull llama3.1
```

O instalador pode deixar o serviço ativo. Se não estiver, inicie-o em um terminal separado:

```bash
ollama serve
```

Confirme que o serviço responde:

```bash
curl http://localhost:11434/api/tags
```

Em outro terminal, execute a aplicação:

```bash
streamlit run src/app.py
```

O modelo precisa suportar chamadas de ferramentas; se necessário, escolha outro modelo compatível e atualize `OLLAMA_MODEL`. Se o serviço local estiver indisponível, a interface mostrará um aviso em vez do traceback de conexão.

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
Para validar a seleção das ferramentas pela Groq, configure `GROQ_API_KEY` e execute:

```bash
RUN_GROQ_INTEGRATION_TESTS=1 pytest -q tests/integration/test_groq_tool_routing.py
```

Esse teste faz chamadas reais à API da Groq e consome a cota da conta. Sem a variável de ativação e a chave configurada, os casos são ignorados.

Se o app exibir erro `429 RESOURCE_EXHAUSTED`, a cota da API do Gemini foi excedida. Confira os limites e o faturamento do projeto no Google AI Studio; o app mostrará um aviso curto e será possível tentar novamente quando a cota estiver disponível.
Para executar sem depender da cota do Gemini, use o provedor Ollama local indicado acima; a inferência usa os recursos da sua máquina.

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
