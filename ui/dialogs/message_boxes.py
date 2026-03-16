from __future__ import annotations

from PySide6.QtWidgets import QLabel

from ui.button_layout_utils import make_dialog_button_row
from ui.dialogs.base import _BaseThemedDialog
from ui.widget_factory_buttons import make_dialog_button


class SimpleMessageDialog(_BaseThemedDialog):
    def __init__(self, title: str, message: str, *, button_text: str, parent=None):
        super().__init__(title=title, parent=parent)
        message_label = QLabel(message, self.card)
        message_label.setObjectName("dialogMessage")
        message_label.setWordWrap(True)
        self.body.addWidget(message_label)

        button = make_dialog_button(button_text, self.card, role="close")
        button.clicked.connect(self.accept)
        self.body.addLayout(make_dialog_button_row([button]))


class ConfirmActionDialog(_BaseThemedDialog):
    def __init__(self, title: str, message: str, confirm_text: str, cancel_text: str, parent=None):
        super().__init__(title=title, parent=parent)
        message_label = QLabel(message, self.card)
        message_label.setObjectName("dialogMessage")
        message_label.setWordWrap(True)
        self.body.addWidget(message_label)

        self.cancel_button = make_dialog_button(cancel_text, self.card, role="cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.confirm_button = make_dialog_button(confirm_text, self.card, role="confirm")
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setDefault(True)

        self.body.addLayout(make_dialog_button_row([self.cancel_button, self.confirm_button]))


__all__ = [
    "ConfirmActionDialog",
    "SimpleMessageDialog",
]
