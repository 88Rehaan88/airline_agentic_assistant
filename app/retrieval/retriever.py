# Runs vector search over the pre-built FAISS index.
# FAISS returns a broader candidate pool first, which later gets refined
# using reranking or numeric/table-based retrieval path.

import json
import numpy as np
import faiss

from app.retrieval.embedder import embed_text
from app.config import FAISS_INDEX_PATH, CHUNKS_PATH, FAISS_FETCH_K

_index: faiss.Index | None = None
_chunks: list[dict] | None = None


def _load() -> None:
    """
    Loads FAISS index and chunk metadata into memory once at runtime.
    """    
    global _index, _chunks
    _index = faiss.read_index(FAISS_INDEX_PATH)
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        _chunks = json.load(f)
    print(f"[retriever] Loaded {len(_chunks)} chunks from index.")


def search(query: str) -> list[dict]:
    """
    Performs semantic vector search over the FAISS index
    and returns the top 'k' chunks.
    """
    if _index is None:
        _load()

    # Converting user query into vector embedding::
    vec = embed_text(query)
    if vec is None:
        return []

    # Convert embedding into FAISS compatible numpy format:
    query_vec = np.array([vec], dtype="float32")
    _, indices = _index.search(query_vec, FAISS_FETCH_K) # Retrieve top semantic matches

    results = []
    for idx in indices[0]: # Ignore invalid entries returned by FAISS:
        if idx == -1:
            continue
        results.append(_chunks[idx])

    return results
