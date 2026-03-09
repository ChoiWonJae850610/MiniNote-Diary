from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QStyle, QWidget

from ui.theme import THEME


def _new_pixmap(size: int) -> tuple[QPixmap, QPainter]:
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing, True)
    return pix, p


def make_image_outline_icon(size: int = 16, color: str | None = None) -> QIcon:
    pix, p = _new_pixmap(size)
    pen = QPen(QColor(color or THEME.color_icon), 1.8)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    inset = 2.0
    frame_w = size - inset * 2
    frame_h = size - inset * 2
    p.drawRoundedRect(inset, inset, frame_w, frame_h, 2.2, 2.2)
    p.drawEllipse(size * 0.63, size * 0.34, size * 0.14, size * 0.14)
    p.drawLine(size * 0.25, size * 0.73, size * 0.45, size * 0.50)
    p.drawLine(size * 0.45, size * 0.50, size * 0.57, size * 0.61)
    p.drawLine(size * 0.57, size * 0.61, size * 0.77, size * 0.39)
    p.end()
    return QIcon(pix)


def make_save_icon(size: int = 16, color: str | None = None) -> QIcon:
    pix, p = _new_pixmap(size)
    pen = QPen(QColor(color or THEME.color_text_on_primary), 1.7)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    inset = 2.0
    body = size - inset * 2
    p.drawRoundedRect(inset, inset, body, body, 1.8, 1.8)
    p.drawRect(size * 0.28, size * 0.20, size * 0.30, size * 0.22)
    p.drawRect(size * 0.28, size * 0.60, size * 0.44, size * 0.18)
    p.drawLine(size * 0.68, size * 0.22, size * 0.68, size * 0.44)
    p.end()
    return QIcon(pix)


def make_calendar_icon(size: int = 16, color: str | None = None) -> QIcon:
    pix, p = _new_pixmap(size)
    p.setPen(QPen(QColor(color or THEME.color_icon), 2))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(1, 2, size - 2, size - 3, 3, 3)
    p.drawLine(2, 6, size - 3, 6)
    p.drawLine(5, 1, 5, 5)
    p.drawLine(size - 6, 1, size - 6, 5)
    p.end()
    return QIcon(pix)


def standard_icon(widget: QWidget, candidates: list[QStyle.StandardPixmap], fallback: QIcon | None = None) -> QIcon:
    style = widget.style()
    for candidate in candidates:
        icon = style.standardIcon(candidate)
        if not icon.isNull():
            return icon
    return fallback or QIcon()
