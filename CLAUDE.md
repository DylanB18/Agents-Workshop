# Literature Review MCP — Claude Code Context

This is a graduate-level AI Applications workshop assignment. The project
implements a literature review assistant as an MCP server, combining Semantic
Scholar search with local PDF retrieval (RAG).

## Project structure

```
workshop/
├── config.yaml              # Students edit: RAG params, prompt selection
├── download_papers.py       # Downloads ~20 arXiv PDFs into pdfs/
├── prompts/
│   └── templates.py         # Students edit: system prompt variants
├── src/
│   ├── mcp_server.py        # MCP server — pre-implemented, read-only
│   ├── rag_pipeline.py      # Students implement: chunk_text(), retrieve()
│   ├── pdf_ingestor.py      # Pre-implemented PDF ingestion — read-only
│   └── semantic_scholar.py  # Pre-implemented API client — read-only
├── pdfs/                    # Local PDF corpus (populated by download_papers.py)
└── chroma_db/               # ChromaDB vector store (created by pdf_ingestor.py)
```

Note: it is possible the root "workshop" folder might be called something different if it was renamed. The files structure should otherwise be the same.

## Setup commands (run in order)

```bash
pip install -r requirements.txt
python download_papers.py
python src/pdf_ingestor.py
claude mcp add literature-review -- python src/mcp_server.py
```

## Student tasks

1. **Implement** `chunk_text()` and `retrieve()` in `src/rag_pipeline.py`
2. **Tune** RAG parameters in `config.yaml` (chunk_size, overlap, top_k, threshold)
3. **Write** system prompt variants in `prompts/templates.py`
4. **Run** comparisons and document results

## Important notes

- Re-run `python src/pdf_ingestor.py` after changing any RAG parameter in config.yaml
- Re-run `claude mcp add` (or restart Claude Code) after changing config.yaml or prompts
- The Semantic Scholar free tier is rate-limited — searches are slightly throttled
- `chroma_db/` and `pdfs/` directories should not be committed to version control
