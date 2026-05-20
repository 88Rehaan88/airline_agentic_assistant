# Detects whether a query is asking for a numeric/table-based performance value.
# Used to route queries into the numeric path instead of the normal reranker path.

import re

# Performance/table keywords:
# (These terms appear frequently in Boeing performance tables and
# help us distinguish numeric queries from general “text” queries.)
_TABLE_KEYWORDS = [
    "takeoff", "calculate", "compute", "landing", "approach",
    "oat", "pressure altitude",
    "climb", "limit", "field length",
    "corrected", "runway",
    "kg", "kgs", "lb", "lbs",
    "ft", "feet",
    "°c", "degrees", "temperature",
    "slope",
    "v1", "v2", "vr",
    "field limit", "climb limit", "limit weight",
    "performance",
]


def is_numeric_query(query: str) -> bool:
    """
    Returns True if the query looks like a numeric performance table question.
    # Classification rule:
     A query is treated as numeric only when both conditions hold:
        1) It includes at least two numbers
        2) It references performance/table terminology
    """
    q = query.lower().strip()


    # Since Table queries almost always include multiple numbers (OAT, weight, altitude, etc.)
    numbers = re.findall(r"\d[\d,]*", q)
    has_table_word = any(k in q for k in _TABLE_KEYWORDS)

    return len(numbers) >= 2 and has_table_word
