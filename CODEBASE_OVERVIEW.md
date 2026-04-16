# Codebase Overview — DataOps ETL Pipeline

## Overview

This is a **DataOps ETL pipeline** with an integrated **RAG-based AI monitoring agent**. It processes data files, validates and transforms them, logs results, then lets you query those logs via a local LLM using semantic search.

---

## Architecture

```
main.py
  ├── etl/pipeline.py        → orchestrates ETL
  │   ├── etl/extract.py     → reads files
  │   ├── etl/transform.py   → validates + transforms
  │   └── etl/load.py        → loads (stub)
  │
  ├── rag/ingest_logs.py     → embeds ETL logs into vector DB
  │
  └── rag/agent_chat.py      → interactive AI chat loop
      └── rag/rag_query.py   → RAG query engine
          ├── rag/retriever.py   → semantic search
          ├── rag/embedder.py    → embedding model
          ├── rag/vector_store.py → ChromaDB
          └── rag/llm_client.py  → local LLM API call
```

---

## ETL Layer (`etl/`)

| File | Purpose |
|---|---|
| `etl/extract.py` | Reads all files from `data/`, auto-detects CSV delimiters, supports `.csv`, `.txt`, `.json`, `.xlsx` |
| `etl/transform.py` | Validates data then adds a `tax` column (`amount * 0.1`) |
| `etl/load.py` | Stub — prints "Data loaded successfully" (no actual DB write yet) |
| `etl/pipeline.py` | Loops over each file, runs E→T→L, catches per-file errors, logs final status as `SUCCESS` / `FAILURE` / `PARTIAL_SUCCESS` |

### Validation Rules (`utils/validation_rules.py`)

Four checks run in order, stopping early on critical failures:

1. **Schema check** — `id` and `amount` columns must exist
2. **Type check** — `amount` must be numeric (non-numeric → `NaN` → error)
3. **Value check** — no negative amounts
4. **Duplicate check** — no duplicate `id` values

### Logging (`utils/logger.py`)

Writes a structured `etl_log.json` with timestamp, per-file status, error details, and aggregate counts.

---

## RAG / AI Layer (`rag/`)

| File | Purpose |
|---|---|
| `rag/embedder.py` | Uses `sentence-transformers/all-MiniLM-L6-v2` to embed text |
| `rag/vector_store.py` | In-memory ChromaDB collection named `etl_logs` |
| `rag/ingest_logs.py` | Reads `etl_log.json`, converts each file's result to a sentence, embeds it, stores in ChromaDB |
| `rag/retriever.py` | Embeds a query, retrieves top-3 most similar log entries from ChromaDB |
| `rag/llm_client.py` | Sends prompts to a **local LM Studio** server at `localhost:1234` running `google/gemma-3-4b` |
| `rag/rag_query.py` | Builds a prompt: injects retrieved log context + user question, instructs LLM to identify failures, explain root causes, and suggest remediation |
| `rag/agent_chat.py` | REPL loop — reads user input, calls `ask_pipeline()`, prints response |

---

## Sample Data (`data/`)

| File | Issue |
|---|---|
| `data/file1.csv` | Duplicate IDs (id=1 appears twice) → will FAIL |
| `data/file2.csv` | Clean data → will SUCCEED |
| `data/file3.csv` | Clean data → will SUCCEED |
| `data/file4.txt` | Pipe-delimited (`\|`) → auto-detected and read correctly |

---

## CI/CD (`.github/workflows/etl.yml`)

- Triggered **manually** via `workflow_dispatch`
- Runs `python main.py` on `ubuntu-latest` with Python 3.10
- On **failure**:
  - Uploads `etl_log.json` as a GitHub Actions artifact
  - Triggers a `repository_dispatch` event to a separate **agentic repo** (`dataops-agentic`) with the `run_id` — designed to kick off an automated remediation agent

---

## End-to-End Flow

1. `main.py` runs the ETL pipeline
2. Results are written to `etl_log.json`
3. Logs are embedded into ChromaDB (in-memory)
4. An interactive chat starts — you can ask questions like "which files failed and why?"
5. The RAG engine retrieves relevant log entries and passes them to the local Gemma model for a natural-language answer

---

## Dependencies (`requirements.txt`)

| Package | Role |
|---|---|
| `pandas` | DataFrame operations |
| `numpy` | Numerical support |
| `openpyxl` | Excel file reading |
| `chromadb` | In-memory vector database |
| `sentence-transformers` | Text embedding model |
| `requests` | HTTP calls to local LLM |
| `langchain` | LLM framework (available, not yet wired in) |
| `langchain-community` | Community integrations for LangChain |
