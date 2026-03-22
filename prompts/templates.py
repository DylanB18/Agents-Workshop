"""
prompts/templates.py — System prompt templates

This file defines the system prompts that govern how the literature review
agent behaves. The active template is selected by agent.system_prompt in
config.yaml.

Part 3 of the assignment asks you to:
  1. Observe how the "default" prompt affects the agent's behavior.
  2. Write at least two alternative prompts (modify the existing stubs or
     create new ones).
  3. Test each and document differences in your write-up.

Things to experiment with:
  - Tone (academic, concise, critical)
  - Structure requirements (headings, bullet points, citations style, etc.)
  - When to use which tool (guide the agent to prefer local PDFs vs. Semantic Scholar)
  - How to handle uncertainty or missing information
  - Depth of synthesis vs. simple summarization
"""


# ---------------------------------------------------------------------------
# Pre-implemented: "default"
# ---------------------------------------------------------------------------

DEFAULT_PROMPT = """You are an expert research assistant helping a graduate student \
conduct a systematic literature review on topics related to AI agents and large \
language models.

You have access to four tools:
  - search_papers: Search Semantic Scholar for papers by topic or keyword.
  - get_paper_details: Fetch full metadata and references for a specific paper.
  - query_local_library: Retrieve passages from a curated local PDF library using \
semantic similarity search.
  - get_citations: Explore citation networks (what a paper cites or is cited by).

Workflow guidelines:
1. Start by searching Semantic Scholar to get an overview of the topic.
2. Use query_local_library to retrieve relevant passages from locally stored papers.
3. Use get_paper_details and get_citations to trace key papers and their relationships.
4. Synthesize findings into a coherent literature review with clear attribution.

In your final review:
- Group related papers thematically, not chronologically.
- For each major claim, cite the source paper (author, year).
- Note gaps, contradictions, or open problems in the literature.
- Clearly distinguish between what the local library contains and what you found \
only via Semantic Scholar metadata.
"""


# ---------------------------------------------------------------------------
# Student-implemented stubs — Part 3 of the assignment
# ---------------------------------------------------------------------------

CONCISE_PROMPT = """
TODO (Part 3a): Write a system prompt that instructs the agent to produce a
concise, bullet-point summary rather than a long prose review.

Consider: How should the agent decide when to stop searching? How many papers
should it reference? What should be omitted from a concise review?

Replace this entire string with your prompt.
"""

STRUCTURED_PROMPT = """
TODO (Part 3b): Write a system prompt that produces a highly structured review
with required sections: Introduction, Key Methods, Datasets & Evaluation,
Open Problems, and Conclusion.

Consider: Should the agent be told to use query_local_library before or after
Semantic Scholar? Does specifying section structure improve or hurt synthesis quality?

Replace this entire string with your prompt.
"""

CRITICAL_PROMPT = """
TODO (Part 3c — optional challenge): Write a system prompt that instructs the
agent to critically evaluate papers rather than just summarize them. It should
flag weak evaluations, limited baselines, or overclaimed results.

Consider: Is it realistic for an agent to critically evaluate papers without
reading full PDFs? What are the limits of RAG-based critique?

Replace this entire string with your prompt.
"""


# ---------------------------------------------------------------------------
# Registry — add new prompt names here
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, str] = {
    "default": DEFAULT_PROMPT,
    "concise": CONCISE_PROMPT,
    "structured": STRUCTURED_PROMPT,
    "critical": CRITICAL_PROMPT,
}


def get_system_prompt(name: str) -> str:
    """
    Return the system prompt template for the given name.
    Falls back to "default" if the name is not found.
    """
    if name not in TEMPLATES:
        print(f"[prompts] Warning: unknown prompt '{name}', using 'default'")
        return TEMPLATES["default"]
    return TEMPLATES[name]
