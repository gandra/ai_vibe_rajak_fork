"""
nodes/ingest.py — Step 1: IngestFiles Node
============================================

PURPOSE:
    Read cv_original.html and job_description.txt from the filesystem
    and load them into the graph state as raw strings.

THIS IS A "TOOL NODE" (no LLM):
    Pure Python file I/O.  This is the simplest kind of LangGraph node —
    it takes state in, does deterministic work, and returns new state keys.

LANGGRAPH CONCEPTS LEARNED:
    - A node is just a function: state_dict in → partial state_dict out
    - The returned dict is MERGED into the existing state (not replaced)
    - START → this node is how every run begins

STATE KEYS WRITTEN:
    cv_html_raw: str  — the full HTML of the original CV
    jd_text: str      — the full text of the job description

ERROR HANDLING (to add later):
    - Check that files exist before reading (raise clear error if not)
    - Validate that cv_html_raw looks like HTML (contains <html> or <body> tag)

EXAMPLE USAGE IN GRAPH:
    workflow.add_node("IngestFiles", ingest_files)
    workflow.add_edge(START, "IngestFiles")
"""

import os


# ── Configuration ───────────────────────────────────────────────────
# Paths are relative to the session10/ directory.
# Change these if your input files are located elsewhere.
CV_INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "input", "cv_original.html")
JD_INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "input", "job_description.txt")


def ingest_files(state: dict) -> dict:
    """Read input files from disk and load into state.

    This is the entry-point node of the graph (START → IngestFiles).
    It reads two files and returns them as new state keys.

    LangGraph will MERGE the returned dict into the existing state,
    so cv_html_raw and jd_text become available to all downstream nodes.

    Args:
        state: Current graph state (expected to be empty on first call).

    Returns:
        Dict with cv_html_raw and jd_text keys.

    Raises:
        FileNotFoundError: If either input file doesn't exist.
    """
    print("--- INGEST FILES ---")

    # Resolve to absolute paths (so it works regardless of working directory)
    cv_path = os.path.abspath(CV_INPUT_PATH)
    jd_path = os.path.abspath(JD_INPUT_PATH)

    # ── Validate files exist before reading ─────────────────────────
    if not os.path.isfile(cv_path):
        raise FileNotFoundError(f"CV file not found: {cv_path}")
    if not os.path.isfile(jd_path):
        raise FileNotFoundError(f"JD file not found: {jd_path}")

    # ── Read files ──────────────────────────────────────────────────
    with open(cv_path, "r", encoding="utf-8") as f:
        cv_html_raw = f.read()

    with open(jd_path, "r", encoding="utf-8") as f:
        jd_text = f.read()

    # ── Sanity checks ───────────────────────────────────────────────
    if not cv_html_raw.strip():
        raise ValueError(f"CV file is empty: {cv_path}")
    if not jd_text.strip():
        raise ValueError(f"JD file is empty: {jd_path}")

    print(f"  ✅ CV loaded: {len(cv_html_raw)} chars from {cv_path}")
    print(f"  ✅ JD loaded: {len(jd_text)} chars from {jd_path}")

    # ── Return state update ─────────────────────────────────────────
    # LangGraph merges this into the shared state.
    return {
        "cv_html_raw": cv_html_raw,
        "jd_text": jd_text,
    }
