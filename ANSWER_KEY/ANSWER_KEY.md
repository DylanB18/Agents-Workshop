# Answer Key — Literature Review MCP Assignment

**Instructor use only. Do not distribute to students.**

---

## Part 1 — Sample Solutions: `src/rag_pipeline.py`

### TODO 1: `chunk_text()`

```python
@staticmethod
def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if not text:
        return []

    chunks = []
    step = chunk_size - chunk_overlap
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += step
    return chunks
```

**What to look for:**
- The step is `chunk_size - chunk_overlap`, not just `chunk_size`
- `text[start : start + chunk_size]` naturally handles the short last chunk (Python slicing doesn't overflow)
- A trailing stub chunk is correct — e.g. `chunk_text("abcdefghij", 4, 1)` → `["abcd", "defg", "ghij", "j"]`
- Empty string guard is good practice but not penalizable if missing
- A common mistake is computing `end = min(start + chunk_size, len(text))` — this is correct but unnecessary due to Python slice semantics; full credit either way

---

### TODO 2: `retrieve()`

```python
def retrieve(self, query: str) -> list[dict]:
    # Step 1: encode the query
    query_embedding = self.model.encode(query).tolist()

    # Step 2: query ChromaDB
    results = self.collection.query(
        query_embeddings=[query_embedding],
        n_results=self.top_k,
        include=["documents", "metadatas", "distances"],
    )

    # Step 3–4: convert distances, filter by threshold
    output = []
    for text, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        similarity = round(1 / (1 + distance), 4)
        if similarity >= self.similarity_threshold:
            output.append({
                "text": text,
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "similarity": similarity,
            })

    # Step 5: sort descending by similarity
    output.sort(key=lambda x: x["similarity"], reverse=True)
    return output
```

**What to look for:**
- `self.model.encode(query)` must be converted to a Python list (`.tolist()`) for ChromaDB — forgetting this causes a type error
- `results["documents"][0]` — the outer list index `[0]` (for the first query) is required; a common mistake is omitting it
- Distance-to-similarity formula `1 / (1 + distance)` — any monotonically decreasing mapping is acceptable, but must use the correct direction (lower distance = higher similarity)
- Filter must be `>=`, not `>`
- Sort must be descending (`reverse=True`)
- Missing `round()` is fine — not a functional issue

**Common mistakes and partial credit guidance:**
- Forgot `.tolist()` on the embedding → runtime error; partial credit if logic is otherwise correct (−5)
- Sorted ascending instead of descending → −5
- Skipped threshold filtering → −5
- Missing `[0]` index on results → runtime error; partial credit if logic is otherwise correct (−5)

---

## Part 2 — Example RAG Configuration Comparisons

*The following represents the kind of observations a strong student should make. Actual outputs will vary with model version and PDF content.*

### Configuration A (Baseline: size=512, overlap=64, top_k=5, threshold=0.3)

A student should observe:
- Chunks are long enough to carry full sentences and often capture a complete argument
- With `top_k=5`, the agent receives 5 varied chunks, possibly from different papers
- Threshold of 0.3 is loose — may include tangentially related chunks

### Configuration B (Small chunks: size=256, overlap=128, top_k=8, threshold=0.2)

A student should observe:
- Short chunks often cut mid-sentence, losing context (e.g., a claim without its supporting evidence)
- High overlap (128/256 = 50%) means consecutive chunks repeat significant content
- Lowering the threshold to 0.2 lets in more results, including some that are only loosely related
- Retrieving 8 chunks from smaller pieces can flood the context with redundant text

### Configuration C (Large chunks: size=1024, overlap=64, top_k=3, threshold=0.4)

A student should observe:
- Large chunks preserve more context per result, but the agent receives fewer (3 total)
- A threshold of 0.4 is strict — some relevant chunks may be excluded entirely, resulting in "No results above threshold" messages for niche queries
- The agent may rely more heavily on Semantic Scholar metadata (abstract only) to compensate for sparse local retrieval
- Large chunks make it harder for the embedding to represent the chunk's "topic" precisely — a 1024-char chunk about three different things gets averaged into a muddled embedding

**What to look for in student comparisons:**
- Specific examples of chunks that were included/excluded, not just general statements
- Observation that Config B produces redundant results due to high overlap
- Observation that Config C's strict threshold can cause empty retrieval — this is a key failure mode to surface
- Understanding that chunk size and embedding quality are linked

---

## Part 3 — Sample Prompt Implementations: `prompts/templates.py`

### CONCISE_PROMPT (sample solution)

```python
CONCISE_PROMPT = """You are a research assistant producing concise literature summaries \
for busy researchers.

Your output must be a structured bullet-point summary, not prose paragraphs.

Tool usage:
- Call query_local_library FIRST with the topic query.
- Then call search_papers ONCE to identify any highly-cited papers not in the local library.
- Do NOT call get_citations or get_paper_details unless specifically asked.
- Stop after two tool calls total. Do not over-search.

Output format (strictly follow this):
**Topic:** [one sentence]

**Key Papers (5–7 max):**
- [Author, Year] — [one sentence: main contribution]
- ...

**Main Themes:** [3 bullets max]

**Gaps / Open Questions:** [2 bullets max]

Do not write introductory or concluding prose. Omit papers you cannot attribute \
to a specific source (local library or Semantic Scholar result).
"""
```

**What makes this a good answer:**
- Explicitly constrains tool usage (stops runaway multi-step search)
- Imposes strict output format — students should observe the agent following it closely
- Forces the agent to prefer `query_local_library` first, illustrating how tool ordering affects what gets cited

**What to look for in student responses:**
- Does the student's prompt actually produce shorter output? (Easy to verify)
- Does it change which tools are called? (Should reduce `get_citations` calls)
- A weak answer just says "be concise" without structural constraints

---

### STRUCTURED_PROMPT (sample solution)

```python
STRUCTURED_PROMPT = """You are an academic research assistant writing a structured \
literature review for a graduate seminar.

Tool usage order:
1. Call query_local_library with 2–3 different queries to gather passages from the \
local PDF library.
2. Call search_papers to find any additional relevant work not in the local library.
3. Use get_paper_details on 1–2 key papers to verify their reference lists.

Output format — your review MUST contain exactly these five sections:

## 1. Introduction
Briefly define the topic and explain why it matters (3–5 sentences).

## 2. Key Methods and Approaches
Describe the main technical contributions across papers. Group by approach \
(e.g., prompting strategies, tool use, multi-agent frameworks), not by paper.

## 3. Datasets and Evaluation
What benchmarks or evaluation methods do these papers use? Note any lack of \
standardization.

## 4. Open Problems
What questions remain unanswered? What limitations do the authors themselves acknowledge?

## 5. Conclusion
Summarize the trajectory of the field in 3–5 sentences.

For every factual claim, include an inline citation: (Author et al., Year). \
If a claim comes only from a Semantic Scholar abstract, note "[abstract only]".
"""
```

**What makes this a good answer:**
- Forces specific section structure, making it easy to compare outputs across prompts
- The "[abstract only]" instruction surfaces the Semantic Scholar limitation naturally
- Students should observe the agent issuing multiple `query_local_library` calls as instructed

**Interesting failure mode to discuss in class:**
The structured prompt sometimes causes the agent to force-fit content into sections even when it doesn't belong (e.g., inventing "limitations" for papers that didn't discuss them). This is a good teaching moment about how structure constraints can introduce hallucination pressure.

