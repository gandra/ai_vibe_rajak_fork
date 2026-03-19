# HOWTO — Session 10 Gandra: CV Tailoring Agent

---

## 1. Kako pokrenuti aplikaciju (korak po korak)

### Preduslov: Python 3.12 + uv

```bash
# Proveri da li imaš uv
uv --version

# Ako nemaš:
brew install uv          # macOS
```

### Korak 1: Instaliraj dependencies

Iz root-a projekta:

```bash
cd /Users/draganmijatovic/learn/_COURSES/rajak/ai_vibe_rajak_fork

# Instaliraj session10_gandra zavisnosti u zajednički venv
uv add langgraph langchain-core langchain-openai beautifulsoup4 typing-extensions
```

Ili ako radiš izolovano samo sa requirements.txt:

```bash
cd session10_gandra
pip install -r requirements.txt
```

### Korak 2: Podesi OpenAI API key

Aplikacija trenutno koristi **hardcoded prazan string** u `nodes/parse_cv.py:54`. Postoji `.env.example` koji možeš kopirati:

```bash
cd session10_gandra
cp .env.example .env
```

Otvori `.env` i postavi svoj ključ:

```
OPENAI_API_KEY=sk-tvoj-kljuc-ovde
```

**Alternativno**, postavi environment varijablu u terminalu pre pokretanja:

```bash
export OPENAI_API_KEY="sk-tvoj-kljuc-ovde"
```

> **Napomena:** Kod u `nodes/parse_cv.py` (linija 54) ima `OPENAI_API_KEY = ""` i odmah ga stavlja u `os.environ`. Ako postaviš env varijablu pre pokretanja, moraš ili obrisati tu liniju ili je izmeniti da čita iz env-a. Najjednostavnije — postavi key pre pokretanja i on će biti dostupan svim LLM nodovima.

### Korak 3: Proveri da postoje input fajlovi

```bash
ls session10_gandra/data/input/
```

Trebalo bi da vidiš:

```
cv_original.html       # Sample CV (Jane Smith, backend developer)
cv_original_1.html     # Alternativni CV (nije aktivan u kodu)
job_description.txt    # Senior Backend Engineer @ FinTech startup
```

Oba fajla koja su potrebna za pokretanje (`cv_original.html` i `job_description.txt`) su već tu.

### Korak 4: Pokreni aplikaciju

```bash
cd session10_gandra
uv run python main.py
```

Ili sa aktiviranim venv-om:

```bash
source ../.venv/bin/activate
cd session10_gandra
python main.py
```

### Korak 5: Šta da očekuješ od pokretanja

Trenutno je aktivan **Checkpoint A** (Steps 1-2). Očekivani output:

```
📊 Graph image saved to graph_visualization.png
============================================================
  CV Tailoring Agent — LangGraph Pipeline
  Checkpoint A: IngestFiles → ParseCVHtml
============================================================
--- INGEST FILES ---
  ✅ CV loaded: 4276 chars from .../data/input/cv_original.html
  ✅ JD loaded: 2068 chars from .../data/input/job_description.txt
--- PARSE CV HTML (LLM-powered) ---
  📋 Name: Jane Smith
  📝 Summary: Experienced backend engineer with 8 years...
  🛠️  Skills: X found
  💼 Experience: Y roles
  🎓 Education: Z entries
  📜 Certifications: W entries

============================================================
  ✅ Checkpoint A complete! State keys populated:
============================================================
  • cv_html_raw: 4276 chars
  • jd_text: 2068 chars
  • cv_structured:
      name: Jane Smith
      skills: [...]
      experience: Y roles
      education: Z entries
```

Takođe se generiše `graph_visualization.png` — slika grafa sa dva čvora.

### Ako nešto ne radi

