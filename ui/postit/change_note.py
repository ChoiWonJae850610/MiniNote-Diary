
from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtWidgets import QFrame, QPlainTextEdit, QSizePolicy, QVBoxLayout

from ui.postit.base import _PostItCardBase
from ui.postit.layout import (
    POSTIT_CHANGE_NOTE_MIN_WIDTH,
    POSTIT_INNER_BOTTOM_PADDING,
    POSTIT_INNER_SIDE_PADDING,
    POSTIT_INNER_TOP_PADDING,
    POSTIT_MEMO_BODY_HEIGHT,
    POSTIT_ZERO_SPACING,
)
from ui.theme import plain_text_edit_style


class ChangeNotePostIt(_PostItCardBase):
    text_changed = Signal(str)
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__("change", parent=parent)
        self.setMinimumSize(QSize(POSTIT_CHANGE_NOTE_MIN_WIDTH, POSTIT_MEMO_BODY_HEIGHT))
        self._block = False
        self._embedded_mode = False
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root = QVBoxLayout(self)
        self._root = root
        uniform_padding = min(POSTIT_INNER_SIDE_PADDING, POSTIT_INNER_TOP_PADDING, POSTIT_INNER_BOTTOM_PADDING)
        root.setContentsMargins(uniform_padding, uniform_padding, uniform_padding, uniform_padding)
        root.setSpacing(POSTIT_ZERO_SPACING)
        self.editor = QPlainTextEdit(self)
        self.editor.setPlaceholderText("")
        self.editor.setStyleSheet(plain_text_edit_style())
        self.editor.setFrameShape(QFrame.NoFrame)
        self.editor.installEventFilter(self)
        self.editor.setTabChangesFocus(True)
        root.addWidget(self.editor, 1)
        self.editor.textChanged.connect(self._on_text)

    def _on_text(self):
        if not self._block:
            self.text_changed.emit(self.text())


    def set_embedded_mode(self, embedded: bool) -> None:
        self._embedded_mode = embedded
        if embedded:
            self._root.setContentsMargins(0, 0, 0, 0)
            self.editor.setPlaceholderText("메모를 입력하세요")
            self.editor.document().setDocumentMargin(12)
            self.editor.setViewportMargins(0, 0, 0, 0)
        else:
            uniform_padding = min(POSTIT_INNER_SIDE_PADDING, POSTIT_INNER_TOP_PADDING, POSTIT_INNER_BOTTOM_PADDING)
            self._root.setContentsMargins(uniform_padding, uniform_padding, uniform_padding, uniform_padding)
            self.editor.document().setDocumentMargin(6)
            self.editor.setViewportMargins(0, 0, 0, 0)
        self.update()

    def set_text(self, text: str):
        self._block = True
        try:
            self.editor.setPlainText(text or "")
        finally:
            self._block = False
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def text(self) -> str:
        return self.editor.toPlainText().rstrip()

    def paintEvent(self, event):
        if self._embedded_mode:
            return
        super().paintEvent(event)

    def eventFilter(self, obj, event):
        if obj is self.editor and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter) and event.modifiers() & Qt.ControlModifier:
                self.save_requested.emit()
                event.accept()
                return True
        return super().eventFilter(obj, event)
