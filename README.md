RAG & Agent-Based Customer Support for Robotic Vacuums

A Python application combining document retrieval and a LangChain tool-calling agent to answer robotic vacuum questions and generate usage reports from sample records. A Streamlit interface brings the retrieval pipeline, agent tools, and report workflow into one chat experience.

The project demonstrates document ingestion, semantic search, LLM tool calling, runtime context handling, and middleware-driven prompt switching. The interface, knowledge base, and responses are primarily in Chinese.

## Key Features

- **Knowledge-base question answering:** Retrieves product guidance, maintenance instructions, and troubleshooting information to support generated answers.
- **Document ingestion:** Loads PDF and UTF-8 text files, splits them into overlapping chunks, and indexes them in persistent Chroma storage.
- **Content deduplication:** Uses file-level MD5 hashes to skip previously ingested document content.
- **Agent tool calling:** Exposes seven tools for RAG summarization, sample usage-record lookup, contextual demo data, and report prompt activation.
- **Dynamic report prompts:** Uses middleware to update runtime context and switch the system prompt for subsequent report generation.
- **Chat interface:** Provides a Streamlit UI with session-level message display and progressive response rendering.

## Architecture

```text
PDF / TXT documents
        |
        v
Document loaders -> Recursive splitting -> DashScope embeddings -> Chroma
                                                                     ^
                                                                     |
Streamlit chat -> LangChain agent -> RAG tool -> Retrieval + LLM summary
                        |
                        +-> Usage-record tool -> Local CSV
                        |
                        +-> Contextual demo tools
                        |
                        +-> Report marker -> Middleware -> Report prompt
                        |
                        v
                 Response displayed in chat
```

The agent uses `langchain.agents.create_agent`. LangGraph runtime types support the middleware integration; orchestration is handled through LangChain's agent API.

### Retrieval Pipeline

1. Load knowledge documents with `PyPDFLoader` and `TextLoader`.
2. Check file hashes against a local ingestion ledger.
3. Split new content with `RecursiveCharacterTextSplitter`.
4. Generate DashScope embeddings and persist chunks in Chroma.
5. Retrieve the top three matching chunks for a query.
6. Pass the query and reference context through a prompt-template → chat-model → string-parser chain.
7. Return the summary as a tool result for the agent's response.

### Report Workflow

The main prompt guides the agent to obtain a demo user ID and report month, activate report context, and retrieve matching usage records. Tool middleware sets a runtime flag after the report marker runs; dynamic prompt middleware selects the report prompt for subsequent model calls. This demonstrates prompt-driven tool coordination with runtime context.

## Technology Stack

| Component | Implementation |
| --- | --- |
| Language | Python |
| Agent and chains | LangChain, LangChain Core |
| Provider integration | LangChain Community, DashScope SDK |
| Chat model | Qwen via ChatTongyi (`qwen3-max`) |
| Embeddings | DashScope (`text-embedding-v4`) |
| Vector store | Chroma via `langchain-chroma` |
| Document processing | PDF/text loaders, recursive character splitting |
| Interface | Streamlit |
| Configuration | YAML |

## Project Structure

```text
agent/
  react_agent.py         # Agent setup and execution
  tools/
    agent_tools.py      # Retrieval, record lookup, and demo tools
    middleware.py       # Tool monitoring and dynamic prompts
config/                 # Model, retrieval, prompt, and data settings
data/
  *.txt, *.pdf          # Robotic vacuum knowledge documents
  external/records.csv  # Sample usage records
model/factory.py        # Chat and embedding model factories
prompts/                # Customer support, RAG, and report prompts
rag/
  vector_store.py       # Ingestion and semantic retrieval
  rag_service.py        # Retrieval and summarization chain
utils/
  app.py                # Streamlit entry point
  ...                   # Configuration, paths, logging, and file utilities
requirements.txt
README.md
```

## Quick Start

Prerequisites: Python 3.12, a DashScope API key, and access to the configured chat and embedding models. Run the following commands from the project root in Windows PowerShell.

### 1. Install Dependencies

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Configure Credentials

```powershell
$env:DASHSCOPE_API_KEY = "YOUR_DASHSCOPE_API_KEY"
$env:PYTHONPATH = (Get-Location).Path
```

Set these variables in the same terminal used to run the application. Credentials are read from the environment; the current implementation does not load `.env` files.

### 3. Build the Knowledge Base

```powershell
.\.venv\Scripts\python.exe -m rag.vector_store
```

This indexes supported files directly inside `data/` and runs a sample retrieval query. Check the logs for ingestion errors before starting the interface.

### 4. Launch the Application

```powershell
.\.venv\Scripts\python.exe -m streamlit run utils/app.py
```

Keep the working directory at the project root so Chroma uses the intended persistence directory.

## Example Requests

| Scenario | Example input |
| --- | --- |
| Product selection | `小户型适合哪些扫地机器人？` |
| Troubleshooting | `扫地机器人迷路了怎么办？` |
| Usage report | `给我生成我的使用报告` |

Model settings are in `config/rag.yml`. Retrieval and chunking settings are in `config/chroma.yml`; defaults are three retrieved chunks, 200 characters per chunk, and a 20-character overlap.

## Demo Scope

- Weather is fixed example data; location, user ID, and report month are randomly selected demo values. Usage reports read a local CSV rather than a live external service.
- Chat history is retained for display within a Streamlit session. Each agent request currently receives only the latest user input.
- Responses are rendered progressively from agent state updates with a character-display delay.
- MD5 checks prevent repeated ingestion of unchanged content; modified or deleted documents are not automatically synchronized with existing vectors.
- The dependency manifest is source-derived. A tested version lock and end-to-end setup validation are pending.

## Future Work

- Add model-visible conversation history and improve response streaming.
- Introduce retrieval evaluation and representative agent workflow tests.
- Support document replacement and deletion in the vector index.
- Replace contextual demo tools with real integrations.
