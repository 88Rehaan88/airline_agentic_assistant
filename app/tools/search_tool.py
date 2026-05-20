# # Main entrypoint for document retrieval.
# Routes queries to either the numeric path (table lookup) or normal path (reranker).
# but both return the same output format: (formatted_text, chunks)

from app.retrieval.retriever import search
from app.retrieval.reranker import rerank
from app.retrieval.query_type import is_numeric_query
from app.retrieval.numeric_selector import choose_best_numeric_chunk
from app.retrieval.table_loader import get_tables_for_page
from app.retrieval.numeric_extractor import extract_numeric_value


def search_documentation(query: str) -> tuple[str, list[dict]]:
    """
    Handles retrieval for both.
    - Numeric/table based queries (2+ numbers + performance keyword):
        FAISS top-8 → chunk selector picks ONE → table extraction → exact value

    Normal queries:
        FAISS top-8 → reranker keeps top-2 → format text
    """
    
    # Initial FAISS retrieval:
    candidates = search(query)

    if not candidates:
        return "No relevant content found in the manual.", []

    # Numeric path (direct table lookup for performance queries):
    if is_numeric_query(query):

        # Multiple pages may look semantically similar,
        # So GPT-4o selects the most likely page containing the correct table.
        chunk = choose_best_numeric_chunk(query, candidates)

        if chunk is not None:

            # Load extracted tables for the selected page:
            tables = get_tables_for_page(chunk["page"])

            if tables:

                # Extract the exact numeric value from the table:
                value = extract_numeric_value(query, chunk["page"], tables, chunk["text"])
                header = f"[{chunk['document_title']} | Page {chunk['page']}]"
                # Prefix helps the agent understand the numeric result clearly
                # instead of only seeing units like "(1000 KG)"
                formatted = f"{header}\nThe answer is: {value}"
                return formatted, [chunk]

    # If numeric extraction fails, fall back to normal reranking flow.

    # Normal text retrieval path:
    chunks = rerank(query, candidates)

    blocks = []

    # Format the text for the agent to read:
    for chunk in chunks:
        header = f"[{chunk['document_title']} | Page {chunk['page']}]"
        blocks.append(f"{header}\n{chunk['text']}")

    formatted = "\n\n---\n\n".join(blocks)
    return formatted, chunks
