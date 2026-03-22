# Sample Queries for Testing the Literature Review Agent

Use these queries to test your MCP server at each stage of the assignment.
Copy them directly into a Claude Code session.

---

## Quick smoke tests (after completing TODOs)

**Test search_papers:**
> "Search for 5 recent papers on retrieval-augmented generation published after 2022."

**Test query_local_library:**
> "Search the local library for passages describing how ReAct interleaves reasoning and acting."

**Test get_citations:**
> "Find the references list for the paper arXiv:2210.03629 (ReAct)."

**Test get_paper_details:**
> "Get full details for the paper arXiv:2005.11401 (RAG by Lewis et al.)."

---

## Part 2 — RAG comparison query (use this exact prompt for all 3 configs)

> "Search the local library and Semantic Scholar to answer: What are the key
> limitations of RAG systems, and how have recent papers addressed them?
> Cite specific papers and passages."

---

## Part 3 — Prompt comparison query (use this exact prompt for all 3 prompts)

> "Write a literature review on the evolution of LLM agents, covering ReAct,
> Reflexion, MetaGPT, and recent surveys. Use both the local library and
> Semantic Scholar."

---

## Additional exploration queries

> "Trace the intellectual lineage of chain-of-thought prompting. What papers
> directly built on Wei et al. 2022?"

> "Compare how CAMEL and MetaGPT approach multi-agent coordination."

> "What evaluation benchmarks exist for LLM-based agents? Summarize what
> AgentBench measures."

> "Find passages from local papers that discuss failure modes or limitations
> of current agent architectures."

> "Which papers in the local library discuss memory mechanisms for long-horizon
> tasks?"
