"""
nodes/tailor_writer.py — Step 6: TailorWriter Node
=====================================================

PURPOSE:
    Apply the tailoring plan (from Step 5) to rewrite the CV sections.
    Produces a new structured CV with tailored content, preserving the
    same structure as the original so it can be compared and validated.

THIS IS THE NODE THAT GETS RETRIED:
    If validation (Step 7) fails, the graph loops BACK to this node.
    On retry, this node receives the validation_result in state, which
    contains the specific issues to fix.  The prompt includes these
    correction instructions so the LLM can fix its mistakes.

LANGGRAPH CONCEPTS LEARNED:
    - state.get() for optional keys (validation_result is None on first pass)
    - State overwrite: each call REPLACES cv_tailored_structured
    - Counter pattern: validation_attempts increments each time
    - Same node called multiple times in a single graph run (via the loop)

RETRY FLOW:
    First pass:  PlannerAgent → TailorWriter (validation_result = None)
    Retry pass:  ValidateTailoredCV → TailorWriter (validation_result has issues)

    The prompt adapts:
    - First pass:  "Apply this tailoring plan..."
    - Retry pass:  "Apply this tailoring plan AND fix these issues: [...]"

STATE KEYS READ:
    cv_structured: dict         (from Step 2 — original, never changes)
    tailoring_plan: dict        (from Step 5)
    validation_result: dict     (from Step 7 — None on first pass, populated on retry)

STATE KEYS WRITTEN:
    cv_tailored_structured: dict — same shape as cv_structured but with tailored content
    validation_attempts: int     — incremented each time this node runs

PROMPT LOCATION:
    prompts/tailor_writer.py
"""

# from langchain_core.output_parsers import JsonOutputParser
# from prompts.tailor_writer import tailor_writer_prompt
# from state import CVTailoringState


# def tailor_writer(state: CVTailoringState) -> dict:
#     """Rewrite CV sections according to the tailoring plan.
#
#     On retry (after failed validation), also incorporates correction
#     instructions from validation_result to fix specific issues.
#
#     Args:
#         state: Must contain cv_structured and tailoring_plan.
#                May contain validation_result (on retry).
#
#     Returns:
#         Dict with cv_tailored_structured and updated validation_attempts.
#     """
#     # TODO: Step 6 implementation
#     #
#     # 1. Read the tailoring plan from state
#     # 2. Check if this is a retry (state.get("validation_result") is not None)
#     #    - If retry: extract correction instructions from validation_result["issues"]
#     #    - If first pass: correction_instructions = ""
#     # 3. Build prompt with cv_structured, tailoring_plan, and correction_instructions
#     # 4. Invoke LLM
#     # 5. Parse JSON output
#     # 6. Increment validation_attempts counter
#     # 7. Return {"cv_tailored_structured": result, "validation_attempts": count}
#     pass
