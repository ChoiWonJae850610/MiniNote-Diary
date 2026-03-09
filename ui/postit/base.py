from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from ui.postit.common import CARD_RADIUS
from ui.theme import THEME, card_colors


class _PostItCardBase(QWidget):
    def __init__(self, kind: str, parent=None):
        super().__init__(parent)
        self.kind = kind
        self._active = False
        bg_hex, bd_hex = card_colors(kind)
        self._bg = QColor(bg_hex)
        self._bd = QColor(bd_hex)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(THEME.card_shadow_blur)
        shadow.setOffset(0, THEME.card_shadow_offset_y)
        shadow_color = QColor(THEME.color_shadow)
        shadow_color.setAlpha(28)
        shadow.setColor(shadow_color)
        self.setGraphicsEffect(shadow)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def set_active(self, active: bool):
        self._active = active
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(0.5, 0.5, self.width() - 1, self.height() - 1)
        pen = QPen(self._bd, 2)
        if self._active:
            pen = QPen(QColor(self._bd).darker(118), 2)
        painter.setPen(pen)
        painter.setBrush(self._bg)
        painter.drawRoundedRect(rect, CARD_RADIUS, CARD_RADIUS)
