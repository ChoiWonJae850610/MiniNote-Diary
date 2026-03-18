from __future__ import annotations

from PySide6.QtWidgets import QDialog, QTextEdit

from ui.messages import Buttons, DialogTitles, Placeholders
from ui.theme import THEME
from ui.button_layout_utils import make_dialog_button_row
from ui.widget_factory_buttons import make_dialog_button
from ui.dialogs.forms.layout_utils import make_dialog_root_layout
from ui.window_policy import lock_window_size


class ChangeNoteDialog(QDialog):
    def __init__(self, initial_text: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle(DialogTitles.NOTE)
        self.setModal(True)
        self.setMinimumSize(THEME.note_dialog_min_width, THEME.note_dialog_min_height)
        layout = make_dialog_root_layout(self)
        self.edit = QTextEdit(self)
        self.edit.setPlainText(initial_text or '')
        self.edit.setPlaceholderText(Placeholders.MEMO)
        layout.addWidget(self.edit, 1)
        btn_cancel = make_dialog_button(Buttons.CANCEL, self, role='cancel')
        btn_ok = make_dialog_button(Buttons.OK, self, role='confirm')
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        layout.addLayout(make_dialog_button_row([btn_cancel, btn_ok]))
        lock_window_size(self, width=THEME.note_dialog_min_width, height=THEME.note_dialog_min_height)

    def get_text(self) -> str:
        return self.edit.toPlainText().strip()
