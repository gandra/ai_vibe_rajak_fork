# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Agents learning repository progressing through 10 sessions — from embedding fundamentals to full LangGraph pipelines with validation loops. Each session is self-contained in its own directory. Written in Python 3.12, managed with **uv**.

**Core stack**: Python 3.12, LangGraph, LangChain, crewAI, LlamaIndex, Ollama, OpenAI API, FastMCP, FAISS

## Common Commands

```bash
# Install all dependencies (from repo root)
uv sync

# Run any session script
uv run python session8/agent_workflow.py

# Add a dependency
uv add <package>
```

### crewAI (session4/hello/)
```bash
cd session4/hello && crewai install
crewai run                  # Run the multi-agent crew
crewai train / replay / test
```

### RAG Server (session4/rag/)
```bash
cd session4/rag
source env.sh               # Sets OPENAI_API_KEY and paths
python load.py              # Ingest documents into vector store
python server_rerank_chat.py # Start Flask RAG server
```

### MCP CLI (session7/)
```bash
cd session7
uv run python mcp_cli.py   # Must run from session7/ (spawns MCP server via stdio)
```

### Session 9 RAG Agent
```bash
cd session9
python indexr.py            # Build FAISS index from URLs
python graph.py             # Run RAG agent with hallucination grading
# Also compatible with LangGraph Studio via langgraph.json
```

### Session 10 CV Tailoring
```bash
cd session10
pip install -r requirements.txt
python main.py              # Runs full 10-step pipeline, generates graph_visualization.png
# Input: data/input/cv_original.html + data/input/job_description.txt
# Output: data/output/cv_tailored.html + data/output/gap_questions.txt
```

### Docker (Ollama)
```bash
docker compose up -d        # Starts Ollama server on port 11435
```

### Dev Container
```bash
docker build -f .devcontainer/Dockerfile -t claude-sandbox .
docker run -it --cap-add=NET_ADMIN --cap-add=NET_RAW -v "$(pwd):/workspace" claude-sandbox
```

## Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI models & embeddings | — |
| `SERPER_API_KEY` | Web search (SerperDevTool, session5) | — |
| `OLLAMA_HOST` | Ollama server URL | `http://127.0.0.1:11434` |
| `OLLAMA_MODEL` | Ollama model name | `gemma3:4b` |

Session 9 also uses Langfuse tracing vars (`LANGFUSE_SECRET_KEY`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_HOST`) configured in `session9/.env`.

## Architecture

### Session Progression

| Session | Focus | Framework |
|---------|-------|-----------|
| 1–3 | Embeddings, cosine similarity, FAISS/CLIP | Ollama, OpenAI |
| 4 | Multi-agent orchestration + RAG server | crewAI, LlamaIndex |
| 5 | Conditional tasks, human-in-loop | crewAI (`ConditionalTask`) |
| 6 | LLM tool binding | LangChain (`bind_tools`) |
| 7 | MCP protocol (server/client over stdio) | FastMCP, LangChain-Ollama |
| 8 | Content generation workflow | LangGraph `StateGraph` |
| 9 | RAG with hallucination detection & retry | LangGraph, FAISS, grading chains |
| 10 | CV tailoring with fabrication validation | LangGraph, BeautifulSoup |

### crewAI Pattern (session 4)

YAML-driven multi-agent system:
- `src/hello/config/agents.yaml` — agent personas (role, goal, backstory with `{topic}` interpolation)
- `src/hello/config/tasks.yaml` — task definitions and agent assignments
- `src/hello/crew.py` — orchestration via `@CrewBase`, `@agent`, `@task`, `@crew` decorators
- Agents execute sequentially via `Process.sequential`

### MCP Three-Tier Pattern (session 7)

`mcp_cli.py` (HOST+CLIENT) spawns `weather-and-air-quality.py` (SERVER) via stdio:
- **Router LLM** (temp=0.0): classifies intent → tool call vs. general chat
- **General LLM** (temp=0.4): handles non-tool conversation
- **Answer LLM** (temp=0.2): formats tool results into natural language

Server exposes `get_weather` and `get_air_quality` tools using Open-Meteo API (no auth needed).

### LangGraph Patterns (sessions 8–10)

All use `StateGraph` with `TypedDict` state. Sessions 9 and 10 introduce **conditional retry loops**:

**Session 9 (RAG)**: `retrieve → grade_documents → generate → hallucination_check` — if hallucinated, retransforms query and retries (no counter limit).

**Session 10 (CV Tailoring)**: 10-node pipeline with counter-based retry (max 3):
```
IngestFiles → ParseCVHtml → AnalyzeJD → GapAnalysis → Planner
    → TailorWriter ↔ Validator (max 3 retries)
    → GapQuestions → RenderHTML → WriteOutputs
```

Key structural pattern in session 10:
- `state.py` — `CVTailoringState` TypedDict with ~12 keys, progressively populated
- `nodes/` — one file per graph node (10 files), each receives/returns state dict
- `prompts/` — separate `PromptTemplate` instances per LLM-calling node
- Validation is both LLM-based (semantic) and deterministic (fabrication detection)

`session10_gandra/` is a parallel variant of session 10 with identical architecture.

### Codex Directory

`codex/CODEX_INSTRUCTIONS.MD` contains a system prompt defining an AI consultant role emphasizing SOLID principles and clean architecture. `codex/PROMPT.MD` tracks active tasks.
