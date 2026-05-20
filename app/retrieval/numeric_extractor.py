# Once the correct page is identified, GPT-4o reads the extracted tables from tables.json
# and returns the exact numeric value from the table.
# No interpolation or calculations are allowed.

from openai import OpenAI
from app.config import NUMERIC_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def extract_numeric_value(
    query: str,
    page_num: int,
    tables: list[list[list]],
    page_text: str,
) -> str:
    """
    Given the raw tables from a page, returns the exact numeric cell value
    needed to answer the query. Returns "NOT FOUND" if the value is not present.

    Tables are passed as raw list-of-lists (from pdfplumber) so the model sees
    structured rows and columns rather than pre-formatted text.
    """
    # Pass tables as raw Python list-of-lists which preserves row/column structure
    table_blocks = []
    for i, table in enumerate(tables):
        table_blocks.append(f"### Table {i}\n{table}\n")
    tables_text = "\n".join(table_blocks)

    prompt = (
        f"You are a performance-calculation assistant for a Boeing 737 manual.\n\n"
        f"User query:\n{query}\n\n"
        f"Page number: {page_num}\n\n"
        f"Page text (for context):\n{page_text}\n\n"
        f"Extracted tables (JSON list-of-lists):\n{tables_text}\n\n"
        f"Your task:\n"
        f"1. Locate the correct table and correct row & column needed to answer the query.\n"
        f"2. If a cell contains multiple values separated by newlines, split them and select the correct one.\n"
        f"3. Use ONLY the information inside these tables.\n"
        f"4. Return ONLY the numeric answer (e.g. '52.2 (1000 KG)') with no explanation.\n"
        f"5. Do NOT compute, estimate, interpolate, or guess. If the value is not present, say: NOT FOUND\n\n"
        f"Now return ONLY the numeric result."
    )

    try:
        response = _get_client().chat.completions.create(
            model=NUMERIC_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    
    # Fallback if extraction fails:
    except Exception as e:
        print(f"[numeric_extractor] Failed: {e}")
        return "NOT FOUND"
