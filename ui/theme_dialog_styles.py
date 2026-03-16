from __future__ import annotations

from ui.theme_tokens import THEME


def dialog_layout_margins() -> tuple[int, int, int, int]:
    return (14, 14, 14, 14)


def dialog_inner_margins() -> tuple[int, int, int, int]:
    return (20, 18, 20, 18)


def compact_popup_margins() -> tuple[int, int, int, int]:
    return (8, 8, 8, 8)


def status_row_margins() -> tuple[int, int, int, int]:
    return (14, 10, 14, 10)


def page_layout_margins(extra_x: int = 0, extra_y: int = 0) -> tuple[int, int, int, int]:
    t = THEME
    return (t.page_padding_x + extra_x, t.page_padding_y + extra_y, t.page_padding_x + extra_x, t.page_padding_y + extra_y)
