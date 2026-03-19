"""
prompts/gap_analysis.py — Prompt Template for Step 4: GapAnalysis
===================================================================

This prompt instructs the LLM to compare structured JD requirements
against structured CV content and identify gaps.

OUTPUT FORMAT:
    JSON object with these keys:
    - matched: list of requirements that ARE evidenced in the CV
    - missing: list of requirements that are NOT evidenced at all
    - weak: list of requirements that are partially evidenced but need strengthening

DESIGN NOTES:
    - Both inputs are structured dicts (from Steps 2 and 3), not raw text
    - We tell the LLM to "only report genuine gaps" to avoid hallucinated weaknesses
    - Each gap entry includes enough detail for the Planner (Step 5) and
      GapQuestions (Step 8) to act on
"""

# from langchain_core.prompts import PromptTemplate

# gap_analysis_prompt = PromptTemplate(
#     template="""You are an expert career advisor comparing a candidate's CV
# against a job description to identify gaps.
#
# CV Content (structured):
# {cv_structured}
#
# JD Requirements (structured):
# {jd_requirements}
#
# Compare every JD requirement against the CV and classify it as:
# - "matched": the CV clearly evidences this requirement
# - "missing": the CV does not mention this at all
# - "weak": the CV partially covers this but lacks detail, metrics, or specificity
#
# For each item, provide:
# - "requirement": what the JD asks for
# - "evidence" (for matched): what in the CV supports it
# - "severity" (for missing): "must_have" or "nice_to_have"
# - "note" (for weak): what's lacking and why
#
# Only report genuine gaps — do NOT invent weaknesses that don't exist.
#
# Return ONLY a JSON object with keys: "matched", "missing", "weak".
# Each is a list of objects. No preamble or explanation.""",
#     input_variables=["cv_structured", "jd_requirements"],
# )
