from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtWidgets import QDialog

from ui.dialogs.forms.fields import build_dialog_actions
from ui.dialogs.forms.layout_utils import make_dialog_form_layout, make_dialog_root_layout
from ui.window_policy import prepare_non_resizable_window


def setup_form_dialog(dialog: QDialog, *, title: str, min_width: int):
    dialog.setWindowTitle(title)
    dialog.setModal(True)
    dialog.setMinimumWidth(min_width)
    prepare_non_resizable_window(dialog, width=min_width)
    return make_dialog_root_layout(dialog), make_dialog_form_layout()


def add_form_to_root(root, form) -> None:
    root.addLayout(form)


def add_action_row(dialog: QDialog, root, *, confirm_text: str, cancel_text: str):
    btn_cancel, btn_ok, button_row = build_dialog_actions(dialog, confirm_text=confirm_text, cancel_text=cancel_text)
    root.addLayout(button_row)
    return btn_cancel, btn_ok


def wire_dialog_reject(buttons: Iterable, reject) -> None:
    for button in buttons:
        button.clicked.connect(reject)


__all__ = [
    "setup_form_dialog",
    "add_form_to_root",
    "add_action_row",
    "wire_dialog_reject",
]