| Problem | Rešenje |
|---------|---------|
| `ModuleNotFoundError: No module named 'langgraph'` | `uv add langgraph langchain-core langchain-openai beautifulsoup4` |
| `openai.AuthenticationError` | Nisi postavio `OPENAI_API_KEY` ili je neispravan |
| `FileNotFoundError: CV file not found` | Pokreni iz `session10_gandra/` direktorijuma (ne iz root-a) |
| `graph_visualization.png` greška | Potreban internet (koristi Mermaid API za rendering) |

---

## 2. Roadmap — Gde smo i šta je sledeće

### Trenutni status

**Checkpoint A je završen** — Steps 1-2 rade. Ovo znači:
- IngestFiles čita CV i JD sa diska
- ParseCVHtml koristi LLM (gpt-4o-mini) da ekstrahuje strukturirane podatke iz HTML-a
- State sadrži: `cv_html_raw`, `jd_text`, `cv_structured`

### Preostali checkpointi

```
✅ Checkpoint A (Steps 1-2) — GOTOVO
     IngestFiles → ParseCVHtml

⬜ Checkpoint B (Steps 3-4) — SLEDEĆI KORAK
     + AnalyzeJD → GapAnalysis
     Prvi LLM pozivi za analizu JD-a i identifikaciju gap-ova.
     Učiš: LLM node, JsonOutputParser, multi-key state.

⬜ Checkpoint C (Steps 5-6)
     + PlannerAgent → TailorWriter
     LLM kreira plan za tailoring i piše novu verziju CV-a.
     Učiš: agent-style reasoning, state transformation, counter pattern.

⬜ Checkpoint D (Step 7) — NAJVAŽNIJI KORAK
     + ValidateTailoredCV + conditional edge (retry loop)
     Validacija da CV nema fabriciranih podataka.
     Učiš: add_conditional_edges, ciklus u grafu, max-retry safety.

⬜ Checkpoint E (Steps 8-10)
     + GenerateGapQuestions → RenderHTML → WriteOutputs
     Kompletiran pipeline — generiše fajlove na disk.
     Učiš: full graph assembly, end-to-end flow.
```

### Šta svaki korak konkretno zahteva

#### Checkpoint B: AnalyzeJD + GapAnalysis

**Step 3 — AnalyzeJD:**
1. Otkomentariši prompt u `prompts/analyze_jd.py`
2. Otkomentariši node funkciju u `nodes/analyze_jd.py`
3. Konfiguriši LLM instancu (isti pattern kao u `nodes/parse_cv.py`)
4. U `main.py`: otkomentariši import, dodaj node, pomeri edge

**Step 4 — GapAnalysis:**
1. Otkomentariši prompt u `prompts/gap_analysis.py`
2. Otkomentariši node u `nodes/gap_analysis.py`
3. Ovaj node čita **dva** state key-a (`cv_structured` + `jd_requirements`)
4. U `main.py`: dodaj node i edge

**Test:** Proveri da `result["gap_report"]["missing"]` lista realne gap-ove.

#### Checkpoint C: PlannerAgent + TailorWriter

**Step 5 — PlannerAgent:**
- Node čita **tri** state key-a (`cv_structured`, `jd_requirements`, `gap_report`)
- LLM generiše per-section instrukcije za tailoring
- Ključno pravilo u promptu: "Ne smeš izmisliti činjenice"

**Step 6 — TailorWriter:**
- LLM prepisuje sekcije CV-a na osnovu plana
- Uvodi `validation_attempts` counter u state
- `state.get("validation_result")` je `None` pri prvom prolazu, popunjen pri retry-u

#### Checkpoint D: ValidateTailoredCV + Retry Loop

**Step 7 — Ovo je srž projekta:**
- `nodes/validator.py` ima i determinističke provere (novi employer, nove datume) i LLM provere (fabricirane skillove)
- `route_after_validation()` routing funkcija u `main.py`:
  - PASS → ide na GenerateGapQuestions
  - FAIL + retries < 3 → loop nazad na TailorWriter
  - FAIL + retries >= 3 → best effort, ide dalje
- U `main.py` koristi `add_conditional_edges()` umesto `add_edge()`

