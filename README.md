# AI Applications Workshop — Agentic AI Assignment

## Overview

This repository is a **complete reference example** of an agentic AI system that
conducts literature reviews. It combines two information sources:

- **Semantic Scholar** — a large database of academic paper metadata, searched via API.
- **Local PDF library** — ~20 full-text papers on LLM agents and RAG, searched via
  retrieval-augmented generation (RAG).

The system runs as an **MCP server** inside Claude Code, giving Claude access to
these sources as callable tools during a conversation.

**Your assignment is to build something like this yourself** — using Claude Code
as your primary coding assistant. You may build a literature review agent (following
the architecture here) or a different agent entirely. Then you will apply it to a
real problem and critically evaluate whether it works.

---

## Estimated Time

| Section | Time |
|---|---|
| Setup (running this example) | ~30 min |
| Part 1 — Build your agent | ~2–3.5 hrs |
| Part 2 — Research question / task analysis | ~90 min |
| Part 3 — Write-up | ~60 min |
| **Total** | **~5–6.5 hours** |

---

## Running This Example

Before building your own agent, run this one to understand what you're aiming for.

### 1. Create and activate a virtual environment

**macOS / Linux:**
```bash
python -m venv agents-workshop
source agents-workshop/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv agents-workshop
.\agents-workshop\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the PDF corpus

```bash
python download_papers.py
```

### 4. Build the vector database

```bash
python src/pdf_ingestor.py
```

### 5. Register the MCP server with Claude Code

```bash
claude mcp add literature-review -- python src/mcp_server.py
```

> **VSCode users:** The `.mcp.json` file in this repo configures the server
> automatically. Replace `"python"` with the full path to your venv Python if
> the server fails to start:
> - macOS/Linux: `"./agents-workshop/bin/python"`
> - Windows: `"./agents-workshop/Scripts/python.exe"`

### 6. Verify the server is running

Start a Claude Code session and ask:

> "List the tools you have access to."

You should see four tools: `search_papers`, `get_paper_details`,
`query_local_library`, and `get_citations`. Then try:

> "Search Semantic Scholar for 'retrieval augmented generation'."

If you get paper results, your setup is complete.

---

## Part 1 — Build Your Agent *(~2.0–3.5 hrs)*

Your goal is to build a working agentic system as an MCP server, using Claude
Code to help you write the code. The two core components are:

1. **A document ingestion pipeline** — reads files (PDFs, text, or whatever fits
   your domain), chunks them into pieces, embeds them, and stores them in a
   vector database
2. **An MCP server** — exposes tools that Claude can call to search that database
   and any external APIs you choose

### Option A — Literature review agent

Build a version of this system yourself. Use this repo as a reference for what the end
result should look like, but write the code from scratch with Claude's help.

Key questions to work through with Claude:
- What does a literature review workflow actually require step by step? Which steps
  can be automated, and which require human judgment?
- Why split into four separate tools rather than one? How does tool granularity
  affect what the agent can do?
- How should text be chunked for retrieval — by character, sentence, or paragraph?

You do not need to reproduce this system exactly — different design choices are
encouraged and worth discussing in your write-up.

### Option B — Agent of your choice

Build a different kind of agent that does something useful for you. Some examples:

- A codebase assistant that ingests a large repo and answers questions about it
- A customer support agent that queries a product documentation database
- A data analysis agent that reads CSV/JSON files and runs queries
- A legal or policy research agent over a domain-specific document corpus

Requirements for either option:
- At least one tool that does **local document retrieval** (RAG over files you
  provide, not just API calls)
- At least one tool that calls an **external API or service**
- A **configurable system prompt** with at least two variants that produce
  observably different agent behavior
- The server must run successfully in Claude Code.

This is an AI-assisted implementation assignment, so you are expected to use Claude
heavily. That said, you should be able to explain the various components of your 
system at a high level.

---

## Part 2 — Research Question / Task Analysis *(~90 min)*

Apply your agent to a real problem and evaluate whether it actually works. You will
write up your findings in a `writeup.md` file.

### Step 1: Choose a question or task

If you built a literature review agent, pick a research question you genuinely care
about that is specific enough that a good review would take a few hours to write.

Examples:
- "How do LLM agents handle tool failures and error recovery?"
- "What evaluation benchmarks exist for multi-agent coordination?"
- "How has RAG system design changed as context windows have grown?"

If you built a different agent, pick an equivalent task that represents a
non-trivial use of your system.

### Step 2: Run the full pipeline

Work through this sequence in Claude Code and save the outputs at each step:

1. **External search** — use your API-based tool to find relevant sources
2. **Identify key results** — ask Claude to identify the 3–5 most central sources
   and explain why; follow at least one connection between them (citation chain,
   related document, etc.)
3. **Local retrieval** — query your vector database for relevant passages; note
   whether they go beyond what the external search returned
4. **Synthesize** — ask Claude to produce a final answer (review, analysis, report)
   integrating both sources, with citations or attribution

A worked example of this workflow is in `examples/research_question_analysis.md`.

### Step 3: Evaluate the output

In your `writeup.md`, add a **"Part 2: Task Analysis"** section addressing:

**Depth beyond surface-level search**
What did your agent surface that a quick web/API search alone would have missed?
Did it miss anything?

**Local retrieval contribution**
Which passages from your vector database actually made it into the final output?
Were they more useful than the external API results, or largely redundant?

**At least one failure**
Describe a case where the system misled you or failed: a hallucinated claim, a
missed key result, an irrelevant retrieved chunk, or a synthesis that sounded
authoritative but was shallow. Would you trust this system for real work?

---

## Part 3 — Reflection Write-Up *(~60 min)*

Add a third part to your `writeup.md` file. Address three of the following questions:

### 3.1 Build process
- What was a major design decision you had to make? How did you decide to take
  a particular course of action.
- What did Claude get right on the first try? Where did you have to push back,
  correct it, or iterate?

### 3.2 System prompt engineering
- What two prompt variants did you implement? How did they differ in behavior? 
  Which produced better output, and how are you defining "better"?

### 3.4 Architecture limitations
- What would you need to change to make this viable for a real workflow?
- What did you learn about the limits of RAG-based agents that you didn't
  expect before building one?

---

## Submission Checklist

- [ ] Working MCP server registered in Claude Code
- [ ] At least one local retrieval tool and one external API tool
- [ ] At least two system prompt variants implemented and tested
- [ ] `writeup.md` — all sections completed

---

## Appendix — How This Example Was Built

This reference system was built iteratively using Claude Code, starting from a
single prompt:

> "I want to build a literature review agent as an MCP server. It should combine
> Semantic Scholar for paper discovery with local PDF retrieval using RAG. I want
> configurable system prompts and tunable retrieval parameters. Ask me questions
> to clarify this task."

From there, the architecture was refined over several subsequent prompts to clarify
tool design, chunking/retrieval logic, and iterate on the prompt templates.