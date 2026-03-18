from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPixmap

from ui.theme import THEME


class ImagePreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = None
        self._placeholder_pixmap = None
        self._placeholder_text = "no image"
        self.set_placeholder_pixmap(None)

    def set_placeholder_pixmap(self, pixmap: QPixmap | None):
        self._placeholder_pixmap = pixmap
        if self._pixmap is None:
            self.update()

    def set_image(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            raise ValueError("이미지를 불러올 수 없습니다.")
        self._pixmap = pix
        self.update_view()

    def clear_image(self):
        self._pixmap = None
        self.clear()
        self.update_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_view()

    def paintEvent(self, event):
        if self._pixmap is not None:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        self._paint_placeholder(painter)
        painter.end()

    def _paint_placeholder(self, painter: QPainter):
        rect = self.contentsRect()
        if rect.width() <= 0 or rect.height() <= 0:
            return

        font = QFont(self.font())
        font_px = max(14, min(24, int(min(rect.width(), rect.height()) * 0.055)))
        font.setPixelSize(font_px)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(THEME.color_text_muted))
        painter.drawText(rect, Qt.AlignCenter, self._placeholder_text)

    def update_view(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
            return

        self.clear()
        self.update()
