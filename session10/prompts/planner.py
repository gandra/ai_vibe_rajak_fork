"""
prompts/planner.py — Prompt Template for Step 5: PlannerAgent
===============================================================

This prompt instructs the LLM to create per-section tailoring instructions.
It's the most constrained prompt in the pipeline — it must enforce the
no-fabrication policy while still maximizing JD alignment.

OUTPUT FORMAT:
    JSON object with per-section instructions.

THE NO-FABRICATION POLICY (embedded in prompt):
    ✅ ALLOWED: rephrase, reorder, emphasize, de-emphasize
    ❌ NOT ALLOWED: new employers, dates, degrees, certifications, 
                   skills not in original, fabricated metrics

DESIGN NOTES:
    - This prompt takes THREE inputs (cv_structured, jd_requirements, gap_report)
    - It explicitly lists what's allowed and what's not
    - It asks the LLM to flag gaps that should go to questions (Step 8)
      instead of being "solved" by fabrication
"""

# from langchain_core.prompts import PromptTemplate

# planner_prompt = PromptTemplate(
#     template="""You are a CV tailoring strategist. Create a detailed plan
# for how to tailor this CV to better match the job description.
#
# ORIGINAL CV (structured):
# {cv_structured}
#
# JD REQUIREMENTS (structured):
# {jd_requirements}
#
# GAP ANALYSIS:
# {gap_report}
#
# RULES — you MUST follow these:
# ✅ You MAY:
#   - Rephrase experience bullets using terminology from the JD
#   - Reorder skills to put JD-relevant ones first
#   - Strengthen the summary to highlight JD-aligned strengths
#   - De-emphasize or shorten irrelevant experience details
#
# ❌ You MUST NOT:
#   - Add new employers, job titles, or date ranges
#   - Add new degrees, certifications, or institutions
#   - Claim proficiency with tools/technologies not in the original CV
#   - Invent metrics, outcomes, or achievements
#   - Add skills the candidate doesn't demonstrably have
#
# If a gap CANNOT be closed without fabrication, note it in
# "no_fabrication_notes" — these will become candidate questions.
#
# Return a JSON object with these keys:
# - "summary_instructions": how to revise the summary section
# - "skills_reorder": suggested order of skills (JD-relevant first)
# - "experience_changes": list of per-role change instructions
# - "sections_to_deemphasize": sections to shorten or remove
# - "no_fabrication_notes": gaps that need candidate input
#
# Return ONLY the JSON object, no preamble or explanation.""",
#     input_variables=["cv_structured", "jd_requirements", "gap_report"],
# )
