from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QToolButton, QVBoxLayout, QWidget, QLabel

from ui.theme import THEME, title_badge_style


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
        self.setFixedHeight(THEME.section_badge_height)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet(title_badge_style(**style_kwargs))



class FolderTabHeader(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self._button = QToolButton(self)
        self._button.setText(text)
        self._button.setCursor(Qt.ArrowCursor)
        self._button.setEnabled(False)
        self._button.setFixedHeight(THEME.dialog_button_height)
        self._button.setMinimumWidth(84)
        self._button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._button.setStyleSheet(self._button_style())

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._button, 0, Qt.AlignLeft)
        root.addStretch(1)

    def _button_style(self) -> str:
        t = THEME
        return (
            'QToolButton{'
            f'padding:0 16px;'
            f'border:1px solid {t.color_border};'
            f'font-weight:700;'
            f'min-height:{t.dialog_button_height}px;'
            f'max-height:{t.dialog_button_height}px;'
            f'border-top-left-radius:{t.control_radius + 5}px;'
            f'border-top-right-radius:{t.control_radius + 5}px;'
            'border-bottom-left-radius:0px;'
            'border-bottom-right-radius:0px;'
            f'background:{t.color_surface};'
            f'color:{t.color_text};'
            'border-bottom:none;'
            '}'
        )

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self._label = QLabel(text, self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setFixedHeight(THEME.dialog_button_height)
        self._label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._label.setStyleSheet(self._label_style())

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._label, 0, Qt.AlignLeft)
        root.addStretch(1)

    def _label_style(self) -> str:
        t = THEME
        return (
            "QLabel{"
            f"background:{t.color_surface};"
            f"color:{t.color_text};"
            f"border:1px solid {t.color_border};"
            "border-bottom:none;"
            f"border-top-left-radius:{t.control_radius + 5}px;"
            f"border-top-right-radius:{t.control_radius + 5}px;"
            "border-bottom-left-radius:0px;"
            "border-bottom-right-radius:0px;"
            f"font-size:{t.section_title_font_px}px;"
            "font-weight:700;"
            "padding:0 14px;"
            "}"
        )
