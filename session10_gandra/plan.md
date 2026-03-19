# CV Tailoring LangGraph — Step-by-Step Implementation Plan

> Gradual build-up optimized for learning LangGraph concepts.
> Each step produces a **runnable** graph you can test before moving on.

---

## Architecture Overview (from diagram)

```
IngestFiles → ParseCVHtml → AnalyzeJD → GapAnalysis → PlannerAgent
    → TailorWriter ⇄ ValidateTailoredCV (loop on FAIL)
    → GenerateGapQuestions → RenderHTML → WriteOutputs
```

### LangGraph Concepts Covered Per Step

| Step | Key LangGraph Concept                  |
|------|----------------------------------------|
| 1    | StateGraph, nodes, edges, entry/end    |
| 2    | TypedDict state, state passing         |
| 3    | LLM node (ChatModel inside a node)     |
| 4    | Multi-key state accumulation           |
| 5    | Agent-style node (LLM + reasoning)     |
| 6    | State transformation node              |
| 7    | **Conditional edges**, retry loop      |
| 8    | Parallel-safe node, depends on step 4  |
| 9-10 | Tool nodes, filesystem I/O             |

---

## Project Structure (target)

```
job_cv_tailoring/
├── main.py                  # graph definition & runner
├── state.py                 # TypedDict state schema
├── nodes/
│   ├── ingest.py            # Step 1: IngestFiles
│   ├── parse_cv.py          # Step 2: ParseCVHtml
│   ├── analyze_jd.py        # Step 3: AnalyzeJD
│   ├── gap_analysis.py      # Step 4: GapAnalysis
│   ├── planner.py           # Step 5: PlannerAgent
│   ├── tailor_writer.py     # Step 6: TailorWriter
│   ├── validator.py         # Step 7: ValidateTailoredCV
│   ├── gap_questions.py     # Step 8: GenerateGapQuestions
│   ├── render_html.py       # Step 9: RenderHTML
│   └── write_outputs.py     # Step 10: WriteOutputs
├── prompts/                 # LLM prompt templates (one per LLM node)
│   ├── analyze_jd.py
│   ├── gap_analysis.py
│   ├── planner.py
│   ├── tailor_writer.py
│   ├── validator.py
│   └── gap_questions.py
├── data/
│   ├── input/
│   │   ├── cv_original.html
│   │   └── job_description.txt
│   └── output/              # generated at runtime
│       ├── cv_tailored.html
│       └── gap_questions.txt
├── tests/                   # optional, per-step smoke tests
└── requirements.txt
```

---

## Shared State Schema (state.py)

Defined once, extended gradually. Each step adds keys it needs.

```python
from typing import TypedDict, Optional

class CVTailoringState(TypedDict, total=False):
    # Step 1 — IngestFiles
    cv_html_raw: str                  # raw HTML string
    jd_text: str                      # raw job description

    # Step 2 — ParseCVHtml
    cv_structured: dict               # parsed sections: summary, skills, experience[]

    # Step 3 — AnalyzeJD
    jd_requirements: dict             # extracted: must_haves, nice_to_haves, responsibilities

    # Step 4 — GapAnalysis
    gap_report: dict                  # matched, missing, weak areas

    # Step 5 — PlannerAgent
    tailoring_plan: dict              # per-section instructions

    # Step 6 — TailorWriter
    cv_tailored_structured: dict      # modified structured CV

    # Step 7 — ValidateTailoredCV
    validation_result: dict           # pass/fail + issues list
    validation_attempts: int          # retry counter

    # Step 8 — GenerateGapQuestions
    gap_questions: list[str]          # list of questions

    # Step 9 — RenderHTML
    cv_tailored_html: str             # final HTML

    # Step 10 — WriteOutputs
    output_paths: dict                # paths to written files
```

---

## STEP 1 — Skeleton Graph + IngestFiles Node

**Goal:** Learn `StateGraph`, `add_node`, `add_edge`, `START`, `END`, running the graph.

**What you build:**
- `state.py` with just `cv_html_raw` and `jd_text`
- `nodes/ingest.py` — reads two files from disk, returns state update
- `main.py` — creates `StateGraph(CVTailoringState)`, adds the node, wires `START → IngestFiles → END`, compiles and invokes

**Node logic (pure Python, no LLM):**
```python
def ingest_files(state: CVTailoringState) -> dict:
    cv_html = open("data/input/cv_original.html").read()
    jd_text = open("data/input/job_description.txt").read()
    return {"cv_html_raw": cv_html, "jd_text": jd_text}
```

