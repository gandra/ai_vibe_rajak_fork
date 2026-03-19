"""
nodes/gap_analysis.py — Step 4: GapAnalysis Node
==================================================

PURPOSE:
    Compare the JD requirements (from Step 3) against the original CV
    content (from Step 2) to identify gaps: missing skills, weak evidence,
    missing metrics, and under-highlighted responsibilities.

THIS IS AN LLM NODE:
    Uses an LLM to perform the comparison because it requires semantic
    understanding (e.g., "managed cloud infrastructure" in the CV
    partially covers "AWS experience" in the JD).

LANGGRAPH CONCEPTS LEARNED:
    - A node that reads MULTIPLE state keys (cv_structured + jd_requirements)
    - Building prompts from structured data (not just raw text)
    - State continuing to grow: now 4 keys populated

KEY DESIGN DECISION:
    The gap analysis is SEPARATE from the planner (Step 5) because:
    1. Separation of concerns: analysis vs. decision-making
    2. The gap report is reused by GenerateGapQuestions (Step 8)
    3. Easier to test: you can verify gaps are correct before planning

STATE KEYS READ:
    cv_structured: dict   (from Step 2)
    jd_requirements: dict (from Step 3)

STATE KEYS WRITTEN:
    gap_report: dict — with keys like:
        {
            "matched": [
                {"skill": "Python", "evidence": "5 years across 3 roles"}
            ],
            "missing": [
                {"requirement": "Terraform", "severity": "nice_to_have",
                 "note": "Not mentioned anywhere in CV"}
            ],
            "weak": [
                {"area": "leadership", "note": "CV mentions 'team' but no team size or leadership specifics"},
                {"area": "metrics", "note": "No quantified impact in 2 of 3 experience entries"}
            ]
        }

PROMPT LOCATION:
    prompts/gap_analysis.py
"""

# from langchain_core.output_parsers import JsonOutputParser
# from prompts.gap_analysis import gap_analysis_prompt
# from state import CVTailoringState


# def gap_analysis(state: CVTailoringState) -> dict:
#     """Compare JD requirements against CV content to identify gaps.
#
#     Args:
#         state: Must contain cv_structured and jd_requirements.
#
#     Returns:
#         Dict with gap_report key containing matched/missing/weak analysis.
#     """
#     # TODO: Step 4 implementation
#     # 1. Build prompt with state["cv_structured"] and state["jd_requirements"]
#     # 2. Invoke LLM
#     # 3. Parse JSON output
#     # 4. Return as {"gap_report": parsed_result}
#     pass
