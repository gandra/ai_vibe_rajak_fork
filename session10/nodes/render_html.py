"""
nodes/render_html.py — Step 9: RenderHTML Node
================================================

PURPOSE:
    Take the tailored structured CV (from Step 6/7) and rebuild it into
    a complete HTML string that preserves the original template/layout.
    The output should look identical to the original CV in a browser,
    but with tailored content.

THIS IS A "TOOL NODE" (no LLM):
    Pure Python HTML reconstruction using BeautifulSoup.
    Uses the raw_template_metadata saved during parsing (Step 2) to
    know which tags, classes, and structure to use.

WHY NOT LET THE LLM GENERATE HTML DIRECTLY?
    1. LLMs often produce subtly broken HTML
    2. The original CV has specific styling (CSS) that must be preserved
    3. Deterministic reconstruction is more reliable than LLM generation
    4. Easier to debug: if the HTML looks wrong, it's a template issue

LANGGRAPH CONCEPTS LEARNED:
    - Non-LLM node in a graph that also contains LLM nodes (mixed graph)
    - Reading state keys from different earlier steps
    - Template reconstruction pattern

STATE KEYS READ:
    cv_html_raw: str               (from Step 1 — original HTML as template)
    cv_tailored_structured: dict   (from Step 6 — tailored content to inject)
    cv_structured: dict            (from Step 2 — for raw_template_metadata)

STATE KEYS WRITTEN:
    cv_tailored_html: str — complete HTML string ready for printing to PDF

IMPLEMENTATION APPROACH:
    1. Parse original HTML (BeautifulSoup)
    2. For each section in cv_tailored_structured:
       a. Find the corresponding element in the original HTML
       b. Replace its text content with the tailored content
       c. Preserve all attributes (class, id, style)
    3. Convert back to string with str(soup)
"""

# from bs4 import BeautifulSoup
# from state import CVTailoringState


# def render_html(state: CVTailoringState) -> dict:
#     """Render tailored CV sections back into HTML, preserving original layout.
#
#     Args:
#         state: Must contain cv_html_raw, cv_tailored_structured,
#                and cv_structured (for template metadata).
#
#     Returns:
#         Dict with cv_tailored_html key containing the final HTML string.
#     """
#     # TODO: Step 9 implementation
#     #
#     # 1. Parse original HTML: soup = BeautifulSoup(state["cv_html_raw"])
#     # 2. Get template metadata: metadata = state["cv_structured"]["raw_template_metadata"]
#     # 3. For each section in state["cv_tailored_structured"]:
#     #    a. Find the corresponding element in soup using metadata
#     #    b. Replace inner content with tailored text/bullets
#     # 4. Return {"cv_tailored_html": str(soup)}
#     pass
