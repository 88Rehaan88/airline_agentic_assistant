"""
Tool: get_current_datetime

Returns the current UTC date and time in a human-readable format.
No external API is required since Python's standard datetime library is sufficient.
"""
from datetime import datetime, timezone


def get_current_datetime() -> str:
    """Returns the current UTC date and time as a readable string."""
    now = datetime.now(timezone.utc)     # Get current UTC time:

    # Format date/time into aviation-style readable output (eg. "Wednesday, 20 May 2026 – 12:00Z"):
    day_of_week = now.strftime("%A")
    readable_date = now.strftime("%d %B %Y")
    time_zulu = now.strftime("%H:%MZ")
    return f"{day_of_week}, {readable_date} – {time_zulu}"
