# Serves raw pdfplumber tables for a given page number at lookup time.
# Built offline by scripts/build_tables.py — we never open the PDF during a request.

import json
from app.config import TABLES_PATH

_table_data: list[dict] | None = None


def _load() -> None:
    global _table_data
    with open(TABLES_PATH, "r", encoding="utf-8") as f:
        _table_data = json.load(f)


def get_tables_for_page(page_num: int) -> list[list[list]]:
    if _table_data is None:
        _load()

    return [entry["table"] for entry in _table_data if entry["page"] == page_num]
