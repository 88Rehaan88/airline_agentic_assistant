# Offline pipeline that converts the PDF manual into a searchable FAISS index.
# Each page is embedded separately along with extracted table text,
# then stored for runtime semantic retrieval.

import json
import os
import fitz
import pdfplumber
import numpy as np
import faiss

from app.retrieval.embedder import embed_text
from app.config import FAISS_INDEX_PATH, CHUNKS_PATH, INDEX_DIR


def _format_table(table: list[list]) -> str:
    """
    Converts raw pdfplumber table rows into a readable text format that 
    gpt can reliably read.
    """
    rows = []
    for row in table:
        cells = [str(cell).strip() if cell is not None else "" for cell in row]
        rows.append(" | ".join(cells))
    return "\n".join(rows)


def _extract_tables_text(pdf_path: str) -> dict[int, str]:
    """
    Extracts all tables from the PDF using pdfplumber.
    Tables are stored separately by page number.
    Pages with no tables are absent from the dict.
    """
    page_tables: dict[int, str] = {}

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_num = i + 1
            try:
                tables = page.extract_tables()
            except Exception:
                continue

            if not tables:
                continue

            formatted_blocks = []

            # Convert each table into readable text:
            for t_idx, table in enumerate(tables):
                formatted = _format_table(table)
                if formatted.strip():
                    formatted_blocks.append(f"[TABLE {t_idx + 1}]\n{formatted}")

            if formatted_blocks:
                page_tables[page_num] = "\n\n".join(formatted_blocks)

    return page_tables


def build_index(pdf_path: str) -> int:
    """
    Builds the FAISS vector index and saves chunk metadata. 
    """
    os.makedirs(INDEX_DIR, exist_ok=True)

    document_title = os.path.splitext(os.path.basename(pdf_path))[0]

    print(f"[indexer] Extracting tables with pdfplumber...")
    page_tables = _extract_tables_text(pdf_path)
    print(f"[indexer] Found tables on {len(page_tables)} pages.")

    print(f"[indexer] Opening: {pdf_path}")
    doc = fitz.open(pdf_path)

    embeddings = []
    chunks = []

    # Processing the PDF page by page:
    for i, page in enumerate(doc):
        page_num = i + 1
        plain_text = page.get_text("text").strip()

        # Add extracted tables into the chunk text so FAISS
        # can better retrieve numeric/table heavy pages.
        if page_num in page_tables:
            enriched_text = plain_text + "\n\n" + page_tables[page_num]
        else:
            enriched_text = plain_text

        # Some pages may contain only diagrams/images, so we add a placeholder:
        if not enriched_text.strip():
            enriched_text = "[no text]"
        
        # Converting the text into vector embeddings:
        vec = embed_text(enriched_text)
        if vec is None:
            print(f"[indexer] Skipping page {page_num} - embedding failed")
            continue

        # Storing the embedding and metadata linked to each page:
        embeddings.append(vec)
        chunks.append({
            "page": page_num,
            "text": enriched_text,
            "document_title": document_title,
        })

        if page_num % 20 == 0:       # logging progress every 20 pages
            print(f"[indexer] Embedded {page_num}/{len(doc)} pages...")

    doc.close()

    if not embeddings:
        raise RuntimeError("No pages were successfully embedded.")

    matrix = np.array(embeddings, dtype="float32")   # Convert embeddings into FAISS compatible matrix:
    dimension = matrix.shape[1]

    # Creates a L2 FAISS index since L2 works well for small datasets like ours:
    index = faiss.IndexFlatL2(dimension) 
    index.add(matrix)

    # Saving the FAISS index:
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"[indexer] Saved FAISS index -> {FAISS_INDEX_PATH}")

    # Saving the chunk metadata:
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"[indexer] Saved chunks metadata -> {CHUNKS_PATH}")

    return len(chunks)   # Return the number of pages successfully indexed.
