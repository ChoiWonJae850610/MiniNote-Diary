from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.postit.common import FIELD_H
from ui.postit.layout import (
    POSTIT_GRID_H_SPACING,
    POSTIT_INNER_BOTTOM_PADDING,
    POSTIT_INNER_SIDE_PADDING,
    POSTIT_INNER_TOP_PADDING,
    POSTIT_UNIFORM_ROW_SPACING,
)
from ui.theme import THEME, field_label_style


class PostItFieldLabel(QLabel):
    def __init__(self, text: str, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setFixedWidth(THEME.field_label_width)
        self.setFixedHeight(FIELD_H)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setStyleSheet(field_label_style())


class PostItBodyLayout(QVBoxLayout):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setContentsMargins(
            POSTIT_INNER_SIDE_PADDING,
            POSTIT_INNER_TOP_PADDING,
            POSTIT_INNER_SIDE_PADDING,
            POSTIT_INNER_BOTTOM_PADDING,
        )
        self.setSpacing(POSTIT_UNIFORM_ROW_SPACING)


class PostItFormRow(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(POSTIT_GRID_H_SPACING)

    def add_item(self, widget, stretch: int = 0):
        self.addWidget(widget, stretch)
        return widget



def make_field_label(text: str, parent: QWidget | None = None) -> PostItFieldLabel:
    return PostItFieldLabel(text, parent)



def make_form_row(*items) -> PostItFormRow:
    row = PostItFormRow()
    for item in items:
        if isinstance(item, tuple):
            widget, stretch = item
            row.addWidget(widget, stretch)
        else:
            row.addWidget(item, 0)
    return row
