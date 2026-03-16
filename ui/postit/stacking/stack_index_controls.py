from __future__ import annotations

from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QWidget

from ui.messages import Symbols
from ui.postit.common import MAX_POSTIT_CARDS
from ui.postit.layout import (
    POSTIT_FOOTER_GAP,
    POSTIT_SINGLE_STRETCH,
    POSTIT_ZERO_MARGIN,
    POSTIT_ZERO_STRETCH,
)
from ui.theme import THEME, disabled_index_button_style, index_button_style


class PostItIndexControls:
    def __init__(self, owner: QWidget, footer_host: QWidget):
        self._owner = owner
        self.footer_host = footer_host
        self.index_row = QHBoxLayout(self.footer_host)
        self.index_row.setContentsMargins(POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN, POSTIT_ZERO_MARGIN)
        self.index_row.setSpacing(POSTIT_FOOTER_GAP)
        self.index_row.addStretch(POSTIT_SINGLE_STRETCH)
        self.index_buttons: list[QToolButton] = []
        self.plus_button: QToolButton | None = None

    def _make_button(self, text: str) -> QToolButton:
        button = QToolButton(self._owner)
        button.setText(text)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedSize(THEME.icon_button_size, THEME.icon_button_size)
        button.setFocusPolicy(Qt.NoFocus)
        return button

    def rebuild(
        self,
        *,
        item_count: int,
        active_index: int,
        on_select,
        on_add,
    ) -> tuple[list[QToolButton], QToolButton]:
        while self.index_row.count() > 1:
            item = self.index_row.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.index_buttons = []
        for idx in range(item_count):
            button = self._make_button(str(idx + 1))
            button.clicked.connect(lambda _=False, i=idx: on_select(i))
            self.index_buttons.append(button)
            self.index_row.addWidget(button, POSTIT_ZERO_STRETCH)
        self.plus_button = self._make_button(Symbols.ADD)
        self.plus_button.clicked.connect(on_add)
        self.index_row.addWidget(self.plus_button, POSTIT_ZERO_STRETCH)
        self.apply_active(active_index=active_index, item_count=item_count)
        return self.index_buttons, self.plus_button

    def apply_active(self, *, active_index: int, item_count: int) -> None:
        for idx, button in enumerate(self.index_buttons):
            button.setStyleSheet(index_button_style(idx == active_index))
        if self.plus_button is not None:
            enabled = item_count < MAX_POSTIT_CARDS
            self.plus_button.setEnabled(enabled)
            self.plus_button.setStyleSheet(index_button_style(False) if enabled else disabled_index_button_style())


__all__ = ["PostItIndexControls"]
