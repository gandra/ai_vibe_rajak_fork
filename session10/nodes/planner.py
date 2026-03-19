"""
nodes/planner.py — Step 5: PlannerAgent Node
==============================================

PURPOSE:
    Create a detailed, per-section tailoring plan that tells the
    TailorWriter (Step 6) exactly what to change in the CV.
    The planner decides WHAT to change; the writer executes it.

THIS IS AN "AGENT-STYLE" LLM NODE:
    Unlike Steps 3-4 (extraction/analysis), this node performs REASONING:
    it weighs the gaps, considers what can be rephrased vs. what must
    be left to gap questions, and produces actionable instructions.

THE CRITICAL CONSTRAINT — NO FABRICATION POLICY:
    The planner must enforce these rules:
    ✅ ALLOWED:
        - Rephrase bullets using JD terminology
        - Reorder/emphasize relevant experience
        - Strengthen summary to highlight JD-aligned strengths
        - De-emphasize irrelevant details
    ❌ NOT ALLOWED:
        - Add new employers, dates, degrees, or certifications
        - Claim experience with tools/technologies not in original CV
        - Invent metrics or outcomes
        - Add skills the candidate doesn't demonstrably have

    If a gap can't be closed without fabrication, the planner should
    flag it for gap questions (Step 8) instead.

LANGGRAPH CONCEPTS LEARNED:
    - Complex multi-input reasoning node
    - "Plan then execute" pattern (planner → writer separation)
    - Using state.get() for defensive reads

STATE KEYS READ:
    cv_structured: dict    (from Step 2)
    jd_requirements: dict  (from Step 3)
    gap_report: dict       (from Step 4)

STATE KEYS WRITTEN:
    tailoring_plan: dict — with keys like:
        {
            "summary_instructions": "Emphasize backend leadership and AWS...",
            "skills_reorder": ["Python", "AWS", "Docker", ...],
            "experience_changes": [
                {
                    "role_index": 0,
                    "bullets_to_rephrase": [1, 3],
                    "jd_terms_to_use": ["microservices", "CI/CD"],
                    "instructions": "Rephrase bullet 1 to emphasize..."
                }
            ],
            "sections_to_deemphasize": ["Hobbies"],
            "no_fabrication_notes": [
                "Cannot claim Terraform — route to gap questions",
                "Cannot add metrics to role 2 — no data in original CV"
            ]
        }

PROMPT LOCATION:
    prompts/planner.py
"""

# from langchain_core.output_parsers import JsonOutputParser
# from prompts.planner import planner_prompt
# from state import CVTailoringState


# def planner_agent(state: CVTailoringState) -> dict:
#     """Create a per-section tailoring plan based on gap analysis.
#
#     Args:
#         state: Must contain cv_structured, jd_requirements, gap_report.
#
#     Returns:
#         Dict with tailoring_plan key containing per-section instructions.
#     """
#     # TODO: Step 5 implementation
#     # 1. Build prompt with all three state keys
#     # 2. Invoke LLM
#     # 3. Parse JSON output
#     # 4. Return as {"tailoring_plan": parsed_result}
#     pass
