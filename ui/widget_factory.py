from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QPushButton

from ui.theme import THEME, icon_button_override


def apply_button_metrics(button: QPushButton, *, width: int | None = None, height: int | None = None, font_px: int | None = None, bold: bool = True, point_cursor: bool = True) -> QPushButton:
    if width is not None and height is not None:
        button.setFixedSize(width, height)
    elif width is not None:
        button.setFixedWidth(width)
    elif height is not None:
        button.setFixedHeight(height)

    font = button.font()
    if font_px is not None:
        font.setPixelSize(font_px)
    font.setBold(bold)
    button.setFont(font)

    if point_cursor:
        button.setCursor(QCursor(Qt.PointingHandCursor))
    return button


def apply_icon_button_metrics(button: QPushButton, *, font_px: int, object_name: str | None = None, tooltip: str | None = None, extra_style: str = "") -> QPushButton:
    apply_button_metrics(
        button,
        width=THEME.icon_button_size,
        height=THEME.icon_button_size,
        font_px=font_px,
        bold=True,
        point_cursor=True,
    )
    button.setContentsMargins(0, 0, 0, 0)
    if object_name:
        button.setObjectName(object_name)
    if tooltip:
        button.setToolTip(tooltip)
    button.setStyleSheet(icon_button_override(font_px) + " QPushButton { text-align: center; padding: 0; margin: 0; }" + extra_style)
    return button


def make_dialog_button(text: str, parent=None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, height=THEME.dialog_button_height)
    return button
