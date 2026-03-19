"""
state.py — Shared Graph State Schema
=====================================

This module defines the single TypedDict that flows through the entire
LangGraph pipeline.  Every node reads from and writes to this shared state.

KEY LANGGRAPH CONCEPT:
    When a node returns a dict like {"cv_html_raw": "..."}, LangGraph
    **merges** those keys into the existing state (it doesn't replace
    the whole state).  So each node only needs to return the keys it
    changes — earlier keys are preserved automatically.

    `total=False` means every field is optional, which lets us start
    the graph with an empty dict `{}` and fill fields progressively
    as nodes run.

HOW THIS GROWS:
    Step 1  adds  cv_html_raw, jd_text
    Step 2  adds  cv_structured
    Step 3  adds  jd_requirements
    Step 4  adds  gap_report
    Step 5  adds  tailoring_plan
    Step 6  adds  cv_tailored_structured, validation_attempts
    Step 7  adds  validation_result
    Step 8  adds  gap_questions
    Step 9  adds  cv_tailored_html
    Step 10 adds  output_paths
"""

from typing import TypedDict


class CVTailoringState(TypedDict, total=False):
    # ── Step 1: IngestFiles ─────────────────────────────────────────
    # The raw HTML string of the candidate's original CV.
    # Source of truth — nothing may be added that isn't supported here.
    cv_html_raw: str

    # The raw text of the job description.
    jd_text: str

    # ── Step 2: ParseCVHtml ─────────────────────────────────────────
    # Structured representation of the CV, extracted by BeautifulSoup.
    # Contains keys like: summary, skills, experience[], education[],
    # and raw_template_metadata (tag names, classes, ids needed to
    # reconstruct the same HTML layout later).
    cv_structured: dict

    # ── Step 3: AnalyzeJD ───────────────────────────────────────────
    # Structured requirements extracted from the JD by an LLM.
    # Contains keys like: must_have_skills, nice_to_have_skills,
    # responsibilities, experience_level, domain.
    jd_requirements: dict

    # ── Step 4: GapAnalysis ─────────────────────────────────────────
    # Comparison of JD requirements vs. CV evidence.
    # Contains keys like: matched[], missing[], weak[].
    # Each entry notes what's present, absent, or under-evidenced.
    gap_report: dict

    # ── Step 5: PlannerAgent ────────────────────────────────────────
    # Per-section instructions for how to tailor the CV.
    # The planner decides WHAT to change; the writer executes it.
    # Contains keys like: summary_instructions, skills_reorder,
    # experience_bullet_changes[], no_fabrication_notes[].
    tailoring_plan: dict

    # ── Step 6: TailorWriter ────────────────────────────────────────
    # The rewritten CV in structured form (same shape as cv_structured
    # but with tailored content).  This is what the validator checks
    # against the original.
    cv_tailored_structured: dict

    # Counter for how many times the TailorWriter has been invoked.
    # Starts at 0, incremented each time TailorWriter runs.
    # Used by the routing function to enforce max retries (e.g., 3).
    validation_attempts: int

    # ── Step 7: ValidateTailoredCV ──────────────────────────────────
    # Result of the validation check.  Contains:
    #   "pass": bool — did the tailored CV pass all checks?
    #   "issues": list[str] — descriptions of any problems found
    # On retry, TailorWriter will read this to know what to fix.
    validation_result: dict

    # ── Step 8: GenerateGapQuestions ─────────────────────────────────
    # List of specific, actionable questions to ask the candidate
    # about gaps between the JD and their CV.
    # e.g., "Which AWS services did you use at Company X?"
    # Must NOT presume experience that isn't in the original CV.
    gap_questions: list[str]

    # ── Step 9: RenderHTML ──────────────────────────────────────────
    # The final tailored CV rendered back as a complete HTML string,
    # preserving the original template/layout so it can be printed
    # to PDF without further formatting.
    cv_tailored_html: str

    # ── Step 10: WriteOutputs ───────────────────────────────────────
    # Paths to the files written to disk.
    # e.g., {"html": "data/output/cv_tailored.html",
    #        "questions": "data/output/gap_questions.txt"}
    output_paths: dict
