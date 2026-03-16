from __future__ import annotations

from PySide6.QtWidgets import QDialog

from ui.dialogs.base import _BaseThemedDialog
from ui.dialogs.message_boxes import ConfirmActionDialog, SimpleMessageDialog
from ui.dialogs.status_dialogs import ValidationStatusDialog
from ui.dialogs.work_order_load_dialog import WorkOrderLoadDialog
from ui.messages import Buttons


def show_info(parent, title: str, message: str) -> int:
    return SimpleMessageDialog(title, message, button_text=Buttons.OK, parent=parent).exec()


def show_warning(parent, title: str, message: str) -> int:
    return SimpleMessageDialog(title, message, button_text=Buttons.OK, parent=parent).exec()


def show_error(parent, title: str, message: str) -> int:
    return SimpleMessageDialog(title, message, button_text=Buttons.OK, parent=parent).exec()


def ask_confirm(parent, title: str, message: str, *, confirm_text: str = Buttons.OK, cancel_text: str = Buttons.CANCEL) -> bool:
    return ConfirmActionDialog(title, message, confirm_text=confirm_text, cancel_text=cancel_text, parent=parent).exec() == QDialog.Accepted


__all__ = [
    "_BaseThemedDialog",
    "ConfirmActionDialog",
    "SimpleMessageDialog",
    "ValidationStatusDialog",
    "WorkOrderLoadDialog",
    "ask_confirm",
    "show_error",
    "show_info",
    "show_warning",
]
