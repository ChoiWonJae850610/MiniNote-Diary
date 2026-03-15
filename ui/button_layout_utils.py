from __future__ import annotations

from typing import Iterable

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ui.theme import THEME


def make_button_row(widgets: Iterable[QWidget], *, stretch: bool = True, spacing: int | None = None) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(THEME.row_spacing if spacing is None else spacing)
    if stretch:
        row.addStretch(1)
    for widget in widgets:
        row.addWidget(widget)
    return row


def make_dialog_button_row(buttons: Iterable[QPushButton], *, stretch: bool = True, spacing: int | None = None) -> QHBoxLayout:
    return make_button_row(buttons, stretch=stretch, spacing=spacing)


__all__ = [
    "make_button_row",
    "make_dialog_button_row",
]
