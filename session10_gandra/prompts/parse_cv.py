"""
prompts/parse_cv.py — Prompt Template for Step 2: ParseCVHtml
===============================================================

This prompt instructs the LLM to extract structured information from
any CV HTML, regardless of the HTML template/structure used.

OUTPUT FORMAT:
    JSON object with keys: name, contact, summary, skills, experience,
    education, certifications, languages, additional_info.

DESIGN NOTES:
    - The LLM handles any CV structure — no CSS selectors needed
    - We ask for EVERY role and bullet to avoid summarization
    - key_results is a separate field from bullets (some CVs have it)
    - Double curly braces {{ }} are used to escape literal braces in
      the PromptTemplate (LangChain uses {var} for variables)
"""

from langchain_core.prompts import PromptTemplate

parse_cv_prompt = PromptTemplate(
    template="""You are an expert CV parser. Extract structured information from the following CV HTML.

CV HTML:
{cv_html}

Extract ALL information into the following JSON structure. Be thorough — do not skip any roles, skills, or bullets.

{{
    "name": "Full name of the candidate",
    "contact": "All contact details (email, phone, location) as a single string",
    "summary": "The professional summary/profile section as a single string. Include ALL bullet points merged into one coherent text.",
    "skills": ["skill1", "skill2", "..."],
    "experience": [
        {{
            "title": "Job title",
            "company": "Company name",
            "dates": "Date range exactly as written",
            "location": "Location if mentioned",
            "bullets": ["Achievement/responsibility 1", "Achievement/responsibility 2", "..."],
            "key_results": "Key results section if present, as a single string. Empty string if none."
        }}
    ],
    "education": [
        {{
            "degree": "Degree name and field",
            "institution": "University/school name",
            "year": "Year or date range"
        }}
    ],
    "certifications": ["Certification 1", "Certification 2", "..."],
    "languages": ["Language 1", "Language 2", "..."],
    "additional_info": "Any other information not captured above (nationality, mobility, etc.)"
}}

RULES:
- Extract EVERY experience role — do not skip any, even short ones
- Preserve all bullet points exactly as written (do not summarize or merge them)
- For skills: if there's no explicit skills section, extract skills mentioned throughout the CV
- For key_results: include the full text if present, empty string if not
- Return ONLY the JSON object, no preamble or explanation
- Ensure the JSON is valid and complete""",
    input_variables=["cv_html"],
)
