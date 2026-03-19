"""
main.py — LangGraph Workflow Definition & Runner
==================================================

This is the central orchestration file.  It:
  1. Imports all node functions from nodes/
  2. Builds the StateGraph with nodes and edges
  3. Adds the conditional validation loop (Step 7)
  4. Compiles and runs the workflow

ARCHITECTURE OVERVIEW:
  
  START
    │
    ▼
  IngestFiles          (Step 1 — pure Python, reads files from disk)
    │
    ▼
  ParseCVHtml          (Step 2 — pure Python, BeautifulSoup parsing)
    │
    ▼
  AnalyzeJD            (Step 3 — LLM node, extracts JD requirements)
    │
    ▼
  GapAnalysis           (Step 4 — LLM node, compares JD vs CV)
    │
    ▼
  PlannerAgent          (Step 5 — LLM node, creates per-section tailoring plan)
    │
    ▼
  TailorWriter          (Step 6 — LLM node, rewrites CV sections per plan)
    │
    ▼
  ValidateTailoredCV    (Step 7 — LLM node, checks for fabrications)
    │
    ├── PASS ──────────▶ GenerateGapQuestions (Step 8)
    │                        │
    ├── FAIL (retry ≤ 3) ──▶ TailorWriter (loop back with correction instructions)
    │                        
    └── FAIL (max retries) ▶ GenerateGapQuestions (proceed with best effort)
    
  GenerateGapQuestions  (Step 8 — LLM node, creates questions from gap report)
    │
    ▼
  RenderHTML            (Step 9 — pure Python, rebuilds HTML from tailored sections)
    │
    ▼
  WriteOutputs          (Step 10 — pure Python, writes files to disk)
    │
    ▼
  END

LANGGRAPH CONCEPTS USED:
  - StateGraph(TypedDict) ........... typed state management
  - add_node / add_edge ............. linear flow
  - add_conditional_edges ........... branching (validation gate)
  - Cycle (TailorWriter ↔ Validator)  retry loop with counter guard
  - START / END ..................... entry and exit points

COMPARISON WITH SESSION 9 (graph.py):
  Session 9 used conditional edges for:
    - grade_documents → decide_to_generate → {transform_query | generate}
    - generate → grade_generation → {not supported → generate | useful → END}
  
  Session 10 uses the same pattern but with:
    - An explicit iteration counter (validation_attempts) for safety
    - More nodes in the linear chain before the conditional section
    - Separate prompt module (prompts/) instead of inline prompts

HOW TO RUN:
  python main.py
"""

# ── Imports ─────────────────────────────────────────────────────────
import os
from langgraph.graph import StateGraph, START, END
from state import CVTailoringState

# ── Tracing Setup (opciono) ───────────────────────────────────────
# Podržava LangSmith, Langfuse, oba istovremeno, ili nijedan.
# Svaki se aktivira nezavisno na osnovu env varijabli.

# — LangSmith: automatski za LangChain/LangGraph (zero-code)
# Podržava oba prefiksa: LANGCHAIN_* (stariji) i LANGSMITH_* (noviji)
_langsmith_enabled = (
    os.environ.get("LANGCHAIN_TRACING_V2", os.environ.get("LANGSMITH_TRACING", "")).lower() == "true"
    and (os.environ.get("LANGCHAIN_API_KEY") or os.environ.get("LANGSMITH_API_KEY"))
)
_langsmith_project = os.environ.get("LANGCHAIN_PROJECT", os.environ.get("LANGSMITH_PROJECT", "default"))
if _langsmith_enabled:
    print(f"🔍 LangSmith tracing: AKTIVIRAN (projekat: {_langsmith_project})")
else:
    print("🔍 LangSmith tracing: nije konfigurisan (opciono — vidi HOWTO.md)")

# — Langfuse: preko callback-a (langfuse v4 + @observe)
# Potrebno: LANGFUSE_SECRET_KEY + LANGFUSE_PUBLIC_KEY
_langfuse_enabled = False
if os.environ.get("LANGFUSE_SECRET_KEY") and os.environ.get("LANGFUSE_PUBLIC_KEY"):
    try:
        from langfuse import observe
        from langfuse.langchain import CallbackHandler as LangfuseCallbackHandler
        _langfuse_enabled = True
        print("🔍 Langfuse tracing: AKTIVIRAN")
    except ImportError:
        print("🔍 Langfuse tracing: LANGFUSE_* keys postavljeni ali paketi nisu instalirani (uv add langfuse langchain)")
else:
    print("🔍 Langfuse tracing: nije konfigurisan (opciono — vidi HOWTO.md)")

# Node functions (Steps 1-2 implemented, rest coming later)
from nodes.ingest import ingest_files
from nodes.parse_cv import parse_cv_html

# TODO: Uncomment as you implement each step:
# from nodes.analyze_jd import analyze_jd
# from nodes.gap_analysis import gap_analysis
# from nodes.planner import planner_agent
# from nodes.tailor_writer import tailor_writer
# from nodes.validator import validate_tailored_cv
# from nodes.gap_questions import generate_gap_questions
# from nodes.render_html import render_html
# from nodes.write_outputs import write_outputs


