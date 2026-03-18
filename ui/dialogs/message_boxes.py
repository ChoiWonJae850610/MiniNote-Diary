from __future__ import annotations

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QHBoxLayout, QLabel

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

        self.confirm_button = make_dialog_button(confirm_text, self.card, role="confirm")
        self.confirm_button.clicked.connect(self.accept)
        self.confirm_button.setDefault(False)
        self.confirm_button.setAutoDefault(False)

        self.cancel_button = make_dialog_button(cancel_text, self.card, role="cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setDefault(False)
        self.cancel_button.setAutoDefault(False)

        self.setFocusPolicy(self.focusPolicy())
        self.setFocus()

        button_row = QHBoxLayout()
        button_row.setSpacing(self.body.spacing())
        button_row.addStretch(1)
        button_row.addWidget(self.confirm_button)
        button_row.addWidget(self.cancel_button)
        button_row.addStretch(1)
        self.body.addLayout(button_row)

        self.shortcut_yes = QShortcut(QKeySequence("Y"), self)
        self.shortcut_yes.activated.connect(self.accept)
        self.shortcut_no = QShortcut(QKeySequence("N"), self)
        self.shortcut_no.activated.connect(self.reject)


__all__ = [
    "ConfirmActionDialog",
    "SimpleMessageDialog",
]
