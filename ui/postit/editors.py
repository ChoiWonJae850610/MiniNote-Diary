from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit

from services.formatters import digits_only, format_commas_from_digits
from ui.postit.common import FIELD_H
from ui.theme import editing_line_edit_style, read_only_line_edit_style


class _ClickToEditLineEdit(QLineEdit):
    committed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFixedHeight(FIELD_H)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setTextMargins(0, 0, 0, 0)
        self._edit_start_text = ""
        self._edit_enabled = True
        self._apply_style(editing=False)

    def _apply_style(self, editing: bool):
        self.setStyleSheet(editing_line_edit_style() if editing else read_only_line_edit_style())

    def set_edit_enabled(self, enabled: bool):
        self._edit_enabled = bool(enabled)
        if not self._edit_enabled:
            self.setReadOnly(True)
            self._apply_style(editing=False)

    def _begin_edit(self):
        if not self._edit_enabled:
            return
        self._edit_start_text = self.text()
        self.setReadOnly(False)
        self._apply_style(editing=True)
        self.selectAll()

    def activate_for_input(self):
        if not self._edit_enabled:
            return
        if self.isReadOnly():
            self._begin_edit()
        self.setFocus(Qt.OtherFocusReason)
        self.selectAll()

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if self._edit_enabled and self.isReadOnly() and event.reason() in (Qt.TabFocusReason, Qt.BacktabFocusReason):
            self._begin_edit()

    def mousePressEvent(self, event):
        if self._edit_enabled and event.button() == Qt.LeftButton and self.isReadOnly():
            self._begin_edit()
            self.setFocus()
        super().mousePressEvent(event)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._commit_lock()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._commit_lock()
            self.deselect()
            event.accept()
            return
        if event.key() == Qt.Key_Tab:
            self._commit_lock()
            self.focusNextPrevChild(True)
            event.accept()
            return
        if event.key() == Qt.Key_Backtab:
            self._commit_lock()
            self.focusNextPrevChild(False)
            event.accept()
            return
        if event.key() == Qt.Key_Escape:
            self.setText(self._edit_start_text)
            self.setReadOnly(True)
            self._apply_style(editing=False)
            self.deselect()
            event.accept()
            return
        super().keyPressEvent(event)

    def _commit_lock(self):
        if not self.isReadOnly():
            changed = self.text() != self._edit_start_text
            self.setReadOnly(True)
            self._apply_style(editing=False)
            if changed:
                self.committed.emit(self.text())

    def set_text_silent(self, text: str):
        old = self.blockSignals(True)
        try:
            self.setText(text or "")
            self._edit_start_text = self.text()
        finally:
            self.blockSignals(old)


class _MoneyLineEdit(_ClickToEditLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(r"[0-9,]*", self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._fmt = False
        self.textChanged.connect(self._on_text)
        self._apply_style(editing=False)

    def _on_text(self, text: str):
        if self._fmt:
            return
        formatted = format_commas_from_digits(text)
        if formatted == text:
            return
        self._fmt = True
        try:
            self.setText(formatted)
            self.setCursorPosition(len(formatted))
        finally:
            self._fmt = False

    def digits(self) -> str:
        return digits_only(self.text())


class _QtyClickToEditLineEdit(_ClickToEditLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setValidator(QRegularExpressionValidator(r"[0-9]*", self))
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

    def _commit_lock(self):
        if not self.isReadOnly():
            digits = digits_only(self.text())
            changed = digits != digits_only(self._edit_start_text)
            self.set_text_silent(digits)
            self.setReadOnly(True)
            self._apply_style(editing=False)
            if changed:
                self.committed.emit(digits)
