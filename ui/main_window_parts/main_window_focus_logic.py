from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QAbstractSpinBox, QApplication, QComboBox, QLineEdit, QPlainTextEdit, QTextEdit, QWidget

if TYPE_CHECKING:
    from ui.main_window import MainWindow


class MainWindowFocusLogic:
    @staticmethod
    def is_text_input_widget(widget) -> bool:
        return isinstance(widget, (QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QAbstractSpinBox))

    @staticmethod
    def has_input_ancestor(widget) -> bool:
        current = widget
        while current is not None:
            if MainWindowFocusLogic.is_text_input_widget(current):
                return True
            current = current.parentWidget()
        return False

    @staticmethod
    def handle_event_filter(window: "MainWindow", obj, event) -> bool:
        if event.type() != QEvent.MouseButtonPress:
            return False
        focused = QApplication.focusWidget()
        target = obj if isinstance(obj, QWidget) else None
        if focused is None or target is None:
            return False
        if not MainWindowFocusLogic.is_text_input_widget(focused):
            return False
        if target is focused or focused.isAncestorOf(target) or MainWindowFocusLogic.has_input_ancestor(target):
            return False
        focused.clearFocus()
        return False
