# Escopo de Projeto: Agente de Atendimento - Empório da Música

## 1. Visão Geral do Projeto
O objetivo deste projeto é construir um agente inteligente de atendimento em **Python** para a loja fictícia **Empório da Música** (Campo Grande/MS). O agente deve simular um especialista em atendimento via WhatsApp, unindo a consulta de dados operacionais dinâmicos (produtos, pedidos, clientes e promoções em arquivos CSV) com políticas internas e procedimentos (disponíveis em PDF).

---

## 2. Requisitos Técnicos & Funcionais

### 2.1 Persona & Tom de Voz
- **Tom de voz:** Informal, acolhedor e profissional (especialista apaixonado por música).
- **Diretriz de Escopo:** Comercializa **apenas instrumentos musicais**. Redireciona educadamente pedidos de acessórios (cordas, cabos, palhetas, pedais, etc.) para lojas parceiras.
- **Fora de Escopo/Segurança:** Lida graciosamente com perguntas fora do escopo da loja ou tentativas de *prompt injection*.

### 2.2 Arquitetura de Decisão do Agente
- **Arquitetura Híbrida (ReAct + Router/Tools):**
  - **RAG (Retrieval-Augmented Generation):** Utilizado para responder dúvidas sobre o manual interno (`politicas_da_loja.pdf`) — regras de troca, garantia, prazos, formas de pagamento e frete.
  - **Function Calling / Text-to-SQL (ou Pandass/DuckDB Tools):** Utilizado para consultar dados operacionais nos arquivos CSV (`categories.csv`, `customers.csv`, `order_items.csv`, `orders.csv`, `products.csv`, `promotions.csv`).
  - **Filtros e Guardrails:** Sanitização e recusa amigável para tópicos alheios ao negócio.

---

## 3. Stack Tecnológica Sugerida

| Camada / Função | Tecnologias Recomendadas | Justificativa |
| :--- | :--- | :--- |
| **Linguagem Principal** | Python 3.10+ | Requisito obrigatório do desafio. |
| **Framework de Agentes** | `LangGraph` ou `LangChain` | Excelente para orquestração de fluxos ReAct, gestão de estado e chamadas de ferramentas. |
| **LLM Provider** | OpenAI (`gpt-4o-mini`) ou Google (`gemini-2.5-flash`) ou Ollama (local) | Equilíbrio entre custo, velocidade e precisão para *Function Calling*. |
| **Engine de Busca SQL/CSV** | `DuckDB` ou `pandas` | Permite fazer consultas analíticas e relacionais de alta performance diretamente em cima dos arquivos CSV. |
| **Vetorização & RAG** | `ChromaDB` ou `FAISS` + `PyPDF` | Armazenamento de embeddings simples e de fácil execução local para as políticas em PDF. |
| **Interface de Interação** | `Streamlit` (WebUI) ou `CLI` | Proporciona uma interface visual rápida estilo chat (simulando WhatsApp) para testes eficientes. |
| **Gestão de Ambiente** | `uv` / `poetry` / `pipenv` | Gerenciamento de dependências limpo e replicável. |

---

## 4. Estrutura do Repositório

```text
emporio-da-musica-agent/
├── data/
│   ├── desafio_tecnico_ai_eng_categories.csv
│   ├── desafio_tecnico_ai_eng_customers.csv
│   ├── desafio_tecnico_ai_eng_order_items.csv
│   ├── desafio_tecnico_ai_eng_orders.csv
│   ├── desafio_tecnico_ai_eng_products.csv
│   ├── desafio_tecnico_ai_eng_promotions.csv
│   └── politicas_da_loja.pdf
├── src/
│   ├── agent/
│   │   ├── prompts.py          # Definição do System Prompt e Persona
│   │   ├── workflow.py         # Grafo / Lógica principal do agente
│   │   └── tools/              # Ferramentas disponíveis para o agente
│   │       ├── sql_tool.py     # Leitura e consulta dos CSVs
│   │       └── rag_tool.py     # Busca vetorial no PDF de políticas
│   ├── database/               # Ingestão e setup de índices (ChromaDB / DuckDB)
│   └── app.py                  # Ponto de entrada da interface (Streamlit / CLI)
├── tests/                      # Testes automatizados de roteamento e respostas
├── examples/                   # Casos de uso e logs em markdown (Entregável 3)
│   ├── conversa_01_catalogo.md
│   ├── conversa_02_politicas.md
│   └── conversa_03_rastreio.md
├── README.md                   # Instruções, justificativas e uso de IA
├── requirements.txt / pyproject.toml
└── escopo.md
```

