# CV Tailoring Agent — Session 10

A **LangGraph** agentic workflow that tailors a CV to match a specific job description, while enforcing a strict **no-fabrication policy** via a validation loop.

## Architecture

```
START → IngestFiles → ParseCVHtml → AnalyzeJD → GapAnalysis → PlannerAgent
    → TailorWriter ⇄ ValidateTailoredCV (retry loop on FAIL, max 3 attempts)
    → GenerateGapQuestions → RenderHTML → WriteOutputs → END
```

## Project Structure

```
session10/
├── main.py                    # LangGraph workflow definition & runner
├── state.py                   # CVTailoringState TypedDict (shared state schema)
├── nodes/                     # One file per graph node
│   ├── ingest.py              # Step 1: Read files from disk
│   ├── parse_cv.py            # Step 2: HTML → structured dict (BeautifulSoup)
│   ├── analyze_jd.py          # Step 3: JD text → structured requirements (LLM)
│   ├── gap_analysis.py        # Step 4: Compare JD vs CV, identify gaps (LLM)
│   ├── planner.py             # Step 5: Create per-section tailoring plan (LLM)
│   ├── tailor_writer.py       # Step 6: Rewrite CV sections per plan (LLM, retryable)
│   ├── validator.py           # Step 7: Check for fabrications (LLM + deterministic)
│   ├── gap_questions.py       # Step 8: Generate candidate questions (LLM)
│   ├── render_html.py         # Step 9: Structured dict → HTML (BeautifulSoup)
│   └── write_outputs.py       # Step 10: Write files to disk
├── prompts/                   # LLM prompt templates (one per LLM node)
│   ├── analyze_jd.py          # Step 3 prompt
│   ├── gap_analysis.py        # Step 4 prompt
│   ├── planner.py             # Step 5 prompt
│   ├── tailor_writer.py       # Step 6 prompt (with retry correction slot)
│   ├── validator.py           # Step 7 prompt
│   └── gap_questions.py       # Step 8 prompt
├── data/
│   ├── input/
│   │   ├── cv_original.html   # YOUR CV (replace sample with your real CV)
│   │   └── job_description.txt # Target job description
│   └── output/                # Generated at runtime
│       ├── cv_tailored.html
│       └── gap_questions.txt
├── plan.md                    # Detailed implementation plan
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Node Types

| Node | Type | LLM? | Purpose |
|------|------|------|---------|
| IngestFiles | Tool | ❌ | Read files from disk |
| ParseCVHtml | Tool | ❌ | Parse HTML with BeautifulSoup |
| AnalyzeJD | LLM | ✅ | Extract JD requirements |
| GapAnalysis | LLM | ✅ | Compare JD vs CV |
| PlannerAgent | LLM | ✅ | Create tailoring plan (agent-style) |
| TailorWriter | LLM | ✅ | Rewrite CV sections (retryable) |
| ValidateTailoredCV | LLM + Tool | ✅ | Quality gate (deterministic + LLM checks) |
| GenerateGapQuestions | LLM | ✅ | Create candidate questions |
| RenderHTML | Tool | ❌ | Rebuild HTML from structured data |
| WriteOutputs | Tool | ❌ | Write files to disk |

## The Validation Loop (Core Pattern)

```
TailorWriter → ValidateTailoredCV
                    ├── PASS → GenerateGapQuestions (continue)
                    ├── FAIL (retries < 3) → TailorWriter (retry with corrections)
                    └── FAIL (retries ≥ 3) → GenerateGapQuestions (best effort)
```

This is the same pattern as session 9's hallucination grader loop, but with a **max-retry counter** for safety.

## Implementation Checkpoints

| Checkpoint | Steps | What You Can Demo |
|------------|-------|-------------------|
| A | 1–2 | Files loaded, CV parsed — no LLM needed |
| B | 3–4 | JD analyzed, gaps identified — first LLM calls |
| C | 5–6 | Plan created, CV rewritten — agent reasoning |
| D | 7 | **Validation loop works** — core LangGraph pattern |
| E | 8–10 | Full pipeline, files on disk — production-ready |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Place your CV and JD in data/input/
# (or use the provided samples)

# Run the pipeline
python main.py
```

## Inputs & Outputs

**Inputs** (place in `data/input/`):
- `cv_original.html` — Your CV in HTML format
- `job_description.txt` — The target job description

**Outputs** (generated in `data/output/`):
- `cv_tailored.html` — Tailored CV (same HTML layout, print-ready)
- `gap_questions.txt` — Questions to gather missing evidence
