"""
prompts/validator.py — Prompt Template for Step 7: ValidateTailoredCV
=======================================================================

This prompt is used for the LLM-ASSISTED portion of validation.
Deterministic checks (new employers, dates, credentials) are done in
Python code in the node itself.  This prompt handles the semantic checks
that require understanding (e.g., "is this new skill actually implied
by the original CV, or was it fabricated?").

THE VALIDATION CHECKS:
    Deterministic (in nodes/validator.py, no LLM):
    ├── No new employer names
    ├── No new dates
    ├── No new degrees/certifications
    └── Same section structure

    LLM-assisted (this prompt):
    ├── No new skills/tools not supported by original
    ├── No fabricated metrics or outcomes
    └── Rephrased content still accurately reflects original meaning

OUTPUT FORMAT:
    JSON object with:
    - "issues": list of strings describing problems found
    - "pass": boolean (true if no issues found)

DESIGN NOTES:
    - The LLM sees BOTH the original and tailored CV for comparison
    - We ask it to be strict — "err on the side of flagging"
    - The issues list is what gets fed back to TailorWriter on retry
"""

# from langchain_core.prompts import PromptTemplate

# validator_prompt = PromptTemplate(
#     template="""You are a strict quality checker for CV tailoring.
# Compare the TAILORED CV against the ORIGINAL CV and flag any fabrications.
#
# ORIGINAL CV (source of truth):
# {cv_original_structured}
#
# TAILORED CV (to validate):
# {cv_tailored_structured}
#
# Check for these violations:
# 1. New skills/tools claimed that are NOT in the original CV
# 2. New metrics or outcomes that were NOT in the original CV
# 3. Rephrased content that changes the MEANING of the original
# 4. Any claims that go beyond what the original CV supports
#
# Be STRICT — err on the side of flagging. It's better to flag a
# borderline case than to let a fabrication through.
#
# Return a JSON object with:
# - "pass": true if no issues found, false otherwise
# - "issues": list of strings describing each problem found
#   (empty list if pass is true)
#
# Return ONLY the JSON object, no preamble or explanation.""",
#     input_variables=["cv_original_structured", "cv_tailored_structured"],
# )
