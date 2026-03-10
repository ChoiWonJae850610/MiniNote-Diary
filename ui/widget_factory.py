from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QCursor, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QPushButton

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


def make_button(text: str, parent=None, *, width: int | None = None, height: int | None = None, object_name: str | None = None, font_px: int | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, width=width, height=height, font_px=font_px)
    if object_name:
        button.setObjectName(object_name)
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
    button.setStyleSheet(
        icon_button_override(font_px)
        + f" QPushButton {{ text-align: center; padding: 0; margin: 0; line-height: {THEME.icon_button_size}px; }}"
        + extra_style
    )
    return button


def make_icon_button(*, parent=None, object_name: str, tooltip: str = "", icon: QIcon | None = None, text: str = "", font_px: int | None = None, icon_size: int | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_icon_button_metrics(
        button,
        font_px=font_px or (THEME.icon_button_font_px + 2),
        object_name=object_name,
        tooltip=tooltip,
    )
    if icon is not None and not icon.isNull():
        button.setText("")
        button.setIcon(icon)
        size = icon_size or THEME.icon_size_md
        button.setIconSize(button.iconSize().__class__(size, size))
    return button


def build_centered_glyph_icon(glyph: str, *, font_px: int, color: str, canvas_size: int | None = None) -> QIcon:
    size = canvas_size or THEME.icon_button_size
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing, True)
    painter.setRenderHint(QPainter.TextAntialiasing, True)

    font = QFont()
    font.setPixelSize(font_px)
    font.setBold(True)
    painter.setFont(font)
    painter.setPen(QColor(color))
    painter.drawText(QRectF(0, 0, size, size), Qt.AlignCenter, glyph)
    painter.end()
    return QIcon(pixmap)


def apply_glyph_icon(button: QPushButton, glyph: str, *, font_px: int, color: str) -> QPushButton:
    button.setText("")
    button.setIcon(build_centered_glyph_icon(glyph, font_px=font_px, color=color))
    button.setIconSize(button.size())
    return button


def make_dialog_button(text: str, parent=None, *, role: str | None = None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, height=THEME.dialog_button_height)
    if role == "confirm":
        button.setObjectName("dialogConfirm")
    elif role == "cancel":
        button.setObjectName("dialogCancel")
    elif role == "close":
        button.setObjectName("dialogClose")
    return button


def make_dialog_button_row(buttons: Iterable[QPushButton], *, stretch: bool = True, spacing: int | None = None) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(THEME.row_spacing if spacing is None else spacing)
    if stretch:
        row.addStretch(1)
    for button in buttons:
        row.addWidget(button)
    return row


def make_inline_icon_button(*, parent=None, tooltip: str = '', icon: QIcon | None = None, size: int | None = None) -> QPushButton:
    button = QPushButton(parent)
    apply_button_metrics(button, width=size or THEME.field_height, height=size or THEME.field_height, font_px=THEME.base_font_px, bold=False, point_cursor=True)
    if tooltip:
        button.setToolTip(tooltip)
    button.setContentsMargins(0, 0, 0, 0)
    if icon is not None and not icon.isNull():
        button.setIcon(icon)
        icon_dim = max(12, (size or THEME.field_height) - 10)
        button.setIconSize(button.iconSize().__class__(icon_dim, icon_dim))
    button.setStyleSheet(icon_button_override(THEME.base_font_px) + ' QPushButton { text-align: center; padding: 0; margin: 0; }')
    return button
