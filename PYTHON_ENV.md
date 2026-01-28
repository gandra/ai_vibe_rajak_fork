# Python Environment Setup (uv)

Kosmodrom API koristi **uv** - ultra-brzi Python package manager napisan u Rust-u.

## Zašto uv?

| Feature | uv | pip/venv | poetry |
|---------|-----|----------|--------|
| Brzina instalacije | 🚀 10-100x brže | Sporo | Srednje |
| Lock file | ✅ `uv.lock` | ❌ | ✅ |
| Resolver | ✅ Brz & tačan | ⚠️ Spor | ✅ |
| Disk space | ✅ Global cache | ❌ Duplikati | ❌ |
| Python management | ✅ Ugrađeno | ❌ | ❌ |

---

## 1. Instalacija uv

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Homebrew (macOS)
brew install uv

# Proveri instalaciju
uv --version
```

---

## 2. Inicijalizacija projekta (od nule)

```bash
cd PROJECT_ROOT

# Kreiraj novi projekat (generiše pyproject.toml, .venv, itd.)
uv init

# Ili kreiraj sa specifičnim imenom
uv init my-project
cd my-project

# Dodaj dependencies
uv add fastapi uvicorn

# Dodaj dev dependencies
uv add --dev pytest

# Aktiviraj virtualenv (opciono - uv run automatski koristi)
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### Ako već imaš pyproject.toml (kloniran repo)

```bash
cd PROJECT_ROOT

# Instaliraj dependencies iz postojećeg pyproject.toml
uv sync

# Aktiviraj virtualenv (opciono)
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

---

## 3. Svakodnevne komande

### Pokretanje aplikacije

```bash
# Pokreni FastAPI server (development)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ili sa aktiviranim venv
uvicorn app.main:app --reload
```

### Dodavanje paketa

```bash
# Dodaj runtime dependency
uv add fastapi

# Dodaj dev dependency
uv add --dev pytest

# Dodaj sa verzijom
uv add "sqlalchemy>=2.0.0,<3.0.0"
```

### Uklanjanje paketa

```bash
uv remove package-name
```

### Ažuriranje paketa

```bash
# Ažuriraj sve
uv sync --upgrade

# Ažuriraj specifičan paket
uv add package-name --upgrade
```

---

## 4. Reset Environment (Čist start)

### Opcija A: Soft Reset (brzo)

```bash
# Obriši venv i ponovo instaliraj
rm -rf .venv
uv sync
```

### Opcija B: Hard Reset (potpuno čišćenje)

```bash
# Obriši sve uv artefakte
rm -rf .venv
rm -f uv.lock

# Ponovo kreiraj od pyproject.toml
uv sync
```

### Opcija C: Nuclear Reset (uključuje cache)

```bash
# Obriši sve + globalni cache
rm -rf .venv
rm -f uv.lock
uv cache clean

# Fresh start
uv sync
```

---

## 5. Kreiranje iz pyproject.toml

Ako dobiješ samo `pyproject.toml` bez `uv.lock`:

```bash
cd /workspace/kosmodrom-api

# Kreiraj venv i generiši lock file
uv sync

# Ovo će:
# 1. Kreirati .venv/ folder
# 2. Instalirati sve dependencies
# 3. Generisati uv.lock file
```

---

## 6. Prebacivanje Python verzije

```bash
# Instaliraj Python verziju
uv python install 3.12

# Koristi specifičnu verziju za projekat
uv python pin 3.12

# Lista instaliranih verzija
uv python list
```

---

## 7. Troubleshooting

### Problem: "No module named 'app'"

```bash
# Proveri da li je venv aktivan
which python  # Treba da pokazuje .venv/bin/python

# Reinstaliraj
uv sync
```

### Problem: Konflikt verzija

```bash
# Obriši lock i ponovo reši
rm uv.lock
uv sync
```

### Problem: Stari cache

```bash
uv cache clean
uv sync
```

### Problem: Permission denied

```bash
# Linux/macOS
chmod +x .venv/bin/*
```

---

## 8. CI/CD integracija

### GitHub Actions

```yaml
- name: Install uv
  uses: astral-sh/setup-uv@v4

- name: Install dependencies
  run: uv sync --frozen

- name: Run tests
  run: uv run pytest
```

### Docker

```dockerfile
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

## 9. Korisni aliasi (.bashrc / .zshrc)

```bash
# Dodaj u ~/.bashrc ili ~/.zshrc
alias uvr="uv run"
alias uvs="uv sync"
alias uva="uv add"
alias uvd="uv add --dev"
alias uvup="uv sync --upgrade"

# Korišćenje
uvr uvicorn app.main:app --reload
uva requests
uvd pytest
```

---

## 10. Struktura fajlova

```
kosmodrom-api/
├── pyproject.toml      # Dependency definicije
├── uv.lock             # Lock file (commit u git)
├── .venv/              # Virtual environment (NE COMMIT)
├── .python-version     # Python verzija (opciono)
└── app/                # Source code
```

### .gitignore (već podešeno)

```gitignore
.venv/
.uv/
__pycache__/
```

---

## Quick Reference Card

| Akcija | Komanda |
|--------|---------|
| Instaliraj sve | `uv sync` |
| Pokreni app | `uv run uvicorn app.main:app --reload` |
| Dodaj paket | `uv add package` |
| Dodaj dev paket | `uv add --dev package` |
| Ukloni paket | `uv remove package` |
| Ažuriraj sve | `uv sync --upgrade` |
| Reset venv | `rm -rf .venv && uv sync` |
| Očisti cache | `uv cache clean` |
| Python verzija | `uv python install 3.12` |

---

*Dokumentacija ažurirana: 2024-12*
