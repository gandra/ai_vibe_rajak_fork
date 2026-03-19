"""
nodes/analyze_jd.py — Step 3: AnalyzeJD Node (First LLM Node)
===============================================================

PURPOSE:
    Use an LLM to analyze the job description text and extract a
    structured representation of its requirements: must-have skills,
    nice-to-have skills, responsibilities, experience level, and domain.

THIS IS AN LLM NODE:
    Unlike Steps 1-2 (pure Python), this node calls an LLM.
    The prompt is defined in prompts/analyze_jd.py and imported here.

LANGGRAPH CONCEPTS LEARNED:
    - Wrapping an LLM call inside a LangGraph node
    - Using JsonOutputParser to get structured output from the LLM
    - Prompt engineering for extraction tasks
    - Extending the linear chain: ParseCVHtml → AnalyzeJD → next

COMPARISON WITH SESSION 9:
    Session 9's retrieval_grader was also an LLM chain that returned JSON.
    This is the same pattern, but the prompt asks for richer structured output.

STATE KEYS READ:
    jd_text: str

STATE KEYS WRITTEN:
    jd_requirements: dict — with keys like:
        {
            "must_have_skills": ["Python", "AWS", "CI/CD"],
            "nice_to_have_skills": ["Terraform", "GraphQL"],
            "responsibilities": ["Lead backend team", "Design APIs"],
            "experience_level": "Senior",
            "domain": "FinTech"
        }

PROMPT LOCATION:
    prompts/analyze_jd.py — contains the PromptTemplate
"""

# from langchain_core.output_parsers import JsonOutputParser
# from prompts.analyze_jd import analyze_jd_prompt
# from state import CVTailoringState

# ── LLM instance ───────────────────────────────────────────────────
# TODO: Import your chosen LLM (one of these):
#   from langchain_openai import ChatOpenAI
#   llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
#
#   from langchain_ollama import ChatOllama
#   llm = ChatOllama(model="your-model", format="json", temperature=0)


# def analyze_jd(state: CVTailoringState) -> dict:
#     """Extract structured requirements from the job description.
#
#     Args:
#         state: Must contain jd_text (set by IngestFiles).
#
#     Returns:
#         Dict with jd_requirements key containing extracted requirements.
#     """
#     # TODO: Step 3 implementation
#     # 1. Build prompt with state["jd_text"]
#     # 2. Invoke LLM
#     # 3. Parse JSON output
#     # 4. Return as {"jd_requirements": parsed_result}
#     pass
