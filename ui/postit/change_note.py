from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout

from ui.postit.base import _PostItCardBase
from ui.theme import plain_text_edit_style


class ChangeNotePostIt(_PostItCardBase):
    text_changed = Signal(str)
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("change", parent=parent)
        self.setMinimumSize(QSize(340, 150))
        self.setMaximumHeight(180)
        self._block = False
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 14)
        root.setSpacing(0)
        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("")
        self.editor.setStyleSheet(plain_text_edit_style())
        self.editor.installEventFilter(self)
        self.editor.setTabChangesFocus(True)
        root.addWidget(self.editor, 1)
        self.editor.textChanged.connect(self._on_text)

    def _on_text(self):
        if not self._block:
            self.text_changed.emit(self.text())

    def set_text(self, text: str):
        self._block = True
        try:
            self.editor.setPlainText(text or "")
        finally:
            self._block = False

    def text(self) -> str:
        return self.editor.toPlainText().rstrip()

    def eventFilter(self, obj, event):
        if obj is self.editor and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
                self.save_requested.emit()
                event.accept()
                return True
        return super().eventFilter(obj, event)
