"""
nodes/gap_questions.py — Step 8: GenerateGapQuestions Node
============================================================

PURPOSE:
    Generate specific, actionable questions to ask the candidate
    about gaps between the JD and their CV.  These questions help
    gather missing evidence for a stronger next iteration.

IMPORTANT CONSTRAINT:
    Questions must be GROUNDED in the gap report.  They must NOT
    presume experience that isn't in the original CV.
    
    ✅ GOOD: "Which AWS services have you used in production?"
           (asks for details about a gap — doesn't assume anything)
    
    ❌ BAD:  "Tell me about your extensive AWS experience."
           (presumes extensive experience that may not exist)

THIS NODE RUNS AFTER VALIDATION PASSES:
    It's the first node on the "happy path" after the validation gate.
    It reads the gap_report (from Step 4) which has been in state
    since early in the pipeline — demonstrating how LangGraph state
    persists across the entire run.

LANGGRAPH CONCEPTS LEARNED:
    - Node that runs after a conditional edge resolves
    - Reading state keys produced much earlier in the pipeline
    - State persistence (gap_report was written in Step 4, read here in Step 8)

STATE KEYS READ:
    gap_report: dict       (from Step 4)
    jd_requirements: dict  (from Step 3)
    cv_structured: dict    (from Step 2 — for context on what IS in the CV)

STATE KEYS WRITTEN:
    gap_questions: list[str]

PROMPT LOCATION:
    prompts/gap_questions.py
"""

# from langchain_core.output_parsers import JsonOutputParser
# from prompts.gap_questions import gap_questions_prompt
# from state import CVTailoringState


# def generate_gap_questions(state: CVTailoringState) -> dict:
#     """Generate clarifying questions based on identified gaps.
#
#     Args:
#         state: Must contain gap_report and jd_requirements.
#
#     Returns:
#         Dict with gap_questions key containing list of question strings.
#     """
#     # TODO: Step 8 implementation
#     # 1. Build prompt with gap_report, jd_requirements, cv_structured
#     # 2. Invoke LLM
#     # 3. Parse JSON output (list of strings)
#     # 4. Return {"gap_questions": parsed_questions}
#     pass
