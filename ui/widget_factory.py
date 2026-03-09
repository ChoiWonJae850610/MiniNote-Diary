from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QCursor, QColor, QFont, QIcon, QPainter, QPixmap
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
    button.setStyleSheet(
        icon_button_override(font_px)
        + f" QPushButton {{ text-align: center; padding: 0; margin: 0; line-height: {THEME.icon_button_size}px; }}"
        + extra_style
    )
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

def make_dialog_button(text: str, parent=None) -> QPushButton:
    button = QPushButton(text, parent)
    apply_button_metrics(button, height=THEME.dialog_button_height)
    return button
