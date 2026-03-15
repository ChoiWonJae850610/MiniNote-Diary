from __future__ import annotations

from typing import Any


def to_text(value: Any) -> str:
    return '' if value is None else str(value)
