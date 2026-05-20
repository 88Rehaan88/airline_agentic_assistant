# FAISS returns several pages that might hold the right performance table.
# This step asks GPT-4o to choose the single page most likely to contain the correct performance table

from openai import OpenAI
from app.config import NUMERIC_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def choose_best_numeric_chunk(query: str, candidates: list[dict]) -> dict | None:
    """
    Uses GPT-4o to select the best matching page/chunk for
    a numeric/table-based aviation query.
    """
    if not candidates:
        return None

    if len(candidates) == 1:
        return candidates[0]

    # Full page text is usually unnecessary for page selection.
    # So only a short preview of each chunk is shown to reduce token usage.
    labeled = "\n\n---\n\n".join(
        f"### Chunk {i}\n(Page {c['page']})\n{c['text'][:2000]}"
        for i, c in enumerate(candidates)
    )

    prompt = (
        f"You are assisting with aircraft performance calculations.\n\n"
        f"User query:\n{query}\n\n"
        f"Examine the retrieved chunks below. Each chunk is a page from a Boeing 737 performance manual.\n"
        f"Identify which ONE chunk is most likely to contain the specific performance table "
        f"needed to answer this query — paying close attention to context clues like "
        f"'Takeoff' vs 'Landing', 'Climb Limit' vs 'Field Limit', and exact table headers.\n\n"
        f"Respond with ONLY a single integer — the chunk index (0, 1, 2, ...). "
        f"If none are useful, respond with -1.\n\n"
        f"Chunks:\n{labeled}"
    )

    try:
        response = _get_client().chat.completions.create(
            model=NUMERIC_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()
        idx = int(raw)
        
        # Make sure the returned index is valid:
        if idx < 0 or idx >= len(candidates):
            return None

        return candidates[idx]

    except Exception as e:
        # If page selection fails, retrieval falls back to normal reranker. 
        print(f"[numeric_selector] Failed, using first candidate: {e}") # Log the error for debugging
        return None