---

### CRITICAL_PROMPT (sample solution — optional)

```python
CRITICAL_PROMPT = """You are a skeptical senior researcher reviewing papers for a \
journal club. Your job is not to summarize papers uncritically, but to evaluate \
the strength of their evidence and claims.

For each paper you discuss, address:
- What is the main claim?
- What is the evidence? (ablation studies, baselines, dataset size)
- Is the evaluation convincing? Note any missing baselines, cherry-picked examples, \
  or limited benchmarks.
- Does the paper's conclusion match what the experiments actually show?

Tool usage:
- Use query_local_library to find methods and evaluation sections of papers.
- Use search_papers to check citation counts as a rough proxy for community reception.
- Prefer passages that describe experiments, metrics, and results over introductions.

Important caveats to surface in your review:
- If you cannot access the full experimental details (only abstract), say so explicitly.
- Do not fabricate evaluation details that are not in the retrieved text.
- Acknowledge when a limitation may reflect the paper's era rather than sloppiness.

Output a critical analysis grouped by paper (not by theme), ending with an overall \
assessment of which 2–3 papers have the most credible empirical support.
"""
```

**Teaching note:** This prompt surfaces the most important limitation of this architecture — RAG over PDFs can retrieve methodology sections, but cannot reliably support fine-grained critique (e.g., checking exact numbers against baselines) without perfect chunking. Strong students will note this in their writeup.

