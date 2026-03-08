from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap




class ImagePreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self._pixmap = None
        self._placeholder_pixmap = None
        self.set_placeholder_pixmap(None)

    def set_placeholder_pixmap(self, pixmap: QPixmap | None):
        self._placeholder_pixmap = pixmap
        if self._pixmap is None:
            self.update_view()

    def set_image(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            raise ValueError("이미지를 불러올 수 없습니다.")
        self._pixmap = pix
        self.update_view()

    def clear_image(self):
        """현재 이미지(픽스맵)와 표시를 완전히 초기화."""
        self._pixmap = None
        self.clear()
        self.update_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_view()

    def update_view(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
            return

        self.clear()
        if self._placeholder_pixmap and not self._placeholder_pixmap.isNull():
            scaled = self._placeholder_pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
