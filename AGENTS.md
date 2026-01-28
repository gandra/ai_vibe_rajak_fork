# Repository Guidelines

## Project Structure & Module Organization
- Root app: `main.py` (simple Python entrypoint).
- Sessions: `session1`–`session7/` contain self‑contained examples and assets (e.g., `index.html`).
- CrewAI demo: `session4/hello/` is a standalone package under `session4/hello/src/hello/` with YAML configs in `.../config/` and sample tool in `.../tools/`.
- RAG utilities: `session4/rag/` (data, loaders, and `server_rerank_chat.py`).
- Tooling: Python pinned via `.python-version` (3.12). Dev container in `.devcontainer/`.

## Build, Test, and Development Commands
- Setup (uv): `uv sync` at repo root. For the CrewAI subproject: `cd session4/hello && uv sync`.
- Run root script: `uv run python main.py`.
- Run CrewAI: `cd session4/hello && uv run hello` (or `uv run run_crew`).
  - Train: `uv run train 3 out.json`  • Replay: `uv run replay <task_id>`  • Test: `uv run test 3 gpt-4o-mini`.
- Example scripts: `uv run python session6/tool_chat.py`, `uv run python session7/mcp_cli.py`.
- RAG server: `uv run python session4/rag/server_rerank_chat.py`.

## Coding Style & Naming Conventions
- Python 3.12 for root; `session4/hello` supports 3.10–3.13.
- 4‑space indentation, type hints, module‑level docstrings.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_CASE`.
- Use f‑strings, avoid global state, keep functions small and focused.
- If adding tooling, prefer Black + Ruff (configure in `pyproject.toml`).

## Testing Guidelines
- Framework: pytest. Place tests in `tests/` or alongside session code.
- Names: files `test_*.py`, functions `test_*`.
- Run: `uv add --dev pytest` then `uv run pytest -q`.
- Aim for ≥80% coverage; mock external APIs.

## Commit & Pull Request Guidelines
- Commits: imperative present (e.g., `session6: add tool calls demo`). Keep changes scoped and atomic.
- PRs: include summary, rationale, run instructions, and screenshots for HTML/UI changes. Link related issues and update docs when commands/paths change.

## Security & Configuration Tips
- Never commit secrets. Export keys as env vars (e.g., `export OPENAI_API_KEY=...`).
- Large assets belong under `session4/rag/data/`; avoid adding files >10MB without context.
