# Agente de Atendimento — Empório da Música

Agente de atendimento em Python para a loja fictícia Empório da Música, em Campo Grande/MS. Combina consultas aos CSVs operacionais com busca RAG no manual de políticas em PDF. A aplicação pode usar modelos hospedados (Gemini ou Groq) ou um modelo local (Ollama).

## Arquitetura e escolhas técnicas

| Componente | Escolha | Motivo |
|---|---|---|
| Orquestração do agente | LangGraph com fluxo ReAct | O modelo decide quais ferramentas chamar; o grafo executa a ferramenta e devolve o resultado ao modelo para compor a resposta. |
| Provedores de LLM | Gemini, Groq e Ollama | Adaptadores LangChain permitem escolher o provedor pela configuração, sem alterar o fluxo do agente. Gemini e Groq são APIs hospedadas; Ollama executa o modelo localmente. |
| Dados operacionais | pandas sobre CSV | Consulta o catálogo, estoque e pedidos do conjunto de dados sem exigir um servidor de banco de dados. |
| Busca de políticas (RAG) | sentence-transformers + FAISS | O PDF é dividido em trechos de até 500 caracteres, vetorizado pelo `all-MiniLM-L6-v2` e indexado localmente. A busca retorna até três trechos relevantes. |
| Memória | Checkpointer SQLite do LangGraph | Mantém o histórico por `thread_id` entre turnos e reinicializações. |
| Interface | CLI e Streamlit | Permite executar conversas pelo terminal ou em uma interface web. |
| Prompt e guardrails | Persona e escopo explícitos, com filtros determinísticos | Define tom, domínio da loja, uso das ferramentas e recusas básicas antes da chamada ao LLM. |

O system prompt está em `src/agent/prompts.py`. Ele orienta o agente a usar ferramentas para informações operacionais e o RAG para políticas; o fluxo também contém ferramentas de catálogo, estoque e pedidos.

**Provedores e modelos configurados:**

| Provedor | Modelo padrão | Credencial | Observações |
|---|---|---|---|
| Gemini | `gemini-2.5-flash` | `GOOGLE_API_KEY` (ou `GEMINI_API_KEY`) | Integrado; disponibilidade e cota dependem da conta Google. |
| Groq | `openai/gpt-oss-20b` | `GROQ_API_KEY` | Integrado com chamadas de ferramentas. Os limites gratuitos variam por modelo/conta; confira o console Groq. |
| Ollama | `llama3.1` | Nenhuma chave externa | Integrado para inferência local; consome memória e processamento da máquina. |

“Agente” aqui é a aplicação LangGraph. Gemini, Groq e Ollama são provedores/modelos que o agente pode usar, não agentes separados. O projeto não troca automaticamente de provedor quando uma cota acaba.

**Limitações conhecidas:**

- O LLM pode inventar informações não presentes nas ferramentas ou nos documentos, apesar das instruções do prompt. Em testes reais, Groq respondeu com endereço, horário e telefone fictícios em perguntas sobre informações gerais da loja. Essas respostas registradas são exemplos de avaliação e não devem ser tratadas como dados corretos.
- Parte das perguntas de acompanhamento pode receber resposta sem nova chamada a uma ferramenta; respostas dependem do histórico e do comportamento do modelo.
- O limite gratuito de tokens por minuto da Groq pode impedir conversas longas. O tamanho máximo de resposta está limitado a 512 tokens e a API pode exigir espera entre chamadas.
- A interface Streamlit aguarda a conclusão da resposta do modelo. O tempo depende do provedor, do tamanho do histórico e, no caso do Ollama, do hardware local.
- Os guardrails são filtros de padrões conhecidos, não uma defesa completa contra prompt injection nem substituem validação e autorização no servidor.
- O catálogo, os pedidos, as políticas e os dados de atendimento representam um cenário de demonstração. Antes de uso real, é necessário validar e manter esses dados, reforçar avaliação de respostas e definir controles de privacidade, acesso e retenção.
- A primeira execução do RAG pode baixar o modelo de embeddings do Hugging Face; depois, a vetorização é feita localmente.

Com mais tempo, eu adicionaria avaliações automatizadas de groundedness e seleção de ferramentas por provedor, testes de regressão para alucinações, limites e observabilidade por chamada, streaming de respostas e dados verificados da loja. Também avaliaria autenticação e autorização apropriadas antes de consultar dados reais de pedidos.

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

Edite `.env` e escolha **um** provedor:

- **Gemini (padrão):** mantenha `LLM_PROVIDER=gemini` e configure `GOOGLE_API_KEY`.
- **Groq:** configure `LLM_PROVIDER=groq`, `GROQ_API_KEY` e, opcionalmente, `GROQ_MODEL`. O modelo padrão é `openai/gpt-oss-20b`.
- **Ollama (local):** configure `LLM_PROVIDER=ollama`, `OLLAMA_MODEL=llama3.1` e `OLLAMA_BASE_URL=http://localhost:11434`. Não precisa de API key externa.