#### Checkpoint E: GapQuestions + RenderHTML + WriteOutputs

**Steps 8-10:**
- Step 8: LLM generiše pitanja za kandidata na osnovu gap-ova
- Step 9: BeautifulSoup rekonstruiše HTML sa tailored sadržajem
- Step 10: Python piše fajlove u `data/output/`

---

## 3. Data Preparation

### Ulazni podaci (data/input/)

Aplikacija zahteva dva fajla u `session10_gandra/data/input/`:

| Fajl | Sadržaj | Status |
|------|---------|--------|
| `cv_original.html` | HTML CV kandidata | ✅ Prisutan (sample: Jane Smith, 4.2 KB) |
| `job_description.txt` | Tekst opisa posla | ✅ Prisutan (sample: Senior Backend Engineer @ FinTech, 2 KB) |
| `cv_original_1.html` | Alternativni CV (24 KB) | Prisutan, ali **nije aktivan** u kodu |

**Oba potrebna fajla su na mestu — ništa ne fali za pokretanje.**

### Sample podaci koji su uključeni

**cv_original.html** — Jane Smith:
- 8 godina backend iskustva
- Skills: Python, Java, cloud infrastructure, CI/CD
- 3 radna mesta, svako sa bullet pointima
- Education, certifications, languages

**job_description.txt** — Senior Backend Engineer (FinTech startup):
- Must-haves: 5+ god Python, PostgreSQL, REST API, microservices, AWS, CI/CD
- Nice-to-haves: Kubernetes, Kafka/RabbitMQ, Terraform, GraphQL, FinTech domain
- Očekuje se: vođenje servisa, code review, mentoring

### Kako koristiti sopstvene podatke

1. Zameni `data/input/cv_original.html` sa sopstvenim CV-om u HTML formatu
2. Zameni `data/input/job_description.txt` sa ciljnim opisom posla
3. CV može biti u bilo kom HTML formatu — LLM parser (Step 2) rukuje svim strukturama

> **Napomena:** Ako menjaš CV za `cv_original_1.html`, moraš ažurirati putanju u `nodes/ingest.py:37` (`CV_INPUT_PATH`).

### Izlazni podaci (data/output/)

Generiše se pri pokretanju kompletnog pipeline-a (Checkpoint E):

| Fajl | Opis | Generiše ga |
|------|------|-------------|
| `cv_tailored.html` | Tailored CV u istom HTML layout-u | Step 10 (WriteOutputs) |
| `gap_questions.txt` | Pitanja za kandidata o gap-ovima | Step 10 (WriteOutputs) |

Trenutno folder sadrži samo `.gitkeep` placeholder.

---

## 4. Eksterne zavisnosti i konfiguracija

### OpenAI API (obavezno)

Jedina eksterna zavisnost za pokretanje aplikacije.

