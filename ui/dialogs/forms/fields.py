from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QLineEdit, QPlainTextEdit, QFrame, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from ui.messages import Buttons
from ui.layout_metrics import DialogLayout
from ui.theme import THEME, hint_label_style, input_line_edit_style, title_label_style
from ui.button_layout_utils import make_dialog_button_row
from ui.widget_factory_buttons import make_dialog_button


def configure_text_field(field: QLineEdit) -> QLineEdit:
    field.setStyleSheet(input_line_edit_style())
    return field


def build_hint_label(text: str, parent: QWidget) -> QLabel:
    label = QLabel(text, parent)
    label.setStyleSheet(hint_label_style())
    return label


def build_dialog_actions(parent: QWidget, *, confirm_text: str, cancel_text: str = Buttons.CANCEL):
    btn_cancel = make_dialog_button(cancel_text, parent, role="cancel")
    btn_confirm = make_dialog_button(confirm_text, parent, role="confirm")
    return btn_cancel, btn_confirm, make_dialog_button_row([btn_cancel, btn_confirm])




def configure_plain_text_field(field: QPlainTextEdit) -> QPlainTextEdit:
    return field


def build_section_title(text: str, parent: QWidget, *, font_px: int | None = None) -> QLabel:
    label = QLabel(text, parent)
    label.setStyleSheet(title_label_style(font_px=font_px or (THEME.section_title_font_px + 1)))
    return label


def build_dialog_card(parent: QWidget, *, object_name: str = "dialogSection") -> tuple[QFrame, QVBoxLayout]:
    card = QFrame(parent)
    card.setObjectName(object_name)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(DialogLayout.CARD_MARGIN, DialogLayout.CARD_MARGIN, DialogLayout.CARD_MARGIN, DialogLayout.CARD_MARGIN)
    layout.setSpacing(DialogLayout.CARD_ROW_SPACING)
    return card, layout


def build_dialog_grid(parent: QWidget | None = None) -> QGridLayout:
    grid = QGridLayout(parent)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setHorizontalSpacing(DialogLayout.FORM_HORIZONTAL_SPACING)
    grid.setVerticalSpacing(DialogLayout.FORM_VERTICAL_SPACING)
    return grid


def add_dialog_grid_row(grid: QGridLayout, row: int, label: QLabel, field: QWidget, *, top_align: bool = False) -> None:
    alignment = Qt.AlignTop if top_align else Qt.AlignVCenter
    grid.addWidget(label, row, 0, alignment)
    if top_align:
        grid.addWidget(field, row, 1, Qt.AlignTop)
    else:
        grid.addWidget(field, row, 1)


def build_labeled_value_row(parent: QWidget, label_text: str, value_widget: QWidget, *, label_width: int, spacing: int, label_builder, top_align: bool = False) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(spacing)
    label = label_builder(label_text, parent)
    label.setFixedWidth(label_width)
    alignment = Qt.AlignTop if top_align else Qt.AlignVCenter
    row.addWidget(label, 0, alignment)
    row.addWidget(value_widget, 1)
    return row

__all__ = [
    "add_dialog_grid_row",
    "build_dialog_actions",
    "build_dialog_card",
    "build_dialog_grid",
    "build_hint_label",
    "build_labeled_value_row",
    "build_section_title",
    "configure_plain_text_field",
    "configure_text_field"
]
