from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class ImagePreview(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("이미지 업로드 영역")
        self._pixmap = None

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
        self.setText("이미지 업로드 영역")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_view()

    def update_view(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
        else:
            # ensure pixmap cleared when no image
            if self.pixmap() is not None:
                self.clear()
                self.setText("이미지 업로드 영역")