**LangGraph concepts learned:**
- `StateGraph(TypedDict)` constructor
- `graph.add_node("IngestFiles", ingest_files)`
- `graph.add_edge(START, "IngestFiles")`
- `graph.add_edge("IngestFiles", END)`
- `graph.compile()` → `app.invoke({})`
- How state merges (returned dict keys update state)

**Test:** Run and print `result["cv_html_raw"][:200]` — confirm file was loaded.

---

## STEP 2 — ParseCVHtml Node (Tool Node, No LLM)

**Goal:** Learn chaining nodes; practice working with structured state.

**What you build:**
- `nodes/parse_cv.py` — uses `BeautifulSoup` to extract sections from CV HTML
- Wire: `IngestFiles → ParseCVHtml → END`

**Node logic (pure Python):**
```python
from bs4 import BeautifulSoup

def parse_cv_html(state: CVTailoringState) -> dict:
    soup = BeautifulSoup(state["cv_html_raw"], "html.parser")
    structured = {
        "summary": extract_summary(soup),
        "skills": extract_skills(soup),
        "experience": extract_experience(soup),
        "education": extract_education(soup),
        "raw_template_metadata": extract_template_info(soup),
    }
    return {"cv_structured": structured}
```

**LangGraph concepts learned:**
- Reading from state (`state["cv_html_raw"]`)
- Multi-node linear chain
- State accumulation (both `cv_html_raw` and `cv_structured` coexist)

**Test:** Print `result["cv_structured"]["skills"]` — confirm parsing works.

---

## STEP 3 — AnalyzeJD Node (First LLM Node)

**Goal:** Learn how to wrap an LLM call inside a LangGraph node.

**What you build:**
- `prompts/analyze_jd.py` — system prompt that extracts requirements from a JD
- `nodes/analyze_jd.py` — calls `ChatOpenAI` (or `ChatAnthropic`), parses structured output
- Wire: `ParseCVHtml → AnalyzeJD → END`

**Node logic:**
```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def analyze_jd(state: CVTailoringState) -> dict:
    prompt = build_analyze_jd_prompt(state["jd_text"])
    response = llm.invoke(prompt)
    parsed = JsonOutputParser().parse(response.content)
    return {"jd_requirements": parsed}
```

**Expected output structure:**
```json
{
  "must_have_skills": ["Python", "AWS", "CI/CD"],
  "nice_to_have_skills": ["Terraform", "GraphQL"],
  "responsibilities": ["Lead backend team", "Design APIs"],
  "experience_level": "Senior",
  "domain": "FinTech"
}
```

**LangGraph concepts learned:**
- LLM inside a node
- Prompt engineering for structured output
- `JsonOutputParser` or Pydantic structured output

**Test:** Print `result["jd_requirements"]` — check extracted requirements make sense.

---

## STEP 4 — GapAnalysis Node

**Goal:** Learn a node that reads multiple state keys and produces a comparison.

**What you build:**
- `nodes/gap_analysis.py` — LLM compares `cv_structured` vs `jd_requirements`
- Wire: `AnalyzeJD → GapAnalysis → END`

**Node logic:**
```python
def gap_analysis(state: CVTailoringState) -> dict:
    prompt = build_gap_prompt(state["cv_structured"], state["jd_requirements"])
    response = llm.invoke(prompt)
    report = JsonOutputParser().parse(response.content)
    return {"gap_report": report}
```

**Expected output structure:**
```json
{
  "matched": [{"skill": "Python", "evidence": "5 years in CV"}],
  "missing": [{"requirement": "Terraform", "severity": "nice_to_have"}],
  "weak": [{"area": "metrics", "note": "No quantified impact in experience bullets"}]
}
```

**LangGraph concepts learned:**
- Node consuming multiple state keys
- Building prompts from structured data
- State growing incrementally

**Test:** Review `result["gap_report"]["missing"]` — should list real gaps.

---

## STEP 5 — PlannerAgent Node

**Goal:** Learn agent-style reasoning node that creates an action plan.

**What you build:**
- `nodes/planner.py` — LLM creates per-section tailoring instructions
- Wire: `GapAnalysis → PlannerAgent → END`

**Node logic:**
```python
def planner_agent(state: CVTailoringState) -> dict:
    prompt = build_planner_prompt(
        state["cv_structured"],
        state["jd_requirements"],
        state["gap_report"]
    )
    response = llm.invoke(prompt)
    plan = JsonOutputParser().parse(response.content)
    return {"tailoring_plan": plan}
```

