"""
LLM reranker — Uses GPT-4o-mini to score FAISS candidates by relevance
and return only the top RERANK_TOP_K chunks.
"""
# In case of failure, we fall back to FAISS order so retrieval never hard-crashes. 

import json
from openai import OpenAI
from app.config import RERANK_MODEL, RERANK_TOP_K

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def rerank(query: str, candidates: list[dict]) -> list[dict]:
    """
    Uses GPT to rerank FAISS-retrieved chunks and keep only
    the most relevant ones for the final context.
    """
    if not candidates:
        return []
    
    # If less than 2 chunks are retrieved, reranking is unnecessary:
    if len(candidates) <= RERANK_TOP_K:
        return candidates

    # Formatting the chunks: 
    formatted = "\n\n".join(
        f"[CHUNK {i} | Page {c['page']}]\n{c['text'][:1500]}" # truncation to avoid heavy token usage
        for i, c in enumerate(candidates)
    )

    prompt = (
        f"You are a retrieval reranker for a Boeing 737 operations manual.\n\n"
        f"User query:\n{query}\n\n"
        f"Score each chunk from 1 to 5 based on how directly it answers the query.\n"
        f"Return ONLY a JSON array: "
        f'[{{"index": 0, "score": 3}}, {{"index": 1, "score": 5}}, ...]\n\n'
        f"Chunks:\n{formatted}"
    )

    try:
        response = _get_client().chat.completions.create(
            model=RERANK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        
        # Parse JSON scores returned by the model:
        scores: list[dict] = json.loads(raw)

        # Sort chunks by descending order of scores:
        ranked = sorted(scores, key=lambda x: x["score"], reverse=True)
        top_indices = [entry["index"] for entry in ranked[:RERANK_TOP_K]]
        return [candidates[i] for i in top_indices if i < len(candidates)]

    except Exception as e:

        # Fall back to FAISS ordering if reranking fails:
        print(f"[reranker] Reranking failed, using FAISS order: {e}")
        return candidates[:RERANK_TOP_K]
