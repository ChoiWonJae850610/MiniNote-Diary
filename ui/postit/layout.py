
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from ui.theme import THEME, title_badge_style

POSTIT_TAB_INSET_LEFT = THEME.filter_panel_margin_h + 22
POSTIT_TAB_OVERLAP = -12
POSTIT_BODY_HEIGHT = THEME.postit_bar_max_height
POSTIT_FOOTER_HEIGHT = THEME.section_badge_height
POSTIT_WRAP_HEIGHT = THEME.dialog_button_height + POSTIT_BODY_HEIGHT


def embedded_tab_style(*, active: bool = True) -> str:
    t = THEME
    base = (
        "QLabel{"
        f"padding:0 16px;"
        f"min-height:{t.dialog_button_height}px;"
        f"max-height:{t.dialog_button_height}px;"
        f"border:1px solid {t.color_border};"
        f"border-top-left-radius:{t.control_radius + 6}px;"
        f"border-top-right-radius:{t.control_radius + 6}px;"
        f"border-bottom-left-radius:{t.control_radius + 2}px;"
        f"border-bottom-right-radius:{t.control_radius + 2}px;"
        f"font-size:{t.section_title_font_px}px;"
        "font-weight:700;"
    )
    if active:
        return base + f"background:{t.color_surface};" + f"color:{t.color_text};" + "}"
    return base + f"background:{t.color_surface_muted};" + f"color:{t.color_text_soft};" + "}"


def folder_tab_style(*, active: bool = True) -> str:
    return embedded_tab_style(active=active)


class SectionContainer(QWidget):
    def __init__(self, header_widget: QWidget, body_widget: QWidget, *, parent=None, spacing: int = POSTIT_TAB_OVERLAP, header_alignment=Qt.AlignLeft):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(spacing)
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
        self._label = QLabel(text, self)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setFixedHeight(THEME.dialog_button_height)
        self._label.setMinimumWidth(92)
        self._label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._label.setStyleSheet(embedded_tab_style(active=True))

        root = QHBoxLayout(self)
        root.setContentsMargins(POSTIT_TAB_INSET_LEFT, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._label, 0, Qt.AlignLeft)
        root.addStretch(1)
