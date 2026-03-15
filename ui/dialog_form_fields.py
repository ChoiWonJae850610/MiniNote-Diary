from __future__ import annotations

from PySide6.QtWidgets import QLabel, QLineEdit, QWidget

from ui.messages import Buttons
from ui.page_builders_common import make_dialog_button_row, make_dialog_form_layout, make_dialog_inline_row
from ui.theme import hint_label_style, input_line_edit_style
from ui.widget_factory import make_dialog_button


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


__all__ = [
    "build_dialog_actions",
    "build_hint_label",
    "configure_text_field",
    "make_dialog_form_layout",
    "make_dialog_inline_row",
]
