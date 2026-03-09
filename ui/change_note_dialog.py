from __future__ import annotations

from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout

from ui.theme import THEME
from ui.widget_factory import make_dialog_button, make_dialog_button_row


class ChangeNoteDialog(QDialog):
    def __init__(self, initial_text: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle('메모')
        self.setModal(True)
        self.setMinimumSize(THEME.note_dialog_min_width, THEME.note_dialog_min_height)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(THEME.page_padding, THEME.page_padding, THEME.page_padding, THEME.page_padding)
        layout.setSpacing(THEME.block_spacing)
        self.edit = QTextEdit(self)
        self.edit.setPlainText(initial_text or '')
        self.edit.setPlaceholderText('메모를 입력하세요.')
        layout.addWidget(self.edit, 1)
        btn_cancel = make_dialog_button('취소', self, role='cancel')
        btn_ok = make_dialog_button('확인', self, role='confirm')
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self.accept)
        layout.addLayout(make_dialog_button_row([btn_cancel, btn_ok]))

    def get_text(self) -> str:
        return self.edit.toPlainText().strip()
