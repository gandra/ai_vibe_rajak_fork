# This file makes the prompts/ directory a Python package.
# Each prompt module exports a PromptTemplate (or string template)
# used by the corresponding LLM node.
#
# Usage in nodes:
#   from prompts.analyze_jd import analyze_jd_prompt
#   from prompts.planner import planner_prompt
#   ... etc.
