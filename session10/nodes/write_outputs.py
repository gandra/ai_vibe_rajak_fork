"""
nodes/write_outputs.py — Step 10: WriteOutputs Node
=====================================================

PURPOSE:
    Write the final output files to disk:
    - cv_tailored.html — the tailored CV, ready for manual printing to PDF
    - gap_questions.txt — clarifying questions for the candidate

THIS IS A "TOOL NODE" (no LLM):
    Pure Python file I/O — the simplest node in the pipeline.
    Mirrors IngestFiles (Step 1) but for output instead of input.

LANGGRAPH CONCEPTS LEARNED:
    - Final node before END
    - Writing results from state to the filesystem
    - Returning metadata about what was written (for logging/debugging)

STATE KEYS READ:
    cv_tailored_html: str      (from Step 9)
    gap_questions: list[str]   (from Step 8)

STATE KEYS WRITTEN:
    output_paths: dict — e.g., {
        "html": "data/output/cv_tailored.html",
        "questions": "data/output/gap_questions.txt"
    }
"""

import os

# from state import CVTailoringState

# ── Configuration ───────────────────────────────────────────────────
OUTPUT_DIR = "data/output"
CV_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "cv_tailored.html")
QUESTIONS_OUTPUT_PATH = os.path.join(OUTPUT_DIR, "gap_questions.txt")


# def write_outputs(state: CVTailoringState) -> dict:
#     """Write tailored CV and gap questions to disk.
#
#     Creates the output directory if it doesn't exist.
#
#     Args:
#         state: Must contain cv_tailored_html and gap_questions.
#
#     Returns:
#         Dict with output_paths key containing paths to written files.
#     """
#     # TODO: Step 10 implementation
#     #
#     # 1. Create output directory if it doesn't exist:
#     #    os.makedirs(OUTPUT_DIR, exist_ok=True)
#     #
#     # 2. Write cv_tailored.html:
#     #    with open(CV_OUTPUT_PATH, "w") as f:
#     #        f.write(state["cv_tailored_html"])
#     #
#     # 3. Write gap_questions.txt:
#     #    with open(QUESTIONS_OUTPUT_PATH, "w") as f:
#     #        f.write("\n\n".join(state["gap_questions"]))
#     #
#     # 4. Print confirmation:
#     #    print(f"✅ Tailored CV written to: {CV_OUTPUT_PATH}")
#     #    print(f"✅ Gap questions written to: {QUESTIONS_OUTPUT_PATH}")
#     #
#     # 5. Return paths:
#     #    return {"output_paths": {"html": CV_OUTPUT_PATH, "questions": QUESTIONS_OUTPUT_PATH}}
#     pass
