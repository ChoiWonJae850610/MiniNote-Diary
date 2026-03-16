from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QPushButton, QWidget

from ui.theme import THEME, icon_button_override


def set_widget_tooltip(widget: QWidget, tooltip: str) -> QWidget:
    widget.setToolTip(tooltip)
    return widget


def refresh_style(widget: QWidget) -> QWidget:
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()
    return widget


def apply_button_metrics(
    button: QPushButton,
    *,
    width: int | None = None,
    height: int | None = None,
    font_px: int | None = None,
    bold: bool = True,
    point_cursor: bool = True,
) -> QPushButton:
    if width is not None:
        button.setFixedWidth(width)
    if height is not None:
        button.setFixedHeight(height)
    font = button.font()
    font.setPixelSize(font_px or THEME.base_font_px)
    font.setBold(bold)
    button.setFont(font)
    if point_cursor:
        button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    return button


def apply_button_role_style(button: QPushButton, *, object_name: str | None = None) -> QPushButton:
    if object_name:
        button.setObjectName(object_name)
    return refresh_style(button)


def apply_icon_button_metrics(
    button: QPushButton,
    *,
    font_px: int | None = None,
    object_name: str = 'iconAction',
    tooltip: str = '',
    size: int | None = None,
) -> QPushButton:
    button_size = size or THEME.icon_button_size
    apply_button_metrics(
        button,
        width=button_size,
        height=button_size,
        font_px=font_px or THEME.icon_button_font_px,
    )
    set_widget_tooltip(button, tooltip)
    button.setText(button.text())
    button.setStyleSheet(icon_button_override(font_px or THEME.icon_button_font_px))
    return apply_button_role_style(button, object_name=object_name)


__all__ = [
    'apply_button_metrics',
    'apply_button_role_style',
    'apply_icon_button_metrics',
    'refresh_style',
    'set_widget_tooltip',
]