**Setup:**
1. Napravi nalog na [platform.openai.com](https://platform.openai.com)
2. Generiši API key: **API keys → Create new secret key**
3. Postavi key:
   ```bash
   export OPENAI_API_KEY="sk-tvoj-kljuc-ovde"
   ```
   Ili u `session10_gandra/.env`:
   ```
   OPENAI_API_KEY=sk-tvoj-kljuc-ovde
   ```

**Model koji se koristi:** `gpt-4o-mini` (najjeftiniji OpenAI model sa dobrim structured output-om)

**Cena:** ~$0.15 / 1M input tokena, ~$0.60 / 1M output tokena. Jedno kompletno pokretanje pipeline-a (svih 10 koraka) troši ~5-10K tokena, što je ~$0.01.

**Alternativni provajderi** (za offline rad ili ako nemaš OpenAI key):

| Provajder | Zavisnost | Kako aktivirati |
|-----------|-----------|-----------------|
| Ollama (lokalno) | `langchain-ollama>=0.2` | Otkomentariši Option B u `nodes/parse_cv.py:61-62` i u `requirements.txt:14` |
| Anthropic (Claude) | `langchain-anthropic>=0.2` | Otkomentariši Option C u `requirements.txt:17` |

Za Ollama: moraš imati pokrenut Ollama server (`ollama serve`) i preuzet model (`ollama pull llama3.1:8b`). Pogledaj `OLLAMA.md` u root-u projekta.

### Langfuse vs LangSmith — čemu služe?

Oba su **observability/tracing** alati za LLM aplikacije. Rešavaju isti osnovni problem: kad imaš pipeline od 10 LLM poziva, nemoguće je debug-ovati bez uvida u svaki pojedinačni poziv (koji prompt je otišao, šta je LLM vratio, koliko je trajalo, koliko je koštalo).

| | Langfuse | LangSmith |
|--|----------|-----------|
| **Ko pravi** | Open-source kompanija (Langfuse GmbH) | LangChain tim (isti ljudi koji prave LangGraph) |
| **Glavna namena** | Generički LLM tracing — radi sa bilo kojim framework-om | Native za LangChain/LangGraph ekosistem |
| **Integracija sa LangGraph** | Preko callback-a (ručno dodaješ) | Automatski — samo postavi env varijable i radi |
| **Self-hosting** | Da (Docker, open-source) | Ne (samo cloud) |
| **Besplatni tier** | 50K observacija/mesec | 5K trace-ova/mesec |
| **Prompt management** | Da (verzionisanje promptova) | Da (Prompt Hub) |
| **Evaluacije** | Da (custom scoreri) | Da (annotation queues, auto-eval) |
| **Dataset/testing** | Da (benchmark dataseti) | Da (jače — sa automatskim eval pipeline-ovima) |
| **Cena (plaćeni)** | Jeftinije | Skuplje |
| **Playground** | Da (testiraj prompt iz UI-a) | Da |

**Preporuka za ovaj projekat:**
- **LangSmith** ako ti je najbitnije da "samo radi" sa LangGraph-om bez dodatnog koda
- **Langfuse** ako želiš open-source, self-hosting opciju, ili već koristiš Langfuse na drugim projektima

Možeš koristiti oba istovremeno — nisu konfliktni.

### Dual Tracing — kako radi u main.py

`main.py` automatski detektuje oba sistema iz env varijabli i ispisuje status pri pokretanju:

```
🔍 LangSmith tracing: AKTIVIRAN (projekat: cv-tailoring)
🔍 Langfuse tracing: AKTIVIRAN
```

**Kako rade paralelno bez konflikta:**
- **LangSmith** se hookuje interno u LangChain/LangGraph runtime — nema callback-a, nema koda. Samo `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY`.
- **Langfuse** radi preko `CallbackHandler` koji se prosleđuje u `app.invoke(config={"callbacks": [...]})`, plus `@observe` decorator za imenovanje root trace-a.
- Oba primaju iste podatke (prompt, response, tokeni, latencija) ali nezavisno.

**Sve kombinacije rade:**

| LangSmith | Langfuse | Rezultat |
|-----------|----------|----------|
| ✅ | ✅ | Oba trace-uju — uporedi side-by-side |
| ✅ | ❌ | Samo LangSmith (zero-code) |
| ❌ | ✅ | Samo Langfuse (callback) |
| ❌ | ❌ | Bez tracinga — app radi normalno |

---

### Langfuse (opciono — observability/tracing)

Langfuse ti daje potpun uvid u svaki LLM poziv: prompt koji je poslat, response koji je dobijen, latencija, cena, token count. Izuzetno korisno za debug kad LLM vrati loš JSON ili kad validacija pada.

#### Korak 1: Napravi Langfuse nalog i projekat

1. Idi na [cloud.langfuse.com](https://cloud.langfuse.com) i registruj se (besplatni tier je dovoljan)
2. Klikni **New Project** → nazovi ga npr. `cv-tailoring`
3. Idi u **Settings → API Keys → Create new API key**
4. Kopiraj tri vrednosti: **Secret Key**, **Public Key**, i **Host**

#### Korak 2: Postavi environment varijable

Dodaj u `session10_gandra/.env` (ili eksportuj u terminalu):

```bash
LANGFUSE_SECRET_KEY=sk-lf-...          # Secret Key sa dashboard-a
LANGFUSE_PUBLIC_KEY=pk-lf-...          # Public Key sa dashboard-a
LANGFUSE_HOST=https://cloud.langfuse.com  # ili self-hosted URL
```

#### Korak 3: Instaliraj langfuse i langchain pakete

```bash
uv add langfuse langchain
```

> **Napomena:** Langfuse v4 zahteva `langchain` paket (ne samo `langchain-core`) za `CallbackHandler`.

#### Korak 4: Pokreni — tracing je već integrisan u main.py

**Ne moraš ništa menjati u kodu.** `main.py` automatski detektuje `LANGFUSE_SECRET_KEY` i `LANGFUSE_PUBLIC_KEY` u environment-u i aktivira Langfuse callback. Videćeš u outputu:

```
🔍 Langfuse tracing: AKTIVIRAN
```

Ako keys nisu postavljeni, aplikacija radi normalno:

```
🔍 Langfuse tracing: nije konfigurisan (opciono — vidi HOWTO.md)
```

Kako radi (u `main.py`):
- Na vrhu fajla: detektuje `LANGFUSE_SECRET_KEY` + `LANGFUSE_PUBLIC_KEY` u env-u
- `_run_pipeline()` je obavijen `@observe(name="cv-tailoring-pipeline")` decoratorom — ovo kreira imenovan root trace
- Pri `app.invoke()`: prosleđuje `LangfuseCallbackHandler` kao callback — svi LangChain pozivi se ugnježdavaju pod root trace-om
- U Langfuse dashboardu trace se zove **"cv-tailoring-pipeline"** (ne "unnamed")

#### Korak 5: Koristi Langfuse dashboard

Posle pokretanja `python main.py`:

1. Idi na [cloud.langfuse.com](https://cloud.langfuse.com) → tvoj projekat
2. Klikni **Traces** — videćeš trace za svako pokretanje pipeline-a
3. Klikni na trace → vidiš svaki LLM poziv:
   - **Input**: kompletan prompt sa svim varijablama
   - **Output**: LLM response (JSON koji je vratio)
   - **Metadata**: model, temperatura, token count, latencija, cena
4. Korisni filteri:
   - **By model**: vidi samo gpt-4o-mini pozive
   - **By latency**: pronađi spore pozive
   - **By cost**: prati potrošnju po pokretanju

#### Tipični debug scenariji sa Langfuse

| Problem | Šta gledaš u Langfuse |
|---------|----------------------|
| LLM vraća neispravan JSON | Otvori Output tab — vidi tačan response |
| Validator stalno pada | Uporedi Input (prompt) sa Output — da li prompt traži pravu stvar? |
| Pipeline je spor | Sortiranje po latenciji — koji node traje najduže? |
| Preveliki troškovi | Cost tab — koji prompt troši najviše tokena? |

> **Napomena:** Session 9 takođe koristi Langfuse — pogledaj `session9/multiagv3faiss_persisted.py` za primer integracije u RAG kontekstu.

---

### LangSmith (opciono — native LangChain/LangGraph tracing)

LangSmith je tracing platforma koju pravi **isti tim koji pravi LangGraph**. Glavna prednost: **nula koda za integraciju** — samo postaviš env varijable i svi LangChain/LangGraph pozivi se automatski loguju.

#### Korak 1: Napravi LangSmith nalog

1. Idi na [smith.langchain.com](https://smith.langchain.com) i registruj se
2. Besplatni tier: 5K trace-ova mesečno (dovoljno za razvoj)
3. Idi u **Settings → API Keys → Create API Key**
4. Kopiraj key (počinje sa `lsv2_...`)

#### Korak 2: Postavi environment varijable

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="lsv2_pt_..."
export LANGCHAIN_PROJECT="cv-tailoring"       # opciono, default je "default"
```

Ili dodaj u `session10_gandra/.env`:

```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=cv-tailoring
```

#### Korak 3: Pokreni — to je sve

```bash
cd session10_gandra
uv run python main.py
```

**Nema izmena u kodu.** LangChain/LangGraph automatski detektuje `LANGCHAIN_TRACING_V2=true` i šalje trace-ove na LangSmith. Svaki `ChatOpenAI` poziv, svaki `JsonOutputParser`, svaki `PromptTemplate.invoke()` — sve se loguje automatski.

#### Korak 4: Koristi LangSmith dashboard

Posle pokretanja:

1. Idi na [smith.langchain.com](https://smith.langchain.com) → tvoj projekat
2. Klikni **Runs** — videćeš ceo LangGraph trace kao stablo:
   ```
   RunnableSequence (root)
   ├── IngestFiles           (0.01s, no LLM)
   ├── ParseCVHtml           (2.3s)
   │   ├── PromptTemplate    → vidi finalni prompt
   │   ├── ChatOpenAI        → vidi request/response, tokeni, cena
   │   └── JsonOutputParser  → vidi parsirani JSON
   ├── AnalyzeJD             (1.8s)
   │   ├── PromptTemplate
   │   ├── ChatOpenAI
   │   └── JsonOutputParser
   └── ...
   ```
3. Za svaki čvor vidiš:
   - **Input/Output** sa kompletnim podacima
   - **Latencija** po koraku
   - **Token count** i **cena** (per-call i kumulativno)
   - **Errori** — ako `JsonOutputParser` padne, vidiš tačno šta je LLM vratio

#### LangSmith specifične prednosti za LangGraph

| Feature | Opis |
|---------|------|
| **Graph visualization** | Automatski prikazuje graf sa indikacijom koji čvor je aktivan |
| **Retry loop tracing** | Kad TailorWriter ↔ Validator loop radi, vidiš svaku iteraciju kao zasebni pod-trace |
| **Playground** | Klikni na bilo koji LLM poziv → "Open in Playground" → testiraj prompt sa izmenjenim varijablama |
| **Comparison** | Uporedi dva pokretanja side-by-side (npr. sa i bez korekcija u promptu) |
| **Annotation** | Ručno oceni output svakog koraka (thumb up/down) za kasniju analizu |

#### Isključivanje tracinga

Ako ne želiš da šalješ podatke na LangSmith:

```bash
unset LANGCHAIN_TRACING_V2
# ili
export LANGCHAIN_TRACING_V2=false
```

---

### Mermaid API (automatski)

`main.py` koristi Mermaid API da generiše `graph_visualization.png`. Ovo zahteva internet konekciju ali **ne zahteva API key** — besplatno je. Ako nemaš internet, aplikacija će i dalje raditi ali generisanje slike će pasti.

### Rezime eksternih servisa

| Servis | Obavezan? | Potreban key? | Za šta se koristi | Izmene u kodu? |
|--------|-----------|---------------|-------------------|----------------|
| OpenAI API | Da | `OPENAI_API_KEY` | Svi LLM nodovi (Steps 2-8) | Ne (već integrisano) |
| Ollama | Alternativa za OpenAI | Ne (lokalan) | Zamena za OpenAI LLM | Da (otkomentariši) |
| LangSmith | Ne | `LANGCHAIN_API_KEY` + `LANGCHAIN_TRACING_V2=true` | Native LangGraph tracing | **Ne — samo env varijable** |
| Langfuse | Ne | `LANGFUSE_SECRET_KEY` + `LANGFUSE_PUBLIC_KEY` | Open-source LLM tracing | **Ne — već integrisano u main.py** |
| Mermaid API | Ne (samo za sliku) | Ne | Generisanje `graph_visualization.png` | Ne |
