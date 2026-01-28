# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Agents Learning Repository focused on multi-agent orchestration using Python. The codebase progresses through 7 sessions exploring different AI frameworks and patterns.

**Core Technologies**: Python 3.10+, crewAI, LangChain, LlamaIndex, Ollama, OpenAI API, FastMCP

## Common Commands

### crewAI Project (session4/hello/)

```bash
# Install dependencies
pip install uv
cd session4/hello && crewai install

# Run the multi-agent crew
crewai run

# Other commands
crewai train        # Train crew for N iterations
crewai replay       # Replay execution from specific task
crewai test         # Test crew execution
```

### RAG Server (session4/rag/)

```bash
cd session4/rag
source env.sh       # Set OPENAI_API_KEY and paths
python load.py      # Load documents into vector store
python server_rerank_chat.py  # Start Flask RAG server
```

### MCP CLI (session7/)

```bash
cd session7
# Requires: OLLAMA_HOST, OLLAMA_MODEL env vars (defaults: http://127.0.0.1:11434, gemma3:4b)
python mcp_cli.py   # Interactive weather/air quality CLI
```

### Individual Session Scripts

```bash
python session5/hitl.py         # Human-in-loop with SerperDevTool
python session5/conditional.py  # Conditional task execution
python session6/tool_chat.py    # LangChain tool binding
```

## Architecture

### Session Structure

| Session | Focus | Key Files |
|---------|-------|-----------|
| 1-3 | Foundation (embeddings with Ollama/OpenAI) | `instruct.txt` notes |
| 4 | crewAI multi-agent + RAG | `hello/` (full crew), `rag/` (LlamaIndex) |
| 5 | Conditional tasks, Human-in-Loop | `hitl.py`, `conditional.py` |
| 6 | LangChain tool integration | `tool_chat.py`, `tools_exp.py` |
| 7 | MCP protocol integration | `mcp_cli.py`, `weather-and-air-quality.py` |

### crewAI Pattern (session4/hello/)

The main multi-agent system uses crewAI's decorator-based architecture:

- **`src/hello/config/agents.yaml`** - Agent definitions (role, goal, backstory with `{topic}` interpolation)
- **`src/hello/config/tasks.yaml`** - Task definitions (description, expected_output, agent assignment)
- **`src/hello/crew.py`** - Crew orchestration using `@CrewBase`, `@agent`, `@task`, `@crew` decorators
- **`src/hello/main.py`** - Entry point with `run()`, `train()`, `replay()`, `test()` functions
- **`knowledge/`** - User preference files for knowledge base

Agents execute tasks sequentially via `Process.sequential` (hierarchical also supported).

### Key Patterns Used

1. **YAML Configuration** - Agent personas and task definitions externalized from code
2. **Decorator Pattern** - `@agent`, `@task`, `@crew` for modular crew setup
3. **Human-in-Loop** - `human_input=True` on tasks for user approval workflows
4. **Conditional Tasks** - `ConditionalTask` with callback functions to skip/execute based on prior output
5. **MCP Protocol** - Server/client pattern for external tool integration (weather, air quality APIs)
6. **LangChain Tool Binding** - `ChatOllama` with Pydantic output parsers for structured routing

## Environment Variables

Required API keys (set in `.env` or `env.sh`):
- `OPENAI_API_KEY` - For OpenAI models and embeddings
- `SERPER_API_KEY` - For web search via SerperDevTool
- `OLLAMA_HOST` - Ollama server URL (default: `http://127.0.0.1:11434`)
- `OLLAMA_MODEL` - Ollama model name (default: `gemma3:4b`)

## Docker Development Environment

The project includes a `.devcontainer/` setup for Claude Code sandbox:

```bash
# Build and run container
docker build -f .devcontainer/Dockerfile -t claude-sandbox .
docker run -it --name claude-container --cap-add=NET_ADMIN --cap-add=NET_RAW -v "$(pwd):/workspace" claude-sandbox

# Install Claude Code in container
npm install -g @anthropic-ai/claude-code
claude auth
```