---

## Part 4 — Sample Writeup

*A-level response. ~550 words. Students should write in their own voice; this is a model of the depth and specificity expected.*

---

### 4.1 RAG Parameter Analysis

**Best configuration:** Configuration A (baseline) produced the most balanced results for the query about RAG limitations. It retrieved coherent, full-sentence passages from papers including `Asai2023_SelfRAG` and `Gao2023_RAG_survey`, giving the agent enough context to synthesize a meaningful answer.

**Configuration B failure mode:** With `chunk_size=256` and `chunk_overlap=128`, I frequently received chunks that opened mid-sentence — for example, a chunk beginning with "...which addresses this by adding a critic model that..." with no referent. The agent had no way to recover the antecedent, so it either guessed or skipped the passage. High overlap also produced near-duplicate chunks from the same paper in a single query result, wasting the `top_k` budget.

**Configuration C failure mode:** Setting `similarity_threshold=0.4` caused the `query_local_library` tool to return "No results above threshold" for a query about self-consistency decoding — a topic that is covered in `Wang2022_self_consistency_chain_of_thought.pdf`. The relevant chunk scored 0.38 and was excluded. The agent then fell back entirely on Semantic Scholar metadata (abstracts), which produced a shallower review.

**What I would change for production:** Character-level chunking is the weakest point of this system. It cuts words and sentences arbitrarily, degrading both embedding quality and readability of retrieved text. A sentence-boundary or paragraph-boundary chunker (using spaCy or NLTK) would produce more semantically coherent units, improving embedding precision and the agent's ability to quote accurately.

---

### 4.2 Prompt Engineering Analysis

**Tool-calling behavior:** Switching from `default` to `structured` caused the agent to issue two or three `query_local_library` calls at the start of each session (as instructed), then one `search_papers` call — in that order. The `default` prompt reversed this: the agent typically called `search_papers` first, then optionally queried the local library. This order difference meaningfully affected what got cited: the structured prompt surfaced more full-text passages, while the default prompt led with Semantic Scholar abstracts.

**Best-quality prompt:** The `structured` prompt produced the highest-quality review by my judgment, defined as: accurate attribution, internal coherence between sections, and honest acknowledgment of what came from abstracts vs. local text. The enforced section structure forced the agent to address evaluation methodology separately, which exposed a real gap — most papers in the corpus evaluate on proprietary tasks or small benchmarks with no shared baseline.

**Observed failure:** With the `concise` prompt, the agent cited "Yao et al., 2023" for Tree of Thoughts but attributed a result that actually came from the ReAct paper. Both papers are by "Yao et al." and share vocabulary; the agent conflated them. This suggests that short prompts that deprioritize verification create more attribution errors.

---

### 4.3 Architecture Limitations

**Coverage gap:** The 20-paper corpus made a significant difference — when I asked about GraphRAG or GPT-4 tool use, the agent noted it had no local sources and relied entirely on Semantic Scholar abstracts, producing noticeably thinner synthesis for those subtopics.

**Metadata-only limitation:** Semantic Scholar cannot substitute for full text. For papers not in the local library, the agent could describe what a paper claimed (from the abstract) but not how it was evaluated or what the actual numbers were. Every claim came hedged as "[abstract only]" when I used the structured prompt — a useful forcing function that made the limitation visible.

**What I would add:** (1) a reranking step after retrieval to filter out low-relevance chunks before sending them to the agent; (2) PDF section detection so the agent can request "methods section" or "evaluation section" specifically, rather than receiving arbitrary character chunks.

---

## Grading Notes

| Component | Full Credit Indicators |
|---|---|
| `chunk_text()` | Correct step size, handles empty input, short last chunk works |
| `retrieve()` | Correct `.tolist()`, `[0]` indexing, threshold filter, descending sort |
| RAG comparison | Specific chunk-level observations, not just "Config B retrieved more results" |
| Prompts | Prompts produce observably different tool-calling behavior (not just different wording) |
| Writeup | Cites specific papers/chunks, identifies at least one concrete failure mode per section |

**Red flags:**
- Writeup describes generic RAG concepts without referencing the actual system behavior → likely not fully tested
- All three prompts produce identical agent behavior → prompts are too similar or student didn't restart the server between tests
- `retrieve()` returns results but ignores `similarity_threshold` → common; check the filter condition
