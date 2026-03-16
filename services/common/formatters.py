from __future__ import annotations


def digits_only(value: str | int | None) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def format_commas_from_digits(digits: str | int | None) -> str:
    digits = digits_only(digits)
    if not digits:
        return ""
    try:
        return f"{int(digits):,}"
    except (TypeError, ValueError):
        return str(digits or "")


def int_from_any(value: str | int | None) -> int:
    digits = digits_only(value)
    return int(digits) if digits else 0
