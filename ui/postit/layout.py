from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from ui.theme import title_badge_style


class SectionContainer(QWidget):
    def __init__(self, header_widget: QWidget, body_widget: QWidget, *, parent=None, spacing: int = 6, header_alignment=Qt.AlignLeft):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(spacing)
        self.header_widget = header_widget
        self.body_widget = body_widget
        if header_alignment is None:
            root.addWidget(header_widget)
        else:
            root.addWidget(header_widget, 0, header_alignment)
        root.addWidget(body_widget, 1)


class SectionTitleBadge(QLabel):
    def __init__(self, text: str, parent=None, **style_kwargs):
        super().__init__(text, parent)
        self.setFixedHeight(28)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet(title_badge_style(**style_kwargs))
