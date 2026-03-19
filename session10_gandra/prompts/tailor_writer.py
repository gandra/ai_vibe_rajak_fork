"""
prompts/tailor_writer.py — Prompt Template for Step 6: TailorWriter
=====================================================================

This prompt instructs the LLM to rewrite the CV sections according to
the tailoring plan.  It has a special {correction_instructions} slot
that is empty on the first pass and filled with validation errors on retry.

THE RETRY MECHANISM:
    First pass:   correction_instructions = ""
    Retry pass:   correction_instructions = "FIX THESE ISSUES:\n- issue 1\n- issue 2"

    This is how the validation loop (Step 7) communicates what went wrong
    back to the writer without needing a separate node or prompt.

OUTPUT FORMAT:
    JSON object with the same shape as cv_structured, but with tailored content.
    This ensures the Validator (Step 7) can do a field-by-field comparison.

DESIGN NOTES:
    - The prompt includes both the original CV and the plan
    - {correction_instructions} is a key architectural element —
      it's what makes the retry loop work
    - "Return the SAME structure" ensures the output can be validated
"""

# from langchain_core.prompts import PromptTemplate

# tailor_writer_prompt = PromptTemplate(
#     template="""You are a professional CV writer. Rewrite the CV sections
# below according to the tailoring plan.
#
# ORIGINAL CV (structured):
# {cv_structured}
#
# TAILORING PLAN:
# {tailoring_plan}
#
# {correction_instructions}
#
# RULES:
# - Follow the tailoring plan exactly
# - Preserve ALL factual claims from the original CV
# - Do NOT add any new employers, dates, degrees, certifications
# - Do NOT claim skills or tools not present in the original CV
# - Do NOT invent metrics or outcomes
# - Return the SAME section structure as the original
#
# Return a JSON object with the same keys as the original CV
# (summary, skills, experience, education) but with tailored content.
# Return ONLY the JSON object, no preamble or explanation.""",
#     input_variables=["cv_structured", "tailoring_plan", "correction_instructions"],
# )
