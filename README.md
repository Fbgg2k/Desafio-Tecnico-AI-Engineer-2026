# Agente de Atendimento — Empório da Música

Agente de atendimento em Python para a loja fictícia Empório da Música, em Campo Grande/MS. Combina consultas aos CSVs operacionais com busca RAG no manual de políticas em PDF. O projeto está configurado para usar os provedores hospedados Gemini ou Groq.

## Arquitetura e escolhas técnicas

| Componente | Escolha | Motivo |
|---|---|---|
| Orquestração do agente | LangGraph com fluxo ReAct | O modelo decide quais ferramentas chamar; o grafo executa a ferramenta e devolve o resultado ao modelo para compor a resposta. |
| Provedores de LLM | Gemini e Groq | Adaptadores LangChain permitem escolher o provedor pela configuração, sem alterar o fluxo do agente. |
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

“Agente” aqui é a aplicação LangGraph. Gemini e Groq são provedores/modelos que o agente pode usar, não agentes separados. O projeto não troca automaticamente de provedor quando uma cota acaba.

**Limitações conhecidas:**

- O LLM pode inventar informações não presentes nas ferramentas ou nos documentos, apesar das instruções do prompt. Em testes reais, Groq respondeu com endereço, horário e telefone fictícios em perguntas sobre informações gerais da loja. Essas respostas registradas são exemplos de avaliação e não devem ser tratadas como dados corretos.
- Parte das perguntas de acompanhamento pode receber resposta sem nova chamada a uma ferramenta; respostas dependem do histórico e do comportamento do modelo.
- O limite gratuito de tokens por minuto da Groq pode impedir conversas longas. O tamanho máximo de resposta está limitado a 512 tokens e a API pode exigir espera entre chamadas.
- A interface Streamlit aguarda a conclusão da resposta do modelo. O tempo depende do provedor e do tamanho do histórico.
- Os guardrails são filtros de padrões conhecidos, não uma defesa completa contra prompt injection nem substituem validação e autorização no servidor.
- O catálogo, os pedidos, as políticas e os dados de atendimento representam um cenário de demonstração. Antes de uso real, é necessário validar e manter esses dados, reforçar avaliação de respostas e definir controles de privacidade, acesso e retenção.
- A primeira execução do RAG pode baixar o modelo de embeddings do Hugging Face; depois, a vetorização é feita localmente.

Com mais tempo, eu adicionaria avaliações automatizadas de groundedness e seleção de ferramentas por provedor, testes de regressão para alucinações, limites e observabilidade por chamada, streaming de respostas e dados verificados da loja. Também avaliaria autenticação e autorização apropriadas antes de consultar dados reais de pedidos.

## Requisitos

- Python 3.10 ou superior.
- Para Gemini: uma chave de API do Google AI Studio.
- Para Groq: uma chave de API do GroqCloud.

## Instalação

```bash
git clone https://github.com/Fbgg2k/Desafio-Tecnico-AI-Engineer-2026.git
cd Desafio-Tecnico-AI-Engineer-2026
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

O arquivo `.env.example` é um modelo de configuração, não contém chaves válidas. Copie-o para `.env`, abra a cópia no editor e escolha **um** provedor. Cada usuário deve gerar e inserir sua própria API key; não reutilize chaves de outra pessoa.

Para editar pelo terminal:

```bash
nano .env
```

Configure somente a variável de chave do provedor escolhido:

Gemini:

```dotenv
LLM_PROVIDER=gemini
GOOGLE_API_KEY=sua-chave-pessoal-do-google
```

Crie a chave no [Google AI Studio](https://aistudio.google.com/apikey). O código também aceita `GEMINI_API_KEY` como alternativa a `GOOGLE_API_KEY`.

Groq:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=sua-chave-pessoal-do-groq
GROQ_MODEL=openai/gpt-oss-20b
```

Crie a chave no [console da Groq](https://console.groq.com/keys). O modelo é opcional e, se omitido, a aplicação usa `openai/gpt-oss-20b`.

Salve o arquivo e execute a aplicação no mesmo ambiente. Se ela já estiver rodando, pare com `Ctrl+C` e inicie novamente para carregar as alterações. Nunca compartilhe nem versione `.env`; ele é ignorado pelo Git. Não coloque suas chaves no código, no README ou em commits. As APIs hospedadas recebem as mensagens enviadas ao modelo; as ferramentas de catálogo, pedidos e RAG são executadas localmente pelo projeto.

A camada gratuita da Groq tem limites que variam por modelo e conta; confira os [limites atuais](https://console.groq.com/docs/rate-limits). A lista de modelos acessíveis pode variar entre contas.

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

Antes de executar, confirme que a chave do provedor escolhido está configurada no `.env`.

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

Se Gemini retornar `429 RESOURCE_EXHAUSTED` ou a Groq indicar limite de tokens por minuto, confira a cota no console do provedor e aguarde a renovação antes de tentar novamente.

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