# ── Routing Function (Step 7) ──────────────────────────────────────
# TODO: Uncomment when implementing Step 7 (validation gate)
#
# def route_after_validation(state: CVTailoringState) -> str:
#     """Decide whether to retry tailoring or proceed to gap questions."""
#     if state["validation_result"]["pass"]:
#         return "GenerateGapQuestions"
#     if state.get("validation_attempts", 0) >= 3:
#         print("⚠️  Max validation retries reached. Proceeding with best effort.")
#         return "GenerateGapQuestions"
#     print(f"🔄 Validation failed (attempt {state.get('validation_attempts', 0)}). Retrying...")
#     return "TailorWriter"


# ── Graph Assembly ──────────────────────────────────────────────────
# CHECKPOINT A: Steps 1-2 only (IngestFiles → ParseCVHtml → END)
# No LLM needed — just file I/O and HTML parsing.

workflow = StateGraph(CVTailoringState)

# ── Register nodes (Steps 1-2) ──
workflow.add_node("IngestFiles", ingest_files)
workflow.add_node("ParseCVHtml", parse_cv_html)

# TODO: Register remaining nodes as you implement them:
# workflow.add_node("AnalyzeJD", analyze_jd)
# workflow.add_node("GapAnalysis", gap_analysis)
# workflow.add_node("PlannerAgent", planner_agent)
# workflow.add_node("TailorWriter", tailor_writer)
# workflow.add_node("ValidateTailoredCV", validate_tailored_cv)
# workflow.add_node("GenerateGapQuestions", generate_gap_questions)
# workflow.add_node("RenderHTML", render_html)
# workflow.add_node("WriteOutputs", write_outputs)

# ── Linear edges (Steps 1-2) ──
workflow.add_edge(START, "IngestFiles")
workflow.add_edge("IngestFiles", "ParseCVHtml")
workflow.add_edge("ParseCVHtml", END)  # ← temporary: move this forward as you add nodes

# TODO: Extend the chain as you implement:
# workflow.add_edge("ParseCVHtml", "AnalyzeJD")
# workflow.add_edge("AnalyzeJD", "GapAnalysis")
# workflow.add_edge("GapAnalysis", "PlannerAgent")
# workflow.add_edge("PlannerAgent", "TailorWriter")
# workflow.add_edge("TailorWriter", "ValidateTailoredCV")
#
# # Conditional edge: validation gate (Step 7)
# workflow.add_conditional_edges(
#     "ValidateTailoredCV",
#     route_after_validation,
#     {"TailorWriter": "TailorWriter", "GenerateGapQuestions": "GenerateGapQuestions"}
# )
#
# workflow.add_edge("GenerateGapQuestions", "RenderHTML")
# workflow.add_edge("RenderHTML", "WriteOutputs")
# workflow.add_edge("WriteOutputs", END)

# ── Compile ──
app = workflow.compile()

# ── Graph Visualization ────────────────────────────────────────────
# Generate a PNG of the current graph state.
# This auto-updates as you add more nodes and edges.
from langchain_core.runnables.graph import MermaidDrawMethod

png_bytes = app.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.API)
with open("graph_visualization.png", "wb") as f:
    f.write(png_bytes)
print("📊 Graph image saved to graph_visualization.png")


# ── Run ─────────────────────────────────────────────────────────────

def _run_pipeline():
    """Run the CV tailoring pipeline and print results.

    Tracing:
      - LangSmith: automatic (zero-code) — if LANGCHAIN_TRACING_V2=true,
        all LangChain/LangGraph calls are traced with no extra config.
      - Langfuse: via CallbackHandler passed in invoke config.
      - Both can run simultaneously — LangSmith traces internally,
        Langfuse traces via callback. No conflicts.
    """
    # Build invoke config — add Langfuse callback if enabled.
    # LangSmith needs nothing here (it hooks in automatically).
    callbacks = []
    if _langfuse_enabled:
        callbacks.append(LangfuseCallbackHandler())

    invoke_config = {"callbacks": callbacks} if callbacks else {}
    result = app.invoke({}, config=invoke_config)

    # Print verification
    print("\n" + "=" * 60)
    print("  ✅ Checkpoint A complete! State keys populated:")
    print("=" * 60)
    for key in result:
        if key == "cv_html_raw":
            print(f"  • cv_html_raw: {len(result[key])} chars")
        elif key == "jd_text":
            print(f"  • jd_text: {len(result[key])} chars")
        elif key == "cv_structured":
            print(f"  • cv_structured:")
            print(f"      name: {result[key]['name']}")
            print(f"      skills: {result[key]['skills']}")
            print(f"      experience: {len(result[key]['experience'])} roles")
            print(f"      education: {len(result[key]['education'])} entries")
        else:
            print(f"  • {key}: {result[key]}")

    return result


# Wrap with @observe for named Langfuse trace (only if Langfuse is enabled)
if _langfuse_enabled:
    _run_pipeline = observe(name="cv-tailoring-pipeline")(_run_pipeline)


if __name__ == "__main__":
    print("=" * 60)
    print("  CV Tailoring Agent — LangGraph Pipeline")
    print("  Checkpoint A: IngestFiles → ParseCVHtml")
    print("=" * 60)

    result = _run_pipeline()
