# Python Environment Setup (uv)

Ovaj projekat (AI Agents kurs) koristi **uv** - ultra-brzi Python package manager napisan u Rust-u.

---

## Najkorišćenije komande

```bash
# Aktiviraj virtualenv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Pokreni bilo koji skript (bez aktivacije venv-a)
uv run python session8/agent_workflow.py
uv run python session10/main.py

# Instaliraj sve dependencies iz pyproject.toml
uv sync

# Dodaj novi paket
uv add langchain-openai

# Dodaj dev dependency
uv add --dev pytest

# Ukloni paket
uv remove package-name

# Ažuriraj sve pakete
uv sync --upgrade

# Ažuriraj samo jedan paket
uv add langchain-core --upgrade

# Reset venv (čist start)
rm -rf .venv && uv sync
```

> **Napomena:** `uv run` automatski koristi `.venv` bez potrebe za aktivacijom. Aktivacija je korisna samo ako želiš da koristiš `python` direktno u terminalu.

---

## Debug u PyCharm

### 1. Podesi Python interpreter

1. **File → Settings → Project → Python Interpreter**
2. Klikni na **Add Interpreter → Add Local Interpreter**
3. Izaberi **Existing** i navigiraj do:
   ```
   <project_root>/.venv/bin/python     # macOS/Linux
   <project_root>/.venv/Scripts/python  # Windows
   ```
4. Klikni **OK** — PyCharm će prepoznati sve instalirane pakete

> Ako `.venv` ne postoji, prvo pokreni `uv sync` u terminalu.

### 2. Podesi Run/Debug konfiguraciju

1. **Run → Edit Configurations → + → Python**
2. Popuni polja:
   - **Name:** npr. `session10 - main`
   - **Script path:** izaberi fajl, npr. `session10/main.py`
   - **Working directory:** postavi na folder sesije, npr. `<project_root>/session10`
     (ovo je bitno jer mnogi skriptovi koriste relativne putanje do `data/` foldera)
   - **Python interpreter:** proveri da je izabran `.venv` interpreter iz koraka 1
3. Klikni **OK**

### 3. Environment varijable u PyCharm

1. U **Run/Debug Configuration** klikni na **Environment variables** polje
2. Dodaj potrebne varijable:
   ```
   OPENAI_API_KEY=sk-...
   OLLAMA_HOST=http://127.0.0.1:11434
   OLLAMA_MODEL=gemma3:4b
   ```
3. Alternativno, instaliraj **EnvFile** plugin i koristi `.env` fajl

### 4. Debugovanje

- Postavi breakpoint klikom levo od broja linije (crvena tačka)
- Pokreni sa **Debug** (ikonica bube, ili `Shift+F9`)
- Koristi debug panel:
  - **Step Over (F8)** — izvrši liniju, preskoči pozive funkcija
  - **Step Into (F7)** — uđi u pozvanu funkciju
  - **Step Out (Shift+F8)** — izađi iz trenutne funkcije
  - **Resume (F9)** — nastavi do sledećeg breakpointa
  - **Evaluate Expression (Alt+F8)** — izvrši proizvoljnu Python ekspresiju tokom pauziranja

### 5. Debug async koda (MCP, LangGraph)

Session 7 (MCP) i session 9/10 (LangGraph) koriste `asyncio`. PyCharm podržava async debug automatski — breakpointi rade normalno unutar `async def` funkcija. Samo se pobrini da je **Gevent compatible** isključen u:
**Settings → Build, Execution, Deployment → Python Debugger** (podrazumevano je isključen).

---

## Zašto uv?

| Feature | uv | pip/venv | poetry |
|---------|-----|----------|--------|
| Brzina instalacije | 10-100x brže | Sporo | Srednje |
| Lock file | `uv.lock` | nema | ima |
| Resolver | Brz & tačan | Spor | OK |
| Disk space | Global cache | Duplikati | Duplikati |
| Python management | Ugrađeno | nema | nema |

---

## Instalacija uv

```bash
# macOS (Homebrew)
brew install uv

# Linux / macOS (curl)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Proveri instalaciju
uv --version
```

---

## Inicijalizacija projekta

### Kloniran repo (već postoji pyproject.toml)

```bash
cd <project_root>
uv sync                           # Kreira .venv/, instalira deps, generiše uv.lock
source .venv/bin/activate          # Opciono
```

### Novi projekat od nule

```bash
uv init
uv add langchain-core langgraph   # Dodaj dependencies
uv add --dev pytest               # Dev dependencies
```

---

## Prebacivanje Python verzije

```bash
uv python install 3.12     # Instaliraj verziju
uv python pin 3.12         # Koristi za ovaj projekat
uv python list              # Lista instaliranih verzija
```

---

## Session-specifične zavisnosti

Projekat drži zavisnosti na nivou root `pyproject.toml`. Za sesije koje zahtevaju dodatne pakete:

```bash
# Session 7: MCP + LangChain + Ollama
uv add mcp httpx langchain-ollama langchain-core pydantic

# Session 9-10: LangGraph + RAG
uv add langgraph langchain-openai faiss-cpu beautifulsoup4

# Ollama server (mora da radi za session 7, 8, 9)
ollama serve
ollama pull gemma3:4b
```

---

## Reset Environment

```bash
# Soft Reset (brzo)
rm -rf .venv && uv sync

# Hard Reset (ponovo reši sve zavisnosti)
rm -rf .venv && rm -f uv.lock && uv sync

# Nuclear Reset (uključuje globalni cache)
rm -rf .venv && rm -f uv.lock && uv cache clean && uv sync
```

---

## Troubleshooting

### "No module named ..."

```bash
which python                # Treba da pokazuje .venv/bin/python
uv sync                     # Reinstaliraj
```

### Konflikt verzija

```bash
rm uv.lock && uv sync       # Ponovo reši zavisnosti
```

### Stari cache

```bash
uv cache clean && uv sync
```

### Permission denied (Linux/macOS)

```bash
chmod +x .venv/bin/*
```

---

## Struktura fajlova

```
ai_vibe_rajak_fork/
├── pyproject.toml      # Dependency definicije
├── uv.lock             # Lock file (commit u git)
├── .venv/              # Virtual environment (NE COMMIT)
├── .python-version     # Python verzija (3.12)
├── session1-10/        # Po jedan folder po sesiji
└── PYTHON_ENV.md       # Ovaj fajl
```

---

## Quick Reference Card

| Akcija | Komanda |
|--------|---------|
| Instaliraj sve | `uv sync` |
| Pokreni skript | `uv run python session8/agent_workflow.py` |
| Dodaj paket | `uv add package` |
| Dodaj dev paket | `uv add --dev package` |
| Ukloni paket | `uv remove package` |
| Ažuriraj sve | `uv sync --upgrade` |
| Reset venv | `rm -rf .venv && uv sync` |
| Očisti cache | `uv cache clean` |
| Python verzija | `uv python install 3.12` |