**Expected output structure:**
```json
{
  "summary": "Emphasize backend leadership and AWS experience",
  "skills": {"add_emphasis": ["Python", "AWS"], "reorder": true},
  "experience": [
    {"role_index": 0, "bullets_to_rephrase": [1, 3], "jd_terms_to_use": ["microservices"]},
    {"role_index": 1, "action": "de-emphasize"}
  ],
  "no_fabrication_notes": ["Cannot claim Terraform — route to gap questions"]
}
```

**Key constraint in prompt:** "You MUST NOT invent facts. If evidence is missing, flag it for gap questions, do NOT plan to add it."

**LangGraph concepts learned:**
- Complex multi-input reasoning node
- Planning pattern (plan then execute)

**Test:** Verify plan references only real CV content.

---

## STEP 6 — TailorWriter Node

**Goal:** Learn a transformation node that modifies structured state.

**What you build:**
- `nodes/tailor_writer.py` — LLM rewrites CV sections per the plan
- Wire: `PlannerAgent → TailorWriter → END`

**Node logic:**
```python
def tailor_writer(state: CVTailoringState) -> dict:
    prompt = build_tailor_prompt(
        state["cv_structured"],
        state["tailoring_plan"],
        state.get("validation_result")  # None on first pass, populated on retry
    )
    response = llm.invoke(prompt)
    tailored = JsonOutputParser().parse(response.content)
    attempts = state.get("validation_attempts", 0)
    return {
        "cv_tailored_structured": tailored,
        "validation_attempts": attempts + 1
    }
```

**LangGraph concepts learned:**
- `state.get()` for optional keys (validation_result is None on first pass)
- State overwrite (each call replaces `cv_tailored_structured`)
- Counter pattern in state

**Test:** Compare `result["cv_tailored_structured"]` with original — should see rephrased bullets.

---

## STEP 7 — ValidateTailoredCV + Conditional Edge (THE KEY STEP)

**Goal:** Learn **conditional edges** and **retry loops** — the core LangGraph pattern.

**What you build:**
- `nodes/validator.py` — compares tailored CV against original, flags fabrications
- `main.py` — add `add_conditional_edges` with routing function
- Wire: `TailorWriter → ValidateTailoredCV → {TailorWriter | GenerateGapQuestions}`

**Node logic:**
```python
def validate_tailored_cv(state: CVTailoringState) -> dict:
    prompt = build_validation_prompt(
        state["cv_structured"],        # original (source of truth)
        state["cv_tailored_structured"] # tailored (to validate)
    )
    response = llm.invoke(prompt)
    result = JsonOutputParser().parse(response.content)
    return {"validation_result": result}
```

**Routing function:**
```python
def route_after_validation(state: CVTailoringState) -> str:
    if state["validation_result"]["pass"]:
        return "GenerateGapQuestions"
    if state.get("validation_attempts", 0) >= 3:
        return "GenerateGapQuestions"  # give up after max retries
    return "TailorWriter"  # retry
```

**Graph wiring:**
```python
graph.add_conditional_edges(
    "ValidateTailoredCV",
    route_after_validation,
    {
        "TailorWriter": "TailorWriter",
        "GenerateGapQuestions": "GenerateGapQuestions",
    }
)
```

**LangGraph concepts learned:**
- `add_conditional_edges(source, routing_fn, path_map)`
- Cycles in the graph (TailorWriter → Validator → TailorWriter)
- Max-iteration safety pattern
- State-driven routing decisions

**Test:** Intentionally weaken the tailor prompt to produce a fabrication, confirm the loop fires and retries.

---

## STEP 8 — GenerateGapQuestions Node

**Goal:** Produce actionable questions from the gap analysis.

**What you build:**
- `nodes/gap_questions.py` — LLM generates questions from `gap_report`
- Wire: validation-pass path → `GenerateGapQuestions → RenderHTML`

**Node logic:**
```python
def generate_gap_questions(state: CVTailoringState) -> dict:
    prompt = build_gap_questions_prompt(
        state["gap_report"],
        state["jd_requirements"]
    )
    response = llm.invoke(prompt)
    questions = JsonOutputParser().parse(response.content)
    return {"gap_questions": questions}
```

**Key prompt constraint:** "Questions must be grounded in JD gaps. Do NOT presume experience not in the original CV."

**LangGraph concepts learned:**
- Node that runs after a conditional edge resolves
- Reading gap_report produced earlier (demonstrates state persistence across the full graph)

**Test:** Check questions are specific ("Which AWS services did you use at Company X?") not generic.

---

