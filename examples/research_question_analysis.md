# Research Question Analysis — Worked Example

This example walks through Part 2 of the assignment using the research question:

> **"How do LLM agents handle tool failures and error recovery — what mechanisms exist and how are they evaluated?"**

Use this as a model for structuring your own analysis.

---

## Step 1: Semantic Scholar Search

**Prompt used:**
> "Search Semantic Scholar for papers on how LLM agents handle tool failures,
> error recovery, and robustness. Include papers from 2022–2024."

**What came back:**
Claude called `search_papers` with the query `"LLM agents tool failure error recovery robustness"`.
Results included:
- ToolLLM (Qin et al., 2023) — 847 citations
- ReAct (Yao et al., 2022) — 2,100+ citations
- AgentBench (Liu et al., 2023) — benchmarks including failure modes
- Reflexion (Shinn et al., 2023) — verbal reinforcement from failure signals
- Several less-cited 2024 papers on agent robustness

**Observation:** The search returned well-known papers quickly. Citation counts
gave a useful signal about impact. However, several relevant papers on
*graceful degradation* and *fallback strategies* didn't appear — suggesting the
keyword framing matters. 
---

## Step 2: Citation Tracing

**Prompt used:**
> "Of those results, which 3–4 papers are most central to understanding how
> agents handle failure? Use get_citations to trace what ReAct and Reflexion
> built on."

**What came back:**
Claude identified ReAct and Reflexion as the core papers, then called
`get_citations` on both with `direction="references"`. This surfaced:
- Chain-of-Thought (Wei et al., 2022) — reasoning basis for both
- Inner Monologue (Huang et al., 2022) — intermediate work connecting reasoning to action
- SayCan (Ahn et al., 2022) — grounding actions in environment affordances

**What the citation trace added:** Inner Monologue was not in the initial
keyword search results — the citation chain found it. That paper's approach to
using environment feedback as a form of error signal is directly relevant to
the question.

**What it missed:** Papers on *structured* error handling (retry logic, exception
types, fallback tools) were not well represented. The citation network is strong
on reasoning-based recovery but light on engineering approaches.

---

## Step 3: Local Library Query

**Prompt used:**
> "Search the local library for passages about how agents recover from failed
> tool calls, handle unexpected outputs, or retry actions."

**What came back:**
Three results above threshold:
1. ReAct paper (chunk 14, similarity 0.62) — passage describing the agent
   observing an error message and issuing a revised action
2. Reflexion paper (chunk 7, similarity 0.58) — passage on verbal feedback
   from failed attempts used to update the agent's strategy
3. ToolLLM paper (chunk 23, similarity 0.41) — passage on the DFSDT search
   algorithm and backtracking when a tool call fails

---

## Step 4: Synthesis Request

**Prompt used:**
> "Write a 4-paragraph literature review on how LLM agents handle tool failures
> and error recovery. Integrate findings from the Semantic Scholar search and
> the local library passages. Cite specific papers. Note open problems."

**Resulting review (summary):**

Claude produced a coherent synthesis covering:
1. **Observation-based recovery** — ReAct's loop where error observations feed
   back into reasoning (well-supported by local passages)
2. **Verbal reinforcement** — Reflexion's use of natural-language failure
   summaries to update future behavior
3. **Structured backtracking** — ToolLLM's DFSDT algorithm as a more systematic
   approach (drawn from the local chunk, not the abstract)
4. **Evaluation gap** — noted that AgentBench measures task success rates but
   that *how* agents fail is underreported in benchmarks

The synthesis was accurate for papers in the local library. For papers found
only via Semantic Scholar, it relied on abstracts — and in one case attributed
a specific mechanism to a paper that the abstract didn't actually describe in
that way.

---

## Evaluation

### Depth beyond surface-level search

Reading the top 5 Google Scholar abstracts for this query gives you paper titles,
one-sentence descriptions of each method, and citation counts. This system
produced more detailed information, but only for papers in the local library
or cited by papers in the local library. For anything else, the synthesis was
abstract-level at best.

The citation trace found Inner Monologue, which the keyword search missed entirely.
That was the clearest win of the full pipeline. However, the citation graph is
biased toward highly-cited papers, so recent work was underrepresented
even when relevant.

For papers in the local corpus, this system is genuinely better than abstract
skimming. For papers only in Semantic Scholar, it is roughly equivalent.

### Local retrieval contribution

Two of the four paragraphs in the synthesis drew on specific local passages.
The ToolLLM backtracking passage materially changed the review — without it,
the synthesis would have only covered reasoning-based recovery, not structured
search. That passage was not accessible from Semantic Scholar metadata at all, 
since the abstract doesn't describe the DFSDT mechanism. 

No passages were retrieved about *evaluation* of error recovery — the second
half of the research question. Rephrasing to "benchmark evaluation agent failure"
returned different but still partial results. Character-level chunking may have
split the relevant sections across chunk boundaries.

### At least one failure

1. **Hallucination risk:** For a 2024 paper found via Semantic Scholar but not
   in the local library, Claude described a specific experimental result that
   the abstract didn't mention. This was likely drawn from training data, not
   retrieved content. It was plausible but unverifiable — the kind of error that
   would pass unnoticed without checking the source.
2. **Query sensitivity:** The local library query for "evaluation" returned no
   relevant passages. Rephrasing to "benchmark" helped but still missed
   AgentBench passages that were clearly relevant.
3. **Corpus boundary:** The question "how are they evaluated" was partly
   unanswerable from the local library. The 20-paper corpus is strong on
   method papers but light on evaluation surveys.

For real research: usable with guardrails. Treat local-library citations as
ground truth, treat Semantic Scholar citations as leads to verify, and never 
include a specific claim without checking the source paper. The system is good
at finding the shape of a literature — what papers exist, how they relate — 
but not at guaranteeing accuracy for papers outside the local corpus.
