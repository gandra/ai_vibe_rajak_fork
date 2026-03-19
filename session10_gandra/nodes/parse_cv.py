"""
nodes/parse_cv.py — Step 2: ParseCVHtml Node (LLM-Powered)
=============================================================

PURPOSE:
    Use an LLM to extract structured information from the raw CV HTML.
    Unlike a rule-based parser (BeautifulSoup selectors), this approach
    works with ANY CV structure — the LLM understands the semantics
    and extracts the right fields regardless of HTML layout.

WHY LLM INSTEAD OF RULE-BASED?
    1. Rule-based parsing breaks when the CV HTML structure changes
    2. An LLM can handle any format: tables, divs, custom classes, etc.
    3. The LLM understands context (e.g., "Dec 2023 - now" is a date range)
    4. Much less code to maintain — no CSS selectors to update

LANGGRAPH CONCEPTS LEARNED:
    - Using an LLM inside a "parsing" node (not just for generation)
    - JsonOutputParser for structured extraction
    - State accumulation: cv_html_raw AND cv_structured coexist

STATE KEYS READ:
    cv_html_raw: str

STATE KEYS WRITTEN:
    cv_structured: dict — structured representation of the CV:
        {
            "name": "...",
            "contact": "...",
            "summary": "...",
            "skills": ["...", ...],
            "experience": [
                {"title": "...", "company": "...", "dates": "...", "bullets": ["...", ...]},
                ...
            ],
            "education": [
                {"degree": "...", "institution": "...", "year": "..."},
                ...
            ],
            "certifications": ["...", ...]
        }
"""

import os
import json

from langchain_core.output_parsers import JsonOutputParser
from prompts.parse_cv import parse_cv_prompt

# ── LLM Configuration ──────────────────────────────────────────────
# Switch between OpenAI and Ollama by commenting/uncommenting below.

# Option A: OpenAI (cloud — fast, best structured output)
OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Option B: Ollama (local — free, works offline)
# from langchain_ollama import ChatOllama
# llm = ChatOllama(model="llama3.1:8b", temperature=0)


# ── Build the chain ─────────────────────────────────────────────────
parse_cv_chain = parse_cv_prompt | llm | JsonOutputParser()


# ── Main node function ─────────────────────────────────────────────

def parse_cv_html(state: dict) -> dict:
    """Parse raw CV HTML into structured sections using an LLM.

    The LLM extracts structured data from any CV HTML format,
    making this parser flexible enough to handle any CV template.

    Args:
        state: Must contain cv_html_raw (set by IngestFiles).

    Returns:
        Dict with cv_structured key containing parsed sections.
    """
    print("--- PARSE CV HTML (LLM-powered) ---")

    # Invoke the LLM to extract structured data
    cv_structured = parse_cv_chain.invoke({"cv_html": state["cv_html_raw"]})

    # ── Print summary for debugging ─────────────────────────────────
    print(f"  📋 Name: {cv_structured.get('name', 'N/A')}")
    summary = cv_structured.get('summary', '')
    print(f"  📝 Summary: {summary[:80]}...")
    skills = cv_structured.get('skills', [])
    print(f"  🛠️  Skills: {len(skills)} found")
    experience = cv_structured.get('experience', [])
    print(f"  💼 Experience: {len(experience)} roles")
    for i, role in enumerate(experience):
        bullets = role.get('bullets', [])
        print(f"     [{i}] {role.get('title', '?')} @ {role.get('company', '?')} ({role.get('dates', '?')}) — {len(bullets)} bullets")
    education = cv_structured.get('education', [])
    print(f"  🎓 Education: {len(education)} entries")
    certs = cv_structured.get('certifications', [])
    print(f"  📜 Certifications: {len(certs)} entries")

    return {"cv_structured": cv_structured}
