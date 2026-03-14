from __future__ import annotations

from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout

from ui.messages import Buttons, DialogTitles, Placeholders
from ui.theme import THEME, dialog_layout_margins
from ui.widget_factory import make_dialog_button, make_dialog_button_row


class ChangeNoteDialog(QDialog):
    def __init__(self, initial_text: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.NOTE)
        self.setModal(True)
        self.setMinimumSize(THEME.note_dialog_min_width, THEME.note_dialog_min_height)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(*dialog_layout_margins())
        layout.setSpacing(THEME.block_spacing)
        self.edit = QTextEdit(self)
        self.edit.setPlainText(initial_text or '')
        self.edit.setPlaceholderText(Placeholders.MEMO)
        layout.addWidget(self.edit, 1)
        btn_cancel = make_dialog_button(Buttons.CANCEL, self, role='cancel')
        btn_ok = make_dialog_button(Buttons.OK, self, role='confirm')
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        layout.addLayout(make_dialog_button_row([btn_cancel, btn_ok]))

    def get_text(self) -> str:
        return self.edit.toPlainText().strip()
