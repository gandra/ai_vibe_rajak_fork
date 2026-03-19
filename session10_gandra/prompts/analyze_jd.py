"""
prompts/analyze_jd.py — Prompt Template for Step 3: AnalyzeJD
===============================================================

This prompt instructs the LLM to extract structured requirements
from a raw job description text.

OUTPUT FORMAT:
    JSON object with these keys:
    - must_have_skills: list[str]
    - nice_to_have_skills: list[str]
    - responsibilities: list[str]
    - experience_level: str
    - domain: str

DESIGN NOTES:
    - The prompt explicitly asks for JSON to work with JsonOutputParser
    - We ask the LLM to CLASSIFY each requirement (must-have vs nice-to-have)
      because this classification drives prioritization in the tailoring plan
    - "No preamble" instruction prevents the LLM from wrapping JSON in markdown
"""

# from langchain_core.prompts import PromptTemplate

# analyze_jd_prompt = PromptTemplate(
#     template="""You are an expert recruiter analyzing a job description.
#
# Extract the key requirements and classify each one.
#
# Job Description:
# {jd_text}
#
# Return a JSON object with these exact keys:
# - "must_have_skills": list of skills/tools explicitly required
# - "nice_to_have_skills": list of skills/tools listed as preferred/bonus
# - "responsibilities": list of key job responsibilities
# - "experience_level": the seniority level (e.g., "Junior", "Mid", "Senior", "Lead")
# - "domain": the industry/domain (e.g., "FinTech", "HealthTech", "E-commerce")
#
# Return ONLY the JSON object, no preamble or explanation.""",
#     input_variables=["jd_text"],
# )
