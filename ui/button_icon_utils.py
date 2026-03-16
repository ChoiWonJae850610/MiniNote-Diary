from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QPushButton


def build_centered_glyph_icon(glyph: str, *, font_px: int, color: str, size_px: int = 20) -> QIcon:
    canvas_size = max(size_px, font_px + 6)
    pixmap = QPixmap(canvas_size, canvas_size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
    painter.setPen(QColor(color))

    font = QFont()
    font.setPixelSize(font_px)
    font.setBold(True)
    painter.setFont(font)

    text_rect = painter.boundingRect(QRect(0, 0, canvas_size, canvas_size), Qt.AlignmentFlag.AlignCenter, glyph)
    text_rect.moveCenter(QRect(0, 0, canvas_size, canvas_size).center())
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, glyph)
    painter.end()
    return QIcon(pixmap)


def apply_glyph_icon(button: QPushButton, glyph: str, *, font_px: int, color: str) -> QPushButton:
    button.setText("")
    button.setIcon(build_centered_glyph_icon(glyph, font_px=font_px, color=color))
    icon_w = max(12, button.width() - 2)
    icon_h = max(12, button.height() - 2)
    button.setIconSize(QSize(icon_w, icon_h))
    return button


__all__ = [
    'apply_glyph_icon',
    'build_centered_glyph_icon',
]