---

## 5. Cronograma de Execução e Checkins

### 📍 Checkin 1: Estruturação & Modelagem dos Dados
- [x] Configuração do ambiente de desenvolvimento Python e controle de versão Git.
- [x] Análise dos 6 arquivos CSV e mapeamento do esquema relacional (Primary Keys e Foreign Keys).
- [x] Leitura e indexação do PDF `politicas_da_loja.pdf` no Vector DB (ChromaDB/FAISS) usando chunking de parágrafos/seções.
- [x] Teste isolado do retriever RAG para confirmar respostas precisas sobre garantia, prazos e políticas.

#### Modelo relacional dos CSVs

| Tabela | Chave primária | Chaves estrangeiras | Cardinalidade / observações |
|---|---|---|---|
| `categories` | `category_id` | — | Uma categoria pode ter vários produtos; 6 das 9 categorias aparecem em `products`. |
| `customers` | `customer_id` | — | Um cliente pode ter vários pedidos; 18 dos 50 clientes aparecem em `orders`. |
| `products` | `product_id` | `category_id` → `categories.category_id` | Cada produto referencia uma categoria; há 65 produtos. |
| `orders` | `order_id` | `customer_id` → `customers.customer_id` | Cada pedido referencia um cliente; um cliente pode ter vários pedidos. |
| `order_items` | (`order_id`, `product_id`) | `order_id` → `orders.order_id`; `product_id` → `products.product_id` | Tabela associativa entre pedidos e produtos; `quantity` registra a quantidade. O par é único nas 22 linhas fornecidas. |
| `promotions` | `promotion_id` | `product_id` → `products.product_id` | Um produto pode aparecer em várias promoções; 22 produtos aparecem nas 25 linhas. |

As cinco relações de chave estrangeira foram conferidas contra os CSVs: não há valores nulos nem referências órfãs nessas colunas. As chaves primárias simples são únicas e não nulas. A chave composta de `order_items` é única neste conjunto de dados; se o modelo passar a permitir várias linhas do mesmo produto no mesmo pedido, será necessário adicionar um identificador próprio para o item.

### 📍 Checkin 2: Desenvolvimento de Ferramentas (Tools) & System Prompt
- [x] Implementação da ferramenta de consulta SQL/Dataframe (`sql_tool.py`) para buscas de estoque, preços e status de pedidos.
- [x] Implementação da ferramenta de RAG (`rag_tool.py`) para consulta ao manual de políticas.
- [x] Construção do prompt do sistema (`prompts.py`) fixando a persona "Empório da Música" (Campo Grande/MS, recusa de acessórios, tom amigável).
- [x] Testes offline de schemas e execução de cada ferramenta pelo grafo com modelo simulado (`tests/test_tool_routing.py`).
- [ ] Validar com chamadas reais ao Gemini a seleção da ferramenta adequada para cada pergunta (`tests/integration/test_gemini_tool_routing.py`).

### 📍 Checkin 3: Orquestração do Agente & Histórico de Conversa
- [x] Conexão das ferramentas ao Grafo do Agente (`LangGraph`/`ReAct`).
- [x] Implementação da memória persistente em SQLite para manter o histórico das conversas por thread.
- [ ] Adição de tratamentos para percursos de exceção (perguntas fora do escopo, produtos indisponíveis ou descontinuados).

### 📍 Checkin 4: Interface & Entregáveis de Avaliação
- [x] Desenvolvimento da interface de chat (`Streamlit` ou script CLI interativo).
- [x] Elaboração das conversas de exemplo (`examples/*.md`) cobrindo cenários simples e complexos (ex.: verificação de estoque + política de parcelamento).
- [x] Redação do `README.md` detalhado com:
  - Instruções de instalação e execução.
  - Justificativa das escolhas técnicas (LLM, RAG, DuckDB, etc.).
  - Declaração transparente do uso de ferramentas de IA (Cursor/Copilot/Claude).
  - Limitações e melhorias futuras.
- [ ] Revisão final dos commits e envio do repositório público.