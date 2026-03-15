from __future__ import annotations

from typing import Iterable

from PySide6.QtWidgets import QDialog, QVBoxLayout

from ui.dialog_form_fields import build_dialog_actions
from ui.dialog_layout_utils import make_dialog_form_layout, make_dialog_root_layout


def setup_form_dialog(dialog: QDialog, *, title: str, min_width: int) -> tuple[QVBoxLayout, object]:
    dialog.setWindowTitle(title)
    dialog.setModal(True)
    dialog.setMinimumWidth(min_width)
    root = make_dialog_root_layout(dialog)
    form = make_dialog_form_layout()
    root.addLayout(form)
    return root, form


def add_dialog_action_row(dialog: QDialog, root: QVBoxLayout, *, confirm_text: str, cancel_text: str) -> tuple[object, object]:
    btn_cancel, btn_confirm, button_row = build_dialog_actions(dialog, confirm_text=confirm_text, cancel_text=cancel_text)
    root.addLayout(button_row)
    return btn_cancel, btn_confirm


def wire_dialog_reject(buttons: Iterable[object], reject) -> None:
    for button in buttons:
        button.clicked.connect(reject)


__all__ = [
    'add_dialog_action_row',
    'setup_form_dialog',
    'wire_dialog_reject',
]
