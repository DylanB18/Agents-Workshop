"""
rag_pipeline.py — RAG retrieval pipeline

This module handles querying the ChromaDB vector database to find relevant
text chunks from the local PDF library.

Your tasks are marked with TODO comments. Read the surrounding code carefully
before implementing.
"""

import pathlib
import yaml
import chromadb
from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path: str = "config.yaml") -> dict:
    config_path = pathlib.Path(config_path)
    if not config_path.exists():
        # Try relative to this file's parent
        config_path = pathlib.Path(__file__).parent.parent / "config.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# RAGPipeline class
# ---------------------------------------------------------------------------

class RAGPipeline:
    """
    Wraps a ChromaDB collection and a sentence-transformer model to provide
    semantic search over ingested PDF chunks.
    """

    def __init__(self, config: dict):
        rag_cfg = config["rag"]

        self.top_k: int = rag_cfg["top_k"]
        self.similarity_threshold: float = rag_cfg["similarity_threshold"]
        self.embedding_model_name: str = rag_cfg["embedding_model"]
        db_path: str = rag_cfg["db_path"]
        collection_name: str = rag_cfg["collection_name"]

        # Load the embedding model
        self.model = SentenceTransformer(self.embedding_model_name)

        # Connect to the persistent ChromaDB collection
        client = chromadb.PersistentClient(path=db_path)
        self.collection = client.get_collection(collection_name)

    # -----------------------------------------------------------------------
    # TODO 1 of 2 — implement chunk_text()
    # -----------------------------------------------------------------------
    @staticmethod
    def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
        """
        Split *text* into overlapping fixed-size character chunks.

        Requirements:
          - Each chunk is at most *chunk_size* characters long.
          - Consecutive chunks overlap by *chunk_overlap* characters.
          - The step between chunk starts is (chunk_size - chunk_overlap).
          - The last chunk may be shorter than chunk_size.
          - If text is empty, return an empty list.

        This is conceptually the same function used during ingestion
        (see src/pdf_ingestor.py). Implement it here independently so
        you understand how chunking works.

        Hint: a while-loop over a sliding `start` index is the simplest approach.

        Args:
            text:          The full document text to split.
            chunk_size:    Maximum characters per chunk.
            chunk_overlap: Characters shared between consecutive chunks.

        Returns:
            List of text chunk strings.

        Example:
            chunk_text("abcdefghij", chunk_size=4, chunk_overlap=1)
            # step = 4 - 1 = 3
            # → ["abcd", "defg", "ghij", "j"]
            # (position 9 still has content, so the trailing stub is included)
        """
        if not text:
            return []

        chunks = []
        step = chunk_size - chunk_overlap
        start = 0
        while start < len(text):
            chunks.append(text[start : start + chunk_size])
            start += step
        return chunks

    # -----------------------------------------------------------------------
    # TODO 2 of 2 — implement retrieve()
    # -----------------------------------------------------------------------
    def retrieve(self, query: str) -> list[dict]:
        """
        Retrieve the most relevant chunks from the PDF library for *query*.

        Steps you must implement:
          1. Encode *query* into an embedding vector using self.model.
          2. Query self.collection for the top self.top_k nearest chunks.
          3. Convert ChromaDB's L2 distances to cosine-like similarity scores.
             Use the formula:  similarity = 1 / (1 + distance)
             (This maps distance=0 → similarity=1.0, and large distances → ~0.)
          4. Filter out any result whose similarity is below self.similarity_threshold.
          5. Return a list of result dicts, one per surviving chunk, each with keys:
               - "text"       : the chunk text (str)
               - "source"     : the PDF filename (str), from chunk metadata
               - "chunk_index": the chunk's position in that PDF (int)
               - "similarity" : the computed similarity score, rounded to 4 decimals (float)
             Sort results by similarity descending (highest first).

        ChromaDB query API reference:
            results = self.collection.query(
                query_embeddings=[query_embedding],   # list of lists
                n_results=self.top_k,
                include=["documents", "metadatas", "distances"],
            )
            # results["documents"][0]  → list of chunk texts
            # results["metadatas"][0]  → list of metadata dicts
            # results["distances"][0]  → list of L2 distances (lower = closer)

        Args:
            query: The natural-language question or topic to search for.

        Returns:
            List of result dicts (may be empty if nothing passes the threshold).
        """
        # Step 1: encode the query into an embedding vector
        query_embedding = self.model.encode(query).tolist()

        # Step 2: query ChromaDB for the top-k nearest chunks
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k,
            include=["documents", "metadatas", "distances"],
        )

        # Steps 3–4: convert L2 distances to similarities and apply threshold
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

        # Step 5: sort by similarity descending
        output.sort(key=lambda x: x["similarity"], reverse=True)
        return output


# ---------------------------------------------------------------------------
# Convenience function used by the MCP server
# ---------------------------------------------------------------------------

_pipeline: RAGPipeline | None = None


def get_pipeline() -> RAGPipeline:
    """Return a cached RAGPipeline instance (lazy-loaded on first call)."""
    global _pipeline
    if _pipeline is None:
        config = load_config()
        _pipeline = RAGPipeline(config)
    return _pipeline


def query_library(query: str) -> list[dict]:
    """Top-level function called by the MCP server tool."""
    return get_pipeline().retrieve(query)
