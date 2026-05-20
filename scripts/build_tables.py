# Extracts all tables from the PDF and saves them to index/tables.json.
# Run after build_index.py — numeric queries use this file, not the FAISS index.

# Run using:
# python scripts/build_tables.py

import json
import os
import sys

# Allow imports from the project root: 
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

import pdfplumber
from app.config import TABLES_PATH, INDEX_DIR

PDF_PATH = "data/Boeing B737 Manual.pdf"


def build_tables(pdf_path: str, output_path: str) -> int:
    """
    Extracts raw tables from every PDF page using pdfplumber
    and saves them as list-of-lists JSON.
    """    # Scans each page with pdfplumber; stores raw list-of-lists (not markdown strings).
    os.makedirs(INDEX_DIR, exist_ok=True)

    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            page_num = i + 1

            try:
                tables = page.extract_tables()
            except Exception as e:
                print(f"[build_tables] Skipping page {page_num}: {e}")
                continue

            if not tables:
                continue

            for table in tables:
                # Keep the raw list-of-lists format because
                # the numeric extractor needs row/column structure.
                all_tables.append({
                    "page": page_num,
                    "table": table,
                })

            if page_num % 20 == 0:       # Logging progress every 20 pages
                print(f"[build_tables] Scanned {page_num}/{total} pages...")
    
    # Save extracted tables into tables.json:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_tables, f, indent=2, ensure_ascii=False)

    print(f"[build_tables] Saved {len(all_tables)} tables -> {output_path}")
    return len(all_tables)


if __name__ == "__main__":
    
    # Makes sure the PDF exists before extraction:
    if not os.path.exists(PDF_PATH):
        print(f"[ERROR] PDF not found: {PDF_PATH}")
        sys.exit(1)

    # Extracts and saves all tables to tables.json:
    count = build_tables(PDF_PATH, TABLES_PATH)
    print(f"[OK] Done. {count} tables extracted.")
