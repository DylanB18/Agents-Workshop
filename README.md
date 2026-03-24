# Assignment: Building and Tuning a Literature Review Agent

## Overview

In this assignment you will build and tune an agentic AI system that conducts
literature reviews. The system combines two information sources:

- **Semantic Scholar** — a large database of academic paper metadata, searched via API
- **Local PDF library** — ~20 full-text papers on LLM agents and RAG, searched via
  retrieval-augmented generation (RAG)

The MCP server you configure here runs inside **Claude Code**, giving Claude access
to these sources as callable tools during a conversation.

Your goals:
1. Complete the RAG pipeline implementation (by following guided TODOs)
2. Observe how RAG parameters affect retrieval quality
3. Observe how system prompt engineering affects review quality
4. Reflect on the strengths and limitations of this architecture

---

## Prerequisites

- **Python 3.10 or later** — check with `python --version`
- **Claude Code** — installed and authenticated ([installation guide](https://docs.anthropic.com/en/docs/claude-code/overview))

## Setup

### 1. Create and activate a virtual environment

**macOS / Linux:**
```bash
python -m venv agents-workshop
source agents-workshop/bin/activate
```

**Windows (Git Bash):**
```bash
python -m venv agents-workshop
source agents-workshop/Scripts/activate
```

**Windows (PowerShell):**
```powershell
python -m venv agents-workshop
.\agents-workshop\Scripts\Activate.ps1
```

> **Note:** Always activate the virtual environment before running any commands
> in this project. If you open a new terminal, re-run the `activate` command.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the PDF corpus

```bash
python download_papers.py
```

This downloads ~20 arXiv papers into `pdfs/`. Re-run it if any downloads fail.

### 4. Build the vector database

```bash
python src/pdf_ingestor.py
```

This reads all PDFs, chunks the text, computes embeddings, and stores them
in `chroma_db/`. You will re-run this whenever you change RAG parameters.

### 5. Register the MCP server with Claude Code

From a terminal, run:

```bash
claude mcp add literature-review -- python src/mcp_server.py
```

> **VSCode users:** If you are using Claude Code inside VSCode (not the CLI),
> the `.mcp.json` file included in this repo will configure the server
> automatically. You can skip the `claude mcp add` command.
>
> **Important:** The `.mcp.json` uses `"command": "python"`, which must resolve
> to the virtual environment's Python (i.e., the venv must be activated). If the
> MCP server fails to start, replace `"python"` in `.mcp.json` with the full
> path to your venv Python — for example:
> - **macOS/Linux:** `"command": "./agents-workshop/bin/python"`
> - **Windows:** `"command": "./agents-workshop/Scripts/python.exe"`

### 6. Verify the MCP server is working

Start a Claude Code session:

```bash
claude
```

Then ask Claude:

> "List the tools you have access to."

You should see four tools: `search_papers`, `get_paper_details`,
`query_local_library`, and `get_citations`. If Claude does not list these
tools, double-check that you ran `claude mcp add` from the project directory
and that your virtual environment is activated.

As an additional check, try:

> "Search Semantic Scholar for 'retrieval augmented generation'."

If the tool call works and returns paper results, your setup is complete.

---

## Part 1 — Implement the RAG Pipeline

Open `src/rag_pipeline.py`. You will find two functions marked `TODO`.

### TODO 1: `chunk_text(text, chunk_size, chunk_overlap)`

Split a string into overlapping character-level chunks. Read the docstring
carefully (an example is provided elsewhere to help you). This is 
the same algorithm used during ingestion, so understanding it will help you
reason about RAG failures later.

**Hint:** Use a `while` loop with a sliding `start` index. The step between
chunk starts is `chunk_size - chunk_overlap`.

### TODO 2: `retrieve(query)`

Query ChromaDB for the most relevant chunks and return filtered, formatted
results. The docstring specifies the exact steps and the ChromaDB API call.

**Steps:**
1. Encode the query with `self.model`
2. Call `self.collection.query(...)` as shown in the docstring
3. Convert L2 distances to similarities: `similarity = 1 / (1 + distance)`
4. Filter by `self.similarity_threshold`
5. Return sorted results as a list of dicts

**Test your implementation** by querying the local library in Claude Code:

> "Search the local library for passages about how ReAct combines reasoning and acting."

You should see retrieved chunks with source filenames and similarity scores.
If you get a `NotImplementedError`, your implementation is not yet complete.

---

## Part 2 — Tune RAG Parameters

Open `config.yaml`. The `rag:` section has four tunable parameters:

| Parameter | Default | What it controls |
|---|---|---|
| `chunk_size` | 512 | Max characters per chunk |
| `chunk_overlap` | 64 | Characters shared between adjacent chunks |
| `top_k` | 5 | Number of chunks retrieved per query |
| `similarity_threshold` | 0.3 | Min similarity score to include a chunk |

**Procedure:**

Run the following test query in Claude Code for each configuration below:

> "What are the key limitations of RAG systems, and how have recent papers
> addressed them?"

Use the same query each time and save Claude's full response.

**Configuration A — Baseline (defaults)**
```yaml
chunk_size: 512
chunk_overlap: 64
top_k: 5
similarity_threshold: 0.3
```

**Configuration B — Small chunks, high overlap**
```yaml
chunk_size: 256
chunk_overlap: 128
top_k: 8
similarity_threshold: 0.2
```

**Configuration C — Large chunks, low retrieval count**
```yaml
chunk_size: 1024
chunk_overlap: 64
top_k: 3
similarity_threshold: 0.4
```

> **Important:** After changing any RAG parameter, re-run ingestion before
> testing:
> ```bash
> python src/pdf_ingestor.py
> ```
> Then restart Claude Code (or run `claude mcp restart literature-review`) to
> reload the server.

In your writeup, compare the three outputs. Consider:
- Did all configurations retrieve the same papers/chunks?
- Which produced more precise quotes vs. broader context?
- Did any configuration fail to retrieve relevant information?
- What did a high vs. low `similarity_threshold` exclude?

---

## Part 3 — Tune the System Prompt

Open `prompts/templates.py`. The `"default"` prompt is already implemented.
You will write two more.

**Step 1:** Run the following request with the `"default"` prompt and save the output:

> "Write a literature review on the evolution of LLM agents, covering ReAct,
> Reflexion, MetaGPT, and recent surveys."

**Step 2:** Set `agent.system_prompt: "concise"` in `config.yaml` and implement
the `CONCISE_PROMPT` stub in `templates.py`. Restart the MCP server and run
the same request.

**Step 3:** Set `agent.system_prompt: "structured"` and implement the
`STRUCTURED_PROMPT` stub. Restart and run the same request again.

> **Restart reminder:** After changing `config.yaml` or `templates.py`, the
> server must be restarted for changes to take effect:
> ```bash
> claude mcp restart literature-review
> ```

In your writeup, compare the three outputs. Consider:
- How did the prompt change the structure of the review?
- Did the prompt affect which tools the agent called, or in what order?
- Which prompt produced the most useful output, and why?

---

## Part 4 — Reflection Write-Up

Create a file `writeup.md` in the project folder. Address four of the following
nine questions concisely:

### 4.1 RAG parameter analysis
- Which configuration produced the best retrieval results for your test query?
  What made it better?
- Describe a case where the similarity threshold excluded a relevant chunk,
  or included an irrelevant one.
- What would you change about the chunking strategy if you were building this
  for production? (Hint: character-level chunking has a known weakness.)

### 4.2 Prompt engineering analysis
- How did changing the system prompt affect tool calling behavior — did the
  agent call different tools, or in a different order?
- Which prompt template produced the highest-quality literature review?
  Define what "quality" means in your answer.
- Describe one specific failure you observed (e.g., the agent cited a paper
  incorrectly, missed a relevant paper, or produced an incoherent synthesis).

### 4.3 Architecture limitations
- The system can only retrieve from ~20 local papers. How did you observe this
  limit affecting the output?
- The Semantic Scholar integration provides metadata only (no full text).
  How did this affect the agent's ability to synthesize findings?
- What would you add or change to make this system viable for a real research workflow?

---

## Submission Checklist

- [ ] `src/rag_pipeline.py` — both TODOs implemented
- [ ] `config.yaml` — shows your final (best) configuration
- [ ] `prompts/templates.py` — `CONCISE_PROMPT` and `STRUCTURED_PROMPT` implemented
- [ ] `writeup.md` — all three reflection sections completed
- [ ] ZIP archive submitted to Canvas

---

## Tips and Common Issues

**"No results above the similarity threshold"**
→ Lower `similarity_threshold` in `config.yaml` and re-ingest. Or rephrase
your query to use vocabulary closer to what appears in the papers.

**Semantic Scholar returns an error**
→ The free tier is rate-limited. Wait a few seconds and retry. Avoid running
many searches in rapid succession.

**Changes to config.yaml not taking effect**
→ Restart the MCP server: `claude mcp restart literature-review`

**Changes to RAG params not affecting retrieval**
→ You must re-run `python src/pdf_ingestor.py` after changing `chunk_size`,
`chunk_overlap`, or `embedding_model`. The vector database must be rebuilt.

**PDF download failed for one paper**
→ Re-run `python download_papers.py`. It skips already-downloaded files.

---

## Grading Rubric

| Component | Points |
|---|---|
| `chunk_text()` correctly implemented | 15 |
| `retrieve()` correctly implemented (embedding, filtering, formatting) | 20 |
| RAG comparison: 3 configs tested, outputs documented | 20 |
| System prompt comparison: 2+ prompts written and tested | 20 |
| Writeup quality: specific observations, not generic | 25 |
| **Total** | **100** |
