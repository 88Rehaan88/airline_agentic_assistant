"""
One-time offline script. Run from the project root:

    python scripts/build_index.py

Reads the PDF from data/, embeds every page with OpenAI,
and writes the FAISS index + chunk metadata to index/.
"""

import sys
import os

# Allow imports from the project root (app.*, etc.)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables before initializing any OpenAI client
from dotenv import load_dotenv
load_dotenv()

from app.retrieval.indexer import build_index

PDF_PATH = "data/Boeing B737 Manual.pdf"

if __name__ == "__main__":
    if not os.path.exists(PDF_PATH):     # Makes sure the PDF exists before indexing
        print(f"[ERROR] PDF not found at: {PDF_PATH}")
        sys.exit(1)

    # Build the FAISS index and chunk metadata:
    count = build_index(PDF_PATH)
    print(f"\n[OK] Indexed {count} pages successfully.")
