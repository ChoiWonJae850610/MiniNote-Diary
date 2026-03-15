from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QVBoxLayout, QWidget

from ui.layout_metrics import OrderPageLayout
from ui.theme import THEME, dialog_layout_margins
from ui.ui_metrics import CommonSymbolsLayout


def make_dialog_root_layout(dialog: QDialog) -> QVBoxLayout:
    layout = QVBoxLayout(dialog)
    layout.setContentsMargins(*dialog_layout_margins())
    layout.setSpacing(THEME.block_spacing)
    return layout


def make_dialog_form_layout() -> QFormLayout:
    form = QFormLayout()
    form.setLabelAlignment(Qt.AlignLeft)
    form.setFormAlignment(Qt.AlignTop)
    form.setHorizontalSpacing(OrderPageLayout.DETAIL_GRID_HORIZONTAL_SPACING + 2)
    form.setVerticalSpacing(OrderPageLayout.DETAIL_GRID_VERTICAL_SPACING + 2)
    return form


def make_dialog_inline_row(parent: QWidget, *widgets: QWidget, stretch: bool = True) -> QWidget:
    row = QWidget(parent)
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(CommonSymbolsLayout.PANEL_INLINE_SPACING)
    for index, widget in enumerate(widgets):
        layout.addWidget(widget, 1 if index == 0 else 0)
    if stretch:
        layout.addStretch(1)
    return row


__all__ = [
    "make_dialog_form_layout",
    "make_dialog_inline_row",
    "make_dialog_root_layout",
]