## STEP 9 — RenderHTML Node (Tool Node, No LLM)

**Goal:** Learn a pure-Python transformation node that reconstructs output.

**What you build:**
- `nodes/render_html.py` — rebuilds HTML from `cv_tailored_structured` using original template metadata

**Node logic:**
```python
def render_html(state: CVTailoringState) -> dict:
    html = rebuild_html(
        state["cv_tailored_structured"],
        state["cv_structured"]["raw_template_metadata"]
    )
    return {"cv_tailored_html": html}
```

**LangGraph concepts learned:**
- Non-LLM node in a graph that contains LLM nodes (mixed graph)
- Template reconstruction pattern

**Test:** Open the HTML in a browser — should look like the original CV, with tailored content.

---

## STEP 10 — WriteOutputs Node + Full Graph Assembly

**Goal:** Complete the pipeline. Learn the full compile-and-run flow.

**What you build:**
- `nodes/write_outputs.py` — writes `cv_tailored.html` and `gap_questions.txt` to disk
- `main.py` — full graph with all 10 nodes, all edges, conditional routing

**Node logic:**
```python
def write_outputs(state: CVTailoringState) -> dict:
    html_path = "data/output/cv_tailored.html"
    questions_path = "data/output/gap_questions.txt"

    with open(html_path, "w") as f:
        f.write(state["cv_tailored_html"])

    with open(questions_path, "w") as f:
        f.write("\n\n".join(state["gap_questions"]))

    return {"output_paths": {"html": html_path, "questions": questions_path}}
```

**Final graph in main.py:**
```python
from langgraph.graph import StateGraph, START, END

graph = StateGraph(CVTailoringState)

# Add all nodes
graph.add_node("IngestFiles", ingest_files)
graph.add_node("ParseCVHtml", parse_cv_html)
graph.add_node("AnalyzeJD", analyze_jd)
graph.add_node("GapAnalysis", gap_analysis)
graph.add_node("PlannerAgent", planner_agent)
graph.add_node("TailorWriter", tailor_writer)
graph.add_node("ValidateTailoredCV", validate_tailored_cv)
graph.add_node("GenerateGapQuestions", generate_gap_questions)
graph.add_node("RenderHTML", render_html)
graph.add_node("WriteOutputs", write_outputs)

# Linear edges
graph.add_edge(START, "IngestFiles")
graph.add_edge("IngestFiles", "ParseCVHtml")
graph.add_edge("ParseCVHtml", "AnalyzeJD")
graph.add_edge("AnalyzeJD", "GapAnalysis")
graph.add_edge("GapAnalysis", "PlannerAgent")
graph.add_edge("PlannerAgent", "TailorWriter")
graph.add_edge("TailorWriter", "ValidateTailoredCV")

# Conditional edge (validation gate)
graph.add_conditional_edges(
    "ValidateTailoredCV",
    route_after_validation,
    {"TailorWriter": "TailorWriter", "GenerateGapQuestions": "GenerateGapQuestions"}
)

# Continue after gap questions
graph.add_edge("GenerateGapQuestions", "RenderHTML")
graph.add_edge("RenderHTML", "WriteOutputs")
graph.add_edge("WriteOutputs", END)

# Compile and run
app = graph.compile()
result = app.invoke({})
```

**LangGraph concepts learned:**
- Full graph assembly
- End-to-end invoke
- Debugging the complete flow

**Test:** Run end-to-end with real CV + JD. Inspect both output files.

---

## Dependencies (requirements.txt)

```
langgraph>=0.2
langchain-core>=0.3
langchain-openai>=0.2        # or langchain-anthropic
beautifulsoup4>=4.12
```

---

## Suggested Learning Order & Checkpoints

| Checkpoint | Steps | What You Can Demo                               |
|------------|-------|--------------------------------------------------|
| A          | 1-2   | Files loaded and CV parsed — no LLM needed yet   |
| B          | 3-4   | JD analyzed, gaps identified — first LLM calls    |
| C          | 5-6   | Plan created and CV rewritten — agent reasoning   |
| D          | 7     | **Validation loop works** — core LangGraph pattern|
| E          | 8-10  | Full pipeline, files on disk — production-ready   |

At each checkpoint, run the graph and inspect the state to confirm everything works before adding the next node.

---

## Error Handling (add after Step 10)

Once the happy path works, add these as a bonus learning step:
- A1: `IngestFiles` checks file existence, raises with clear message
- A2: `ParseCVHtml` catches parse errors, terminates gracefully
- A3: `route_after_validation` handles max-retries → writes partial output + error report
