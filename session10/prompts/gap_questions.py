"""
prompts/gap_questions.py — Prompt Template for Step 8: GenerateGapQuestions
============================================================================

This prompt instructs the LLM to generate specific, actionable questions
that would help the candidate provide missing evidence for a stronger
next version of the tailored CV.

THE KEY CONSTRAINT:
    Questions must be GROUNDED in the gap report — they must not
    presume experience that isn't in the original CV.

    ✅ GOOD: "Which AWS services have you used in production?"
    ❌ BAD:  "Tell me about your extensive AWS experience."

OUTPUT FORMAT:
    JSON array of question strings.

DESIGN NOTES:
    - We include the gap_report AND the original cv_structured
      so the LLM knows what IS in the CV (to avoid presuming things)
    - Each question should be specific enough that the candidate's answer
      can be directly incorporated into the CV
    - Questions are ordered by priority (must-have gaps first)
"""

# from langchain_core.prompts import PromptTemplate

# gap_questions_prompt = PromptTemplate(
#     template="""You are a career coach helping a candidate strengthen their CV
# for a specific job application.
#
# Based on the gap analysis below, generate specific questions to ask
# the candidate that would help fill the gaps with REAL information.
#
# GAP ANALYSIS:
# {gap_report}
#
# JD REQUIREMENTS:
# {jd_requirements}
#
# ORIGINAL CV (for context on what the candidate HAS mentioned):
# {cv_structured}
#
# RULES:
# - Questions must be grounded in actual gaps from the analysis
# - Do NOT presume experience the candidate doesn't have
# - Questions should be specific enough that answers can be added to the CV
# - Order questions by priority (must-have gaps first)
# - Include context in each question (e.g., "The JD requires X. You mentioned Y at Company Z — can you elaborate on...")
#
# GOOD EXAMPLES:
# - "Which specific AWS services (EC2, S3, Lambda, etc.) have you used?"
# - "In your role at Company X, what was the size of the team you managed?"
# - "Can you quantify the performance improvement from the optimization you described?"
#
# BAD EXAMPLES (do NOT do this):
# - "Tell me about your Kubernetes experience" (presumes experience not in CV)
# - "How many years of Terraform experience do you have?" (presumes Terraform)
#
# Return a JSON array of question strings.
# Return ONLY the JSON array, no preamble or explanation.""",
#     input_variables=["gap_report", "jd_requirements", "cv_structured"],
# )
