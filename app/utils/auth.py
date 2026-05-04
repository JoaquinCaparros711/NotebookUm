"""Small auth helpers for extracting the X-User-ID header."""
from __future__ import annotations

from typing import Optional


def parse_x_user_id(raw_value: Optional[str]) -> Optional[int]:
    """Parse the X-User-ID header value.

    Returns an int when present and valid, None when header not provided.
    Raises ValueError when the header is present but not a valid integer.
    """
    if raw_value is None:
        return None
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        raise ValueError("Invalid X-User-ID header value") from None
