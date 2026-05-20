# Used both during offline index creation and runtime FAISS retrieval.

from openai import OpenAI
from app.config import EMBED_MODEL

# Lazy initialization makes sure the API key is loaded before creating the OpenAI client.

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def embed_text(text: str) -> list[float] | None:
    """
    Converts text into vector embeddings for semantic similarity search.
    """
    text = text.strip()
    
    # Prevents embedding empty strings:
    if not text:
        return None

    try:
        response = _get_client().embeddings.create(model=EMBED_MODEL, input=text)
        return response.data[0].embedding
    except Exception as e:
        print(f"[embedder] Error: {e}")  # Fallback if embedding request fails:
        return None
