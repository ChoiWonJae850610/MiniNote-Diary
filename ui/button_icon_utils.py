from __future__ import annotations

from PySide6.QtCore import QRect, Qt, QSize
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QPushButton


def build_centered_glyph_icon(glyph: str, *, font_px: int, color: str, size_px: int = 20) -> QIcon:
    canvas_size = max(size_px + 2, font_px + 12)
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

    inset = 3
    target_rect = QRect(inset, inset, canvas_size - (inset * 2), canvas_size - (inset * 2))
    text_rect = painter.boundingRect(target_rect, Qt.AlignmentFlag.AlignCenter, glyph)
    text_rect.moveCenter(target_rect.center())
    painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, glyph)
    painter.end()
    return QIcon(pixmap)


def apply_glyph_icon(button: QPushButton, glyph: str, *, font_px: int, color: str) -> QPushButton:
    button.setText("")
    icon_edge = max(12, min(button.width(), button.height()) - 8)
    button.setIcon(build_centered_glyph_icon(glyph, font_px=font_px, color=color, size_px=icon_edge))
    button.setIconSize(QSize(icon_edge, icon_edge))
    return button


__all__ = [
    'apply_glyph_icon',
    'build_centered_glyph_icon',
]