Exemplos de configuração:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=sua-chave-do-groq
GROQ_MODEL=openai/gpt-oss-20b
```

Para Groq, crie uma chave no [console](https://console.groq.com/keys). Para Gemini, crie uma chave no [Google AI Studio](https://aistudio.google.com/apikey). Não compartilhe nem versione `.env`; o arquivo já é ignorado pelo Git. As APIs hospedadas recebem as mensagens enviadas ao modelo. As ferramentas de catálogo, pedidos e RAG são executadas pelo projeto localmente.

A camada gratuita da Groq tem limites que variam por modelo e conta; confira os [limites atuais](https://console.groq.com/docs/rate-limits). A lista de modelos acessíveis pode variar entre contas.

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

O modelo precisa suportar chamadas de ferramentas; se necessário, escolha outro modelo compatível e atualize `OLLAMA_MODEL`. Se o serviço local estiver indisponível, a interface mostrará um aviso em vez do traceback de conexão.

## Executar

Execute os comandos a partir da raiz do projeto, com o ambiente virtual ativado e o provedor configurado no `.env`.

### Agente no terminal

```bash
python src/app.py
```

Digite uma pergunta no prompt `Cliente:` e pressione Enter. Para encerrar, use `Ctrl+C`. A CLI usa o identificador `conversa-001` e retoma a conversa em execuções posteriores.

### Interface web

```bash
streamlit run src/app.py
```

Abra `http://localhost:8501` no navegador. Enquanto o modelo responde, o chat mostra o tempo de espera e desabilita o envio de outra pergunta. Erros de configuração, indisponibilidade e cota do provedor aparecem como mensagens no chat.

Com o Ollama, mantenha o serviço ativo em outro terminal. Com Gemini ou Groq, confirme que a variável de API correspondente está configurada localmente.

## Testes automáticos e validação manual

### Suíte automática (offline)

```bash
python -m pytest -q
```

Os testes cobrem ingestão de documentos, RAG, consultas aos CSVs, guardrails, memória SQLite, seleção de provedor, execução/roteamento de ferramentas e comportamento da interface Streamlit, incluindo respostas vazias e mensagens de erro de limite Groq. Eles não fazem chamadas reais às APIs hospedadas por padrão.

Na última validação desta revisão: **57 testes passaram e 5 foram ignorados**. Os ignorados são integrações externas que exigem ativação explícita e credenciais.

### Testes de integração com APIs

As integrações fazem chamadas reais e consomem cotas do provedor. Execute-as apenas quando desejar validar o roteamento de ferramentas com a conta configurada.

Gemini:

```bash
RUN_GEMINI_INTEGRATION_TESTS=1 python -m pytest -q tests/integration/test_gemini_tool_routing.py
```

Groq:

```bash
RUN_GROQ_INTEGRATION_TESTS=1 python -m pytest -q tests/integration/test_groq_tool_routing.py
```

Sem a variável de ativação e a chave válida, os testes de integração são ignorados. Confira os limites atuais no console do provedor; erros HTTP `413`/`429` indicam que a chamada não cabe na cota ou no limite de tokens por minuto.

### Roteiro de teste manual pelo chat

1. Inicie o agente no terminal (`python src/app.py`) ou a interface (`streamlit run src/app.py`).
2. Envie uma saudação, por exemplo `Olá!`, para verificar uma resposta simples.
3. Envie `Quanto custa o Takamine GD20?` ou `Quais opções de violões disponíveis custando até R$1000?` e confira se a resposta corresponde ao catálogo e se a ferramenta de produtos foi usada.
4. Opcionalmente, envie `Qual é o prazo para devolução por arrependimento?` e confira se o agente consulta a política no RAG.
5. Se estiver validando uma API hospedada, observe a mensagem no chat e o terminal do processo em caso de falha de chave, conexão ou cota. Para Groq, faça poucas chamadas seguidas e respeite o limite de tokens por minuto.

Na revisão manual do frontend com Groq, foram testadas duas perguntas pelo navegador: `Olá! Tudo bem?` e `Quanto custa o Takamine GD20?`. Ambas receberam resposta, a segunda consultou o catálogo e retornou preço e estoque. O teste verificou também o carregamento visual, a preservação das mensagens e a resposta HTTP `200` do Streamlit.

Os arquivos em `conversations/historias_testadas/` são avaliações de conversas mais longas. Como o modelo pode inventar informações, trate as transcrições como evidência de comportamento observado, não como respostas oficiais da loja. Uma saudação ou uma resposta plausível, por si só, não valida a precisão factual: compare preços, estoque e políticas com as ferramentas e fontes locais.

Se Gemini retornar `429 RESOURCE_EXHAUSTED` ou a Groq indicar limite de tokens por minuto, aguarde a renovação da cota ou use Ollama local, considerando os recursos disponíveis na máquina.

## Estrutura

```text
src/agent/       Prompt, workflow, memória e guardrails
src/agent/tools/ Consultas operacionais e recuperação de políticas
src/database/    Ingestão de documentos e armazenamento RAG
data/            CSVs operacionais e PDF de políticas
examples/        Conversas de exemplo
conversations/   Checkpoints e transcrições locais de avaliação
tests/           Testes automatizados
```

O banco SQLite e os logs de execução em `conversations/runtime/` são locais e ignorados pelo Git. `conversations/historias_testadas/` contém transcrições fictícias de avaliações manuais dos modelos; elas são mantidas separadas dos exemplos revisados e podem conter alucinações. Não armazene dados reais de clientes sem definir controles de acesso, retenção e privacidade apropriados.

## Uso de IA

Foi utilizado **GitHub Copilot no VS Code** como assistente de código. O fluxo de trabalho incluiu pedir sugestões e implementações pontuais, analisar erros e stack traces, gerar/ajustar testes e revisar documentação. As alterações foram executadas e verificadas localmente com testes automatizados e, quando indicado, chamadas manuais aos provedores. As respostas dos modelos também foram revisadas: as transcrições de avaliação documentam casos em que o agente inventou dados da loja, uma limitação que permanece explícita no projeto.
